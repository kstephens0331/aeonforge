"""
AeonForge Advanced Tools System
Scalable architecture for 6000+ specialized tools across all domains
"""

import os
import sys
import asyncio
import json
import uuid
import importlib
import inspect
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable, Union, Type
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ToolCategory(Enum):
    """Tool categories for organization"""
    CODE_INTELLIGENCE = "code_intelligence"
    DATA_ANALYSIS = "data_analysis"
    WEB_DEVELOPMENT = "web_development"
    MOBILE_DEVELOPMENT = "mobile_development"
    DEVOPS_AUTOMATION = "devops_automation"
    SECURITY_ANALYSIS = "security_analysis"
    MACHINE_LEARNING = "machine_learning"
    BLOCKCHAIN = "blockchain"
    CLOUD_SERVICES = "cloud_services"
    DATABASE_OPERATIONS = "database_operations"
    API_INTEGRATIONS = "api_integrations"
    FILE_OPERATIONS = "file_operations"
    NETWORK_TOOLS = "network_tools"
    SYSTEM_ADMINISTRATION = "system_administration"
    CONTENT_CREATION = "content_creation"
    IMAGE_PROCESSING = "image_processing"
    AUDIO_PROCESSING = "audio_processing"
    VIDEO_PROCESSING = "video_processing"
    NATURAL_LANGUAGE = "natural_language"
    RESEARCH_TOOLS = "research_tools"

class ToolComplexity(Enum):
    """Tool complexity levels"""
    SIMPLE = "simple"        # Single function, minimal dependencies
    MODERATE = "moderate"    # Multiple functions, some dependencies
    COMPLEX = "complex"      # Class-based, many dependencies
    ENTERPRISE = "enterprise" # Full system integration

class ToolExecutionMode(Enum):
    """Tool execution modes"""
    SYNCHRONOUS = "sync"
    ASYNCHRONOUS = "async"
    BACKGROUND = "background"
    STREAMING = "streaming"

@dataclass
class ToolMetadata:
    """Comprehensive tool metadata"""
    name: str
    category: ToolCategory
    complexity: ToolComplexity
    execution_mode: ToolExecutionMode
    description: str
    version: str = "1.0.0"
    author: str = "AeonForge"
    dependencies: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    return_type: str = "Any"
    examples: List[Dict[str, Any]] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    use_cases: List[str] = field(default_factory=list)
    related_tools: List[str] = field(default_factory=list)
    performance_rating: float = 5.0  # 1-10 scale
    reliability_score: float = 5.0   # 1-10 scale
    last_updated: datetime = field(default_factory=datetime.utcnow)
    usage_count: int = 0
    success_rate: float = 1.0

class ToolResult:
    """Standardized tool execution result"""
    def __init__(self, success: bool = True, data: Any = None, 
                 error: str = None, metadata: Dict[str, Any] = None,
                 execution_time: float = 0.0):
        self.success = success
        self.data = data
        self.error = error
        self.metadata = metadata or {}
        self.execution_time = execution_time
        self.timestamp = datetime.utcnow()

class BaseTool(ABC):
    """Base class for all AeonForge tools"""
    
    def __init__(self, metadata: ToolMetadata):
        self.metadata = metadata
        self.id = str(uuid.uuid4())
        self._initialized = False
        
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the tool (load dependencies, setup, etc.)"""
        pass
    
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with given parameters"""
        pass
    
    @abstractmethod
    async def validate_input(self, **kwargs) -> bool:
        """Validate input parameters"""
        pass
    
    async def cleanup(self):
        """Cleanup resources after execution"""
        pass
    
    def get_help(self) -> Dict[str, Any]:
        """Get comprehensive help information"""
        return {
            "name": self.metadata.name,
            "description": self.metadata.description,
            "category": self.metadata.category.value,
            "complexity": self.metadata.complexity.value,
            "parameters": self.metadata.parameters,
            "examples": self.metadata.examples,
            "use_cases": self.metadata.use_cases,
            "dependencies": self.metadata.dependencies
        }

