"""
Popular Service Integrations for Aeonforge
Authentication, Analytics, Monitoring, and other essential services
"""

import os
import json
import requests
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging
import jwt
from datetime import datetime, timedelta
from platform_integrations import PlatformIntegration, PlatformCredentials

@dataclass
class AuthSetup:
    """Authentication setup result"""
    success: bool
    platform: str
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    auth_url: Optional[str] = None
    callback_url: Optional[str] = None
    config: Dict[str, Any] = None
    error_message: Optional[str] = None

class Auth0Integration(PlatformIntegration):
    """Auth0 authentication service integration"""
    
    def __init__(self, credentials: PlatformCredentials):
        super().__init__(credentials)
        self.domain = credentials.additional_config.get("domain")
        self.client_id = credentials.api_key
        self.client_secret = credentials.secret_key
        self.base_url = f"https://{self.domain}"
    
    def validate_credentials(self) -> bool:
        try:
            # Get management API token
            token = self._get_management_token()
            return token is not None
        except Exception as e:
            self.logger.error(f"Auth0 credential validation failed: {e}")
            return False
    
    def get_platform_info(self) -> Dict[str, Any]:
        try:
            token = self._get_management_token()
            headers = {"Authorization": f"Bearer {token}"}
            
            # Get tenant info
            response = requests.get(f"{self.base_url}/api/v2/tenants/settings", headers=headers)
            tenant_info = response.json() if response.status_code == 200 else {}
            
            return {
                "platform": "auth0",
                "domain": self.domain,
                "tenant": tenant_info.get("friendly_name", ""),
                "features": ["authentication", "authorization", "social_login", "mfa", "user_management"]
            }
        except Exception as e:
            return {"platform": "auth0", "error": str(e)}
    
    def setup_application(self, app_name: str, app_type: str = "spa",
                         callback_urls: List[str] = None,
                         logout_urls: List[str] = None) -> AuthSetup:
        """Setup Auth0 application"""
        try:
            token = self._get_management_token()
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            app_data = {
                "name": app_name,
                "app_type": app_type,
                "callbacks": callback_urls or ["http://localhost:3000/callback"],
                "allowed_logout_urls": logout_urls or ["http://localhost:3000"],
                "web_origins": ["http://localhost:3000"],
                "allowed_origins": ["http://localhost:3000"],
                "grant_types": [
                    "authorization_code",
                    "implicit",
                    "refresh_token",
                    "client_credentials"
                ]
            }
            
            response = requests.post(
                f"{self.base_url}/api/v2/clients",
                headers=headers,
                json=app_data
            )
            
            if response.status_code == 201:
                app = response.json()
                return AuthSetup(
                    success=True,
                    platform="auth0",
                    client_id=app["client_id"],
                    client_secret=app.get("client_secret"),
                    auth_url=f"{self.base_url}/authorize",
                    callback_url=callback_urls[0] if callback_urls else "http://localhost:3000/callback",
                    config={
                        "domain": self.domain,
                        "clientId": app["client_id"],
                        "clientSecret": app.get("client_secret"),
                        "audience": f"{self.base_url}/api/v2/",
                        "scope": "openid profile email"
                    }
                )
            else:
                return AuthSetup(
                    success=False,
                    platform="auth0",
                    error_message=f"Application setup failed: {response.text}"
                )
                
        except Exception as e:
            return AuthSetup(
                success=False,
                platform="auth0",
                error_message=str(e)
            )
    
    def _get_management_token(self) -> Optional[str]:
        """Get Auth0 Management API token"""
        try:
            token_data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "audience": f"{self.base_url}/api/v2/",
                "grant_type": "client_credentials"
            }
            
            response = requests.post(f"{self.base_url}/oauth/token", json=token_data)
            
            if response.status_code == 200:
                return response.json()["access_token"]
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to get management token: {e}")
            return None

