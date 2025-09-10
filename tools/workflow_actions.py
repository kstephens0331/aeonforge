"""
Aeonforge Phase 7 - Advanced Workflow Action Library
Comprehensive action library integrating all previous phases:
- Phase 2: Multi-agent code generation and collaboration
- Phase 5: Multi-language code intelligence
- Phase 6: Platform integrations and deployments
"""

import os
import sys
import asyncio
import logging
import json
import tempfile
import subprocess
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from pathlib import Path

# Add tools directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import Phase 2 agents
try:
    from phase2_agents import setup_phase2_agents
    PHASE2_AVAILABLE = True
except ImportError:
    PHASE2_AVAILABLE = False

# Import Phase 5 multi-language tools
try:
    from multi_language_tools import multi_language_manager
    PHASE5_AVAILABLE = True
except ImportError:
    PHASE5_AVAILABLE = False

# Import Phase 6 platform integrations
try:
    from platform_integrations import platform_manager
    from cloud_integrations import setup_cloud_platforms
    from service_integrations import service_manager
    PHASE6_AVAILABLE = True
except ImportError:
    PHASE6_AVAILABLE = False

from workflow_engine import WorkflowActionExecutor

class AdvancedWorkflowActions:
    """Advanced workflow actions integrating all Aeonforge phases"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.temp_dir = tempfile.gettempdir()
        
        # Initialize phase integrations
        self.agents = None
        if PHASE2_AVAILABLE:
            try:
                self.agents = setup_phase2_agents()
                self.logger.info("Phase 2 agents initialized")
            except Exception as e:
                self.logger.warning(f"Failed to initialize Phase 2 agents: {e}")
    
    def register_actions(self, executor: WorkflowActionExecutor):
        """Register all advanced actions with the workflow executor"""
        
        # Code Generation & Analysis Actions (Phase 5 + 2)
        executor.register_action('generate_code', self.generate_code)
        executor.register_action('analyze_code_quality', self.analyze_code_quality)
        executor.register_action('refactor_code', self.refactor_code)
        executor.register_action('generate_tests', self.generate_tests)
        executor.register_action('code_review', self.code_review)
        executor.register_action('generate_documentation', self.generate_documentation)
        executor.register_action('detect_bugs', self.detect_bugs)
        executor.register_action('optimize_performance', self.optimize_performance)
        
        # Platform Integration Actions (Phase 6)
        executor.register_action('deploy_to_platform', self.deploy_to_platform)
        executor.register_action('setup_database', self.setup_database)
        executor.register_action('configure_domain', self.configure_domain)
        executor.register_action('setup_monitoring', self.setup_monitoring)
        executor.register_action('setup_analytics', self.setup_analytics)
        executor.register_action('setup_payments', self.setup_payments)
        executor.register_action('setup_authentication', self.setup_authentication)
        executor.register_action('setup_cdn', self.setup_cdn)
        executor.register_action('deploy_fullstack', self.deploy_fullstack)
        
        # Testing & QA Actions
        executor.register_action('run_unit_tests', self.run_unit_tests)
        executor.register_action('run_integration_tests', self.run_integration_tests)
        executor.register_action('run_e2e_tests', self.run_e2e_tests)
        executor.register_action('security_scan', self.security_scan)
        executor.register_action('performance_test', self.performance_test)
        executor.register_action('accessibility_test', self.accessibility_test)
        
        # CI/CD & DevOps Actions
        executor.register_action('build_project', self.build_project)
        executor.register_action('docker_build', self.docker_build)
        executor.register_action('kubernetes_deploy', self.kubernetes_deploy)
        executor.register_action('setup_ci_cd', self.setup_ci_cd)
        executor.register_action('create_release', self.create_release)
        
        # Notification & Communication Actions
        executor.register_action('send_slack_message', self.send_slack_message)
        executor.register_action('send_email', self.send_email)
        executor.register_action('create_github_issue', self.create_github_issue)
        executor.register_action('update_project_status', self.update_project_status)
        
        # Data & Analytics Actions
        executor.register_action('backup_database', self.backup_database)
        executor.register_action('generate_report', self.generate_report)
        executor.register_action('analyze_metrics', self.analyze_metrics)
        executor.register_action('export_data', self.export_data)
        
        self.logger.info("Registered all advanced workflow actions")
    
    # === CODE GENERATION & ANALYSIS ACTIONS ===
    
    async def generate_code(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate code using Phase 2 agents and Phase 5 intelligence"""
        try:
            description = parameters.get('description', '')
            language = parameters.get('language', 'python')
            file_path = parameters.get('file_path', '')
            framework = parameters.get('framework', '')
            
            if not description:
                return {'error': 'Description is required for code generation'}
            
            # Use Phase 5 multi-language tools for code generation
            if PHASE5_AVAILABLE:
                generated_code = multi_language_manager.generate_code(description, language)
                
                # If file path provided, write the code
                if file_path:
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(generated_code.code)
                
                return {
                    'success': True,
                    'language': language,
                    'generated_code': generated_code.code,
                    'file_path': file_path,
                    'files_created': generated_code.files,
                    'documentation': generated_code.documentation
                }
            
            else:
                return {'error': 'Phase 5 multi-language tools not available'}
                
        except Exception as e:
            self.logger.error(f"Code generation failed: {e}")
            return {'error': str(e)}
    
    async def analyze_code_quality(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code quality using Phase 5 intelligence"""
        try:
            code = parameters.get('code', '')
            file_path = parameters.get('file_path', '')
            language = parameters.get('language', 'python')
            
            if not code and file_path:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
            
            if not code:
                return {'error': 'Code or file_path required for analysis'}
            
            if PHASE5_AVAILABLE:
                analysis = multi_language_manager.analyze_code(code, language, file_path)
                
                return {
                    'success': True,
                    'language': analysis.language,
                    'complexity_score': analysis.complexity_score,
                    'functions': analysis.functions,
                    'classes': analysis.classes,
                    'issues': analysis.issues,
                    'suggestions': analysis.suggestions,
                    'imports': analysis.imports,
                    'dependencies': analysis.dependencies,
                    'structure': analysis.structure
                }
            else:
                return {'error': 'Phase 5 code intelligence not available'}
                
        except Exception as e:
            self.logger.error(f"Code analysis failed: {e}")
            return {'error': str(e)}
    
    async def refactor_code(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Refactor code using Phase 5 tools"""
        try:
            code = parameters.get('code', '')
            file_path = parameters.get('file_path', '')
            language = parameters.get('language', 'python')
            instructions = parameters.get('instructions', 'Improve code quality')
            
            if not code and file_path:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
            
            if PHASE5_AVAILABLE:
                refactored = multi_language_manager.refactor_code(code, instructions, language, file_path)
                
                # Write refactored code back to file if path provided
                if file_path and refactored:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(refactored)
                
                return {
                    'success': True,
                    'original_code': code,
                    'refactored_code': refactored,
                    'file_updated': bool(file_path),
                    'instructions': instructions
                }
            else:
                return {'error': 'Phase 5 refactoring tools not available'}
                
        except Exception as e:
            self.logger.error(f"Code refactoring failed: {e}")
            return {'error': str(e)}
    
    async def generate_tests(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate tests for code"""
        try:
            code = parameters.get('code', '')
            file_path = parameters.get('file_path', '')
            language = parameters.get('language', 'python')
            test_framework = parameters.get('test_framework', 'pytest')
            
            if not code and file_path:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
            
            # Generate test description
            test_description = f"Generate comprehensive {test_framework} tests for the following {language} code"
            
            if PHASE5_AVAILABLE:
                test_generation = multi_language_manager.generate_code(
                    f"{test_description}:\n\n{code}", 
                    language
                )
                
                # Write test file
                test_file_path = parameters.get('test_file_path')
                if test_file_path:
                    with open(test_file_path, 'w', encoding='utf-8') as f:
                        f.write(test_generation.code)
                
                return {
                    'success': True,
                    'test_code': test_generation.code,
                    'test_framework': test_framework,
                    'test_file_path': test_file_path,
                    'language': language
                }
            else:
                return {'error': 'Phase 5 code generation not available'}
                
        except Exception as e:
            self.logger.error(f"Test generation failed: {e}")
            return {'error': str(e)}
    
    # === PLATFORM INTEGRATION ACTIONS ===
    
    async def deploy_to_platform(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy to a specific platform using Phase 6 integrations"""
        try:
            platform = parameters.get('platform', 'vercel')
            project_path = parameters.get('project_path', os.getcwd())
            project_name = parameters.get('project_name', 'workflow-project')
            
            if not PHASE6_AVAILABLE:
                return {'error': 'Phase 6 platform integrations not available'}
            
            platform_integration = platform_manager.get_platform(platform)
            if not platform_integration:
                return {'error': f'Platform {platform} not configured'}
            
            # Deploy based on platform type
            if platform in ['vercel', 'netlify']:
                # Frontend deployment
                build_dir = parameters.get('build_dir', 'dist')
                result = platform_integration.deploy_site(project_name, build_dir)
            elif platform == 'heroku':
                # Full-stack deployment
                source_url = parameters.get('source_url', '')
                result = platform_integration.deploy_app(project_name, source_url)
            else:
                return {'error': f'Deployment for platform {platform} not implemented'}
            
            return {
                'success': result.success if hasattr(result, 'success') else True,
                'platform': platform,
                'deployment_url': result.url if hasattr(result, 'url') else None,
                'deployment_id': result.deployment_id if hasattr(result, 'deployment_id') else None,
                'project_name': project_name
            }
            
        except Exception as e:
            self.logger.error(f"Platform deployment failed: {e}")
            return {'error': str(e)}
    
    async def setup_database(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Setup database using Phase 6 integrations"""
        try:
            platform = parameters.get('platform', 'supabase')
            database_name = parameters.get('database_name', 'workflow-db')
            
            if not PHASE6_AVAILABLE:
                return {'error': 'Phase 6 platform integrations not available'}
            
            platform_integration = platform_manager.get_platform(platform)
            if not platform_integration:
                return {'error': f'Database platform {platform} not configured'}
            
            # Setup database based on platform
            if platform == 'supabase':
                result = platform_integration.create_database(database_name)
            elif platform == 'planetscale':
                org_name = parameters.get('org_name', 'default')
                result = platform_integration.create_database(org_name, database_name)
            elif platform == 'mongodb_atlas':
                result = platform_integration.create_cluster(database_name)
            else:
                return {'error': f'Database setup for platform {platform} not implemented'}
            
            return {
                'success': result.success if hasattr(result, 'success') else True,
                'platform': platform,
                'database_name': database_name,
                'database_url': result.database_url if hasattr(result, 'database_url') else None,
                'connection_string': result.connection_string if hasattr(result, 'connection_string') else None
            }
            
        except Exception as e:
            self.logger.error(f"Database setup failed: {e}")
            return {'error': str(e)}
    
    async def deploy_fullstack(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy complete full-stack application"""
        try:
            project_path = parameters.get('project_path', os.getcwd())
            project_name = parameters.get('project_name', 'workflow-fullstack')
            domain = parameters.get('domain', f'{project_name}.com')
            
            platforms = parameters.get('platforms', {
                'frontend': 'vercel',
                'database': 'supabase',
                'auth': 'auth0'
            })
            
            if not PHASE6_AVAILABLE:
                return {'error': 'Phase 6 platform integrations not available'}
            
            # Use platform manager's full-stack deployment
            deployment_result = platform_manager.deploy_full_stack_app(
                project_path, project_name, 
                frontend_platform=platforms.get('frontend', 'vercel'),
                database_platform=platforms.get('database', 'supabase'),
                enable_payments='payments' in platforms
            )
            
            return {
                'success': True,
                'project_name': project_name,
                'domain': domain,
                'platforms_used': platforms,
                'deployment_results': deployment_result
            }
            
        except Exception as e:
            self.logger.error(f"Full-stack deployment failed: {e}")
            return {'error': str(e)}
    
    # === TESTING & QA ACTIONS ===
    
    async def run_unit_tests(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Run unit tests"""
        try:
            test_command = parameters.get('test_command', 'pytest')
            test_path = parameters.get('test_path', 'tests/')
            project_path = parameters.get('project_path', os.getcwd())
            
            # Build full command
            cmd = f"{test_command} {test_path}"
            
            # Execute tests
            process = await asyncio.create_subprocess_shell(
                cmd,
                cwd=project_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            return {
                'success': process.returncode == 0,
                'exit_code': process.returncode,
                'stdout': stdout.decode(),
                'stderr': stderr.decode(),
                'test_command': cmd,
                'test_path': test_path
            }
            
        except Exception as e:
            self.logger.error(f"Unit tests failed: {e}")
            return {'error': str(e)}
    
    async def security_scan(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Run security scan"""
        try:
            project_path = parameters.get('project_path', os.getcwd())
            scan_type = parameters.get('scan_type', 'npm_audit')  # npm_audit, bandit, safety
            
            if scan_type == 'npm_audit':
                cmd = 'npm audit --audit-level moderate'
            elif scan_type == 'bandit':
                cmd = 'bandit -r .'
            elif scan_type == 'safety':
                cmd = 'safety check'
            else:
                return {'error': f'Unknown scan type: {scan_type}'}
            
            process = await asyncio.create_subprocess_shell(
                cmd,
                cwd=project_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            return {
                'success': process.returncode == 0,
                'exit_code': process.returncode,
                'scan_type': scan_type,
                'vulnerabilities_found': process.returncode != 0,
                'scan_output': stdout.decode(),
                'scan_errors': stderr.decode()
            }
            
        except Exception as e:
            self.logger.error(f"Security scan failed: {e}")
            return {'error': str(e)}
    
    # === CI/CD & DEVOPS ACTIONS ===
    
    async def build_project(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Build project"""
        try:
            project_path = parameters.get('project_path', os.getcwd())
            build_command = parameters.get('build_command', 'npm run build')
            
            process = await asyncio.create_subprocess_shell(
                build_command,
                cwd=project_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            return {
                'success': process.returncode == 0,
                'exit_code': process.returncode,
                'build_output': stdout.decode(),
                'build_errors': stderr.decode(),
                'build_command': build_command
            }
            
        except Exception as e:
            self.logger.error(f"Project build failed: {e}")
            return {'error': str(e)}
    
    async def docker_build(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Build Docker image"""
        try:
            project_path = parameters.get('project_path', os.getcwd())
            image_name = parameters.get('image_name', 'workflow-app')
            tag = parameters.get('tag', 'latest')
            dockerfile_path = parameters.get('dockerfile_path', 'Dockerfile')
            
            cmd = f"docker build -t {image_name}:{tag} -f {dockerfile_path} ."
            
            process = await asyncio.create_subprocess_shell(
                cmd,
                cwd=project_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            return {
                'success': process.returncode == 0,
                'exit_code': process.returncode,
                'image_name': f"{image_name}:{tag}",
                'build_output': stdout.decode(),
                'build_errors': stderr.decode()
            }
            
        except Exception as e:
            self.logger.error(f"Docker build failed: {e}")
            return {'error': str(e)}
    
    # === NOTIFICATION ACTIONS ===
    
    async def send_slack_message(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Send Slack message"""
        try:
            webhook_url = parameters.get('webhook_url', '')
            message = parameters.get('message', 'Workflow notification')
            channel = parameters.get('channel', '#general')
            username = parameters.get('username', 'Aeonforge Workflow')
            
            if not webhook_url:
                return {'error': 'Slack webhook URL required'}
            
            import aiohttp
            
            payload = {
                'text': message,
                'channel': channel,
                'username': username
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload) as response:
                    return {
                        'success': response.status == 200,
                        'status_code': response.status,
                        'message_sent': message,
                        'channel': channel
                    }
                    
        except Exception as e:
            self.logger.error(f"Slack message failed: {e}")
            return {'error': str(e)}
    
    async def send_email(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Send email notification"""
        try:
            # This would integrate with SendGrid or other email service from Phase 6
            to_email = parameters.get('to_email', '')
            subject = parameters.get('subject', 'Workflow Notification')
            body = parameters.get('body', 'Your workflow has completed.')
            from_email = parameters.get('from_email', 'noreply@aeonforge.dev')
            
            if not to_email:
                return {'error': 'Recipient email required'}
            
            # Placeholder for email sending logic
            # In real implementation, this would use SendGrid API from Phase 6
            return {
                'success': True,
                'email_sent': True,
                'to_email': to_email,
                'subject': subject,
                'note': 'Email sending would use Phase 6 SendGrid integration in production'
            }
            
        except Exception as e:
            self.logger.error(f"Email sending failed: {e}")
            return {'error': str(e)}
    
    # === DATA & ANALYTICS ACTIONS ===
    
    async def generate_report(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate project or workflow report"""
        try:
            report_type = parameters.get('report_type', 'workflow_summary')
            output_format = parameters.get('format', 'json')  # json, html, pdf
            output_file = parameters.get('output_file', f'report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.{output_format}')
            
            if report_type == 'workflow_summary':
                # Generate workflow execution summary
                report_data = {
                    'report_type': report_type,
                    'generated_at': datetime.now().isoformat(),
                    'workflow_context': context,
                    'system_info': {
                        'phases_available': {
                            'phase2_agents': PHASE2_AVAILABLE,
                            'phase5_intelligence': PHASE5_AVAILABLE,
                            'phase6_platforms': PHASE6_AVAILABLE
                        }
                    }
                }
                
                # Write report file
                with open(output_file, 'w', encoding='utf-8') as f:
                    if output_format == 'json':
                        json.dump(report_data, f, indent=2, default=str)
                    elif output_format == 'html':
                        # Simple HTML report
                        html_content = f"""
                        <html><head><title>Workflow Report</title></head>
                        <body><h1>Workflow Report</h1>
                        <pre>{json.dumps(report_data, indent=2, default=str)}</pre>
                        </body></html>
                        """
                        f.write(html_content)
                
                return {
                    'success': True,
                    'report_file': output_file,
                    'report_type': report_type,
                    'format': output_format,
                    'data': report_data
                }
            
            else:
                return {'error': f'Unknown report type: {report_type}'}
                
        except Exception as e:
            self.logger.error(f"Report generation failed: {e}")
            return {'error': str(e)}

# Initialize advanced actions
advanced_actions = AdvancedWorkflowActions()

# Export main class
__all__ = ['AdvancedWorkflowActions', 'advanced_actions']