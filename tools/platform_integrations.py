"""
Aeonforge Platform Integration Hub
Integrates with major deployment platforms, databases, and services
"""

import os
import json
import requests
import subprocess
import tempfile
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
import logging
from datetime import datetime
import base64

@dataclass
class PlatformCredentials:
    """Platform credentials and configuration"""
    platform_name: str
    api_key: Optional[str] = None
    secret_key: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    org_id: Optional[str] = None
    project_id: Optional[str] = None
    additional_config: Dict[str, Any] = None

@dataclass
class DeploymentResult:
    """Result of deployment operation"""
    success: bool
    platform: str
    url: Optional[str] = None
    deployment_id: Optional[str] = None
    build_logs: List[str] = None
    error_message: Optional[str] = None
    deployment_time: Optional[str] = None
    
@dataclass 
class DatabaseSetup:
    """Database setup result"""
    success: bool
    platform: str
    database_url: Optional[str] = None
    database_id: Optional[str] = None
    connection_string: Optional[str] = None
    credentials: Dict[str, str] = None
    error_message: Optional[str] = None

@dataclass
class RepositorySetup:
    """Repository setup result"""
    success: bool
    platform: str
    repo_url: Optional[str] = None
    repo_name: Optional[str] = None
    clone_url: Optional[str] = None
    webhook_url: Optional[str] = None
    error_message: Optional[str] = None

class PlatformIntegration(ABC):
    """Abstract base class for platform integrations"""
    
    def __init__(self, credentials: PlatformCredentials):
        self.credentials = credentials
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
    
    @abstractmethod
    def validate_credentials(self) -> bool:
        """Validate platform credentials"""
        pass
    
    @abstractmethod
    def get_platform_info(self) -> Dict[str, Any]:
        """Get platform information and capabilities"""
        pass

class VercelIntegration(PlatformIntegration):
    """Vercel deployment platform integration"""
    
    def __init__(self, credentials: PlatformCredentials):
        super().__init__(credentials)
        self.base_url = "https://api.vercel.com"
        self.headers = {
            "Authorization": f"Bearer {credentials.access_token}",
            "Content-Type": "application/json"
        }
    
    def validate_credentials(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/v2/user", headers=self.headers)
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Credential validation failed: {e}")
            return False
    
    def get_platform_info(self) -> Dict[str, Any]:
        try:
            user_resp = requests.get(f"{self.base_url}/v2/user", headers=self.headers)
            teams_resp = requests.get(f"{self.base_url}/v2/teams", headers=self.headers)
            
            return {
                "platform": "vercel",
                "user": user_resp.json() if user_resp.status_code == 200 else None,
                "teams": teams_resp.json() if teams_resp.status_code == 200 else None,
                "features": ["static_sites", "serverless_functions", "edge_functions", "analytics"]
            }
        except Exception as e:
            return {"platform": "vercel", "error": str(e)}
    
    def deploy_project(self, project_path: str, project_name: str, 
                      environment_vars: Dict[str, str] = None) -> DeploymentResult:
        """Deploy project to Vercel"""
        try:
            # Create deployment payload
            deployment_data = {
                "name": project_name,
                "files": self._prepare_files(project_path),
                "projectSettings": {
                    "framework": self._detect_framework(project_path),
                    "buildCommand": self._get_build_command(project_path),
                    "outputDirectory": self._get_output_directory(project_path)
                }
            }
            
            if environment_vars:
                deployment_data["env"] = environment_vars
            
            # Deploy to Vercel
            response = requests.post(
                f"{self.base_url}/v13/deployments",
                headers=self.headers,
                json=deployment_data
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                return DeploymentResult(
                    success=True,
                    platform="vercel",
                    url=f"https://{result.get('url', '')}",
                    deployment_id=result.get('id'),
                    deployment_time=datetime.now().isoformat()
                )
            else:
                return DeploymentResult(
                    success=False,
                    platform="vercel",
                    error_message=f"Deployment failed: {response.text}"
                )
                
        except Exception as e:
            return DeploymentResult(
                success=False,
                platform="vercel", 
                error_message=str(e)
            )
    
    def _prepare_files(self, project_path: str) -> List[Dict[str, Any]]:
        """Prepare files for Vercel deployment"""
        files = []
        for root, dirs, filenames in os.walk(project_path):
            # Skip common ignore patterns
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '.next', 'dist', '__pycache__']]
            
            for filename in filenames:
                if filename.startswith('.') and filename not in ['.env.example', '.gitignore']:
                    continue
                    
                file_path = os.path.join(root, filename)
                relative_path = os.path.relpath(file_path, project_path)
                
                try:
                    with open(file_path, 'rb') as f:
                        content = f.read()
                        # Encode binary files as base64
                        if self._is_binary_file(filename):
                            file_data = base64.b64encode(content).decode('utf-8')
                            encoding = "base64"
                        else:
                            file_data = content.decode('utf-8')
                            encoding = "utf8"
                            
                        files.append({
                            "file": relative_path.replace("\\", "/"),
                            "data": file_data,
                            "encoding": encoding
                        })
                except Exception as e:
                    self.logger.warning(f"Failed to read file {file_path}: {e}")
        
        return files
    
    def _detect_framework(self, project_path: str) -> str:
        """Detect framework type"""
        if os.path.exists(os.path.join(project_path, "next.config.js")):
            return "nextjs"
        elif os.path.exists(os.path.join(project_path, "package.json")):
            with open(os.path.join(project_path, "package.json"), 'r') as f:
                package_json = json.load(f)
                deps = {**package_json.get("dependencies", {}), **package_json.get("devDependencies", {})}
                
                if "react" in deps and "react-scripts" in deps:
                    return "create-react-app"
                elif "vue" in deps:
                    return "vue"
                elif "svelte" in deps:
                    return "svelte"
                else:
                    return "static"
        elif os.path.exists(os.path.join(project_path, "index.html")):
            return "static"
        else:
            return "static"
    
    def _get_build_command(self, project_path: str) -> Optional[str]:
        """Get build command for project"""
        package_json_path = os.path.join(project_path, "package.json")
        if os.path.exists(package_json_path):
            with open(package_json_path, 'r') as f:
                package_json = json.load(f)
                scripts = package_json.get("scripts", {})
                if "build" in scripts:
                    return "npm run build"
        return None
    
    def _get_output_directory(self, project_path: str) -> Optional[str]:
        """Get output directory for project"""
        framework = self._detect_framework(project_path)
        if framework == "create-react-app":
            return "build"
        elif framework == "nextjs":
            return ".next"
        elif framework == "vue":
            return "dist"
        return None
    
    def _is_binary_file(self, filename: str) -> bool:
        """Check if file is binary"""
        binary_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.ico', '.pdf', '.zip', '.tar', '.gz']
        return any(filename.lower().endswith(ext) for ext in binary_extensions)

