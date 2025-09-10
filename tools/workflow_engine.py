"""
Aeonforge Phase 7 - Advanced Workflow Automation Engine
Core workflow execution engine with state management and action orchestration
"""

import os
import json
import uuid
import asyncio
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, asdict, field
import sqlite3
from pathlib import Path
import threading
from concurrent.futures import ThreadPoolExecutor
import time

# Workflow execution states
class WorkflowStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"

class ActionStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class TriggerType(Enum):
    MANUAL = "manual"
    GIT_PUSH = "git_push"
    GIT_PR = "git_pr"
    FILE_CHANGE = "file_change"
    SCHEDULED = "scheduled"
    WEBHOOK = "webhook"
    API = "api"

@dataclass
class WorkflowAction:
    """Individual action within a workflow"""
    id: str
    name: str
    action_type: str  # 'code_gen', 'deploy', 'test', 'notify', etc.
    parameters: Dict[str, Any] = field(default_factory=dict)
    depends_on: List[str] = field(default_factory=list)  # Action IDs this depends on
    status: ActionStatus = ActionStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3

@dataclass
class WorkflowTrigger:
    """Trigger configuration for workflows"""
    trigger_type: TriggerType
    parameters: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True

@dataclass
class Workflow:
    """Complete workflow definition"""
    id: str
    name: str
    description: str
    actions: List[WorkflowAction] = field(default_factory=list)
    triggers: List[WorkflowTrigger] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: str = "system"
    enabled: bool = True

@dataclass
class WorkflowExecution:
    """Runtime execution instance of a workflow"""
    id: str
    workflow_id: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    trigger_data: Optional[Dict[str, Any]] = None
    context: Dict[str, Any] = field(default_factory=dict)
    action_results: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    logs: List[str] = field(default_factory=list)

