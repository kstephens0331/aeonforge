"""
Aeonforge Phase 7 - Workflow Trigger System
Comprehensive trigger system for Git events, file changes, scheduling, and webhooks
"""

import os
import asyncio
import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Set
from abc import ABC, abstractmethod
from pathlib import Path
import json
from croniter import croniter
import hashlib
import sqlite3
from dataclasses import dataclass
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent, FileDeletedEvent
import subprocess
from concurrent.futures import ThreadPoolExecutor

from workflow_engine import WorkflowTrigger, TriggerType, workflow_engine

@dataclass
class TriggerEvent:
    """Event data passed to triggered workflows"""
    trigger_type: TriggerType
    workflow_id: str
    timestamp: datetime
    data: Dict[str, Any]
    source: str = "system"

class BaseTriggerHandler(ABC):
    """Abstract base class for trigger handlers"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.active_workflows: Dict[str, WorkflowTrigger] = {}
    
    @abstractmethod
    def register_trigger(self, workflow_id: str, trigger: WorkflowTrigger) -> bool:
        """Register a trigger for a workflow"""
        pass
    
    @abstractmethod
    def unregister_trigger(self, workflow_id: str) -> bool:
        """Unregister trigger for a workflow"""
        pass
    
    @abstractmethod
    def start(self):
        """Start the trigger handler"""
        pass
    
    @abstractmethod
    def stop(self):
        """Stop the trigger handler"""
        pass
    
    async def trigger_workflow(self, workflow_id: str, event_data: Dict[str, Any]):
        """Trigger workflow execution"""
        try:
            execution = await workflow_engine.execute_workflow(workflow_id, event_data)
            self.logger.info(f"Triggered workflow {workflow_id} with execution {execution.id}")
            return execution
        except Exception as e:
            self.logger.error(f"Failed to trigger workflow {workflow_id}: {e}")
            return None

class GitTriggerHandler(BaseTriggerHandler):
    """Handler for Git-based triggers (push, PR, etc.)"""
    
    def __init__(self, repo_path: str = "."):
        super().__init__()
        self.repo_path = repo_path
        self.monitoring = False
        self.last_commit_hash = None
        self.monitor_thread = None
        self.check_interval = 30  # Check every 30 seconds
    
    def register_trigger(self, workflow_id: str, trigger: WorkflowTrigger) -> bool:
        """Register Git trigger"""
        if trigger.trigger_type not in [TriggerType.GIT_PUSH, TriggerType.GIT_PR]:
            return False
        
        self.active_workflows[workflow_id] = trigger
        
        # Start monitoring if this is the first trigger
        if not self.monitoring:
            self.start()
        
        self.logger.info(f"Registered Git trigger for workflow {workflow_id}")
        return True
    
    def unregister_trigger(self, workflow_id: str) -> bool:
        """Unregister Git trigger"""
        if workflow_id in self.active_workflows:
            del self.active_workflows[workflow_id]
            
            # Stop monitoring if no more triggers
            if not self.active_workflows and self.monitoring:
                self.stop()
            
            return True
        return False
    
    def start(self):
        """Start Git monitoring"""
        if not self.monitoring:
            self.monitoring = True
            self.last_commit_hash = self._get_latest_commit_hash()
            self.monitor_thread = threading.Thread(target=self._monitor_git_changes, daemon=True)
            self.monitor_thread.start()
            self.logger.info("Started Git monitoring")
    
    def stop(self):
        """Stop Git monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.logger.info("Stopped Git monitoring")
    
    def _get_latest_commit_hash(self) -> Optional[str]:
        """Get the latest commit hash"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception as e:
            self.logger.error(f"Failed to get commit hash: {e}")
        return None
    
    def _get_commit_info(self, commit_hash: str) -> Dict[str, Any]:
        """Get detailed commit information"""
        try:
            # Get commit details
            result = subprocess.run([
                'git', 'show', '--format=%H|%an|%ae|%at|%s', '--name-only', commit_hash
            ], cwd=self.repo_path, capture_output=True, text=True)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if lines:
                    commit_line = lines[0].split('|')
                    changed_files = lines[1:] if len(lines) > 1 else []
                    
                    return {
                        'commit_hash': commit_line[0],
                        'author_name': commit_line[1],
                        'author_email': commit_line[2],
                        'timestamp': datetime.fromtimestamp(int(commit_line[3])),
                        'message': commit_line[4],
                        'changed_files': [f for f in changed_files if f.strip()]
                    }
        except Exception as e:
            self.logger.error(f"Failed to get commit info: {e}")
        
        return {}
    
    def _monitor_git_changes(self):
        """Monitor Git repository for changes"""
        while self.monitoring:
            try:
                current_hash = self._get_latest_commit_hash()
                
                if current_hash and current_hash != self.last_commit_hash:
                    # New commit detected
                    commit_info = self._get_commit_info(current_hash)
                    
                    # Trigger workflows for Git push events
                    for workflow_id, trigger in self.active_workflows.items():
                        if trigger.trigger_type == TriggerType.GIT_PUSH:
                            # Check if trigger conditions are met
                            if self._should_trigger_for_push(trigger, commit_info):
                                asyncio.run_coroutine_threadsafe(
                                    self.trigger_workflow(workflow_id, {
                                        'event_type': 'git_push',
                                        'commit': commit_info,
                                        'repository_path': self.repo_path
                                    }),
                                    asyncio.get_event_loop()
                                )
                    
                    self.last_commit_hash = current_hash
                
                time.sleep(self.check_interval)
                
            except Exception as e:
                self.logger.error(f"Error in Git monitoring: {e}")
                time.sleep(self.check_interval)
    
    def _should_trigger_for_push(self, trigger: WorkflowTrigger, commit_info: Dict[str, Any]) -> bool:
        """Check if trigger conditions are met for push event"""
        parameters = trigger.parameters
        
        # Check branch filter
        if 'branches' in parameters:
            try:
                current_branch = subprocess.run(
                    ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                    cwd=self.repo_path, capture_output=True, text=True
                ).stdout.strip()
                
                if current_branch not in parameters['branches']:
                    return False
            except:
                pass
        
        # Check file pattern filter
        if 'file_patterns' in parameters:
            changed_files = commit_info.get('changed_files', [])
            patterns = parameters['file_patterns']
            
            import fnmatch
            if not any(any(fnmatch.fnmatch(f, pattern) for pattern in patterns) for f in changed_files):
                return False
        
        # Check author filter
        if 'authors' in parameters:
            author_email = commit_info.get('author_email', '')
            if author_email not in parameters['authors']:
                return False
        
        return True

class FileWatchTriggerHandler(BaseTriggerHandler, FileSystemEventHandler):
    """Handler for file system change triggers"""
    
    def __init__(self, watch_paths: List[str] = None):
        super().__init__()
        self.watch_paths = watch_paths or [os.getcwd()]
        self.observer = Observer()
        self.watching = False
        self.file_hashes: Dict[str, str] = {}
    
    def register_trigger(self, workflow_id: str, trigger: WorkflowTrigger) -> bool:
        """Register file watch trigger"""
        if trigger.trigger_type != TriggerType.FILE_CHANGE:
            return False
        
        self.active_workflows[workflow_id] = trigger
        
        # Start watching if this is the first trigger
        if not self.watching:
            self.start()
        
        self.logger.info(f"Registered file watch trigger for workflow {workflow_id}")
        return True
    
    def unregister_trigger(self, workflow_id: str) -> bool:
        """Unregister file watch trigger"""
        if workflow_id in self.active_workflows:
            del self.active_workflows[workflow_id]
            
            # Stop watching if no more triggers
            if not self.active_workflows and self.watching:
                self.stop()
            
            return True
        return False
    
    def start(self):
        """Start file system watching"""
        if not self.watching:
            for path in self.watch_paths:
                if os.path.exists(path):
                    self.observer.schedule(self, path, recursive=True)
            
            self.observer.start()
            self.watching = True
            self.logger.info(f"Started file watching on paths: {self.watch_paths}")
    
    def stop(self):
        """Stop file system watching"""
        if self.watching:
            self.observer.stop()
            self.observer.join(timeout=5)
            self.watching = False
            self.logger.info("Stopped file watching")
    
    def on_modified(self, event):
        """Handle file modification events"""
        if not event.is_directory:
            self._handle_file_event('modified', event.src_path)
    
    def on_created(self, event):
        """Handle file creation events"""
        if not event.is_directory:
            self._handle_file_event('created', event.src_path)
    
    def on_deleted(self, event):
        """Handle file deletion events"""
        if not event.is_directory:
            self._handle_file_event('deleted', event.src_path)
    
    def _handle_file_event(self, event_type: str, file_path: str):
        """Handle file system events"""
        try:
            # Calculate file hash for change detection (if file exists)
            current_hash = None
            if os.path.exists(file_path) and event_type != 'deleted':
                with open(file_path, 'rb') as f:
                    current_hash = hashlib.md5(f.read()).hexdigest()
                
                # Skip if file hasn't actually changed
                if file_path in self.file_hashes and self.file_hashes[file_path] == current_hash:
                    return
                
                self.file_hashes[file_path] = current_hash
            elif event_type == 'deleted' and file_path in self.file_hashes:
                del self.file_hashes[file_path]
            
            # Trigger workflows that match this file event
            for workflow_id, trigger in self.active_workflows.items():
                if self._should_trigger_for_file_event(trigger, file_path, event_type):
                    asyncio.run_coroutine_threadsafe(
                        self.trigger_workflow(workflow_id, {
                            'event_type': 'file_change',
                            'file_path': file_path,
                            'change_type': event_type,
                            'file_hash': current_hash,
                            'timestamp': datetime.now()
                        }),
                        asyncio.get_event_loop()
                    )
        
        except Exception as e:
            self.logger.error(f"Error handling file event: {e}")
    
    def _should_trigger_for_file_event(self, trigger: WorkflowTrigger, file_path: str, event_type: str) -> bool:
        """Check if trigger conditions are met for file event"""
        parameters = trigger.parameters
        
        # Check event type filter
        if 'event_types' in parameters and event_type not in parameters['event_types']:
            return False
        
        # Check file pattern filter
        if 'file_patterns' in parameters:
            import fnmatch
            patterns = parameters['file_patterns']
            if not any(fnmatch.fnmatch(file_path, pattern) for pattern in patterns):
                return False
        
        # Check path filter
        if 'paths' in parameters:
            if not any(file_path.startswith(path) for path in parameters['paths']):
                return False
        
        # Check ignore patterns
        if 'ignore_patterns' in parameters:
            import fnmatch
            patterns = parameters['ignore_patterns']
            if any(fnmatch.fnmatch(file_path, pattern) for pattern in patterns):
                return False
        
        return True

class ScheduledTriggerHandler(BaseTriggerHandler):
    """Handler for scheduled/cron-based triggers"""
    
    def __init__(self):
        super().__init__()
        self.scheduler_thread = None
        self.running = False
        self.scheduled_workflows: Dict[str, Dict[str, Any]] = {}
    
    def register_trigger(self, workflow_id: str, trigger: WorkflowTrigger) -> bool:
        """Register scheduled trigger"""
        if trigger.trigger_type != TriggerType.SCHEDULED:
            return False
        
        parameters = trigger.parameters
        cron_expression = parameters.get('cron', '0 0 * * *')  # Default: daily at midnight
        
        try:
            # Validate cron expression
            cron = croniter(cron_expression)
            next_run = cron.get_next(datetime)
            
            self.scheduled_workflows[workflow_id] = {
                'trigger': trigger,
                'cron_expression': cron_expression,
                'next_run': next_run,
                'last_run': None
            }
            
            self.active_workflows[workflow_id] = trigger
            
            # Start scheduler if this is the first trigger
            if not self.running:
                self.start()
            
            self.logger.info(f"Registered scheduled trigger for workflow {workflow_id}: {cron_expression}")
            return True
            
        except Exception as e:
            self.logger.error(f"Invalid cron expression '{cron_expression}': {e}")
            return False
    
    def unregister_trigger(self, workflow_id: str) -> bool:
        """Unregister scheduled trigger"""
        if workflow_id in self.active_workflows:
            del self.active_workflows[workflow_id]
            if workflow_id in self.scheduled_workflows:
                del self.scheduled_workflows[workflow_id]
            
            # Stop scheduler if no more triggers
            if not self.active_workflows and self.running:
                self.stop()
            
            return True
        return False
    
    def start(self):
        """Start scheduler"""
        if not self.running:
            self.running = True
            self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
            self.scheduler_thread.start()
            self.logger.info("Started workflow scheduler")
    
    def stop(self):
        """Stop scheduler"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        self.logger.info("Stopped workflow scheduler")
    
    def _scheduler_loop(self):
        """Main scheduler loop"""
        while self.running:
            try:
                current_time = datetime.now()
                
                for workflow_id, schedule_info in list(self.scheduled_workflows.items()):
                    next_run = schedule_info['next_run']
                    
                    if current_time >= next_run:
                        # Time to run this workflow
                        asyncio.run_coroutine_threadsafe(
                            self.trigger_workflow(workflow_id, {
                                'event_type': 'scheduled',
                                'cron_expression': schedule_info['cron_expression'],
                                'scheduled_time': next_run,
                                'actual_time': current_time
                            }),
                            asyncio.get_event_loop()
                        )
                        
                        # Calculate next run time
                        cron = croniter(schedule_info['cron_expression'], current_time)
                        schedule_info['next_run'] = cron.get_next(datetime)
                        schedule_info['last_run'] = current_time
                
                # Check every minute
                time.sleep(60)
                
            except Exception as e:
                self.logger.error(f"Error in scheduler loop: {e}")
                time.sleep(60)