class SupabaseIntegration(PlatformIntegration):
    """Supabase database platform integration"""
    
    def __init__(self, credentials: PlatformCredentials):
        super().__init__(credentials)
        self.base_url = "https://api.supabase.com/v1"
        self.headers = {
            "Authorization": f"Bearer {credentials.access_token}",
            "Content-Type": "application/json"
        }
    
    def validate_credentials(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/projects", headers=self.headers)
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Credential validation failed: {e}")
            return False
    
    def get_platform_info(self) -> Dict[str, Any]:
        try:
            projects_resp = requests.get(f"{self.base_url}/projects", headers=self.headers)
            
            return {
                "platform": "supabase",
                "projects": projects_resp.json() if projects_resp.status_code == 200 else [],
                "features": ["postgresql", "realtime", "auth", "storage", "edge_functions"]
            }
        except Exception as e:
            return {"platform": "supabase", "error": str(e)}
    
    def create_project(self, project_name: str, region: str = "us-east-1", 
                      db_password: str = None) -> DatabaseSetup:
        """Create new Supabase project"""
        try:
            project_data = {
                "name": project_name,
                "region": region,
                "plan": "free"
            }
            
            if db_password:
                project_data["db_pass"] = db_password
            
            response = requests.post(
                f"{self.base_url}/projects",
                headers=self.headers,
                json=project_data
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                
                # Get connection details
                project_id = result.get("id")
                connection_string = f"postgresql://postgres:{db_password}@db.{result.get('ref', '')}.supabase.co:5432/postgres"
                
                return DatabaseSetup(
                    success=True,
                    platform="supabase",
                    database_url=result.get("url"),
                    database_id=project_id,
                    connection_string=connection_string,
                    credentials={
                        "anon_key": result.get("anon_key", ""),
                        "service_role_key": result.get("service_role_key", ""),
                        "url": result.get("url", ""),
                        "ref": result.get("ref", "")
                    }
                )
            else:
                return DatabaseSetup(
                    success=False,
                    platform="supabase",
                    error_message=f"Project creation failed: {response.text}"
                )
                
        except Exception as e:
            return DatabaseSetup(
                success=False,
                platform="supabase",
                error_message=str(e)
            )
    
    def setup_database_schema(self, project_id: str, schema_sql: str) -> bool:
        """Setup database schema"""
        try:
            # Get project details
            project_resp = requests.get(f"{self.base_url}/projects/{project_id}", headers=self.headers)
            if project_resp.status_code != 200:
                return False
                
            project_data = project_resp.json()
            db_url = project_data.get("db", {}).get("host")
            
            # Execute schema SQL
            sql_headers = {
                **self.headers,
                "apikey": project_data.get("anon_key", "")
            }
            
            response = requests.post(
                f"{project_data.get('url')}/rest/v1/rpc/execute_sql",
                headers=sql_headers,
                json={"sql": schema_sql}
            )
            
            return response.status_code == 200
            
        except Exception as e:
            self.logger.error(f"Schema setup failed: {e}")
            return False

class StripeIntegration(PlatformIntegration):
    """Stripe payment platform integration"""
    
    def __init__(self, credentials: PlatformCredentials):
        super().__init__(credentials)
        self.base_url = "https://api.stripe.com/v1"
        self.headers = {
            "Authorization": f"Bearer {credentials.secret_key}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
    
    def validate_credentials(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/account", headers=self.headers)
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Credential validation failed: {e}")
            return False
    
    def get_platform_info(self) -> Dict[str, Any]:
        try:
            account_resp = requests.get(f"{self.base_url}/account", headers=self.headers)
            
            return {
                "platform": "stripe",
                "account": account_resp.json() if account_resp.status_code == 200 else None,
                "features": ["payments", "subscriptions", "invoicing", "connect", "radar"]
            }
        except Exception as e:
            return {"platform": "stripe", "error": str(e)}
    
    def create_product(self, name: str, description: str = None, 
                      price_cents: int = None, interval: str = None) -> Dict[str, Any]:
        """Create Stripe product with pricing"""
        try:
            # Create product
            product_data = {
                "name": name,
                "type": "service"
            }
            if description:
                product_data["description"] = description
            
            product_resp = requests.post(
                f"{self.base_url}/products",
                headers=self.headers,
                data=product_data
            )
            
            if product_resp.status_code != 200:
                return {"success": False, "error": product_resp.text}
            
            product = product_resp.json()
            
            # Create price if specified
            if price_cents:
                price_data = {
                    "unit_amount": price_cents,
                    "currency": "usd",
                    "product": product["id"]
                }
                
                if interval:  # For subscriptions
                    price_data["recurring"] = {"interval": interval}
                
                price_resp = requests.post(
                    f"{self.base_url}/prices",
                    headers=self.headers,
                    data=price_data
                )
                
                if price_resp.status_code == 200:
                    product["price"] = price_resp.json()
            
            return {
                "success": True,
                "product": product
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_payment_link(self, price_id: str, success_url: str, 
                           cancel_url: str = None) -> Dict[str, Any]:
        """Create Stripe payment link"""
        try:
            link_data = {
                "line_items[0][price]": price_id,
                "line_items[0][quantity]": "1",
                "after_completion[type]": "redirect",
                "after_completion[redirect][url]": success_url
            }
            
            if cancel_url:
                link_data["automatic_tax[enabled]"] = "true"
            
            response = requests.post(
                f"{self.base_url}/payment_links",
                headers=self.headers,
                data=link_data
            )
            
            if response.status_code == 200:
                return {"success": True, "payment_link": response.json()}
            else:
                return {"success": False, "error": response.text}
                
        except Exception as e:
            return {"success": False, "error": str(e)}

class GitHubIntegration(PlatformIntegration):
    """GitHub repository platform integration"""
    
    def __init__(self, credentials: PlatformCredentials):
        super().__init__(credentials)
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"Bearer {credentials.access_token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        }
    
    def validate_credentials(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/user", headers=self.headers)
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Credential validation failed: {e}")
            return False
    
    def get_platform_info(self) -> Dict[str, Any]:
        try:
            user_resp = requests.get(f"{self.base_url}/user", headers=self.headers)
            orgs_resp = requests.get(f"{self.base_url}/user/orgs", headers=self.headers)
            
            return {
                "platform": "github",
                "user": user_resp.json() if user_resp.status_code == 200 else None,
                "organizations": orgs_resp.json() if orgs_resp.status_code == 200 else [],
                "features": ["repositories", "actions", "pages", "packages", "security"]
            }
        except Exception as e:
            return {"platform": "github", "error": str(e)}
    
    def create_repository(self, repo_name: str, description: str = None, 
                         private: bool = False, auto_init: bool = True) -> RepositorySetup:
        """Create GitHub repository"""
        try:
            repo_data = {
                "name": repo_name,
                "private": private,
                "auto_init": auto_init,
                "has_issues": True,
                "has_projects": True,
                "has_wiki": False
            }
            
            if description:
                repo_data["description"] = description
            
            response = requests.post(
                f"{self.base_url}/user/repos",
                headers=self.headers,
                json=repo_data
            )
            
            if response.status_code == 201:
                repo = response.json()
                return RepositorySetup(
                    success=True,
                    platform="github",
                    repo_url=repo["html_url"],
                    repo_name=repo["full_name"],
                    clone_url=repo["clone_url"]
                )
            else:
                return RepositorySetup(
                    success=False,
                    platform="github",
                    error_message=f"Repository creation failed: {response.text}"
                )
                
        except Exception as e:
            return RepositorySetup(
                success=False,
                platform="github",
                error_message=str(e)
            )
    
    def push_project_to_repo(self, project_path: str, repo_name: str, 
                            commit_message: str = "Initial commit") -> bool:
        """Push local project to GitHub repository"""
        try:
            # Initialize git repo
            subprocess.run(["git", "init"], cwd=project_path, check=True)
            subprocess.run(["git", "add", "."], cwd=project_path, check=True)
            subprocess.run(["git", "commit", "-m", commit_message], cwd=project_path, check=True)
            
            # Add remote and push
            user_resp = requests.get(f"{self.base_url}/user", headers=self.headers)
            if user_resp.status_code == 200:
                username = user_resp.json()["login"]
                remote_url = f"https://{self.credentials.access_token}@github.com/{username}/{repo_name}.git"
                
                subprocess.run(["git", "remote", "add", "origin", remote_url], cwd=project_path, check=True)
                subprocess.run(["git", "push", "-u", "origin", "main"], cwd=project_path, check=True)
                
                return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Git operation failed: {e}")
        except Exception as e:
            self.logger.error(f"Push failed: {e}")
        
        return False

class NetlifyIntegration(PlatformIntegration):
    """Netlify deployment and hosting integration"""
    
    def __init__(self, credentials: PlatformCredentials):
        super().__init__(credentials)
        self.base_url = "https://api.netlify.com/api/v1"
        self.headers = {
            "Authorization": f"Bearer {credentials.api_key}",
            "Content-Type": "application/json"
        }
    
    def validate_credentials(self) -> bool:
        """Validate Netlify API credentials"""
        try:
            response = requests.get(f"{self.base_url}/user", headers=self.headers)
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Netlify credential validation failed: {e}")
            return False
    
    def get_platform_info(self) -> Dict[str, Any]:
        """Get Netlify account information"""
        try:
            user_response = requests.get(f"{self.base_url}/user", headers=self.headers)
            sites_response = requests.get(f"{self.base_url}/sites", headers=self.headers)
            
            if user_response.status_code == 200:
                user_data = user_response.json()
                sites_data = sites_response.json() if sites_response.status_code == 200 else []
                
                return {
                    "platform": "netlify",
                    "user_name": user_data.get("full_name", "N/A"),
                    "email": user_data.get("email", "N/A"),
                    "sites_count": len(sites_data),
                    "account_type": user_data.get("site_count", 0)
                }
        except Exception as e:
            self.logger.error(f"Failed to get Netlify info: {e}")
        
        return {"platform": "netlify", "error": "Failed to retrieve information"}
    
    def create_site(self, site_name: str, repo_url: str = None, 
                   build_command: str = "npm run build", 
                   publish_dir: str = "dist") -> Dict[str, Any]:
        """Create a new Netlify site"""
        try:
            site_data = {
                "name": site_name,
                "build_settings": {
                    "cmd": build_command,
                    "dir": publish_dir
                }
            }
            
            if repo_url:
                site_data["repo"] = {"repo": repo_url}
            
            response = requests.post(
                f"{self.base_url}/sites", 
                headers=self.headers,
                json=site_data
            )
            
            if response.status_code == 201:
                site_info = response.json()
                return {
                    "success": True,
                    "site_id": site_info["id"],
                    "site_name": site_info["name"],
                    "url": f"https://{site_info['name']}.netlify.app",
                    "admin_url": site_info["admin_url"]
                }
            else:
                return {"success": False, "error": response.text}
                
        except Exception as e:
            self.logger.error(f"Failed to create Netlify site: {e}")
            return {"success": False, "error": str(e)}
    
    def deploy_site(self, site_id: str, build_dir: str) -> DeploymentResult:
        """Deploy site to Netlify"""
        try:
            # Create zip of build directory
            import zipfile
            import io
            
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for root, dirs, files in os.walk(build_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        archive_name = os.path.relpath(file_path, build_dir)
                        zip_file.write(file_path, archive_name)
            
            zip_buffer.seek(0)
            
            # Deploy to Netlify
            response = requests.post(
                f"{self.base_url}/sites/{site_id}/deploys",
                headers={"Authorization": f"Bearer {self.credentials.api_key}"},
                files={"file": ("site.zip", zip_buffer.getvalue(), "application/zip")}
            )
            
            if response.status_code == 200:
                deploy_info = response.json()
                return DeploymentResult(
                    success=True,
                    platform="netlify",
                    url=deploy_info["url"],
                    deployment_id=deploy_info["id"],
                    deployment_time=deploy_info["created_at"]
                )
            else:
                return DeploymentResult(
                    success=False,
                    platform="netlify", 
                    error_message=response.text
                )
                
        except Exception as e:
            self.logger.error(f"Netlify deployment failed: {e}")
            return DeploymentResult(
                success=False,
                platform="netlify",
                error_message=str(e)
            )
    
    def setup_custom_domain(self, site_id: str, domain: str) -> bool:
        """Setup custom domain for Netlify site"""
        try:
            response = requests.post(
                f"{self.base_url}/sites/{site_id}/domains",
                headers=self.headers,
                json={"domain": domain}
            )
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Failed to setup Netlify custom domain: {e}")
            return False

class PlanetScaleIntegration(PlatformIntegration):
    """PlanetScale MySQL database integration"""
    
    def __init__(self, credentials: PlatformCredentials):
        super().__init__(credentials)
        self.base_url = "https://api.planetscale.com/v1"
        self.headers = {
            "Authorization": f"Bearer {credentials.api_key}",
            "Content-Type": "application/json"
        }
    
    def validate_credentials(self) -> bool:
        """Validate PlanetScale API credentials"""
        try:
            response = requests.get(f"{self.base_url}/user", headers=self.headers)
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"PlanetScale credential validation failed: {e}")
            return False
    
    def get_platform_info(self) -> Dict[str, Any]:
        """Get PlanetScale account information"""
        try:
            user_response = requests.get(f"{self.base_url}/user", headers=self.headers)
            orgs_response = requests.get(f"{self.base_url}/organizations", headers=self.headers)
            
            if user_response.status_code == 200:
                user_data = user_response.json()
                orgs_data = orgs_response.json() if orgs_response.status_code == 200 else []
                
                return {
                    "platform": "planetscale",
                    "user_name": user_data.get("display_name", "N/A"),
                    "email": user_data.get("email", "N/A"),
                    "organizations": len(orgs_data.get("data", [])),
                    "tier": user_data.get("tier", "hobby")
                }
        except Exception as e:
            self.logger.error(f"Failed to get PlanetScale info: {e}")
        
        return {"platform": "planetscale", "error": "Failed to retrieve information"}
    
    def create_database(self, org_name: str, database_name: str, 
                       region: str = "us-east") -> DatabaseSetup:
        """Create a new PlanetScale database"""
        try:
            db_data = {
                "name": database_name,
                "region": region,
                "cluster_size": "PS-10"  # Smallest cluster
            }
            
            response = requests.post(
                f"{self.base_url}/organizations/{org_name}/databases",
                headers=self.headers,
                json=db_data
            )
            
            if response.status_code == 201:
                db_info = response.json()
                
                # Get connection details
                connection_response = requests.get(
                    f"{self.base_url}/organizations/{org_name}/databases/{database_name}/branches/main/connection-strings",
                    headers=self.headers
                )
                
                connection_string = None
                if connection_response.status_code == 200:
                    conn_data = connection_response.json()
                    connection_string = conn_data.get("general", {}).get("connection_string")
                
                return DatabaseSetup(
                    success=True,
                    platform="planetscale",
                    database_id=db_info["id"],
                    database_url=f"https://app.planetscale.com/{org_name}/{database_name}",
                    connection_string=connection_string,
                    credentials={
                        "host": db_info.get("region", {}).get("slug", "") + ".planetscale.sh",
                        "database": database_name,
                        "sslmode": "require"
                    }
                )
            else:
                return DatabaseSetup(
                    success=False,
                    platform="planetscale",
                    error_message=response.text
                )
                
        except Exception as e:
            self.logger.error(f"Failed to create PlanetScale database: {e}")
            return DatabaseSetup(
                success=False,
                platform="planetscale",
                error_message=str(e)
            )
    
    def create_branch(self, org_name: str, database_name: str, 
                     branch_name: str, parent_branch: str = "main") -> Dict[str, Any]:
        """Create a new database branch"""
        try:
            response = requests.post(
                f"{self.base_url}/organizations/{org_name}/databases/{database_name}/branches",
                headers=self.headers,
                json={
                    "name": branch_name,
                    "parent_branch": parent_branch
                }
            )
            
            if response.status_code == 201:
                branch_info = response.json()
                return {
                    "success": True,
                    "branch_id": branch_info["id"],
                    "branch_name": branch_info["name"],
                    "ready": branch_info["ready"]
                }
            else:
                return {"success": False, "error": response.text}
                
        except Exception as e:
            self.logger.error(f"Failed to create PlanetScale branch: {e}")
            return {"success": False, "error": str(e)}
    
    def create_deploy_request(self, org_name: str, database_name: str,
                             branch_name: str, target_branch: str = "main") -> Dict[str, Any]:
        """Create deploy request (like a PR for database schema)"""
        try:
            response = requests.post(
                f"{self.base_url}/organizations/{org_name}/databases/{database_name}/deploy-requests",
                headers=self.headers,
                json={
                    "branch": branch_name,
                    "into_branch": target_branch
                }
            )
            
            if response.status_code == 201:
                deploy_info = response.json()
                return {
                    "success": True,
                    "deploy_request_id": deploy_info["id"],
                    "number": deploy_info["number"],
                    "url": deploy_info["html_url"]
                }
            else:
                return {"success": False, "error": response.text}
                
        except Exception as e:
            self.logger.error(f"Failed to create PlanetScale deploy request: {e}")
            return {"success": False, "error": str(e)}

class HerokuIntegration(PlatformIntegration):
    """Heroku cloud platform integration"""
    
    def __init__(self, credentials: PlatformCredentials):
        super().__init__(credentials)
        self.base_url = "https://api.heroku.com"
        self.headers = {
            "Authorization": f"Bearer {credentials.api_key}",
            "Accept": "application/vnd.heroku+json; version=3",
            "Content-Type": "application/json"
        }
    
    def validate_credentials(self) -> bool:
        """Validate Heroku API credentials"""
        try:
            response = requests.get(f"{self.base_url}/account", headers=self.headers)
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Heroku credential validation failed: {e}")
            return False
    
    def get_platform_info(self) -> Dict[str, Any]:
        """Get Heroku account information"""
        try:
            account_response = requests.get(f"{self.base_url}/account", headers=self.headers)
            apps_response = requests.get(f"{self.base_url}/apps", headers=self.headers)
            
            if account_response.status_code == 200:
                account_data = account_response.json()
                apps_data = apps_response.json() if apps_response.status_code == 200 else []
                
                return {
                    "platform": "heroku",
                    "user_name": account_data.get("name", "N/A"),
                    "email": account_data.get("email", "N/A"),
                    "apps_count": len(apps_data),
                    "verified": account_data.get("verified", False),
                    "tier": account_data.get("tier", "hobby")
                }
        except Exception as e:
            self.logger.error(f"Failed to get Heroku info: {e}")
        
        return {"platform": "heroku", "error": "Failed to retrieve information"}
    
    def create_app(self, app_name: str, region: str = "us", stack: str = "heroku-22") -> Dict[str, Any]:
        """Create a new Heroku app"""
        try:
            app_data = {
                "name": app_name,
                "region": region,
                "stack": stack
            }
            
            response = requests.post(
                f"{self.base_url}/apps",
                headers=self.headers,
                json=app_data
            )
            
            if response.status_code == 201:
                app_info = response.json()
                return {
                    "success": True,
                    "app_id": app_info["id"],
                    "app_name": app_info["name"],
                    "web_url": app_info["web_url"],
                    "git_url": app_info["git_url"],
                    "region": app_info["region"]["name"]
                }
            else:
                return {"success": False, "error": response.text}
                
        except Exception as e:
            self.logger.error(f"Failed to create Heroku app: {e}")
            return {"success": False, "error": str(e)}
    
    def deploy_app(self, app_name: str, source_url: str) -> DeploymentResult:
        """Deploy app to Heroku"""
        try:
            # Create build
            build_data = {
                "source_blob": {
                    "url": source_url
                }
            }
            
            response = requests.post(
                f"{self.base_url}/apps/{app_name}/builds",
                headers=self.headers,
                json=build_data
            )
            
            if response.status_code == 201:
                build_info = response.json()
                return DeploymentResult(
                    success=True,
                    platform="heroku",
                    url=f"https://{app_name}.herokuapp.com",
                    deployment_id=build_info["id"],
                    deployment_time=build_info["created_at"]
                )
            else:
                return DeploymentResult(
                    success=False,
                    platform="heroku",
                    error_message=response.text
                )
                
        except Exception as e:
            self.logger.error(f"Heroku deployment failed: {e}")
            return DeploymentResult(
                success=False,
                platform="heroku",
                error_message=str(e)
            )
    
    def add_addon(self, app_name: str, addon_service: str, plan: str = "hobby-dev") -> Dict[str, Any]:
        """Add addon to Heroku app"""
        try:
            addon_data = {
                "plan": f"{addon_service}:{plan}"
            }
            
            response = requests.post(
                f"{self.base_url}/apps/{app_name}/addons",
                headers=self.headers,
                json=addon_data
            )
            
            if response.status_code == 201:
                addon_info = response.json()
                return {
                    "success": True,
                    "addon_id": addon_info["id"],
                    "plan": addon_info["plan"]["name"],
                    "state": addon_info["state"]
                }
            else:
                return {"success": False, "error": response.text}
                
        except Exception as e:
            self.logger.error(f"Failed to add Heroku addon: {e}")
            return {"success": False, "error": str(e)}
    
    def set_config_vars(self, app_name: str, config_vars: Dict[str, str]) -> bool:
        """Set environment variables"""
        try:
            response = requests.patch(
                f"{self.base_url}/apps/{app_name}/config-vars",
                headers=self.headers,
                json=config_vars
            )
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Failed to set Heroku config vars: {e}")
            return False

class RailwayIntegration(PlatformIntegration):
    """Railway deployment platform integration"""
    
    def __init__(self, credentials: PlatformCredentials):
        super().__init__(credentials)
        self.base_url = "https://backboard.railway.app/graphql/v2"
        self.headers = {
            "Authorization": f"Bearer {credentials.api_key}",
            "Content-Type": "application/json"
        }
    
    def validate_credentials(self) -> bool:
        """Validate Railway credentials"""
        try:
            query = """
            query {
                me {
                    id
                    email
                }
            }
            """
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json={"query": query}
            )
            return response.status_code == 200 and "data" in response.json()
        except Exception as e:
            self.logger.error(f"Railway credential validation failed: {e}")
            return False
    
    def get_platform_info(self) -> Dict[str, Any]:
        """Get Railway account information"""
        try:
            query = """
            query {
                me {
                    id
                    email
                    name
                }
                projects {
                    edges {
                        node {
                            id
                            name
                        }
                    }
                }
            }
            """
            
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json={"query": query}
            )
            
            if response.status_code == 200:
                data = response.json().get("data", {})
                user_data = data.get("me", {})
                projects_data = data.get("projects", {}).get("edges", [])
                
                return {
                    "platform": "railway",
                    "user_name": user_data.get("name", "N/A"),
                    "email": user_data.get("email", "N/A"),
                    "projects_count": len(projects_data),
                    "user_id": user_data.get("id")
                }
        except Exception as e:
            self.logger.error(f"Failed to get Railway info: {e}")
        
        return {"platform": "railway", "error": "Failed to retrieve information"}
    
    def create_project(self, project_name: str, repo_url: str = None) -> Dict[str, Any]:
        """Create a new Railway project"""
        try:
            mutation = """
            mutation projectCreate($input: ProjectCreateInput!) {
                projectCreate(input: $input) {
                    id
                    name
                }
            }
            """
            
            variables = {
                "input": {
                    "name": project_name
                }
            }
            
            if repo_url:
                variables["input"]["repo"] = {
                    "url": repo_url
                }
            
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json={"query": mutation, "variables": variables}
            )
            
            if response.status_code == 200:
                data = response.json().get("data", {})
                project_data = data.get("projectCreate", {})
                
                return {
                    "success": True,
                    "project_id": project_data.get("id"),
                    "project_name": project_data.get("name"),
                    "url": f"https://{project_name}.up.railway.app"
                }
            else:
                return {"success": False, "error": response.text}
                
        except Exception as e:
            self.logger.error(f"Failed to create Railway project: {e}")
            return {"success": False, "error": str(e)}

class MongoDBAtlasIntegration(PlatformIntegration):
    """MongoDB Atlas database integration"""
    
    def __init__(self, credentials: PlatformCredentials):
        super().__init__(credentials)
        self.base_url = "https://cloud.mongodb.com/api/atlas/v1.0"
        self.public_key = credentials.api_key
        self.private_key = credentials.secret_key
        self.group_id = credentials.additional_config.get("group_id") if credentials.additional_config else None
    
    def _get_digest_auth(self):
        """Get digest authentication for MongoDB Atlas API"""
        from requests.auth import HTTPDigestAuth
        return HTTPDigestAuth(self.public_key, self.private_key)
    
    def validate_credentials(self) -> bool:
        """Validate MongoDB Atlas credentials"""
        try:
            response = requests.get(
                f"{self.base_url}/groups",
                auth=self._get_digest_auth()
            )
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"MongoDB Atlas credential validation failed: {e}")
            return False
    
    def get_platform_info(self) -> Dict[str, Any]:
        """Get MongoDB Atlas account information"""
        try:
            groups_response = requests.get(
                f"{self.base_url}/groups",
                auth=self._get_digest_auth()
            )
            
            if groups_response.status_code == 200:
                groups_data = groups_response.json()
                
                # Get clusters info if group_id is available
                clusters_count = 0
                if self.group_id:
                    clusters_response = requests.get(
                        f"{self.base_url}/groups/{self.group_id}/clusters",
                        auth=self._get_digest_auth()
                    )
                    if clusters_response.status_code == 200:
                        clusters_data = clusters_response.json()
                        clusters_count = len(clusters_data.get("results", []))
                
                return {
                    "platform": "mongodb_atlas",
                    "organizations": len(groups_data.get("results", [])),
                    "clusters_count": clusters_count,
                    "group_id": self.group_id
                }
        except Exception as e:
            self.logger.error(f"Failed to get MongoDB Atlas info: {e}")
        
        return {"platform": "mongodb_atlas", "error": "Failed to retrieve information"}
    
    def create_cluster(self, cluster_name: str, provider: str = "AWS", 
                      region: str = "US_EAST_1", instance_size: str = "M10") -> DatabaseSetup:
        """Create a new MongoDB Atlas cluster"""
        try:
            cluster_data = {
                "name": cluster_name,
                "clusterType": "REPLICASET",
                "replicationSpecs": [{
                    "numShards": 1,
                    "regionsConfig": {
                        region: {
                            "analyticsNodes": 0,
                            "electableNodes": 3,
                            "priority": 7,
                            "readOnlyNodes": 0
                        }
                    }
                }],
                "cloudBackup": True,
                "autoScaling": {
                    "diskGBEnabled": True,
                    "compute": {
                        "enabled": False,
                        "scaleDownEnabled": False
                    }
                },
                "providerSettings": {
                    "providerName": provider,
                    "instanceSizeName": instance_size,
                    "regionName": region
                }
            }
            
            response = requests.post(
                f"{self.base_url}/groups/{self.group_id}/clusters",
                auth=self._get_digest_auth(),
                json=cluster_data
            )
            
            if response.status_code == 201:
                cluster_info = response.json()
                
                # Generate connection string
                connection_string = f"mongodb+srv://<username>:<password>@{cluster_name.lower()}.mongodb.net/<database>?retryWrites=true&w=majority"
                
                return DatabaseSetup(
                    success=True,
                    platform="mongodb_atlas",
                    database_id=cluster_info["id"],
                    database_url=f"https://cloud.mongodb.com/v2/{self.group_id}#clusters/detail/{cluster_name}",
                    connection_string=connection_string,
                    credentials={
                        "cluster_name": cluster_name,
                        "srv_address": cluster_info.get("srvAddress", ""),
                        "provider": provider,
                        "region": region
                    }
                )
            else:
                return DatabaseSetup(
                    success=False,
                    platform="mongodb_atlas",
                    error_message=response.text
                )
                
        except Exception as e:
            self.logger.error(f"Failed to create MongoDB Atlas cluster: {e}")
            return DatabaseSetup(
                success=False,
                platform="mongodb_atlas",
                error_message=str(e)
            )
    
    def create_database_user(self, username: str, password: str, 
                           database_name: str = "admin", roles: List[str] = None) -> Dict[str, Any]:
        """Create database user for cluster access"""
        try:
            roles = roles or [{"roleName": "readWrite", "databaseName": database_name}]
            
            user_data = {
                "databaseName": database_name,
                "groupId": self.group_id,
                "password": password,
                "roles": roles,
                "username": username
            }
            
            response = requests.post(
                f"{self.base_url}/groups/{self.group_id}/databaseUsers",
                auth=self._get_digest_auth(),
                json=user_data
            )
            
            if response.status_code == 201:
                user_info = response.json()
                return {
                    "success": True,
                    "username": user_info["username"],
                    "database_name": user_info["databaseName"],
                    "roles": user_info["roles"]
                }
            else:
                return {"success": False, "error": response.text}
                
        except Exception as e:
            self.logger.error(f"Failed to create MongoDB Atlas user: {e}")
            return {"success": False, "error": str(e)}
    
    def whitelist_ip(self, ip_address: str, comment: str = "API Access") -> Dict[str, Any]:
        """Add IP address to whitelist"""
        try:
            whitelist_data = {
                "ipAddress": ip_address,
                "comment": comment
            }
            
            response = requests.post(
                f"{self.base_url}/groups/{self.group_id}/whitelist",
                auth=self._get_digest_auth(),
                json=whitelist_data
            )
            
            if response.status_code == 201:
                return {"success": True, "ip_address": ip_address}
            else:
                return {"success": False, "error": response.text}
                
        except Exception as e:
            self.logger.error(f"Failed to whitelist IP in MongoDB Atlas: {e}")
            return {"success": False, "error": str(e)}

class CockroachDBIntegration(PlatformIntegration):
    """CockroachDB Serverless integration"""
    
    def __init__(self, credentials: PlatformCredentials):
        super().__init__(credentials)
        self.base_url = "https://cockroachlabs.cloud/api/v1"
        self.headers = {
            "Authorization": f"Bearer {credentials.api_key}",
            "Content-Type": "application/json"
        }
    
    def validate_credentials(self) -> bool:
        """Validate CockroachDB credentials"""
        try:
            response = requests.get(f"{self.base_url}/clusters", headers=self.headers)
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"CockroachDB credential validation failed: {e}")
            return False
    
    def get_platform_info(self) -> Dict[str, Any]:
        """Get CockroachDB account information"""
        try:
            clusters_response = requests.get(f"{self.base_url}/clusters", headers=self.headers)
            
            if clusters_response.status_code == 200:
                clusters_data = clusters_response.json()
                
                return {
                    "platform": "cockroachdb",
                    "clusters_count": len(clusters_data.get("clusters", [])),
                    "status": "active"
                }
        except Exception as e:
            self.logger.error(f"Failed to get CockroachDB info: {e}")
        
        return {"platform": "cockroachdb", "error": "Failed to retrieve information"}
    
    def create_cluster(self, cluster_name: str, cloud_provider: str = "GCP", 
                      region: str = "us-central1") -> DatabaseSetup:
        """Create a new CockroachDB Serverless cluster"""
        try:
            cluster_data = {
                "name": cluster_name,
                "cockroach_version": "v22.2",
                "plan": "BASIC",
                "cloud_provider": cloud_provider,
                "regions": [region],
                "serverless": {
                    "spending_limit": {
                        "limit_cents": 0  # No spending limit for free tier
                    }
                }
            }
            
            response = requests.post(
                f"{self.base_url}/clusters",
                headers=self.headers,
                json=cluster_data
            )
            
            if response.status_code == 200:
                cluster_info = response.json()
                
                return DatabaseSetup(
                    success=True,
                    platform="cockroachdb",
                    database_id=cluster_info["id"],
                    database_url=cluster_info.get("ui_url", ""),
                    connection_string=cluster_info.get("connection_string", ""),
                    credentials={
                        "cluster_name": cluster_name,
                        "host": cluster_info.get("host", ""),
                        "port": cluster_info.get("port", "26257")
                    }
                )
            else:
                return DatabaseSetup(
                    success=False,
                    platform="cockroachdb",
                    error_message=response.text
                )
                
        except Exception as e:
            self.logger.error(f"Failed to create CockroachDB cluster: {e}")
            return DatabaseSetup(
                success=False,
                platform="cockroachdb",
                error_message=str(e)
            )

class GitLabIntegration(PlatformIntegration):
    """GitLab version control integration"""
    
    def __init__(self, credentials: PlatformCredentials):
        super().__init__(credentials)
        self.base_url = "https://gitlab.com/api/v4"
        self.headers = {
            "Authorization": f"Bearer {credentials.api_key}",
            "Content-Type": "application/json"
        }
    
    def validate_credentials(self) -> bool:
        """Validate GitLab credentials"""
        try:
            response = requests.get(f"{self.base_url}/user", headers=self.headers)
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"GitLab credential validation failed: {e}")
            return False
    
    def get_platform_info(self) -> Dict[str, Any]:
        """Get GitLab account information"""
        try:
            user_response = requests.get(f"{self.base_url}/user", headers=self.headers)
            projects_response = requests.get(f"{self.base_url}/projects?owned=true", headers=self.headers)
            
            if user_response.status_code == 200:
                user_data = user_response.json()
                projects_data = projects_response.json() if projects_response.status_code == 200 else []
                
                return {
                    "platform": "gitlab",
                    "username": user_data.get("username", "N/A"),
                    "name": user_data.get("name", "N/A"),
                    "email": user_data.get("email", "N/A"),
                    "projects_count": len(projects_data),
                    "user_id": user_data.get("id"),
                    "plan": user_data.get("plan", "free")
                }
        except Exception as e:
            self.logger.error(f"Failed to get GitLab info: {e}")
        
        return {"platform": "gitlab", "error": "Failed to retrieve information"}
    
    def create_repository(self, repo_name: str, description: str = "", 
                         private: bool = True, initialize_with_readme: bool = True) -> RepositorySetup:
        """Create a new GitLab repository"""
        try:
            repo_data = {
                "name": repo_name,
                "description": description,
                "visibility": "private" if private else "public",
                "initialize_with_readme": initialize_with_readme
            }
            
            response = requests.post(
                f"{self.base_url}/projects",
                headers=self.headers,
                json=repo_data
            )
            
            if response.status_code == 201:
                repo_info = response.json()
                return RepositorySetup(
                    success=True,
                    platform="gitlab",
                    repo_name=repo_info["name"],
                    repo_url=repo_info["web_url"],
                    clone_url=repo_info["http_url_to_repo"],
                    ssh_url=repo_info["ssh_url_to_repo"],
                    repo_id=str(repo_info["id"])
                )
            else:
                return RepositorySetup(
                    success=False,
                    platform="gitlab",
                    error_message=response.text
                )
                
        except Exception as e:
            self.logger.error(f"Failed to create GitLab repository: {e}")
            return RepositorySetup(
                success=False,
                platform="gitlab",
                error_message=str(e)
            )
    
    def setup_ci_cd(self, project_id: str, pipeline_config: str) -> Dict[str, Any]:
        """Setup GitLab CI/CD pipeline"""
        try:
            # Create .gitlab-ci.yml file
            file_data = {
                "branch": "main",
                "content": pipeline_config,
                "commit_message": "Add GitLab CI/CD configuration"
            }
            
            response = requests.post(
                f"{self.base_url}/projects/{project_id}/repository/files/.gitlab-ci.yml",
                headers=self.headers,
                json=file_data
            )
            
            if response.status_code == 201:
                return {"success": True, "pipeline_configured": True}
            else:
                return {"success": False, "error": response.text}
                
        except Exception as e:
            self.logger.error(f"Failed to setup GitLab CI/CD: {e}")
            return {"success": False, "error": str(e)}
    
    def create_merge_request(self, project_id: str, source_branch: str, 
                           target_branch: str = "main", title: str = "", 
                           description: str = "") -> Dict[str, Any]:
        """Create a merge request"""
        try:
            mr_data = {
                "source_branch": source_branch,
                "target_branch": target_branch,
                "title": title or f"Merge {source_branch} into {target_branch}",
                "description": description
            }
            
            response = requests.post(
                f"{self.base_url}/projects/{project_id}/merge_requests",
                headers=self.headers,
                json=mr_data
            )
            
            if response.status_code == 201:
                mr_info = response.json()
                return {
                    "success": True,
                    "merge_request_id": mr_info["iid"],
                    "web_url": mr_info["web_url"],
                    "title": mr_info["title"]
                }
            else:
                return {"success": False, "error": response.text}
                
        except Exception as e:
            self.logger.error(f"Failed to create GitLab merge request: {e}")
            return {"success": False, "error": str(e)}

