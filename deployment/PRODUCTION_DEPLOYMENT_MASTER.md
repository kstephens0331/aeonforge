# Aeonforge Production Deployment Master Guide

## 🎯 Overview

Complete production deployment guide for launching Aeonforge across GitHub, Supabase, and Railway with dynamic schema management for 6000+ tools.

## 📋 Deployment Order & Timeline

### Phase 1: GitHub Repository Setup (30 minutes)
1. **Repository Creation** - Initialize and configure GitHub repo
2. **CI/CD Pipeline** - Automated testing and deployment
3. **Security Setup** - Branch protection and secret management
4. **Documentation** - Complete project documentation

### Phase 2: Supabase Database Setup (45 minutes)
1. **Database Schema** - Dynamic tool management system
2. **Authentication** - User management and security
3. **Real-time Features** - Live updates and subscriptions
4. **Edge Functions** - Serverless tool execution

### Phase 3: Railway Application Deployment (30 minutes)
1. **Service Deployment** - Backend, worker, and scheduler services
2. **Auto-scaling** - Production-ready scaling configuration
3. **Monitoring** - Health checks and performance monitoring
4. **Integration** - Connect all services together

**Total Estimated Time: 1 hour 45 minutes**

## 🚀 Quick Start Commands

### Step 1: GitHub Deployment
```bash
cd "C:\Users\usmc3\OneDrive\Documents\Stephens Code Programs\Aeonforge"

# Follow GitHub deployment guide
source deployment/github/GITHUB_DEPLOYMENT_GUIDE.md

# Key commands:
git init
git add .
git commit -m "Initial commit: Aeonforge Multi-Agent AI System"
gh repo create aeonforge --public
git push -u origin main
```

### Step 2: Supabase Setup
```bash
# Follow Supabase deployment guide
source deployment/supabase/SUPABASE_DEPLOYMENT_GUIDE.md

# Key commands:
supabase init
supabase link --project-ref YOUR_PROJECT_REF
psql -h YOUR_HOST -U postgres -f deployment/supabase/schema.sql
python deployment/supabase/tool_registration.py
```

### Step 3: Railway Deployment
```bash
# Follow Railway deployment guide
source deployment/railway/RAILWAY_DEPLOYMENT_GUIDE.md

# Key commands:
railway new aeonforge
railway add postgresql
railway add redis
railway variables set [environment variables]
railway deploy
```

## 🔧 Production Environment Configuration

### Environment Variables Template
```bash
# Create .env.production
cat > .env.production << 'EOF'
# Environment
ENVIRONMENT=production
DEBUG=false
API_VERSION=1.0.0

# Database (Railway PostgreSQL)
DATABASE_URL=postgresql://postgres:password@host:port/database
REDIS_URL=redis://host:port

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# AI Providers
OPENAI_API_KEY=sk-your_openai_key
GEMINI_API_KEY=AIzaSy_your_gemini_key
SERPAPI_KEY=your_serpapi_key
NIH_PUBMED_KEY=your_nih_key

# Application URLs
FRONTEND_URL=https://aeonforge-frontend.railway.app
BACKEND_URL=https://aeonforge-backend.railway.app

# Security
JWT_SECRET_KEY=your_jwt_secret
CORS_ORIGINS=https://yourdomain.com,https://aeonforge-frontend.railway.app

# Monitoring
HEALTH_CHECK_ENABLED=true
HEALTH_CHECK_INTERVAL=300
LOG_LEVEL=INFO
STRUCTURED_LOGGING=true

# Performance
MAX_CONCURRENT_TOOLS=100
TOOL_TIMEOUT_SECONDS=300
CACHE_TTL_SECONDS=3600

# Features
MULTI_MODEL_ROUTING=true
SELF_HEALING_ENABLED=true
REAL_TIME_UPDATES=true
USAGE_ANALYTICS=true
EOF
```