class FirebaseIntegration(PlatformIntegration):
    """Google Firebase integration"""
    
    def __init__(self, credentials: PlatformCredentials):
        super().__init__(credentials)
        self.project_id = credentials.project_id
        self.api_key = credentials.api_key
        self.service_account = credentials.additional_config.get("service_account_json")
    
    def validate_credentials(self) -> bool:
        try:
            # Test Firebase Auth REST API
            response = requests.get(
                f"https://identitytoolkit.googleapis.com/v1/projects/{self.project_id}:getConfig?key={self.api_key}"
            )
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Firebase credential validation failed: {e}")
            return False
    
    def get_platform_info(self) -> Dict[str, Any]:
        try:
            # Get project config
            response = requests.get(
                f"https://identitytoolkit.googleapis.com/v1/projects/{self.project_id}:getConfig?key={self.api_key}"
            )
            config = response.json() if response.status_code == 200 else {}
            
            return {
                "platform": "firebase",
                "project_id": self.project_id,
                "auth_domain": f"{self.project_id}.firebaseapp.com",
                "features": ["authentication", "firestore", "realtime_database", "hosting", "functions", "storage"]
            }
        except Exception as e:
            return {"platform": "firebase", "error": str(e)}
    
    def setup_authentication(self, enable_providers: List[str] = None) -> AuthSetup:
        """Setup Firebase Authentication"""
        try:
            # Default providers
            providers = enable_providers or ["email", "google"]
            
            # Firebase config for frontend
            config = {
                "apiKey": self.api_key,
                "authDomain": f"{self.project_id}.firebaseapp.com",
                "projectId": self.project_id,
                "storageBucket": f"{self.project_id}.appspot.com",
                "messagingSenderId": "123456789",  # Would be actual sender ID
                "appId": "1:123456789:web:abcdef123456"  # Would be actual app ID
            }
            
            return AuthSetup(
                success=True,
                platform="firebase",
                auth_url=f"https://{self.project_id}.firebaseapp.com/__/auth/handler",
                config=config
            )
            
        except Exception as e:
            return AuthSetup(
                success=False,
                platform="firebase",
                error_message=str(e)
            )

class AnalyticsIntegration(PlatformIntegration):
    """Google Analytics integration"""
    
    def __init__(self, credentials: PlatformCredentials):
        super().__init__(credentials)
        self.measurement_id = credentials.api_key  # GA4 Measurement ID
        self.api_secret = credentials.secret_key   # Measurement Protocol API Secret
    
    def validate_credentials(self) -> bool:
        try:
            # Test measurement protocol
            test_event = {
                "client_id": "test_client",
                "events": [{
                    "name": "test_event",
                    "params": {"test_param": "test_value"}
                }]
            }
            
            response = requests.post(
                f"https://www.google-analytics.com/mp/collect?measurement_id={self.measurement_id}&api_secret={self.api_secret}",
                json=test_event
            )
            
            return response.status_code == 204
        except Exception as e:
            self.logger.error(f"Analytics validation failed: {e}")
            return False
    
    def get_platform_info(self) -> Dict[str, Any]:
        return {
            "platform": "google_analytics",
            "measurement_id": self.measurement_id,
            "features": ["page_tracking", "event_tracking", "conversion_tracking", "real_time_data"]
        }
    
    def generate_tracking_code(self, website_url: str) -> Dict[str, str]:
        """Generate Google Analytics tracking code"""
        gtag_code = f"""
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id={self.measurement_id}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{self.measurement_id}');
</script>
"""
        
        react_code = f"""
import {{ gtag }} from 'ga-gtag';

// Initialize GA
gtag('config', '{self.measurement_id}');

// Track page view
export const trackPageView = (page_path) => {{
  gtag('config', '{self.measurement_id}', {{
    page_path: page_path,
  }});
}};

// Track custom event
export const trackEvent = (action, category, label, value) => {{
  gtag('event', action, {{
    event_category: category,
    event_label: label,
    value: value,
  }});
}};
"""
        
        return {
            "html": gtag_code.strip(),
            "react": react_code.strip(),
            "measurement_id": self.measurement_id
        }

