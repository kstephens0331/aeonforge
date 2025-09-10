"""
Phase 7: Advanced Workflow Automation - Scheduler and Monitor
Provides comprehensive workflow scheduling, monitoring, and performance analytics
"""

import asyncio
import json
import sqlite3
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from pathlib import Path
from collections import defaultdict, deque
import logging
import threading
from queue import Queue, Empty

try:
    import psutil
    import matplotlib.pyplot as plt
    import numpy as np
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False

from .workflow_engine import WorkflowEngine, WorkflowExecution
from .workflow_triggers import TriggerManager

@dataclass
class ScheduledWorkflow:
    """Represents a scheduled workflow"""
    id: str
    workflow_id: str
    schedule_type: str  # 'cron', 'interval', 'once', 'manual'
    schedule_config: Dict[str, Any]
    enabled: bool
    next_run: Optional[datetime]
    last_run: Optional[datetime]
    run_count: int
    failure_count: int
    max_retries: int
    retry_delay: int  # seconds
    timeout: int  # seconds
    priority: int  # 1-10, higher is more important
    tags: List[str]
    metadata: Dict[str, Any]

@dataclass
class WorkflowMetrics:
    """Workflow execution metrics"""
    workflow_id: str
    execution_id: str
    start_time: datetime
    end_time: Optional[datetime]
    duration: Optional[float]  # seconds
    status: str
    error_message: Optional[str]
    resource_usage: Dict[str, Any]
    step_metrics: List[Dict[str, Any]]
    trigger_data: Dict[str, Any]