class WebhookTriggerHandler(BaseTriggerHandler):
    """Handler for webhook-based triggers"""
    
    def __init__(self, port: int = 8080):
        super().__init__()
        self.port = port
        self.server = None
        self.webhook_endpoints: Dict[str, str] = {}  # endpoint -> workflow_id
    
    def register_trigger(self, workflow_id: str, trigger: WorkflowTrigger) -> bool:
        """Register webhook trigger"""
        if trigger.trigger_type != TriggerType.WEBHOOK:
            return False
        
        parameters = trigger.parameters
        endpoint = parameters.get('endpoint', f'/webhook/{workflow_id}')
        
        self.webhook_endpoints[endpoint] = workflow_id
        self.active_workflows[workflow_id] = trigger
        
        # Start server if this is the first trigger
        if not self.server:
            self.start()
        
        self.logger.info(f"Registered webhook trigger for workflow {workflow_id} at {endpoint}")
        return True
    
    def unregister_trigger(self, workflow_id: str) -> bool:
        """Unregister webhook trigger"""
        if workflow_id in self.active_workflows:
            # Remove endpoint mapping
            endpoint_to_remove = None
            for endpoint, wf_id in self.webhook_endpoints.items():
                if wf_id == workflow_id:
                    endpoint_to_remove = endpoint
                    break
            
            if endpoint_to_remove:
                del self.webhook_endpoints[endpoint_to_remove]
            
            del self.active_workflows[workflow_id]
            
            # Stop server if no more triggers
            if not self.active_workflows and self.server:
                self.stop()
            
            return True
        return False
    
    def start(self):
        """Start webhook server"""
        if not self.server:
            from aiohttp import web
            import aiohttp
            
            async def handle_webhook(request):
                """Handle incoming webhook requests"""
                endpoint = request.path
                
                if endpoint in self.webhook_endpoints:
                    workflow_id = self.webhook_endpoints[endpoint]
                    
                    # Extract webhook data
                    webhook_data = {
                        'event_type': 'webhook',
                        'endpoint': endpoint,
                        'method': request.method,
                        'headers': dict(request.headers),
                        'query_params': dict(request.query),
                        'remote_addr': request.remote,
                        'timestamp': datetime.now()
                    }
                    
                    # Get request body
                    try:
                        if request.content_type == 'application/json':
                            webhook_data['json'] = await request.json()
                        else:
                            webhook_data['text'] = await request.text()
                    except:
                        pass
                    
                    # Trigger workflow
                    await self.trigger_workflow(workflow_id, webhook_data)
                    
                    return web.json_response({'status': 'triggered', 'workflow_id': workflow_id})
                else:
                    return web.json_response({'error': 'Endpoint not found'}, status=404)
            
            app = web.Application()
            
            # Add routes for all registered endpoints
            for endpoint in self.webhook_endpoints:
                app.router.add_post(endpoint, handle_webhook)
                app.router.add_get(endpoint, handle_webhook)
                app.router.add_put(endpoint, handle_webhook)
            
            # Catch-all route
            app.router.add_route('*', '/{path:.*}', handle_webhook)
            
            # Start server in background
            def run_server():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                web.run_app(app, host='0.0.0.0', port=self.port, print=None)
            
            self.server = threading.Thread(target=run_server, daemon=True)
            self.server.start()
            self.logger.info(f"Started webhook server on port {self.port}")
    
    def stop(self):
        """Stop webhook server"""
        if self.server:
            # Note: aiohttp server is harder to stop cleanly in this setup
            # In production, we'd use proper async context management
            self.server = None
            self.logger.info("Stopped webhook server")