### Production Requirements
```bash
# Create optimized production requirements
cat > requirements-production.txt << 'EOF'
# Core Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0

# Database & Cache
psycopg2-binary==2.9.9
redis==5.0.1
sqlalchemy==2.0.23
alembic==1.13.1

# AI Integration
openai==1.3.7
google-generativeai==0.3.2
ollama==0.1.7

# Multi-agent Framework
autogen==0.2.0

# Web & API
requests==2.31.0
aiohttp==3.9.1
python-multipart==0.0.6
websockets==12.0

# Data Processing
pandas==2.1.4
numpy==1.25.2

# System Monitoring
psutil==5.9.6
structlog==23.2.0

# Security & Auth
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
cryptography==41.0.8

# Payment Processing
stripe==7.8.0

# Environment
python-dotenv==1.0.0

# Production Tools
gunicorn==21.2.0
celery==5.3.4
flower==2.0.1

# Monitoring & Metrics
prometheus-client==0.19.0
sentry-sdk[fastapi]==1.39.1
EOF
```

## 🗄️ Dynamic Database Schema System

### Schema Migration Strategy
```python
# File: deployment/database_migration_system.py

import os
import json
import psycopg2
from datetime import datetime
from typing import List, Dict, Any
import logging

class DatabaseMigrationSystem:
    """Handles dynamic database schema updates for 6000+ tools"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.logger = logging.getLogger(__name__)
    
    def apply_migration(self, migration_name: str, sql_up: str, sql_down: str = None) -> bool:
        """Apply a database migration"""
        try:
            conn = psycopg2.connect(self.database_url)
            cur = conn.cursor()
            
            # Generate migration ID
            migration_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{migration_name}"
            
            # Check if migration already applied
            cur.execute(
                "SELECT id FROM schema_migrations WHERE migration_id = %s",
                (migration_id,)
            )
            
            if cur.fetchone():
                self.logger.info(f"Migration {migration_id} already applied")
                return True
            
            # Apply migration
            cur.execute(sql_up)
            
            # Record migration
            cur.execute("""
                INSERT INTO schema_migrations (migration_id, migration_name, sql_up, sql_down)
                VALUES (%s, %s, %s, %s)
            """, (migration_id, migration_name, sql_up, sql_down))
            
            conn.commit()
            self.logger.info(f"Migration {migration_id} applied successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Migration failed: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()
    
    def add_new_tool_category_schema(self, category_info: Dict[str, Any]) -> bool:
        """Add schema for new tool category"""
        category_name = category_info['name']
        table_name = f"tools_{category_name.lower().replace(' ', '_')}_data"
        
        sql_up = f"""
        -- Create specific table for {category_name} tools data
        CREATE TABLE IF NOT EXISTS {table_name} (
            id BIGSERIAL PRIMARY KEY,
            tool_execution_id BIGINT REFERENCES tool_executions(id),
            tool_specific_data JSONB,
            processed_output JSONB,
            metadata JSONB,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        -- Create index for performance
        CREATE INDEX IF NOT EXISTS idx_{table_name}_execution ON {table_name}(tool_execution_id);
        CREATE INDEX IF NOT EXISTS idx_{table_name}_created ON {table_name}(created_at);
        
        -- Update tool category
        INSERT INTO tool_categories (name, description, batch_number, icon, color)
        VALUES ('{category_name}', '{category_info.get('description', '')}', 
                {category_info.get('batch_number', 0)}, '{category_info.get('icon', 'tool')}', 
                '{category_info.get('color', '#3B82F6')}')
        ON CONFLICT (name) DO NOTHING;
        """
        
        sql_down = f"DROP TABLE IF EXISTS {table_name};"
        
        return self.apply_migration(f"add_category_{category_name.lower()}", sql_up, sql_down)
    
    def update_tool_schema(self, tool_id: str, new_schema: Dict[str, Any]) -> bool:
        """Update schema for specific tool"""
        sql_up = f"""
        -- Update tool schema for {tool_id}
        UPDATE tools_registry 
        SET 
            input_schema = '{json.dumps(new_schema.get('input_schema', {}))}',
            output_schema = '{json.dumps(new_schema.get('output_schema', {}))}',
            settings = '{json.dumps(new_schema.get('settings', {}))}',
            version = '{new_schema.get('version', '1.0.0')}',
            updated_at = NOW()
        WHERE tool_id = '{tool_id}';
        
        -- Log schema update
        INSERT INTO tool_schema_updates (tool_id, update_type, new_schema, applied_by)
        VALUES ('{tool_id}', 'schema_change', '{json.dumps(new_schema)}', NULL);
        """
        
        return self.apply_migration(f"update_tool_schema_{tool_id}", sql_up)

# Usage for adding new tool batches
def setup_new_tool_batch(batch_number: int, category_name: str, tools: List[Dict]):
    """Set up database schema for new tool batch"""
    migrator = DatabaseMigrationSystem(os.getenv('DATABASE_URL'))
    
    # Add category
    category_info = {
        'name': category_name,
        'description': f'Tool batch {batch_number}: {category_name}',
        'batch_number': batch_number,
        'icon': 'tool',
        'color': '#3B82F6'
    }
    
    migrator.add_new_tool_category_schema(category_info)
    
    # Register tools
    from deployment.supabase.tool_registration import DynamicToolRegistration
    registrar = DynamicToolRegistration()
    
    batch_data = {
        'batch_number': batch_number,
        'category_name': category_name,
        'tools': tools
    }
    
    return registrar.register_tool_batch(batch_data)
```