class BitbucketIntegration(PlatformIntegration):
    """Bitbucket version control integration"""
    
    def __init__(self, credentials: PlatformCredentials):
        super().__init__(credentials)
        self.base_url = "https://api.bitbucket.org/2.0"
        self.username = credentials.additional_config.get("username") if credentials.additional_config else None
        self.headers = {
            "Authorization": f"Bearer {credentials.api_key}",
            "Content-Type": "application/json"
        }
    
    def validate_credentials(self) -> bool:
        """Validate Bitbucket credentials"""
        try:
            response = requests.get(f"{self.base_url}/user", headers=self.headers)
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Bitbucket credential validation failed: {e}")
            return False
    
    def get_platform_info(self) -> Dict[str, Any]:
        """Get Bitbucket account information"""
        try:
            user_response = requests.get(f"{self.base_url}/user", headers=self.headers)
            repos_response = requests.get(f"{self.base_url}/repositories/{self.username}", headers=self.headers)
            
            if user_response.status_code == 200:
                user_data = user_response.json()
                repos_data = repos_response.json() if repos_response.status_code == 200 else {}
                
                return {
                    "platform": "bitbucket",
                    "username": user_data.get("username", "N/A"),
                    "display_name": user_data.get("display_name", "N/A"),
                    "account_id": user_data.get("account_id", "N/A"),
                    "repositories_count": len(repos_data.get("values", [])),
                    "account_status": user_data.get("account_status", "active")
                }
        except Exception as e:
            self.logger.error(f"Failed to get Bitbucket info: {e}")
        
        return {"platform": "bitbucket", "error": "Failed to retrieve information"}
    
    def create_repository(self, repo_name: str, description: str = "", 
                         private: bool = True, language: str = "python") -> RepositorySetup:
        """Create a new Bitbucket repository"""
        try:
            repo_data = {
                "name": repo_name,
                "description": description,
                "is_private": private,
                "language": language,
                "has_wiki": False,
                "has_issues": True,
                "scm": "git"
            }
            
            response = requests.post(
                f"{self.base_url}/repositories/{self.username}/{repo_name}",
                headers=self.headers,
                json=repo_data
            )
            
            if response.status_code == 200:
                repo_info = response.json()
                clone_links = repo_info.get("links", {}).get("clone", [])
                
                https_clone = next((link["href"] for link in clone_links if link["name"] == "https"), "")
                ssh_clone = next((link["href"] for link in clone_links if link["name"] == "ssh"), "")
                
                return RepositorySetup(
                    success=True,
                    platform="bitbucket",
                    repo_name=repo_info["name"],
                    repo_url=repo_info["links"]["html"]["href"],
                    clone_url=https_clone,
                    ssh_url=ssh_clone,
                    repo_id=repo_info["uuid"]
                )
            else:
                return RepositorySetup(
                    success=False,
                    platform="bitbucket",
                    error_message=response.text
                )
                
        except Exception as e:
            self.logger.error(f"Failed to create Bitbucket repository: {e}")
            return RepositorySetup(
                success=False,
                platform="bitbucket",
                error_message=str(e)
            )
    
    def setup_pipeline(self, repo_name: str, pipeline_config: str) -> Dict[str, Any]:
        """Setup Bitbucket Pipelines"""
        try:
            # Create bitbucket-pipelines.yml file
            file_data = {
                "message": "Add Bitbucket Pipelines configuration",
                "files": {
                    "bitbucket-pipelines.yml": pipeline_config
                }
            }
            
            response = requests.post(
                f"{self.base_url}/repositories/{self.username}/{repo_name}/src",
                headers=self.headers,
                json=file_data
            )
            
            if response.status_code == 201:
                return {"success": True, "pipeline_configured": True}
            else:
                return {"success": False, "error": response.text}
                
        except Exception as e:
            self.logger.error(f"Failed to setup Bitbucket Pipelines: {e}")
            return {"success": False, "error": str(e)}