class TriggerManager:
    """Central manager for all trigger types"""
    
    def __init__(self):
        self.handlers: Dict[TriggerType, BaseTriggerHandler] = {}
        self.logger = logging.getLogger(__name__)
        self._initialize_handlers()
    
    def _initialize_handlers(self):
        """Initialize trigger handlers"""
        self.handlers[TriggerType.GIT_PUSH] = GitTriggerHandler()
        self.handlers[TriggerType.GIT_PR] = self.handlers[TriggerType.GIT_PUSH]  # Same handler
        self.handlers[TriggerType.FILE_CHANGE] = FileWatchTriggerHandler()
        self.handlers[TriggerType.SCHEDULED] = ScheduledTriggerHandler()
        self.handlers[TriggerType.WEBHOOK] = WebhookTriggerHandler()
    
    def register_workflow_triggers(self, workflow_id: str, triggers: List[WorkflowTrigger]) -> Dict[TriggerType, bool]:
        """Register all triggers for a workflow"""
        results = {}
        
        for trigger in triggers:
            if trigger.enabled and trigger.trigger_type in self.handlers:
                handler = self.handlers[trigger.trigger_type]
                success = handler.register_trigger(workflow_id, trigger)
                results[trigger.trigger_type] = success
                
                if success:
                    self.logger.info(f"Registered {trigger.trigger_type.value} trigger for workflow {workflow_id}")
                else:
                    self.logger.error(f"Failed to register {trigger.trigger_type.value} trigger for workflow {workflow_id}")
            else:
                results[trigger.trigger_type] = False
        
        return results
    
    def unregister_workflow_triggers(self, workflow_id: str) -> bool:
        """Unregister all triggers for a workflow"""
        success = True
        
        for handler in self.handlers.values():
            try:
                handler.unregister_trigger(workflow_id)
            except Exception as e:
                self.logger.error(f"Error unregistering trigger for workflow {workflow_id}: {e}")
                success = False
        
        return success
    
    def get_trigger_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all trigger handlers"""
        status = {}
        
        for trigger_type, handler in self.handlers.items():
            status[trigger_type.value] = {
                'active_workflows': len(handler.active_workflows),
                'running': hasattr(handler, 'monitoring') and handler.monitoring or 
                          hasattr(handler, 'watching') and handler.watching or
                          hasattr(handler, 'running') and handler.running or
                          handler.server is not None if hasattr(handler, 'server') else False
            }
        
        return status
    
    def shutdown(self):
        """Shutdown all trigger handlers"""
        for handler in self.handlers.values():
            try:
                handler.stop()
            except Exception as e:
                self.logger.error(f"Error stopping trigger handler: {e}")

# Global trigger manager instance
trigger_manager = TriggerManager()

# Export main classes
__all__ = [
    'TriggerManager', 'BaseTriggerHandler', 'GitTriggerHandler', 
    'FileWatchTriggerHandler', 'ScheduledTriggerHandler', 'WebhookTriggerHandler',
    'TriggerEvent', 'trigger_manager'
]