@dataclass
class SystemMetrics:
    """System-wide metrics"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    active_workflows: int
    queued_workflows: int
    failed_workflows: int
    total_executions: int
    avg_execution_time: float

class WorkflowScheduler:
    """Advanced workflow scheduler with priority queues and resource management"""
    
    def __init__(self, data_dir: str = "workflow_data", max_concurrent: int = 10):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.db_path = self.data_dir / "scheduler.db"
        self.max_concurrent = max_concurrent
        
        # Core components
        self.engine = WorkflowEngine(data_dir)
        self.trigger_manager = TriggerManager()
        
        # Scheduling state
        self.scheduled_workflows: Dict[str, ScheduledWorkflow] = {}
        self.execution_queue = Queue()
        self.priority_queues = {i: deque() for i in range(1, 11)}  # Priority 1-10
        self.running_executions: Dict[str, WorkflowExecution] = {}
        self.execution_history: deque = deque(maxlen=10000)
        
        # Threading
        self.scheduler_thread: Optional[threading.Thread] = None
        self.executor_threads: List[threading.Thread] = []
        self.running = False
        self.lock = threading.Lock()
        
        # Monitoring
        self.metrics_collector = WorkflowMetricsCollector(self)
        self.performance_monitor = PerformanceMonitor(self)
        
        # Initialize database
        self._init_database()
        
        # Load existing schedules
        self._load_schedules()
    
    def _init_database(self):
        """Initialize scheduler database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Scheduled workflows table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scheduled_workflows (
                id TEXT PRIMARY KEY,
                workflow_id TEXT NOT NULL,
                schedule_type TEXT NOT NULL,
                schedule_config TEXT NOT NULL,
                enabled BOOLEAN NOT NULL,
                next_run TIMESTAMP,
                last_run TIMESTAMP,
                run_count INTEGER DEFAULT 0,
                failure_count INTEGER DEFAULT 0,
                max_retries INTEGER DEFAULT 3,
                retry_delay INTEGER DEFAULT 60,
                timeout INTEGER DEFAULT 3600,
                priority INTEGER DEFAULT 5,
                tags TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Execution metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workflow_metrics (
                id TEXT PRIMARY KEY,
                workflow_id TEXT NOT NULL,
                execution_id TEXT NOT NULL,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP,
                duration REAL,
                status TEXT NOT NULL,
                error_message TEXT,
                resource_usage TEXT,
                step_metrics TEXT,
                trigger_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # System metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP NOT NULL,
                cpu_usage REAL,
                memory_usage REAL,
                disk_usage REAL,
                active_workflows INTEGER,
                queued_workflows INTEGER,
                failed_workflows INTEGER,
                total_executions INTEGER,
                avg_execution_time REAL
            )
        """)
        
        # Performance indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_scheduled_next_run ON scheduled_workflows(next_run)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_workflow ON workflow_metrics(workflow_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_time ON workflow_metrics(start_time)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_system_time ON system_metrics(timestamp)")
        
        conn.commit()
        conn.close()
    
    def _load_schedules(self):
        """Load scheduled workflows from database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM scheduled_workflows WHERE enabled = 1")
        rows = cursor.fetchall()
        
        columns = [desc[0] for desc in cursor.description]
        
        for row in rows:
            data = dict(zip(columns, row))
            
            scheduled_workflow = ScheduledWorkflow(
                id=data['id'],
                workflow_id=data['workflow_id'],
                schedule_type=data['schedule_type'],
                schedule_config=json.loads(data['schedule_config']),
                enabled=bool(data['enabled']),
                next_run=datetime.fromisoformat(data['next_run']) if data['next_run'] else None,
                last_run=datetime.fromisoformat(data['last_run']) if data['last_run'] else None,
                run_count=data['run_count'],
                failure_count=data['failure_count'],
                max_retries=data['max_retries'],
                retry_delay=data['retry_delay'],
                timeout=data['timeout'],
                priority=data['priority'],
                tags=json.loads(data['tags']) if data['tags'] else [],
                metadata=json.loads(data['metadata']) if data['metadata'] else {}
            )
            
            self.scheduled_workflows[scheduled_workflow.id] = scheduled_workflow
        
        conn.close()
    
    def start(self):
        """Start the scheduler"""
        if self.running:
            return
        
        self.running = True
        
        # Start scheduler thread
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        
        # Start executor threads
        for i in range(self.max_concurrent):
            thread = threading.Thread(target=self._executor_loop, daemon=True)
            thread.start()
            self.executor_threads.append(thread)
        
        # Start metrics collection
        self.metrics_collector.start()
        self.performance_monitor.start()
        
        print(f"Workflow scheduler started with {self.max_concurrent} executor threads")
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        
        # Stop metrics collection
        self.metrics_collector.stop()
        self.performance_monitor.stop()
        
        # Wait for threads to complete
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        for thread in self.executor_threads:
            thread.join(timeout=5)
        
        print("Workflow scheduler stopped")
    
    def _scheduler_loop(self):
        """Main scheduler loop"""
        while self.running:
            try:
                current_time = datetime.now()
                
                with self.lock:
                    # Check for workflows ready to run
                    for schedule_id, scheduled_workflow in self.scheduled_workflows.items():
                        if not scheduled_workflow.enabled:
                            continue
                        
                        if (scheduled_workflow.next_run and 
                            scheduled_workflow.next_run <= current_time):
                            
                            # Queue workflow for execution
                            self._queue_workflow(scheduled_workflow)
                            
                            # Update next run time
                            self._calculate_next_run(scheduled_workflow)
                
                # Process priority queues
                self._process_priority_queues()
                
                time.sleep(1)  # Check every second
                
            except Exception as e:
                logging.error(f"Scheduler loop error: {e}")
                time.sleep(5)
    
    def _executor_loop(self):
        """Workflow executor loop"""
        while self.running:
            try:
                # Get workflow from execution queue
                try:
                    workflow_data = self.execution_queue.get(timeout=1)
                except Empty:
                    continue
                
                # Execute workflow
                self._execute_workflow(workflow_data)
                
            except Exception as e:
                logging.error(f"Executor loop error: {e}")
    
    def _queue_workflow(self, scheduled_workflow: ScheduledWorkflow):
        """Queue workflow for execution"""
        workflow_data = {
            'schedule_id': scheduled_workflow.id,
            'workflow_id': scheduled_workflow.workflow_id,
            'priority': scheduled_workflow.priority,
            'timeout': scheduled_workflow.timeout,
            'retry_count': 0,
            'max_retries': scheduled_workflow.max_retries,
            'retry_delay': scheduled_workflow.retry_delay
        }
        
        # Add to priority queue
        self.priority_queues[scheduled_workflow.priority].append(workflow_data)
        
        # Update schedule statistics
        scheduled_workflow.run_count += 1
        self._save_schedule(scheduled_workflow)
    
    def _process_priority_queues(self):
        """Process workflows from priority queues"""
        # Process from highest priority to lowest
        for priority in range(10, 0, -1):
            if self.priority_queues[priority] and not self.execution_queue.full():
                workflow_data = self.priority_queues[priority].popleft()
                self.execution_queue.put(workflow_data)
    
    def _execute_workflow(self, workflow_data: Dict[str, Any]):
        """Execute a workflow"""
        start_time = datetime.now()
        execution_id = None
        
        try:
            # Start metrics collection
            metrics = WorkflowMetrics(
                workflow_id=workflow_data['workflow_id'],
                execution_id="",
                start_time=start_time,
                end_time=None,
                duration=None,
                status="running",
                error_message=None,
                resource_usage={},
                step_metrics=[],
                trigger_data={}
            )
            
            # Execute workflow using engine
            execution = asyncio.run(
                self.engine.execute_workflow(
                    workflow_data['workflow_id'],
                    timeout=workflow_data['timeout']
                )
            )
            
            execution_id = execution.id
            metrics.execution_id = execution_id
            
            # Track execution
            with self.lock:
                self.running_executions[execution_id] = execution
            
            # Wait for completion or timeout
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Update metrics
            metrics.end_time = end_time
            metrics.duration = duration
            metrics.status = execution.status
            metrics.error_message = execution.error
            
            # Collect resource usage
            if MONITORING_AVAILABLE:
                metrics.resource_usage = {
                    'cpu_percent': psutil.cpu_percent(),
                    'memory_mb': psutil.virtual_memory().used / (1024 * 1024),
                    'peak_memory_mb': execution.metadata.get('peak_memory', 0)
                }
            
            # Store metrics
            self._store_metrics(metrics)
            
            # Handle success/failure
            if execution.status == "completed":
                self._handle_workflow_success(workflow_data, execution)
            else:
                self._handle_workflow_failure(workflow_data, execution)
        
        except Exception as e:
            # Handle execution error
            error_msg = str(e)
            logging.error(f"Workflow execution error: {error_msg}")
            
            if execution_id:
                metrics.status = "failed"
                metrics.error_message = error_msg
                metrics.end_time = datetime.now()
                metrics.duration = (metrics.end_time - start_time).total_seconds()
                self._store_metrics(metrics)
            
            self._handle_workflow_failure(workflow_data, None, error_msg)
        
        finally:
            # Cleanup
            if execution_id:
                with self.lock:
                    self.running_executions.pop(execution_id, None)
    
    def _handle_workflow_success(self, workflow_data: Dict[str, Any], execution: WorkflowExecution):
        """Handle successful workflow execution"""
        schedule_id = workflow_data['schedule_id']
        scheduled_workflow = self.scheduled_workflows.get(schedule_id)
        
        if scheduled_workflow:
            scheduled_workflow.last_run = datetime.now()
            scheduled_workflow.failure_count = 0  # Reset failure count on success
            self._save_schedule(scheduled_workflow)
    
    def _handle_workflow_failure(self, workflow_data: Dict[str, Any], execution: Optional[WorkflowExecution], error_msg: str = ""):
        """Handle failed workflow execution"""
        schedule_id = workflow_data['schedule_id']
        scheduled_workflow = self.scheduled_workflows.get(schedule_id)
        
        if scheduled_workflow:
            scheduled_workflow.failure_count += 1
            
            # Check if retry is needed
            if workflow_data['retry_count'] < workflow_data['max_retries']:
                # Schedule retry
                retry_data = workflow_data.copy()
                retry_data['retry_count'] += 1
                
                # Add delay before retry
                retry_time = datetime.now() + timedelta(seconds=workflow_data['retry_delay'])
                
                # Schedule retry (simplified - would use proper delay mechanism)
                threading.Timer(
                    workflow_data['retry_delay'],
                    lambda: self.execution_queue.put(retry_data)
                ).start()
            
            self._save_schedule(scheduled_workflow)
    
    def _calculate_next_run(self, scheduled_workflow: ScheduledWorkflow):
        """Calculate next run time for scheduled workflow"""
        current_time = datetime.now()
        config = scheduled_workflow.schedule_config
        
        if scheduled_workflow.schedule_type == "interval":
            # Interval-based scheduling
            interval_seconds = config.get('interval_seconds', 3600)
            scheduled_workflow.next_run = current_time + timedelta(seconds=interval_seconds)
        
        elif scheduled_workflow.schedule_type == "cron":
            # Cron-based scheduling (simplified)
            # Would use croniter for full cron support
            hour = config.get('hour', 0)
            minute = config.get('minute', 0)
            
            next_run = current_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= current_time:
                next_run += timedelta(days=1)
            
            scheduled_workflow.next_run = next_run
        
        elif scheduled_workflow.schedule_type == "once":
            # One-time execution
            scheduled_workflow.enabled = False
            scheduled_workflow.next_run = None
        
        elif scheduled_workflow.schedule_type == "manual":
            # Manual execution only
            scheduled_workflow.next_run = None
        
        self._save_schedule(scheduled_workflow)
    
    def _save_schedule(self, scheduled_workflow: ScheduledWorkflow):
        """Save scheduled workflow to database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO scheduled_workflows 
            (id, workflow_id, schedule_type, schedule_config, enabled, next_run, 
             last_run, run_count, failure_count, max_retries, retry_delay, timeout, 
             priority, tags, metadata, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            scheduled_workflow.id,
            scheduled_workflow.workflow_id,
            scheduled_workflow.schedule_type,
            json.dumps(scheduled_workflow.schedule_config),
            scheduled_workflow.enabled,
            scheduled_workflow.next_run.isoformat() if scheduled_workflow.next_run else None,
            scheduled_workflow.last_run.isoformat() if scheduled_workflow.last_run else None,
            scheduled_workflow.run_count,
            scheduled_workflow.failure_count,
            scheduled_workflow.max_retries,
            scheduled_workflow.retry_delay,
            scheduled_workflow.timeout,
            scheduled_workflow.priority,
            json.dumps(scheduled_workflow.tags),
            json.dumps(scheduled_workflow.metadata),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def _store_metrics(self, metrics: WorkflowMetrics):
        """Store workflow metrics"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO workflow_metrics 
            (id, workflow_id, execution_id, start_time, end_time, duration, status,
             error_message, resource_usage, step_metrics, trigger_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            f"{metrics.workflow_id}_{metrics.execution_id}",
            metrics.workflow_id,
            metrics.execution_id,
            metrics.start_time.isoformat(),
            metrics.end_time.isoformat() if metrics.end_time else None,
            metrics.duration,
            metrics.status,
            metrics.error_message,
            json.dumps(metrics.resource_usage),
            json.dumps(metrics.step_metrics),
            json.dumps(metrics.trigger_data)
        ))
        
        conn.commit()
        conn.close()
    
    # Public API methods
    def schedule_workflow(self, workflow_id: str, schedule_type: str, schedule_config: Dict[str, Any], **kwargs) -> str:
        """Schedule a workflow for execution"""
        import uuid
        
        schedule_id = str(uuid.uuid4())
        
        scheduled_workflow = ScheduledWorkflow(
            id=schedule_id,
            workflow_id=workflow_id,
            schedule_type=schedule_type,
            schedule_config=schedule_config,
            enabled=kwargs.get('enabled', True),
            next_run=None,
            last_run=None,
            run_count=0,
            failure_count=0,
            max_retries=kwargs.get('max_retries', 3),
            retry_delay=kwargs.get('retry_delay', 60),
            timeout=kwargs.get('timeout', 3600),
            priority=kwargs.get('priority', 5),
            tags=kwargs.get('tags', []),
            metadata=kwargs.get('metadata', {})
        )
        
        # Calculate first run time
        self._calculate_next_run(scheduled_workflow)
        
        # Store schedule
        self.scheduled_workflows[schedule_id] = scheduled_workflow
        self._save_schedule(scheduled_workflow)
        
        return schedule_id
    
    def unschedule_workflow(self, schedule_id: str):
        """Remove workflow from schedule"""
        if schedule_id in self.scheduled_workflows:
            del self.scheduled_workflows[schedule_id]
            
            # Remove from database
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("DELETE FROM scheduled_workflows WHERE id = ?", (schedule_id,))
            conn.commit()
            conn.close()
    
    def trigger_workflow(self, workflow_id: str, priority: int = 5) -> str:
        """Manually trigger workflow execution"""
        import uuid
        
        execution_data = {
            'schedule_id': None,
            'workflow_id': workflow_id,
            'priority': priority,
            'timeout': 3600,
            'retry_count': 0,
            'max_retries': 0,
            'retry_delay': 0
        }
        
        self.execution_queue.put(execution_data)
        return str(uuid.uuid4())
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get current status of a workflow"""
        # Get scheduled info
        schedules = [s for s in self.scheduled_workflows.values() if s.workflow_id == workflow_id]
        
        # Get running executions
        running = [e for e in self.running_executions.values() if e.workflow_id == workflow_id]
        
        # Get recent metrics
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM workflow_metrics 
            WHERE workflow_id = ? 
            ORDER BY start_time DESC 
            LIMIT 10
        """, (workflow_id,))
        
        recent_executions = cursor.fetchall()
        conn.close()
        
        return {
            'workflow_id': workflow_id,
            'schedules': len(schedules),
            'running_executions': len(running),
            'recent_executions': len(recent_executions),
            'next_scheduled_run': min([s.next_run for s in schedules if s.next_run], default=None)
        }