class PlatformManager:
    """Central manager for all platform integrations"""
    
    def __init__(self):
        self.platforms: Dict[str, PlatformIntegration] = {}
        self.logger = logging.getLogger(__name__)
    
    def register_platform(self, platform_name: str, integration: PlatformIntegration):
        """Register a platform integration"""
        self.platforms[platform_name] = integration
        self.logger.info(f"Registered platform: {platform_name}")
    
    def get_platform(self, platform_name: str) -> Optional[PlatformIntegration]:
        """Get platform integration by name"""
        return self.platforms.get(platform_name)
    
    def validate_all_credentials(self) -> Dict[str, bool]:
        """Validate credentials for all registered platforms"""
        results = {}
        for name, platform in self.platforms.items():
            try:
                results[name] = platform.validate_credentials()
            except Exception as e:
                results[name] = False
                self.logger.error(f"Validation failed for {name}: {e}")
        return results
    
    def get_all_platform_info(self) -> Dict[str, Any]:
        """Get information for all registered platforms"""
        info = {}
        for name, platform in self.platforms.items():
            try:
                info[name] = platform.get_platform_info()
            except Exception as e:
                info[name] = {"platform": name, "error": str(e)}
        return info
    
    def deploy_full_stack_app(self, project_path: str, project_name: str,
                             frontend_platform: str = "vercel",
                             database_platform: str = "supabase",
                             repo_platform: str = "github",
                             enable_payments: bool = False) -> Dict[str, Any]:
        """Deploy complete full-stack application"""
        results = {
            "project_name": project_name,
            "deployment_started": datetime.now().isoformat(),
            "steps": []
        }
        
        try:
            # Step 1: Create GitHub repository
            if repo_platform in self.platforms:
                github = self.platforms[repo_platform]
                repo_result = github.create_repository(
                    repo_name=project_name,
                    description=f"Full-stack application: {project_name}",
                    private=False
                )
                results["steps"].append({
                    "step": "repository_creation",
                    "platform": repo_platform,
                    "success": repo_result.success,
                    "details": asdict(repo_result)
                })
                
                if repo_result.success:
                    # Push code to repository
                    push_success = github.push_project_to_repo(project_path, project_name)
                    results["steps"].append({
                        "step": "code_push",
                        "platform": repo_platform,
                        "success": push_success
                    })
            
            # Step 2: Setup database
            if database_platform in self.platforms:
                db = self.platforms[database_platform]
                db_result = db.create_project(
                    project_name=f"{project_name}-db",
                    region="us-east-1"
                )
                results["steps"].append({
                    "step": "database_setup",
                    "platform": database_platform,
                    "success": db_result.success,
                    "details": asdict(db_result)
                })
            
            # Step 3: Deploy frontend
            if frontend_platform in self.platforms:
                deploy = self.platforms[frontend_platform]
                
                # Prepare environment variables
                env_vars = {}
                if database_platform in self.platforms and "database_setup" in [s["step"] for s in results["steps"]]:
                    db_step = next(s for s in results["steps"] if s["step"] == "database_setup")
                    if db_step["success"] and db_step["details"].get("credentials"):
                        creds = db_step["details"]["credentials"]
                        env_vars.update({
                            "DATABASE_URL": db_step["details"].get("connection_string", ""),
                            "NEXT_PUBLIC_SUPABASE_URL": creds.get("url", ""),
                            "NEXT_PUBLIC_SUPABASE_ANON_KEY": creds.get("anon_key", ""),
                            "SUPABASE_SERVICE_ROLE_KEY": creds.get("service_role_key", "")
                        })
                
                deploy_result = deploy.deploy_project(project_path, project_name, env_vars)
                results["steps"].append({
                    "step": "frontend_deployment",
                    "platform": frontend_platform,
                    "success": deploy_result.success,
                    "details": asdict(deploy_result)
                })
            
            # Step 4: Setup payments (optional)
            if enable_payments and "stripe" in self.platforms:
                stripe = self.platforms["stripe"]
                product_result = stripe.create_product(
                    name=f"{project_name} Subscription",
                    description=f"Subscription for {project_name}",
                    price_cents=999,  # $9.99
                    interval="month"
                )
                results["steps"].append({
                    "step": "payment_setup",
                    "platform": "stripe",
                    "success": product_result.get("success", False),
                    "details": product_result
                })
            
            # Calculate overall success
            results["overall_success"] = all(step.get("success", False) for step in results["steps"])
            results["deployment_completed"] = datetime.now().isoformat()
            
            return results
            
        except Exception as e:
            results["error"] = str(e)
            results["overall_success"] = False
            return results