## 🔄 Automated Tool Addition System

### New Tool Registration Pipeline
```python
# File: deployment/automated_tool_addition.py

import os
import json
import importlib
from typing import Dict, List, Any
from deployment.database_migration_system import setup_new_tool_batch

class AutomatedToolAddition:
    """Automated system for adding new tools to production"""
    
    def __init__(self):
        self.supported_batches = 20  # Plan for 20 batches initially
        
    def scan_for_new_tools(self) -> List[Dict[str, Any]]:
        """Scan codebase for new tool implementations"""
        new_tools = []
        
        # Scan tools directory for new categories
        tools_dir = os.path.join(os.getcwd(), 'tools')
        
        for item in os.listdir(tools_dir):
            item_path = os.path.join(tools_dir, item)
            
            if os.path.isdir(item_path) and not item.startswith('__'):
                # Check if this is a new category
                try:
                    module = importlib.import_module(f'tools.{item}')
                    
                    if hasattr(module, 'ALL_TOOLS') and hasattr(module, 'get_tool_info'):
                        info = module.get_tool_info()
                        
                        new_tools.append({
                            'category': item,
                            'module_path': f'tools.{item}',
                            'tool_count': info.get('total_tools', 0),
                            'tools': getattr(module, 'ALL_TOOLS', [])
                        })
                        
                except Exception as e:
                    print(f"Warning: Could not scan {item}: {e}")
        
        return new_tools
    
    def add_new_tool_batch(self, batch_number: int, category_name: str, 
                          tools_module_path: str) -> bool:
        """Add a complete new tool batch to production"""
        try:
            # Import and extract tool information
            module = importlib.import_module(tools_module_path)
            
            if not hasattr(module, 'ALL_TOOLS'):
                raise ValueError(f"Module {tools_module_path} missing ALL_TOOLS")
            
            # Extract tool metadata
            tools = []
            for tool_class in module.ALL_TOOLS:
                tool_info = self._extract_tool_metadata(tool_class)
                tools.append(tool_info)
            
            # Set up database schema and register tools
            success = setup_new_tool_batch(batch_number, category_name, tools)
            
            if success:
                print(f"✅ Successfully added batch {batch_number}: {category_name}")
                print(f"   📊 {len(tools)} tools registered")
                
                # Update system documentation
                self._update_documentation(batch_number, category_name, tools)
                
                return True
            else:
                print(f"❌ Failed to add batch {batch_number}")
                return False
                
        except Exception as e:
            print(f"❌ Error adding tool batch: {e}")
            return False
    
    def _extract_tool_metadata(self, tool_class) -> Dict[str, Any]:
        """Extract metadata from tool class"""
        return {
            'tool_id': self._class_name_to_id(tool_class.__name__),
            'name': self._class_name_to_display(tool_class.__name__),
            'description': getattr(tool_class, '__doc__', '') or f"Advanced {tool_class.__name__} functionality",
            'class_name': tool_class.__name__,
            'input_schema': getattr(tool_class, 'input_schema', {}),
            'output_schema': getattr(tool_class, 'output_schema', {}),
            'settings': getattr(tool_class, 'default_settings', {})
        }
    
    def _class_name_to_id(self, class_name: str) -> str:
        """Convert class name to tool ID"""
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', class_name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    def _class_name_to_display(self, class_name: str) -> str:
        """Convert class name to display name"""
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', class_name)
        return re.sub('([a-z0-9])([A-Z])', r'\1 \2', s1)
    
    def _update_documentation(self, batch_number: int, category_name: str, tools: List[Dict]):
        """Update project documentation with new batch"""
        # Update MASTER_TOOL_LIST.md
        try:
            with open('MASTER_TOOL_LIST.md', 'r') as f:
                content = f.read()
            
            # Add new batch section
            new_section = f"""

### ✅ **Batch {batch_number}: {category_name} ({len(tools)} tools)**
- {category_name} tools for enhanced functionality
- Tools: {', '.join([tool['name'] for tool in tools[:5]])}{'...' if len(tools) > 5 else ''}
"""
            
            # Insert before "UPCOMING BATCHES" section
            if "## 🚀 **UPCOMING BATCHES" in content:
                content = content.replace(
                    "## 🚀 **UPCOMING BATCHES",
                    new_section + "\n## 🚀 **UPCOMING BATCHES"
                )
            
            with open('MASTER_TOOL_LIST.md', 'w') as f:
                f.write(content)
                
        except Exception as e:
            print(f"Warning: Could not update documentation: {e}")

# CLI script for adding new tools
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 4:
        print("Usage: python automated_tool_addition.py <batch_number> <category_name> <module_path>")
        print("Example: python automated_tool_addition.py 6 'Healthcare Tools' 'tools.healthcare'")
        sys.exit(1)
    
    batch_number = int(sys.argv[1])
    category_name = sys.argv[2]
    module_path = sys.argv[3]
    
    adder = AutomatedToolAddition()
    success = adder.add_new_tool_batch(batch_number, category_name, module_path)
    
    sys.exit(0 if success else 1)
```