class WorkflowMetricsCollector:
    """Collects and stores workflow execution metrics"""
    
    def __init__(self, scheduler: WorkflowScheduler):
        self.scheduler = scheduler
        self.running = False
        self.thread: Optional[threading.Thread] = None
    
    def start(self):
        """Start metrics collection"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._collection_loop, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop metrics collection"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
    
    def _collection_loop(self):
        """Main metrics collection loop"""
        while self.running:
            try:
                self._collect_system_metrics()
                time.sleep(60)  # Collect every minute
            except Exception as e:
                logging.error(f"Metrics collection error: {e}")
                time.sleep(60)
    
    def _collect_system_metrics(self):
        """Collect system-wide metrics"""
        if not MONITORING_AVAILABLE:
            return
        
        timestamp = datetime.now()
        
        # System resource usage
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Workflow statistics
        with self.scheduler.lock:
            active_workflows = len(self.scheduler.running_executions)
            queued_workflows = self.scheduler.execution_queue.qsize()
        
        # Calculate average execution time from recent executions
        conn = sqlite3.connect(str(self.scheduler.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT AVG(duration), COUNT(*) 
            FROM workflow_metrics 
            WHERE start_time > datetime('now', '-1 hour')
            AND status = 'completed'
        """)
        
        result = cursor.fetchone()
        avg_execution_time = result[0] or 0
        recent_executions = result[1] or 0
        
        cursor.execute("""
            SELECT COUNT(*) 
            FROM workflow_metrics 
            WHERE start_time > datetime('now', '-1 hour')
            AND status = 'failed'
        """)
        
        failed_workflows = cursor.fetchone()[0] or 0
        
        # Store system metrics
        system_metrics = SystemMetrics(
            timestamp=timestamp,
            cpu_usage=cpu_usage,
            memory_usage=memory.percent,
            disk_usage=disk.percent,
            active_workflows=active_workflows,
            queued_workflows=queued_workflows,
            failed_workflows=failed_workflows,
            total_executions=recent_executions + failed_workflows,
            avg_execution_time=avg_execution_time
        )
        
        cursor.execute("""
            INSERT INTO system_metrics 
            (timestamp, cpu_usage, memory_usage, disk_usage, active_workflows,
             queued_workflows, failed_workflows, total_executions, avg_execution_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            timestamp.isoformat(),
            system_metrics.cpu_usage,
            system_metrics.memory_usage,
            system_metrics.disk_usage,
            system_metrics.active_workflows,
            system_metrics.queued_workflows,
            system_metrics.failed_workflows,
            system_metrics.total_executions,
            system_metrics.avg_execution_time
        ))
        
        conn.commit()
        conn.close()

class PerformanceMonitor:
    """Monitors workflow performance and generates alerts"""
    
    def __init__(self, scheduler: WorkflowScheduler):
        self.scheduler = scheduler
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.alerts: deque = deque(maxlen=1000)
        
        # Thresholds
        self.cpu_threshold = 80.0
        self.memory_threshold = 90.0
        self.failure_rate_threshold = 0.5
        self.avg_time_increase_threshold = 2.0
    
    def start(self):
        """Start performance monitoring"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop performance monitoring"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                self._check_system_health()
                self._check_workflow_performance()
                time.sleep(300)  # Check every 5 minutes
            except Exception as e:
                logging.error(f"Performance monitoring error: {e}")
                time.sleep(300)
    
    def _check_system_health(self):
        """Check system resource health"""
        if not MONITORING_AVAILABLE:
            return
        
        # Check current resource usage
        cpu_usage = psutil.cpu_percent()
        memory_usage = psutil.virtual_memory().percent
        
        if cpu_usage > self.cpu_threshold:
            self._generate_alert(
                "high_cpu",
                f"High CPU usage detected: {cpu_usage:.1f}%",
                "warning"
            )
        
        if memory_usage > self.memory_threshold:
            self._generate_alert(
                "high_memory",
                f"High memory usage detected: {memory_usage:.1f}%",
                "critical"
            )
    
    def _check_workflow_performance(self):
        """Check workflow execution performance"""
        conn = sqlite3.connect(str(self.scheduler.db_path))
        cursor = conn.cursor()
        
        # Check failure rate in last hour
        cursor.execute("""
            SELECT 
                COUNT(CASE WHEN status = 'failed' THEN 1 END) as failures,
                COUNT(*) as total
            FROM workflow_metrics 
            WHERE start_time > datetime('now', '-1 hour')
        """)
        
        result = cursor.fetchone()
        failures = result[0] or 0
        total = result[1] or 0
        
        if total > 0:
            failure_rate = failures / total
            if failure_rate > self.failure_rate_threshold:
                self._generate_alert(
                    "high_failure_rate",
                    f"High workflow failure rate: {failure_rate:.1%} ({failures}/{total})",
                    "critical"
                )
        
        # Check average execution time increase
        cursor.execute("""
            SELECT AVG(duration) 
            FROM workflow_metrics 
            WHERE start_time > datetime('now', '-1 hour')
            AND status = 'completed'
        """)
        
        current_avg = cursor.fetchone()[0] or 0
        
        cursor.execute("""
            SELECT AVG(duration) 
            FROM workflow_metrics 
            WHERE start_time BETWEEN datetime('now', '-25 hour') AND datetime('now', '-1 hour')
            AND status = 'completed'
        """)
        
        previous_avg = cursor.fetchone()[0] or 0
        
        if previous_avg > 0 and current_avg / previous_avg > self.avg_time_increase_threshold:
            self._generate_alert(
                "performance_degradation",
                f"Workflow execution time increased by {((current_avg/previous_avg - 1) * 100):.1f}%",
                "warning"
            )
        
        conn.close()
    
    def _generate_alert(self, alert_type: str, message: str, severity: str):
        """Generate performance alert"""
        alert = {
            'type': alert_type,
            'message': message,
            'severity': severity,
            'timestamp': datetime.now().isoformat()
        }
        
        self.alerts.append(alert)
        logging.warning(f"Performance Alert [{severity.upper()}]: {message}")
        
        # Could integrate with notification systems here
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        if not MONITORING_AVAILABLE:
            return {"error": "Monitoring not available"}
        
        conn = sqlite3.connect(str(self.scheduler.db_path))
        cursor = conn.cursor()
        
        # Get recent system metrics
        cursor.execute("""
            SELECT * FROM system_metrics 
            WHERE timestamp > datetime('now', '-24 hour')
            ORDER BY timestamp DESC
        """)
        
        system_metrics = cursor.fetchall()
        
        # Get workflow statistics
        cursor.execute("""
            SELECT 
                workflow_id,
                COUNT(*) as executions,
                AVG(duration) as avg_duration,
                COUNT(CASE WHEN status = 'failed' THEN 1 END) as failures,
                MAX(start_time) as last_execution
            FROM workflow_metrics 
            WHERE start_time > datetime('now', '-24 hour')
            GROUP BY workflow_id
        """)
        
        workflow_stats = cursor.fetchall()
        
        conn.close()
        
        return {
            'system_metrics': system_metrics,
            'workflow_statistics': workflow_stats,
            'recent_alerts': list(self.alerts)[-10:],  # Last 10 alerts
            'summary': {
                'total_workflows_monitored': len(workflow_stats),
                'active_alerts': len([a for a in self.alerts if a['severity'] in ['warning', 'critical']]),
                'system_health': 'healthy' if len(self.alerts) == 0 else 'degraded'
            }
        }

def main():
    """Run the workflow scheduler"""
    scheduler = WorkflowScheduler()
    
    try:
        scheduler.start()
        
        print("Workflow Scheduler started. Press Ctrl+C to stop.")
        
        # Example: Schedule a workflow every hour
        # schedule_id = scheduler.schedule_workflow(
        #     workflow_id="example-workflow",
        #     schedule_type="interval",
        #     schedule_config={"interval_seconds": 3600},
        #     priority=5
        # )
        
        # Keep running
        while True:
            time.sleep(10)
            
            # Show status every 10 seconds
            with scheduler.lock:
                active = len(scheduler.running_executions)
                queued = scheduler.execution_queue.qsize()
                scheduled = len(scheduler.scheduled_workflows)
            
            print(f"Status: {active} active, {queued} queued, {scheduled} scheduled workflows")
    
    except KeyboardInterrupt:
        print("Shutting down scheduler...")
        scheduler.stop()

if __name__ == "__main__":
    main()