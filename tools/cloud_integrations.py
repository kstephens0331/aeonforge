"""
Cloud Platform Integrations for Aeonforge
AWS, Azure, Google Cloud Platform, and other cloud services
"""

import os
import json
import requests
import boto3
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.web import WebSiteManagementClient
from google.cloud import storage, functions_v1, run_v1
from google.oauth2 import service_account
import docker
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging
import tempfile
import zipfile
from platform_integrations import PlatformIntegration, PlatformCredentials, DeploymentResult

@dataclass
class CloudResource:
    """Cloud resource information"""
    resource_type: str
    name: str
    id: str
    url: Optional[str] = None
    status: str = "unknown"
    metadata: Dict[str, Any] = None

class AWSIntegration(PlatformIntegration):
    """Amazon Web Services integration"""
    
    def __init__(self, credentials: PlatformCredentials):
        super().__init__(credentials)
        self.region = credentials.additional_config.get("region", "us-east-1")
        
        # Initialize AWS clients
        self.session = boto3.Session(
            aws_access_key_id=credentials.api_key,
            aws_secret_access_key=credentials.secret_key,
            region_name=self.region
        )
        
        self.s3 = self.session.client('s3')
        self.lambda_client = self.session.client('lambda')
        self.ecs = self.session.client('ecs')
        self.rds = self.session.client('rds')
        self.cloudformation = self.session.client('cloudformation')
        self.apigateway = self.session.client('apigateway')
    
    def validate_credentials(self) -> bool:
        try:
            self.session.client('sts').get_caller_identity()
            return True
        except Exception as e:
            self.logger.error(f"AWS credential validation failed: {e}")
            return False
    
    def get_platform_info(self) -> Dict[str, Any]:
        try:
            identity = self.session.client('sts').get_caller_identity()
            regions = self.session.client('ec2').describe_regions()
            
            return {
                "platform": "aws",
                "account_id": identity.get("Account"),
                "user_id": identity.get("UserId"),
                "arn": identity.get("Arn"),
                "regions": [r["RegionName"] for r in regions["Regions"]],
                "current_region": self.region,
                "features": ["s3", "lambda", "ecs", "rds", "api_gateway", "cloudformation", "ec2"]
            }
        except Exception as e:
            return {"platform": "aws", "error": str(e)}
    
    def deploy_static_site(self, project_path: str, bucket_name: str) -> DeploymentResult:
        """Deploy static site to S3 with CloudFront"""
        try:
            # Create S3 bucket
            self.s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': self.region} if self.region != 'us-east-1' else {}
            )
            
            # Configure bucket for static website hosting
            self.s3.put_bucket_website(
                Bucket=bucket_name,
                WebsiteConfiguration={
                    'IndexDocument': {'Suffix': 'index.html'},
                    'ErrorDocument': {'Key': 'error.html'}
                }
            )
            
            # Upload files
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    local_path = os.path.join(root, file)
                    s3_path = os.path.relpath(local_path, project_path).replace("\\", "/")
                    
                    content_type = self._get_content_type(file)
                    
                    self.s3.upload_file(
                        local_path, 
                        bucket_name, 
                        s3_path,
                        ExtraArgs={'ContentType': content_type, 'ACL': 'public-read'}
                    )
            
            website_url = f"http://{bucket_name}.s3-website-{self.region}.amazonaws.com"
            
            return DeploymentResult(
                success=True,
                platform="aws",
                url=website_url,
                deployment_id=bucket_name
            )
            
        except Exception as e:
            return DeploymentResult(
                success=False,
                platform="aws",
                error_message=str(e)
            )
    
    def deploy_lambda_function(self, function_code: str, function_name: str,
                              runtime: str = "python3.9") -> DeploymentResult:
        """Deploy Lambda function"""
        try:
            # Create deployment package
            with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
                with zipfile.ZipFile(tmp.name, 'w') as zip_file:
                    zip_file.writestr('lambda_function.py', function_code)
                
                tmp.seek(0)
                zip_content = tmp.read()
            
            # Create Lambda function
            response = self.lambda_client.create_function(
                FunctionName=function_name,
                Runtime=runtime,
                Role=f"arn:aws:iam::{self.session.client('sts').get_caller_identity()['Account']}:role/lambda-execution-role",
                Handler='lambda_function.lambda_handler',
                Code={'ZipFile': zip_content}
            )
            
            # Create API Gateway to trigger Lambda
            api_response = self.apigateway.create_rest_api(
                name=f"{function_name}-api",
                description=f"API for {function_name}"
            )
            
            api_id = api_response['id']
            api_url = f"https://{api_id}.execute-api.{self.region}.amazonaws.com/prod/{function_name}"
            
            return DeploymentResult(
                success=True,
                platform="aws",
                url=api_url,
                deployment_id=response['FunctionArn']
            )
            
        except Exception as e:
            return DeploymentResult(
                success=False,
                platform="aws",
                error_message=str(e)
            )
    
    def create_rds_database(self, db_name: str, db_engine: str = "postgres",
                           instance_class: str = "db.t3.micro") -> Dict[str, Any]:
        """Create RDS database instance"""
        try:
            response = self.rds.create_db_instance(
                DBName=db_name,
                DBInstanceIdentifier=f"{db_name}-instance",
                DBInstanceClass=instance_class,
                Engine=db_engine,
                MasterUsername="admin",
                MasterUserPassword="TempPassword123!",  # Should be generated securely
                AllocatedStorage=20,
                VpcSecurityGroupIds=[],
                PubliclyAccessible=True
            )
            
            return {
                "success": True,
                "instance_id": response['DBInstance']['DBInstanceIdentifier'],
                "endpoint": response['DBInstance'].get('Endpoint', {}).get('Address', ''),
                "port": response['DBInstance'].get('Endpoint', {}).get('Port', 5432)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _get_content_type(self, filename: str) -> str:
        """Get content type for file"""
        content_types = {
            '.html': 'text/html',
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.json': 'application/json',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml'
        }
        
        ext = os.path.splitext(filename.lower())[1]
        return content_types.get(ext, 'application/octet-stream')

class AzureIntegration(PlatformIntegration):
    """Microsoft Azure integration"""
    
    def __init__(self, credentials: PlatformCredentials):
        super().__init__(credentials)
        self.subscription_id = credentials.additional_config.get("subscription_id")
        self.resource_group = credentials.additional_config.get("resource_group", "aeonforge-rg")
        
        # Initialize Azure clients
        self.credential = DefaultAzureCredential()
        self.resource_client = ResourceManagementClient(self.credential, self.subscription_id)
        self.web_client = WebSiteManagementClient(self.credential, self.subscription_id)
    
    def validate_credentials(self) -> bool:
        try:
            list(self.resource_client.resource_groups.list())
            return True
        except Exception as e:
            self.logger.error(f"Azure credential validation failed: {e}")
            return False
    
    def get_platform_info(self) -> Dict[str, Any]:
        try:
            subscription = self.resource_client.subscriptions.get(self.subscription_id)
            resource_groups = list(self.resource_client.resource_groups.list())
            
            return {
                "platform": "azure",
                "subscription_id": self.subscription_id,
                "subscription_name": subscription.display_name,
                "resource_groups": [rg.name for rg in resource_groups],
                "features": ["app_service", "functions", "storage", "sql_database", "cosmos_db", "container_instances"]
            }
        except Exception as e:
            return {"platform": "azure", "error": str(e)}
    
    def deploy_web_app(self, project_path: str, app_name: str,
                      runtime_stack: str = "NODE|16-lts") -> DeploymentResult:
        """Deploy web app to Azure App Service"""
        try:
            # Ensure resource group exists
            self.resource_client.resource_groups.create_or_update(
                self.resource_group,
                {"location": "eastus"}
            )
            
            # Create App Service Plan
            plan_name = f"{app_name}-plan"
            
            # Create Web App
            web_app = self.web_client.web_apps.begin_create_or_update(
                self.resource_group,
                app_name,
                {
                    "location": "eastus",
                    "kind": "app,linux",
                    "properties": {
                        "serverFarmId": f"/subscriptions/{self.subscription_id}/resourceGroups/{self.resource_group}/providers/Microsoft.Web/serverfarms/{plan_name}",
                        "siteConfig": {
                            "linuxFxVersion": runtime_stack,
                            "appSettings": [
                                {"name": "WEBSITES_ENABLE_APP_SERVICE_STORAGE", "value": "false"}
                            ]
                        }
                    }
                }
            ).result()
            
            app_url = f"https://{app_name}.azurewebsites.net"
            
            return DeploymentResult(
                success=True,
                platform="azure",
                url=app_url,
                deployment_id=web_app.id
            )
            
        except Exception as e:
            return DeploymentResult(
                success=False,
                platform="azure",
                error_message=str(e)
            )

class GCPIntegration(PlatformIntegration):
    """Google Cloud Platform integration"""
    
    def __init__(self, credentials: PlatformCredentials):
        super().__init__(credentials)
        self.project_id = credentials.project_id
        
        # Initialize GCP clients
        if credentials.additional_config and "service_account_json" in credentials.additional_config:
            service_account_info = json.loads(credentials.additional_config["service_account_json"])
            self.credentials = service_account.Credentials.from_service_account_info(service_account_info)
        else:
            self.credentials = None
        
        self.storage_client = storage.Client(credentials=self.credentials, project=self.project_id)
        self.functions_client = functions_v1.CloudFunctionsServiceClient(credentials=self.credentials)
        self.run_client = run_v1.ServicesClient(credentials=self.credentials)
    
    def validate_credentials(self) -> bool:
        try:
            list(self.storage_client.list_buckets())
            return True
        except Exception as e:
            self.logger.error(f"GCP credential validation failed: {e}")
            return False
    
    def get_platform_info(self) -> Dict[str, Any]:
        try:
            buckets = list(self.storage_client.list_buckets())
            
            return {
                "platform": "gcp",
                "project_id": self.project_id,
                "buckets_count": len(buckets),
                "features": ["cloud_storage", "cloud_functions", "cloud_run", "firestore", "app_engine"]
            }
        except Exception as e:
            return {"platform": "gcp", "error": str(e)}
    
    def deploy_static_site(self, project_path: str, bucket_name: str) -> DeploymentResult:
        """Deploy static site to Cloud Storage"""
        try:
            # Create bucket
            bucket = self.storage_client.bucket(bucket_name)
            bucket.create(location="US")
            
            # Configure bucket for website hosting
            bucket.configure_website(main_page_suffix="index.html", not_found_page="404.html")
            
            # Upload files
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    local_path = os.path.join(root, file)
                    blob_path = os.path.relpath(local_path, project_path).replace("\\", "/")
                    
                    blob = bucket.blob(blob_path)
                    blob.upload_from_filename(local_path)
                    blob.make_public()
            
            website_url = f"https://storage.googleapis.com/{bucket_name}/index.html"
            
            return DeploymentResult(
                success=True,
                platform="gcp",
                url=website_url,
                deployment_id=bucket_name
            )
            
        except Exception as e:
            return DeploymentResult(
                success=False,
                platform="gcp",
                error_message=str(e)
            )
    
    def deploy_cloud_function(self, function_code: str, function_name: str,
                             runtime: str = "python39") -> DeploymentResult:
        """Deploy Cloud Function"""
        try:
            # Create deployment package
            with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
                with zipfile.ZipFile(tmp.name, 'w') as zip_file:
                    zip_file.writestr('main.py', function_code)
                    zip_file.writestr('requirements.txt', 'functions-framework==3.*')
                
                # Upload to Cloud Storage
                bucket_name = f"{self.project_id}-functions"
                bucket = self.storage_client.bucket(bucket_name)
                blob = bucket.blob(f"{function_name}.zip")
                blob.upload_from_filename(tmp.name)
            
            # Deploy function
            parent = f"projects/{self.project_id}/locations/us-central1"
            
            function = {
                "name": f"{parent}/functions/{function_name}",
                "source_archive_url": f"gs://{bucket_name}/{function_name}.zip",
                "entry_point": "hello_world",
                "runtime": runtime,
                "https_trigger": {}
            }
            
            operation = self.functions_client.create_function(
                parent=parent,
                function=function
            )
            
            result = operation.result()
            
            return DeploymentResult(
                success=True,
                platform="gcp",
                url=result.https_trigger.url,
                deployment_id=result.name
            )
            
        except Exception as e:
            return DeploymentResult(
                success=False,
                platform="gcp",
                error_message=str(e)
            )

class DockerIntegration(PlatformIntegration):
    """Docker containerization integration"""
    
    def __init__(self, credentials: PlatformCredentials):
        super().__init__(credentials)
        self.client = docker.from_env()
    
    def validate_credentials(self) -> bool:
        try:
            self.client.ping()
            return True
        except Exception as e:
            self.logger.error(f"Docker validation failed: {e}")
            return False
    
    def get_platform_info(self) -> Dict[str, Any]:
        try:
            info = self.client.info()
            version = self.client.version()
            
            return {
                "platform": "docker",
                "version": version.get("Version"),
                "api_version": version.get("ApiVersion"),
                "containers": info.get("Containers", 0),
                "images": info.get("Images", 0),
                "features": ["containerization", "multi_platform_builds", "registry_push"]
            }
        except Exception as e:
            return {"platform": "docker", "error": str(e)}
    
    def containerize_project(self, project_path: str, image_name: str,
                           dockerfile_content: str = None) -> Dict[str, Any]:
        """Containerize project with Docker"""
        try:
            # Generate Dockerfile if not provided
            if not dockerfile_content:
                dockerfile_content = self._generate_dockerfile(project_path)
            
            # Write Dockerfile
            dockerfile_path = os.path.join(project_path, "Dockerfile")
            with open(dockerfile_path, 'w') as f:
                f.write(dockerfile_content)
            
            # Build image
            image, build_logs = self.client.images.build(
                path=project_path,
                tag=image_name,
                dockerfile="Dockerfile"
            )
            
            return {
                "success": True,
                "image_id": image.id,
                "image_name": image_name,
                "build_logs": [log for log in build_logs]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _generate_dockerfile(self, project_path: str) -> str:
        """Generate Dockerfile based on project structure"""
        if os.path.exists(os.path.join(project_path, "package.json")):
            # Node.js project
            return """FROM node:16-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
"""
        elif os.path.exists(os.path.join(project_path, "requirements.txt")):
            # Python project
            return """FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "main.py"]
"""
        else:
            # Generic
            return """FROM alpine:latest
WORKDIR /app
COPY . .
CMD ["echo", "Hello from Docker!"]
"""

# Additional service integrations
class EmailIntegration(PlatformIntegration):
    """Email service integration (SendGrid, Mailgun, etc.)"""
    
    def __init__(self, credentials: PlatformCredentials):
        super().__init__(credentials)
        self.api_key = credentials.api_key
        self.service = credentials.platform_name  # "sendgrid" or "mailgun"
    
    def validate_credentials(self) -> bool:
        if self.service == "sendgrid":
            try:
                headers = {"Authorization": f"Bearer {self.api_key}"}
                response = requests.get("https://api.sendgrid.com/v3/user/account", headers=headers)
                return response.status_code == 200
            except:
                return False
        return False
    
    def get_platform_info(self) -> Dict[str, Any]:
        return {
            "platform": self.service,
            "features": ["transactional_email", "templates", "analytics"]
        }
    
    def send_email(self, to_email: str, subject: str, content: str,
                  from_email: str = None) -> Dict[str, Any]:
        """Send email via configured service"""
        if self.service == "sendgrid":
            try:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                data = {
                    "personalizations": [{"to": [{"email": to_email}]}],
                    "from": {"email": from_email or "noreply@example.com"},
                    "subject": subject,
                    "content": [{"type": "text/html", "value": content}]
                }
                
                response = requests.post(
                    "https://api.sendgrid.com/v3/mail/send",
                    headers=headers,
                    json=data
                )
                
                return {
                    "success": response.status_code == 202,
                    "message_id": response.headers.get("X-Message-Id"),
                    "error": None if response.status_code == 202 else response.text
                }
                
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        return {"success": False, "error": "Unsupported email service"}

# Update platform manager to include cloud integrations
def setup_cloud_platforms(platform_configs: Dict[str, Dict[str, Any]]) -> Dict[str, bool]:
    """Setup cloud platform integrations"""
    from platform_integrations import platform_manager
    
    results = {}
    
    for platform_name, config in platform_configs.items():
        try:
            credentials = PlatformCredentials(
                platform_name=platform_name,
                **config
            )
            
            if platform_name == "aws":
                integration = AWSIntegration(credentials)
            elif platform_name == "azure":
                integration = AzureIntegration(credentials)
            elif platform_name == "gcp":
                integration = GCPIntegration(credentials)
            elif platform_name == "docker":
                integration = DockerIntegration(credentials)
            elif platform_name in ["sendgrid", "mailgun"]:
                integration = EmailIntegration(credentials)
            else:
                results[platform_name] = False
                continue
            
            platform_manager.register_platform(platform_name, integration)
            results[platform_name] = integration.validate_credentials()
            
        except Exception as e:
            logging.error(f"Failed to setup {platform_name}: {e}")
            results[platform_name] = False
    
    return results