class WorkflowStateStore:
    """Persistent storage for workflows and executions"""
    
    def __init__(self, db_path: str = "workflows.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Workflows table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS workflows (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            definition TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            created_by TEXT,
            enabled BOOLEAN DEFAULT 1
        )
        ''')
        
        # Workflow executions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS workflow_executions (
            id TEXT PRIMARY KEY,
            workflow_id TEXT NOT NULL,
            status TEXT NOT NULL,
            trigger_data TEXT,
            context TEXT,
            action_results TEXT,
            started_at TEXT,
            completed_at TEXT,
            error_message TEXT,
            logs TEXT,
            FOREIGN KEY (workflow_id) REFERENCES workflows (id)
        )
        ''')
        
        # Scheduled workflows table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS scheduled_workflows (
            id TEXT PRIMARY KEY,
            workflow_id TEXT NOT NULL,
            schedule_expression TEXT NOT NULL,
            next_run TEXT NOT NULL,
            enabled BOOLEAN DEFAULT 1,
            FOREIGN KEY (workflow_id) REFERENCES workflows (id)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_workflow(self, workflow: Workflow) -> bool:
        """Save workflow to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            workflow_json = json.dumps(asdict(workflow), default=str)
            
            cursor.execute('''
            INSERT OR REPLACE INTO workflows 
            (id, name, description, definition, created_at, updated_at, created_by, enabled)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                workflow.id, workflow.name, workflow.description, workflow_json,
                workflow.created_at.isoformat(), workflow.updated_at.isoformat(),
                workflow.created_by, workflow.enabled
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save workflow {workflow.id}: {e}")
            return False
    
    def load_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Load workflow from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT definition FROM workflows WHERE id = ?', (workflow_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                workflow_data = json.loads(result[0])
                # Convert datetime strings back to datetime objects
                workflow_data['created_at'] = datetime.fromisoformat(workflow_data['created_at'])
                workflow_data['updated_at'] = datetime.fromisoformat(workflow_data['updated_at'])
                
                # Convert action dataclasses
                actions = []
                for action_data in workflow_data.get('actions', []):
                    action_data['status'] = ActionStatus(action_data['status'])
                    if action_data.get('started_at'):
                        action_data['started_at'] = datetime.fromisoformat(action_data['started_at'])
                    if action_data.get('completed_at'):
                        action_data['completed_at'] = datetime.fromisoformat(action_data['completed_at'])
                    actions.append(WorkflowAction(**action_data))
                
                # Convert trigger dataclasses
                triggers = []
                for trigger_data in workflow_data.get('triggers', []):
                    trigger_data['trigger_type'] = TriggerType(trigger_data['trigger_type'])
                    triggers.append(WorkflowTrigger(**trigger_data))
                
                workflow_data['actions'] = actions
                workflow_data['triggers'] = triggers
                
                return Workflow(**workflow_data)
                
        except Exception as e:
            self.logger.error(f"Failed to load workflow {workflow_id}: {e}")
            
        return None
    
    def save_execution(self, execution: WorkflowExecution) -> bool:
        """Save workflow execution to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT OR REPLACE INTO workflow_executions
            (id, workflow_id, status, trigger_data, context, action_results, 
             started_at, completed_at, error_message, logs)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                execution.id, execution.workflow_id, execution.status.value,
                json.dumps(execution.trigger_data) if execution.trigger_data else None,
                json.dumps(execution.context), json.dumps(execution.action_results),
                execution.started_at.isoformat() if execution.started_at else None,
                execution.completed_at.isoformat() if execution.completed_at else None,
                execution.error_message, json.dumps(execution.logs)
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save execution {execution.id}: {e}")
            return False
    
    def get_workflow_executions(self, workflow_id: str, limit: int = 50) -> List[WorkflowExecution]:
        """Get recent executions for a workflow"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT id, workflow_id, status, trigger_data, context, action_results,
                   started_at, completed_at, error_message, logs
            FROM workflow_executions 
            WHERE workflow_id = ?
            ORDER BY started_at DESC
            LIMIT ?
            ''', (workflow_id, limit))
            
            executions = []
            for row in cursor.fetchall():
                execution = WorkflowExecution(
                    id=row[0],
                    workflow_id=row[1],
                    status=WorkflowStatus(row[2]),
                    trigger_data=json.loads(row[3]) if row[3] else None,
                    context=json.loads(row[4]),
                    action_results=json.loads(row[5]),
                    started_at=datetime.fromisoformat(row[6]) if row[6] else None,
                    completed_at=datetime.fromisoformat(row[7]) if row[7] else None,
                    error_message=row[8],
                    logs=json.loads(row[9])
                )
                executions.append(execution)
            
            conn.close()
            return executions
            
        except Exception as e:
            self.logger.error(f"Failed to get executions for workflow {workflow_id}: {e}")
            return []

class WorkflowActionExecutor:
    """Executor for individual workflow actions"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.action_handlers: Dict[str, Callable] = {}
        self._register_built_in_actions()
    
    def _register_built_in_actions(self):
        """Register built-in action handlers"""
        self.action_handlers.update({
            'log': self._handle_log,
            'delay': self._handle_delay,
            'set_variable': self._handle_set_variable,
            'http_request': self._handle_http_request,
            'run_command': self._handle_run_command,
            'code_analysis': self._handle_code_analysis,
            'file_operation': self._handle_file_operation
        })
    
    def register_action(self, action_type: str, handler: Callable):
        """Register custom action handler"""
        self.action_handlers[action_type] = handler
    
    async def execute_action(self, action: WorkflowAction, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single action"""
        if action.action_type not in self.action_handlers:
            raise ValueError(f"Unknown action type: {action.action_type}")
        
        handler = self.action_handlers[action.action_type]
        action.started_at = datetime.now()
        action.status = ActionStatus.RUNNING
        
        try:
            # Execute the action handler
            result = await handler(action.parameters, context)
            
            action.status = ActionStatus.COMPLETED
            action.completed_at = datetime.now()
            action.result = result
            
            return result
            
        except Exception as e:
            action.status = ActionStatus.FAILED
            action.completed_at = datetime.now()
            action.error_message = str(e)
            
            # Retry logic
            if action.retry_count < action.max_retries:
                action.retry_count += 1
                action.status = ActionStatus.PENDING
                self.logger.warning(f"Action {action.id} failed, retrying ({action.retry_count}/{action.max_retries})")
                await asyncio.sleep(2 ** action.retry_count)  # Exponential backoff
                return await self.execute_action(action, context)
            
            raise e
    
    # Built-in action handlers
    async def _handle_log(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Log message action"""
        message = parameters.get('message', 'No message')
        level = parameters.get('level', 'info').upper()
        
        getattr(self.logger, level.lower())(f"Workflow: {message}")
        
        return {'logged': message, 'level': level}
    
    async def _handle_delay(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Delay execution"""
        seconds = parameters.get('seconds', 1)
        await asyncio.sleep(seconds)
        return {'delayed': seconds}
    
    async def _handle_set_variable(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Set context variable"""
        name = parameters.get('name')
        value = parameters.get('value')
        
        if name:
            context[name] = value
        
        return {'variable': name, 'value': value}
    
    async def _handle_http_request(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Make HTTP request"""
        import aiohttp
        
        url = parameters.get('url')
        method = parameters.get('method', 'GET').upper()
        headers = parameters.get('headers', {})
        data = parameters.get('data')
        
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, headers=headers, json=data) as response:
                result = {
                    'status_code': response.status,
                    'headers': dict(response.headers),
                    'text': await response.text()
                }
                
                if response.content_type == 'application/json':
                    try:
                        result['json'] = await response.json()
                    except:
                        pass
                
                return result
    
    async def _handle_run_command(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Run shell command"""
        command = parameters.get('command')
        cwd = parameters.get('cwd', os.getcwd())
        
        proc = await asyncio.create_subprocess_shell(
            command,
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await proc.communicate()
        
        return {
            'exit_code': proc.returncode,
            'stdout': stdout.decode(),
            'stderr': stderr.decode(),
            'command': command
        }
    
    async def _handle_code_analysis(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code using Phase 5 tools"""
        try:
            # Import Phase 5 multi-language tools
            import sys
            sys.path.append('tools')
            from multi_language_tools import multi_language_manager
            
            code = parameters.get('code', '')
            language = parameters.get('language', 'python')
            file_path = parameters.get('file_path')
            
            analysis = multi_language_manager.analyze_code(code, language, file_path)
            
            return {
                'analysis': {
                    'functions': analysis.functions,
                    'classes': analysis.classes,
                    'complexity_score': analysis.complexity_score,
                    'issues': analysis.issues,
                    'suggestions': analysis.suggestions
                }
            }
            
        except Exception as e:
            return {'error': f'Code analysis failed: {str(e)}'}
    
    async def _handle_file_operation(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle file operations"""
        operation = parameters.get('operation')  # 'read', 'write', 'delete', 'copy'
        file_path = parameters.get('file_path')
        
        if operation == 'read':
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return {'content': content, 'size': len(content)}
            except Exception as e:
                return {'error': str(e)}
                
        elif operation == 'write':
            content = parameters.get('content', '')
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return {'written': len(content), 'file_path': file_path}
            except Exception as e:
                return {'error': str(e)}
                
        elif operation == 'delete':
            try:
                os.remove(file_path)
                return {'deleted': file_path}
            except Exception as e:
                return {'error': str(e)}
        
        return {'error': f'Unknown file operation: {operation}'}

class WorkflowEngine:
    """Core workflow execution engine"""
    
    def __init__(self, state_store: WorkflowStateStore = None):
        self.state_store = state_store or WorkflowStateStore()
        self.action_executor = WorkflowActionExecutor()
        self.logger = logging.getLogger(__name__)
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.running_executions: Dict[str, WorkflowExecution] = {}
    
    def create_workflow(self, name: str, description: str = "") -> Workflow:
        """Create a new workflow"""
        workflow = Workflow(
            id=str(uuid.uuid4()),
            name=name,
            description=description
        )
        self.state_store.save_workflow(workflow)
        return workflow
    
    def add_action(self, workflow_id: str, action: WorkflowAction) -> bool:
        """Add action to workflow"""
        workflow = self.state_store.load_workflow(workflow_id)
        if not workflow:
            return False
        
        workflow.actions.append(action)
        workflow.updated_at = datetime.now()
        return self.state_store.save_workflow(workflow)
    
    def add_trigger(self, workflow_id: str, trigger: WorkflowTrigger) -> bool:
        """Add trigger to workflow"""
        workflow = self.state_store.load_workflow(workflow_id)
        if not workflow:
            return False
        
        workflow.triggers.append(trigger)
        workflow.updated_at = datetime.now()
        return self.state_store.save_workflow(workflow)
    
    async def execute_workflow(self, workflow_id: str, trigger_data: Dict[str, Any] = None) -> WorkflowExecution:
        """Execute a workflow"""
        workflow = self.state_store.load_workflow(workflow_id)
        if not workflow or not workflow.enabled:
            raise ValueError(f"Workflow {workflow_id} not found or disabled")
        
        execution = WorkflowExecution(
            id=str(uuid.uuid4()),
            workflow_id=workflow_id,
            trigger_data=trigger_data,
            context=workflow.variables.copy()
        )
        
        execution.started_at = datetime.now()
        execution.status = WorkflowStatus.RUNNING
        execution.logs.append(f"Started workflow execution {execution.id}")
        
        self.running_executions[execution.id] = execution
        
        try:
            # Build dependency graph
            dependency_graph = self._build_dependency_graph(workflow.actions)
            
            # Execute actions in dependency order
            completed_actions = set()
            
            while len(completed_actions) < len(workflow.actions):
                # Find actions ready to execute (dependencies met)
                ready_actions = []
                for action in workflow.actions:
                    if (action.id not in completed_actions and 
                        all(dep in completed_actions for dep in action.depends_on)):
                        ready_actions.append(action)
                
                if not ready_actions:
                    raise RuntimeError("Circular dependency detected in workflow")
                
                # Execute ready actions in parallel
                tasks = []
                for action in ready_actions:
                    task = asyncio.create_task(
                        self._execute_workflow_action(action, execution)
                    )
                    tasks.append((action, task))
                
                # Wait for all tasks to complete
                for action, task in tasks:
                    try:
                        result = await task
                        execution.action_results[action.id] = result
                        completed_actions.add(action.id)
                        execution.logs.append(f"Completed action {action.name}")
                    except Exception as e:
                        execution.status = WorkflowStatus.FAILED
                        execution.error_message = f"Action {action.name} failed: {str(e)}"
                        execution.logs.append(f"Failed action {action.name}: {str(e)}")
                        raise
            
            execution.status = WorkflowStatus.COMPLETED
            execution.logs.append("Workflow completed successfully")
            
        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.error_message = str(e)
            execution.logs.append(f"Workflow failed: {str(e)}")
            
        finally:
            execution.completed_at = datetime.now()
            self.state_store.save_execution(execution)
            if execution.id in self.running_executions:
                del self.running_executions[execution.id]
        
        return execution
    
    async def _execute_workflow_action(self, action: WorkflowAction, execution: WorkflowExecution) -> Dict[str, Any]:
        """Execute a single action within workflow context"""
        try:
            result = await self.action_executor.execute_action(action, execution.context)
            return result
        except Exception as e:
            self.logger.error(f"Action {action.id} failed: {e}")
            raise
    
    def _build_dependency_graph(self, actions: List[WorkflowAction]) -> Dict[str, List[str]]:
        """Build action dependency graph"""
        graph = {}
        for action in actions:
            graph[action.id] = action.depends_on.copy()
        return graph
    
    def get_execution_status(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get current execution status"""
        if execution_id in self.running_executions:
            return self.running_executions[execution_id]
        
        # Try to load from database
        try:
            conn = sqlite3.connect(self.state_store.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT id, workflow_id, status, trigger_data, context, action_results,
                   started_at, completed_at, error_message, logs
            FROM workflow_executions WHERE id = ?
            ''', (execution_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return WorkflowExecution(
                    id=row[0],
                    workflow_id=row[1],
                    status=WorkflowStatus(row[2]),
                    trigger_data=json.loads(row[3]) if row[3] else None,
                    context=json.loads(row[4]),
                    action_results=json.loads(row[5]),
                    started_at=datetime.fromisoformat(row[6]) if row[6] else None,
                    completed_at=datetime.fromisoformat(row[7]) if row[7] else None,
                    error_message=row[8],
                    logs=json.loads(row[9])
                )
        except Exception as e:
            self.logger.error(f"Failed to get execution status: {e}")
        
        return None
    
    def cancel_execution(self, execution_id: str) -> bool:
        """Cancel running execution"""
        if execution_id in self.running_executions:
            execution = self.running_executions[execution_id]
            execution.status = WorkflowStatus.CANCELLED
            execution.completed_at = datetime.now()
            execution.logs.append("Execution cancelled by user")
            self.state_store.save_execution(execution)
            del self.running_executions[execution_id]
            return True
        return False

# Global workflow engine instance
workflow_engine = WorkflowEngine()

# Export main classes for use in other modules
__all__ = [
    'WorkflowEngine', 'Workflow', 'WorkflowAction', 'WorkflowTrigger', 
    'WorkflowExecution', 'WorkflowStateStore', 'WorkflowActionExecutor',
    'WorkflowStatus', 'ActionStatus', 'TriggerType', 'workflow_engine'
]