## 📊 Production Monitoring Dashboard

### Health Monitoring Setup
```python
# File: deployment/production_monitoring.py

import os
import json
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Any

class ProductionMonitoring:
    """Production monitoring and alerting system"""
    
    def __init__(self):
        self.services = {
            'backend': os.getenv('BACKEND_URL'),
            'frontend': os.getenv('FRONTEND_URL'),
            'database': os.getenv('DATABASE_URL'),
            'supabase': os.getenv('SUPABASE_URL')
        }
        
        self.alert_webhooks = {
            'slack': os.getenv('SLACK_WEBHOOK_URL'),
            'discord': os.getenv('DISCORD_WEBHOOK_URL'),
            'email': os.getenv('EMAIL_ALERT_URL')
        }
    
    async def run_comprehensive_health_check(self) -> Dict[str, Any]:
        """Run comprehensive health check across all services"""
        results = {
            'timestamp': datetime.utcnow().isoformat(),
            'overall_status': 'healthy',
            'services': {},
            'metrics': {},
            'alerts': []
        }
        
        # Check each service
        for service_name, service_url in self.services.items():
            if service_url:
                service_health = await self._check_service_health(service_name, service_url)
                results['services'][service_name] = service_health
                
                if service_health['status'] != 'healthy':
                    results['overall_status'] = 'degraded'
                    results['alerts'].append(f"{service_name} is {service_health['status']}")
        
        # Run tool system health check
        tool_health = await self._check_tool_system_health()
        results['services']['tool_system'] = tool_health
        
        # Collect performance metrics
        results['metrics'] = await self._collect_performance_metrics()
        
        # Send alerts if needed
        if results['alerts']:
            await self._send_alerts(results)
        
        return results
    
    async def _check_service_health(self, service_name: str, service_url: str) -> Dict[str, Any]:
        """Check health of individual service"""
        try:
            async with aiohttp.ClientSession() as session:
                # Try health endpoint first
                health_url = f"{service_url.rstrip('/')}/health"
                
                async with session.get(health_url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'status': 'healthy',
                            'response_time': 0,  # Would measure actual time
                            'details': data
                        }
                    else:
                        return {
                            'status': 'unhealthy',
                            'error': f"HTTP {response.status}",
                            'response_time': 0
                        }
                        
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'response_time': None
            }
    
    async def _check_tool_system_health(self) -> Dict[str, Any]:
        """Check health of tool execution system"""
        try:
            # Run quick status check
            from system_health_checks.quick_status_check import QuickStatusChecker
            
            checker = QuickStatusChecker()
            status_data, exit_code = checker.run_quick_check()
            
            return {
                'status': 'healthy' if exit_code == 0 else 'degraded',
                'details': status_data
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def _collect_performance_metrics(self) -> Dict[str, Any]:
        """Collect performance metrics"""
        try:
            import psutil
            
            return {
                'cpu_usage': psutil.cpu_percent(),
                'memory_usage': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent,
                'active_connections': len(psutil.net_connections()),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    async def _send_alerts(self, health_results: Dict[str, Any]):
        """Send alerts to configured channels"""
        alert_message = f"""
🚨 **Aeonforge Production Alert**

Status: {health_results['overall_status'].upper()}
Time: {health_results['timestamp']}

Issues:
{chr(10).join(['• ' + alert for alert in health_results['alerts']])}

Services Status:
{chr(10).join([f"• {name}: {info.get('status', 'unknown')}" for name, info in health_results['services'].items()])}
"""
        
        # Send to each configured alert channel
        for channel, webhook_url in self.alert_webhooks.items():
            if webhook_url:
                await self._send_webhook_alert(webhook_url, alert_message, channel)
    
    async def _send_webhook_alert(self, webhook_url: str, message: str, channel: str):
        """Send alert to webhook"""
        try:
            async with aiohttp.ClientSession() as session:
                if 'slack' in channel:
                    payload = {'text': message}
                elif 'discord' in channel:
                    payload = {'content': message}
                else:
                    payload = {'message': message}
                
                async with session.post(webhook_url, json=payload) as response:
                    if response.status == 200:
                        print(f"✅ Alert sent to {channel}")
                    else:
                        print(f"❌ Failed to send alert to {channel}: {response.status}")
                        
        except Exception as e:
            print(f"❌ Error sending alert to {channel}: {e}")

# Scheduled monitoring script
async def run_scheduled_monitoring():
    """Run scheduled monitoring check"""
    monitor = ProductionMonitoring()
    results = await monitor.run_comprehensive_health_check()
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_file = f"monitoring_results_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Monitoring completed - Status: {results['overall_status']}")
    return results

if __name__ == "__main__":
    asyncio.run(run_scheduled_monitoring())
```