class ToolRegistry:
    """Central registry for all tools"""
    
    def __init__(self):
        self.tools: Dict[str, Type[BaseTool]] = {}
        self.categories: Dict[ToolCategory, List[str]] = {}
        self.tool_instances: Dict[str, BaseTool] = {}
        self.performance_stats: Dict[str, Dict[str, Any]] = {}
        
    def register_tool(self, tool_class: Type[BaseTool]):
        """Register a new tool"""
        metadata = tool_class.__dict__.get('METADATA')
        if not metadata:
            raise ValueError(f"Tool {tool_class.__name__} must have METADATA attribute")
        
        tool_name = metadata.name
        self.tools[tool_name] = tool_class
        
        # Organize by category
        category = metadata.category
        if category not in self.categories:
            self.categories[category] = []
        self.categories[category].append(tool_name)
        
        logger.info(f"Registered tool: {tool_name} ({category.value})")
    
    async def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """Get an initialized tool instance"""
        if tool_name not in self.tools:
            return None
        
        # Check if already instantiated
        if tool_name in self.tool_instances:
            return self.tool_instances[tool_name]
        
        # Create new instance
        tool_class = self.tools[tool_name]
        metadata = tool_class.METADATA
        tool_instance = tool_class(metadata)
        
        # Initialize
        if await tool_instance.initialize():
            self.tool_instances[tool_name] = tool_instance
            return tool_instance
        
        return None
    
    async def execute_tool(self, tool_name: str, **kwargs) -> ToolResult:
        """Execute a tool by name"""
        start_time = datetime.utcnow()
        
        try:
            tool = await self.get_tool(tool_name)
            if not tool:
                return ToolResult(
                    success=False,
                    error=f"Tool '{tool_name}' not found or failed to initialize"
                )
            
            # Validate input
            if not await tool.validate_input(**kwargs):
                return ToolResult(
                    success=False,
                    error="Invalid input parameters"
                )
            
            # Execute
            result = await tool.execute(**kwargs)
            
            # Update stats
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_performance_stats(tool_name, True, execution_time)
            
            return result
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_performance_stats(tool_name, False, execution_time)
            
            logger.error(f"Tool execution failed: {tool_name} - {str(e)}")
            return ToolResult(
                success=False,
                error=f"Execution failed: {str(e)}",
                execution_time=execution_time
            )
    
    def _update_performance_stats(self, tool_name: str, success: bool, execution_time: float):
        """Update performance statistics"""
        if tool_name not in self.performance_stats:
            self.performance_stats[tool_name] = {
                "total_executions": 0,
                "successful_executions": 0,
                "average_execution_time": 0.0,
                "last_execution": None
            }
        
        stats = self.performance_stats[tool_name]
        stats["total_executions"] += 1
        if success:
            stats["successful_executions"] += 1
        
        # Update average execution time
        current_avg = stats["average_execution_time"]
        total = stats["total_executions"]
        stats["average_execution_time"] = (current_avg * (total - 1) + execution_time) / total
        stats["last_execution"] = datetime.utcnow().isoformat()
    
    def list_tools(self, category: ToolCategory = None, 
                   complexity: ToolComplexity = None) -> List[Dict[str, Any]]:
        """List available tools with optional filtering"""
        tools_list = []
        
        for tool_name, tool_class in self.tools.items():
            metadata = tool_class.METADATA
            
            # Apply filters
            if category and metadata.category != category:
                continue
            if complexity and metadata.complexity != complexity:
                continue
            
            tool_info = {
                "name": metadata.name,
                "category": metadata.category.value,
                "complexity": metadata.complexity.value,
                "description": metadata.description,
                "version": metadata.version,
                "tags": metadata.tags,
                "performance_rating": metadata.performance_rating,
                "usage_count": metadata.usage_count
            }
            
            # Add performance stats if available
            if tool_name in self.performance_stats:
                stats = self.performance_stats[tool_name]
                success_rate = stats["successful_executions"] / max(stats["total_executions"], 1)
                tool_info.update({
                    "success_rate": success_rate,
                    "average_execution_time": stats["average_execution_time"],
                    "total_executions": stats["total_executions"]
                })
            
            tools_list.append(tool_info)
        
        # Sort by performance rating and usage
        tools_list.sort(key=lambda x: (x["performance_rating"], x.get("usage_count", 0)), reverse=True)
        return tools_list
    
    def get_tool_recommendations(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get tool recommendations based on query"""
        query_lower = query.lower()
        scored_tools = []
        
        for tool_name, tool_class in self.tools.items():
            metadata = tool_class.METADATA
            score = 0
            
            # Check name match
            if query_lower in metadata.name.lower():
                score += 10
            
            # Check description match
            if query_lower in metadata.description.lower():
                score += 5
            
            # Check tags match
            for tag in metadata.tags:
                if query_lower in tag.lower():
                    score += 3
            
            # Check use cases match
            for use_case in metadata.use_cases:
                if query_lower in use_case.lower():
                    score += 2
            
            if score > 0:
                tool_info = {
                    "name": metadata.name,
                    "description": metadata.description,
                    "category": metadata.category.value,
                    "score": score,
                    "use_cases": metadata.use_cases[:3]  # Top 3 use cases
                }
                scored_tools.append(tool_info)
        
        # Sort by score and return top results
        scored_tools.sort(key=lambda x: x["score"], reverse=True)
        return scored_tools[:limit]

class ToolManager:
    """Main tool management system"""
    
    def __init__(self):
        self.registry = ToolRegistry()
        self.tool_paths = ["tools/code_intelligence", "tools/data_analysis", "tools/web_dev"]
        self._load_lock = asyncio.Lock()
        
    async def initialize(self):
        """Initialize the tool management system"""
        logger.info("Initializing AeonForge Tools System...")
        await self._discover_and_load_tools()
        logger.info(f"Loaded {len(self.registry.tools)} tools across {len(self.registry.categories)} categories")
    
    async def _discover_and_load_tools(self):
        """Discover and load all tools from tool directories"""
        async with self._load_lock:
            for tool_path in self.tool_paths:
                if os.path.exists(tool_path):
                    await self._load_tools_from_directory(tool_path)
    
    async def _load_tools_from_directory(self, directory: str):
        """Load tools from a specific directory"""
        import importlib.util
        for filename in os.listdir(directory):
            if filename.endswith('.py') and not filename.startswith('__'):
                module_name = filename[:-3]
                try:
                    # Dynamic import
                    spec = importlib.util.spec_from_file_location(
                        module_name, os.path.join(directory, filename)
                    )
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Find tool classes
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if issubclass(obj, BaseTool) and obj != BaseTool:
                            if hasattr(obj, 'METADATA'):
                                self.registry.register_tool(obj)
                
                except Exception as e:
                    logger.error(f"Failed to load tool from {filename}: {e}")
    
    async def execute_tool(self, tool_name: str, **kwargs) -> ToolResult:
        """Execute a tool"""
        return await self.registry.execute_tool(tool_name, **kwargs)
    
    def search_tools(self, query: str) -> List[Dict[str, Any]]:
        """Search for tools"""
        return self.registry.get_tool_recommendations(query)
    
    def list_tools_by_category(self, category: ToolCategory) -> List[Dict[str, Any]]:
        """List tools by category"""
        return self.registry.list_tools(category=category)
    
    def get_tool_analytics(self) -> Dict[str, Any]:
        """Get comprehensive tool usage analytics"""
        analytics = {
            "total_tools": len(self.registry.tools),
            "categories": {cat.value: len(tools) for cat, tools in self.registry.categories.items()},
            "performance_stats": self.registry.performance_stats,
            "top_performing_tools": [],
            "most_used_tools": []
        }
        
        # Calculate top performing tools
        tools_with_stats = []
        for tool_name, stats in self.registry.performance_stats.items():
            if stats["total_executions"] > 0:
                success_rate = stats["successful_executions"] / stats["total_executions"]
                tools_with_stats.append({
                    "name": tool_name,
                    "success_rate": success_rate,
                    "usage_count": stats["total_executions"],
                    "avg_time": stats["average_execution_time"]
                })
        
        analytics["top_performing_tools"] = sorted(
            tools_with_stats, key=lambda x: x["success_rate"], reverse=True
        )[:10]
        
        analytics["most_used_tools"] = sorted(
            tools_with_stats, key=lambda x: x["usage_count"], reverse=True
        )[:10]
        
        return analytics

# Global tool manager instance
tool_manager = ToolManager()

async def get_tool_manager() -> ToolManager:
    """Get the global tool manager"""
    if not tool_manager.registry.tools:
        await tool_manager.initialize()
    return tool_manager

# Decorator for easy tool registration
def register_tool(metadata: ToolMetadata):
    """Decorator to register a tool"""
    def decorator(cls):
        cls.METADATA = metadata
        return cls
    return decorator

# Tool Category Loaders
def get_all_code_intelligence_tools() -> List[BaseTool]:
    """Get all Code Intelligence tools from all batches - First 20 revolutionary tools"""
    tools = []
    
    try:
        # Batch 1: Advanced Analyzers (Tools 1-3)
        from .code_intelligence.batch1_advanced_analyzers import get_advanced_analyzer_tools
        tools.extend(get_advanced_analyzer_tools())
    except ImportError as e:
        logger.warning(f"Could not load advanced analyzer tools: {e}")
    
    try:
        # Batch 2: Generators & Optimizers (Tools 4-5) 
        from .code_intelligence.batch1_generators_optimizers import get_generator_optimizer_tools
        tools.extend(get_generator_optimizer_tools())
    except ImportError as e:
        logger.warning(f"Could not load generator/optimizer tools: {e}")
    
    try:
        # Batch 3: Remaining Tools (Tools 6-8)
        from .code_intelligence.batch1_remaining_tools import get_remaining_tools
        tools.extend(get_remaining_tools())
    except ImportError as e:
        logger.warning(f"Could not load remaining tools: {e}")
    
    try:
        # Batch 4: Final Tools (Tools 9-13)
        from .code_intelligence.batch1_final_tools import get_final_batch_tools
        tools.extend(get_final_batch_tools())
    except ImportError as e:
        logger.warning(f"Could not load final batch tools: {e}")
    
    try:
        # Batch 5: Ultimate Tools (Tools 14-20)
        from .code_intelligence.batch1_ultimate_tools import get_ultimate_batch_tools
        tools.extend(get_ultimate_batch_tools())
    except ImportError as e:
        logger.warning(f"Could not load ultimate batch tools: {e}")
    
    logger.info(f"Successfully loaded {len(tools)} Code Intelligence tools")
    return tools

def register_all_code_intelligence_tools(registry: ToolRegistry):
    """Register all Code Intelligence tools with the registry"""
    tools = get_all_code_intelligence_tools()
    for tool in tools:
        try:
            # Create a temporary class with METADATA for registration
            tool_class = type(f"{tool.__class__.__name__}Registered", (tool.__class__,), {
                'METADATA': ToolMetadata(
                    name=tool.name,
                    category=ToolCategory.CODE_INTELLIGENCE,
                    complexity=ToolComplexity.COMPLEX,
                    execution_mode=ToolExecutionMode.ASYNCHRONOUS,
                    description=tool.description,
                    tags=['code_intelligence', 'analysis', 'ai_powered'],
                    use_cases=['Code analysis', 'Quality assurance', 'Development assistance']
                )
            })
            registry.register_tool(tool_class)
        except Exception as e:
            logger.error(f"Failed to register tool {tool.name}: {e}")

# Export main classes
__all__ = [
    'BaseTool', 'ToolResult', 'ToolMetadata', 'ToolManager', 
    'ToolCategory', 'ToolComplexity', 'ToolExecutionMode',
    'register_tool', 'get_tool_manager', 'tool_manager',
    'get_all_code_intelligence_tools', 'register_all_code_intelligence_tools'
]