class MonitoringIntegration(PlatformIntegration):
    """Application monitoring integration (Sentry, LogRocket, etc.)"""
    
    def __init__(self, credentials: PlatformCredentials):
        super().__init__(credentials)
        self.platform_type = credentials.platform_name  # "sentry" or "logrocket"
        self.dsn = credentials.api_key
        self.project_id = credentials.project_id
    
    def validate_credentials(self) -> bool:
        if self.platform_type == "sentry":
            try:
                # Test Sentry DSN
                response = requests.post(
                    self.dsn,
                    json={"message": "test", "level": "info"},
                    headers={"Content-Type": "application/json"}
                )
                return True  # Sentry accepts most requests
            except:
                return False
        return True
    
    def get_platform_info(self) -> Dict[str, Any]:
        return {
            "platform": self.platform_type,
            "dsn": self.dsn,
            "features": ["error_tracking", "performance_monitoring", "session_replay", "alerts"]
        }
    
    def generate_monitoring_code(self) -> Dict[str, str]:
        """Generate monitoring integration code"""
        if self.platform_type == "sentry":
            javascript_code = f"""
import * as Sentry from "@sentry/browser";
import {{ Integrations }} from "@sentry/tracing";

Sentry.init({{
  dsn: "{self.dsn}",
  integrations: [
    new Integrations.BrowserTracing(),
  ],
  tracesSampleRate: 1.0,
  environment: process.env.NODE_ENV || "development",
}});

// Capture exception
export const captureException = (error) => {{
  Sentry.captureException(error);
}};

// Add breadcrumb
export const addBreadcrumb = (message, category = "custom") => {{
  Sentry.addBreadcrumb({{
    message,
    category,
    level: "info",
  }});
}};
"""
            
            python_code = f"""
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="{self.dsn}",
    integrations=[
        DjangoIntegration(auto_enabling=True),
        FlaskIntegration(auto_enabling=True),
    ],
    traces_sample_rate=1.0,
    send_default_pii=True
)

# Capture exception
def capture_exception(error):
    sentry_sdk.capture_exception(error)

# Add context
def add_context(key, value):
    sentry_sdk.set_context(key, value)
"""
            
            return {
                "javascript": javascript_code.strip(),
                "python": python_code.strip(),
                "dsn": self.dsn
            }
        
        return {"error": "Unsupported monitoring platform"}

class CDNIntegration(PlatformIntegration):
    """CDN service integration (Cloudflare, AWS CloudFront)"""
    
    def __init__(self, credentials: PlatformCredentials):
        super().__init__(credentials)
        self.platform_type = credentials.platform_name  # "cloudflare"
        self.api_key = credentials.api_key
        self.email = credentials.additional_config.get("email")
        self.zone_id = credentials.additional_config.get("zone_id")
    
    def validate_credentials(self) -> bool:
        if self.platform_type == "cloudflare":
            try:
                headers = {
                    "X-Auth-Email": self.email,
                    "X-Auth-Key": self.api_key,
                    "Content-Type": "application/json"
                }
                
                response = requests.get(
                    "https://api.cloudflare.com/client/v4/user",
                    headers=headers
                )
                
                return response.status_code == 200
            except:
                return False
        return False
    
    def get_platform_info(self) -> Dict[str, Any]:
        if self.platform_type == "cloudflare":
            try:
                headers = {
                    "X-Auth-Email": self.email,
                    "X-Auth-Key": self.api_key,
                    "Content-Type": "application/json"
                }
                
                # Get zones
                response = requests.get(
                    "https://api.cloudflare.com/client/v4/zones",
                    headers=headers
                )
                
                zones = response.json().get("result", []) if response.status_code == 200 else []
                
                return {
                    "platform": "cloudflare",
                    "zones": [{"name": zone["name"], "id": zone["id"]} for zone in zones],
                    "features": ["cdn", "ddos_protection", "ssl", "caching", "dns"]
                }
            except Exception as e:
                return {"platform": "cloudflare", "error": str(e)}
        
        return {"platform": self.platform_type}
    
    def setup_cdn(self, domain: str, origin_url: str) -> Dict[str, Any]:
        """Setup CDN for domain"""
        if self.platform_type == "cloudflare":
            try:
                headers = {
                    "X-Auth-Email": self.email,
                    "X-Auth-Key": self.api_key,
                    "Content-Type": "application/json"
                }
                
                # Create DNS record
                dns_data = {
                    "type": "CNAME",
                    "name": domain,
                    "content": origin_url,
                    "ttl": 1,  # Auto TTL
                    "proxied": True  # Enable Cloudflare proxy (CDN)
                }
                
                response = requests.post(
                    f"https://api.cloudflare.com/client/v4/zones/{self.zone_id}/dns_records",
                    headers=headers,
                    json=dns_data
                )
                
                if response.status_code == 200:
                    result = response.json()["result"]
                    return {
                        "success": True,
                        "record_id": result["id"],
                        "cdn_url": f"https://{domain}",
                        "proxied": result["proxied"]
                    }
                else:
                    return {"success": False, "error": response.text}
                    
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        return {"success": False, "error": "Unsupported CDN platform"}