# Global platform manager instance
platform_manager = PlatformManager()

def setup_platform_credentials(platform_configs: Dict[str, Dict[str, str]]) -> Dict[str, bool]:
    """Setup credentials for multiple platforms"""
    results = {}
    
    for platform_name, config in platform_configs.items():
        try:
            credentials = PlatformCredentials(
                platform_name=platform_name,
                **config
            )
            
            if platform_name == "vercel":
                integration = VercelIntegration(credentials)
            elif platform_name == "supabase":
                integration = SupabaseIntegration(credentials)
            elif platform_name == "stripe":
                integration = StripeIntegration(credentials)
            elif platform_name == "github":
                integration = GitHubIntegration(credentials)
            else:
                results[platform_name] = False
                continue
            
            platform_manager.register_platform(platform_name, integration)
            results[platform_name] = integration.validate_credentials()
            
        except Exception as e:
            logging.error(f"Failed to setup {platform_name}: {e}")
            results[platform_name] = False
    
    return results

def deploy_full_stack_project(project_path: str, project_name: str, 
                             deployment_config: Dict[str, Any] = None) -> Dict[str, Any]:
    """Deploy complete full-stack project to configured platforms"""
    config = deployment_config or {
        "frontend_platform": "vercel",
        "database_platform": "supabase", 
        "repo_platform": "github",
        "enable_payments": False
    }
    
    return platform_manager.deploy_full_stack_app(project_path, project_name, **config)