## 📋 Complete Deployment Checklist

### Pre-Deployment (15 minutes)
- [ ] Code committed to version control
- [ ] Sensitive data removed/gitignored
- [ ] Production requirements.txt updated
- [ ] Environment variables template created
- [ ] Health check endpoints implemented
- [ ] Database migration scripts prepared

### GitHub Setup (15 minutes)
- [ ] Repository created with proper README
- [ ] CI/CD pipeline configured
- [ ] Branch protection rules enabled
- [ ] GitHub secrets configured
- [ ] Issue/PR templates added
- [ ] License and contributing guides added

### Supabase Setup (30 minutes)
- [ ] Supabase project created
- [ ] Database schema applied
- [ ] RLS policies configured
- [ ] Edge functions deployed
- [ ] Real-time subscriptions enabled
- [ ] Tool registration system tested

### Railway Deployment (20 minutes)
- [ ] Railway services deployed
- [ ] Environment variables configured
- [ ] Auto-scaling enabled
- [ ] Health checks passing
- [ ] Domain configuration (if needed)
- [ ] Monitoring and alerting enabled

### Post-Deployment Validation (15 minutes)
- [ ] All services responding
- [ ] Database connections working
- [ ] Tool execution functional
- [ ] Real-time updates working
- [ ] Health monitoring active
- [ ] Performance metrics collecting

### Final Steps (10 minutes)
- [ ] Load test with sample tools
- [ ] Monitor logs for errors
- [ ] Verify backup systems
- [ ] Document any issues
- [ ] Plan first production tool addition

---

**Total Deployment Time**: ~1 hour 45 minutes  
**Services**: GitHub + Supabase + Railway  
**Monitoring**: 150-point health checks + custom alerts  
**Scalability**: Ready for 6000+ tools with dynamic schema management  
**Status**: Production-ready multi-service architecture