class AlgoliaIntegration(PlatformIntegration):
    """Algolia search service integration"""
    
    def __init__(self, credentials: PlatformCredentials):
        super().__init__(credentials)
        self.app_id = credentials.additional_config.get("app_id") if credentials.additional_config else None
        self.admin_key = credentials.api_key
        self.search_key = credentials.secret_key
        self.base_url = f"https://{self.app_id}-dsn.algolia.net/1"
        self.headers = {
            "X-Algolia-API-Key": self.admin_key,
            "X-Algolia-Application-Id": self.app_id,
            "Content-Type": "application/json"
        }
    
    def validate_credentials(self) -> bool:
        """Validate Algolia credentials"""
        try:
            response = requests.get(f"{self.base_url}/keys", headers=self.headers)
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Algolia credential validation failed: {e}")
            return False
    
    def get_platform_info(self) -> Dict[str, Any]:
        """Get Algolia application information"""
        try:
            # Get indices
            indices_response = requests.get(f"{self.base_url}/indexes", headers=self.headers)
            
            if indices_response.status_code == 200:
                indices_data = indices_response.json()
                
                return {
                    "platform": "algolia",
                    "app_id": self.app_id,
                    "indices_count": len(indices_data.get("items", [])),
                    "plan": "Unknown",  # Algolia doesn't expose plan info via API
                    "status": "active"
                }
        except Exception as e:
            self.logger.error(f"Failed to get Algolia info: {e}")
        
        return {"platform": "algolia", "error": "Failed to retrieve information"}
    
    def create_index(self, index_name: str, settings: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a new Algolia search index"""
        try:
            # Create index by adding a dummy record (Algolia creates index automatically)
            dummy_record = {"objectID": "dummy", "title": "Dummy record"}
            
            response = requests.post(
                f"{self.base_url}/indexes/{index_name}",
                headers=self.headers,
                json=[dummy_record]
            )
            
            if response.status_code == 201:
                # Set index settings if provided
                if settings:
                    settings_response = requests.put(
                        f"{self.base_url}/indexes/{index_name}/settings",
                        headers=self.headers,
                        json=settings
                    )
                
                # Remove dummy record
                requests.delete(
                    f"{self.base_url}/indexes/{index_name}/dummy",
                    headers=self.headers
                )
                
                return {
                    "success": True,
                    "index_name": index_name,
                    "app_id": self.app_id,
                    "search_url": f"https://{self.app_id}-dsn.algolia.net/1/indexes/{index_name}"
                }
            else:
                return {"success": False, "error": response.text}
                
        except Exception as e:
            self.logger.error(f"Failed to create Algolia index: {e}")
            return {"success": False, "error": str(e)}
    
    def configure_search_settings(self, index_name: str, settings: Dict[str, Any]) -> bool:
        """Configure search settings for an index"""
        try:
            response = requests.put(
                f"{self.base_url}/indexes/{index_name}/settings",
                headers=self.headers,
                json=settings
            )
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Failed to configure Algolia settings: {e}")
            return False
    
    def upload_data(self, index_name: str, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Upload data to Algolia index"""
        try:
            # Ensure all records have objectID
            for i, record in enumerate(records):
                if "objectID" not in record:
                    record["objectID"] = str(i)
            
            response = requests.post(
                f"{self.base_url}/indexes/{index_name}/batch",
                headers=self.headers,
                json={"requests": [{"action": "addObject", "body": record} for record in records]}
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "task_id": result.get("taskID"),
                    "records_uploaded": len(records)
                }
            else:
                return {"success": False, "error": response.text}
                
        except Exception as e:
            self.logger.error(f"Failed to upload data to Algolia: {e}")
            return {"success": False, "error": str(e)}
    
    def get_api_keys(self) -> Dict[str, Any]:
        """Get API keys for frontend integration"""
        return {
            "app_id": self.app_id,
            "search_key": self.search_key,
            "admin_key": "***HIDDEN***"  # Don't expose admin key
        }

class ClerkIntegration(PlatformIntegration):
    """Clerk authentication service integration"""
    
    def __init__(self, credentials: PlatformCredentials):
        super().__init__(credentials)
        self.secret_key = credentials.api_key
        self.base_url = "https://api.clerk.com/v1"
        self.headers = {
            "Authorization": f"Bearer {credentials.api_key}",
            "Content-Type": "application/json"
        }
    
    def validate_credentials(self) -> bool:
        """Validate Clerk credentials"""
        try:
            response = requests.get(f"{self.base_url}/applications", headers=self.headers)
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Clerk credential validation failed: {e}")
            return False
    
    def get_platform_info(self) -> Dict[str, Any]:
        """Get Clerk application information"""
        try:
            apps_response = requests.get(f"{self.base_url}/applications", headers=self.headers)
            users_response = requests.get(f"{self.base_url}/users", headers=self.headers)
            
            if apps_response.status_code == 200:
                apps_data = apps_response.json()
                users_data = users_response.json() if users_response.status_code == 200 else []
                
                return {
                    "platform": "clerk",
                    "applications": len(apps_data),
                    "users_count": len(users_data),
                    "plan": "Unknown"
                }
        except Exception as e:
            self.logger.error(f"Failed to get Clerk info: {e}")
        
        return {"platform": "clerk", "error": "Failed to retrieve information"}
    
    def setup_application(self, app_name: str, allowed_origins: List[str] = None) -> AuthSetup:
        """Setup Clerk authentication for application"""
        try:
            # Create application instance
            instance_data = {
                "name": app_name,
                "allowed_origins": allowed_origins or []
            }
            
            response = requests.post(
                f"{self.base_url}/instances",
                headers=self.headers,
                json=instance_data
            )
            
            if response.status_code == 201:
                instance_info = response.json()
                
                return AuthSetup(
                    success=True,
                    platform="clerk",
                    client_id=instance_info.get("publishable_key"),
                    auth_url=f"https://{instance_info.get('slug')}.clerk.accounts.dev",
                    config={
                        "publishable_key": instance_info.get("publishable_key"),
                        "secret_key": self.secret_key,
                        "frontend_api": instance_info.get("frontend_api"),
                        "instance_id": instance_info.get("id")
                    }
                )
            else:
                return AuthSetup(
                    success=False,
                    platform="clerk",
                    error_message=response.text
                )
                
        except Exception as e:
            self.logger.error(f"Failed to setup Clerk application: {e}")
            return AuthSetup(
                success=False,
                platform="clerk",
                error_message=str(e)
            )

class PayPalIntegration(PlatformIntegration):
    """PayPal payment service integration"""
    
    def __init__(self, credentials: PlatformCredentials):
        super().__init__(credentials)
        self.client_id = credentials.api_key
        self.client_secret = credentials.secret_key
        self.sandbox = credentials.additional_config.get("sandbox", True) if credentials.additional_config else True
        self.base_url = "https://api.sandbox.paypal.com" if self.sandbox else "https://api.paypal.com"
        self.access_token = None
    
    def _get_access_token(self) -> str:
        """Get PayPal access token"""
        try:
            import base64
            
            auth_string = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
            headers = {
                "Authorization": f"Basic {auth_string}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            response = requests.post(
                f"{self.base_url}/v1/oauth2/token",
                headers=headers,
                data="grant_type=client_credentials"
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data["access_token"]
                return self.access_token
            
        except Exception as e:
            self.logger.error(f"Failed to get PayPal access token: {e}")
        
        return None
    
    def validate_credentials(self) -> bool:
        """Validate PayPal credentials"""
        try:
            token = self._get_access_token()
            return token is not None
        except Exception as e:
            self.logger.error(f"PayPal credential validation failed: {e}")
            return False
    
    def get_platform_info(self) -> Dict[str, Any]:
        """Get PayPal account information"""
        try:
            if not self.access_token:
                self._get_access_token()
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            # Get account info
            response = requests.get(f"{self.base_url}/v1/identity/oauth2/userinfo", headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                return {
                    "platform": "paypal",
                    "account_id": user_data.get("user_id", "N/A"),
                    "email": user_data.get("email", "N/A"),
                    "name": user_data.get("name", "N/A"),
                    "verified": user_data.get("verified_account", False),
                    "sandbox": self.sandbox
                }
        except Exception as e:
            self.logger.error(f"Failed to get PayPal info: {e}")
        
        return {"platform": "paypal", "error": "Failed to retrieve information"}
    
    def create_product(self, product_name: str, description: str, 
                      product_type: str = "DIGITAL") -> Dict[str, Any]:
        """Create a PayPal product"""
        try:
            if not self.access_token:
                self._get_access_token()
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            product_data = {
                "name": product_name,
                "description": description,
                "type": product_type,
                "category": "SOFTWARE"
            }
            
            response = requests.post(
                f"{self.base_url}/v1/catalogs/products",
                headers=headers,
                json=product_data
            )
            
            if response.status_code == 201:
                product_info = response.json()
                return {
                    "success": True,
                    "product_id": product_info["id"],
                    "name": product_info["name"],
                    "status": product_info["status"]
                }
            else:
                return {"success": False, "error": response.text}
                
        except Exception as e:
            self.logger.error(f"Failed to create PayPal product: {e}")
            return {"success": False, "error": str(e)}
    
    def create_subscription_plan(self, product_id: str, plan_name: str, 
                               price: str, currency: str = "USD", 
                               interval: str = "MONTH") -> Dict[str, Any]:
        """Create a PayPal subscription plan"""
        try:
            if not self.access_token:
                self._get_access_token()
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            plan_data = {
                "product_id": product_id,
                "name": plan_name,
                "billing_cycles": [{
                    "frequency": {
                        "interval_unit": interval,
                        "interval_count": 1
                    },
                    "tenure_type": "REGULAR",
                    "sequence": 1,
                    "total_cycles": 0,
                    "pricing_scheme": {
                        "fixed_price": {
                            "value": price,
                            "currency_code": currency
                        }
                    }
                }],
                "payment_preferences": {
                    "auto_bill_outstanding": True,
                    "setup_fee": {
                        "value": "0",
                        "currency_code": currency
                    },
                    "setup_fee_failure_action": "CONTINUE",
                    "payment_failure_threshold": 3
                }
            }
            
            response = requests.post(
                f"{self.base_url}/v1/billing/plans",
                headers=headers,
                json=plan_data
            )
            
            if response.status_code == 201:
                plan_info = response.json()
                return {
                    "success": True,
                    "plan_id": plan_info["id"],
                    "name": plan_info["name"],
                    "status": plan_info["status"]
                }
            else:
                return {"success": False, "error": response.text}
                
        except Exception as e:
            self.logger.error(f"Failed to create PayPal subscription plan: {e}")
            return {"success": False, "error": str(e)}

class DatadogIntegration(PlatformIntegration):
    """Datadog monitoring integration"""
    
    def __init__(self, credentials: PlatformCredentials):
        super().__init__(credentials)
        self.api_key = credentials.api_key
        self.app_key = credentials.secret_key
        self.base_url = "https://api.datadoghq.com/api/v1"
        self.headers = {
            "DD-API-KEY": self.api_key,
            "DD-APPLICATION-KEY": self.app_key,
            "Content-Type": "application/json"
        }
    
    def validate_credentials(self) -> bool:
        """Validate Datadog credentials"""
        try:
            response = requests.get(f"{self.base_url}/validate", headers=self.headers)
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Datadog credential validation failed: {e}")
            return False
    
    def get_platform_info(self) -> Dict[str, Any]:
        """Get Datadog account information"""
        try:
            dashboards_response = requests.get(f"{self.base_url}/dashboard", headers=self.headers)
            
            if dashboards_response.status_code == 200:
                dashboards_data = dashboards_response.json()
                
                return {
                    "platform": "datadog",
                    "dashboards_count": len(dashboards_data.get("dashboards", [])),
                    "status": "active"
                }
        except Exception as e:
            self.logger.error(f"Failed to get Datadog info: {e}")
        
        return {"platform": "datadog", "error": "Failed to retrieve information"}
    
    def create_dashboard(self, title: str, description: str = "", 
                        widgets: List[Dict] = None) -> Dict[str, Any]:
        """Create a Datadog dashboard"""
        try:
            dashboard_data = {
                "title": title,
                "description": description,
                "widgets": widgets or [],
                "layout_type": "ordered",
                "is_read_only": False
            }
            
            response = requests.post(
                f"{self.base_url}/dashboard",
                headers=self.headers,
                json=dashboard_data
            )
            
            if response.status_code == 200:
                dashboard_info = response.json()
                return {
                    "success": True,
                    "dashboard_id": dashboard_info["id"],
                    "url": dashboard_info["url"],
                    "title": dashboard_info["title"]
                }
            else:
                return {"success": False, "error": response.text}
                
        except Exception as e:
            self.logger.error(f"Failed to create Datadog dashboard: {e}")
            return {"success": False, "error": str(e)}
    
    def create_monitor(self, monitor_name: str, query: str, 
                      message: str = "", monitor_type: str = "metric alert") -> Dict[str, Any]:
        """Create a Datadog monitor"""
        try:
            monitor_data = {
                "name": monitor_name,
                "type": monitor_type,
                "query": query,
                "message": message,
                "options": {
                    "notify_audit": False,
                    "locked": False,
                    "timeout_h": 0,
                    "renotify_interval": 0,
                    "no_data_timeframe": None
                }
            }
            
            response = requests.post(
                f"{self.base_url}/monitor",
                headers=self.headers,
                json=monitor_data
            )
            
            if response.status_code == 200:
                monitor_info = response.json()
                return {
                    "success": True,
                    "monitor_id": monitor_info["id"],
                    "name": monitor_info["name"],
                    "state": monitor_info.get("overall_state", "OK")
                }
            else:
                return {"success": False, "error": response.text}
                
        except Exception as e:
            self.logger.error(f"Failed to create Datadog monitor: {e}")
            return {"success": False, "error": str(e)}

# Service integration manager
class ServiceIntegrationManager:
    """Manager for all service integrations"""
    
    def __init__(self):
        self.services: Dict[str, PlatformIntegration] = {}
        self.logger = logging.getLogger(__name__)
    
    def register_service(self, service_name: str, integration: PlatformIntegration):
        """Register a service integration"""
        self.services[service_name] = integration
        self.logger.info(f"Registered service: {service_name}")
    
    def setup_full_application_stack(self, app_name: str, domain: str,
                                   services: List[str] = None) -> Dict[str, Any]:
        """Setup complete application stack with multiple services"""
        services = services or ["auth", "analytics", "monitoring"]
        
        results = {
            "app_name": app_name,
            "domain": domain,
            "setup_started": datetime.now().isoformat(),
            "services": {}
        }
        
        # Setup authentication
        if "auth" in services and "auth0" in self.services:
            auth_result = self.services["auth0"].setup_application(
                app_name,
                callback_urls=[f"https://{domain}/callback"],
                logout_urls=[f"https://{domain}"]
            )
            results["services"]["auth"] = asdict(auth_result)
        
        # Setup analytics
        if "analytics" in services and "analytics" in self.services:
            tracking_code = self.services["analytics"].generate_tracking_code(f"https://{domain}")
            results["services"]["analytics"] = {
                "success": True,
                "tracking_code": tracking_code
            }
        
        # Setup monitoring
        if "monitoring" in services and "sentry" in self.services:
            monitoring_code = self.services["sentry"].generate_monitoring_code()
            results["services"]["monitoring"] = {
                "success": True,
                "monitoring_code": monitoring_code
            }
        
        # Setup CDN
        if "cdn" in services and "cloudflare" in self.services:
            cdn_result = self.services["cloudflare"].setup_cdn(domain, f"https://{app_name}.vercel.app")
            results["services"]["cdn"] = cdn_result
        
        results["setup_completed"] = datetime.now().isoformat()
        results["overall_success"] = all(
            service_result.get("success", True) 
            for service_result in results["services"].values()
        )
        
        return results

# Global service manager
service_manager = ServiceIntegrationManager()

def setup_application_services(service_configs: Dict[str, Dict[str, Any]]) -> Dict[str, bool]:
    """Setup application services"""
    results = {}
    
    for service_name, config in service_configs.items():
        try:
            credentials = PlatformCredentials(
                platform_name=service_name,
                **config
            )
            
            if service_name == "auth0":
                integration = Auth0Integration(credentials)
            elif service_name == "firebase":
                integration = FirebaseIntegration(credentials)
            elif service_name == "analytics":
                integration = AnalyticsIntegration(credentials)
            elif service_name in ["sentry", "logrocket"]:
                integration = MonitoringIntegration(credentials)
            elif service_name == "cloudflare":
                integration = CDNIntegration(credentials)
            else:
                results[service_name] = False
                continue
            
            service_manager.register_service(service_name, integration)
            results[service_name] = integration.validate_credentials()
            
        except Exception as e:
            logging.error(f"Failed to setup {service_name}: {e}")
            results[service_name] = False
    
    return results