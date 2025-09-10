"""
Aeonforge Memory Integration Layer
Integrates memory and project management with all existing phases
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import asdict
from datetime import datetime

from .memory_system import MemorySystem
from .project_manager import ProjectManager
from .instruction_manager import InstructionManager, InstructionType, InstructionScope

class AeonforgeMemoryCore:
    """Central memory integration for all Aeonforge phases"""
    
    def __init__(self, data_dir: str = "memory_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Initialize core systems
        self.memory = MemorySystem(str(self.data_dir))
        self.project_manager = ProjectManager(str(self.data_dir))
        self.instruction_manager = InstructionManager(self.memory)
        
        # Phase integration flags
        self.phase_integrations = {
            "phase1": False,  # Foundation
            "phase2": False,  # Multi-Agent System  
            "phase3": False,  # Advanced Code Intelligence
            "phase4": False,  # Intelligent Testing
            "phase5": False,  # Multi-Language Intelligence
            "phase6": False,  # Platform Integrations
            "phase7": False,  # Workflow Automation
        }
        
        # Load existing integrations
        self._check_phase_integrations()
    
    def _check_phase_integrations(self):
        """Check which phases are available and integrated"""
        try:
            # Check Phase 2 - Multi-Agent System
            from backend.main import AgentManager
            self.phase_integrations["phase2"] = True
        except ImportError:
            pass
        
        try:
            # Check Phase 5 - Multi-Language Intelligence  
            from tools.multi_language_manager import MultiLanguageManager
            self.phase_integrations["phase5"] = True
        except ImportError:
            pass
        
        try:
            # Check Phase 6 - Platform Integrations
            from tools.service_integrations import ServiceIntegrationManager
            self.phase_integrations["phase6"] = True
        except ImportError:
            pass
        
        try:
            # Check Phase 7 - Workflow Automation
            from tools.workflow_engine import WorkflowEngine
            self.phase_integrations["phase7"] = True
        except ImportError:
            pass
    
    def initialize_session_with_memory(self, user_message: str = "", context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Initialize session with full memory context"""
        # Auto-detect project if working in a project directory
        current_dir = os.getcwd()
        project = self.project_manager.memory.get_project_by_path(current_dir)
        
        session_context = {
            "session_id": self.memory.current_session.id if self.memory.current_session else None,
            "current_project": None,
            "project_instructions": {},
            "contextual_instructions": [],
            "recent_conversations": [],
            "relevant_knowledge": [],
            "phase_states": {},
            "available_phases": self.phase_integrations
        }
        
        # Switch to project if detected
        if project:
            success = self.project_manager.switch_to_project(project.id)
            if success:
                session_context["current_project"] = {
                    "id": project.id,
                    "name": project.name,
                    "path": project.base_path,
                    "description": project.description
                }
                
                # Load project instructions
                instructions = self.instruction_manager.get_contextual_instructions(
                    project.id,
                    current_file=context.get("current_file", "") if context else "",
                    file_type=context.get("file_type", "") if context else ""
                )
                
                session_context["contextual_instructions"] = [
                    {
                        "title": instr.instruction.title,
                        "content": instr.resolved_content,
                        "type": instr.instruction.type.value,
                        "priority": instr.instruction.priority,
                        "applies": instr.applies_to_current_context,
                        "examples": instr.active_examples
                    }
                    for instr in instructions if instr.applies_to_current_context
                ]
                
                # Generate instruction summary
                session_context["instruction_summary"] = self.instruction_manager.generate_instruction_summary(
                    project.id,
                    context.get("current_file", "") if context else ""
                )
        
        # Get memory context
        memory_context = self.memory.get_context_for_current_session()
        session_context.update({
            "recent_conversations": memory_context.get("recent_conversations", []),
            "phase_states": memory_context.get("phase_states", {})
        })
        
        # Search for relevant knowledge if user provided a message
        if user_message:
            relevant_knowledge = self.memory.search_memory(user_message, limit=5)
            session_context["relevant_knowledge"] = relevant_knowledge
        
        return session_context
    
    def remember_interaction(self, user_message: str, assistant_response: str, 
                           context: Dict[str, Any] = None) -> str:
        """Remember interaction with enhanced context"""
        # Extract context information
        files_referenced = context.get("files_referenced", []) if context else []
        tools_used = context.get("tools_used", []) if context else []
        context_tags = context.get("tags", []) if context else []
        
        # Auto-extract additional context
        if "```" in assistant_response:
            context_tags.append("code")
        
        if any(keyword in user_message.lower() for keyword in ["create", "new", "add"]):
            context_tags.append("creation")
        elif any(keyword in user_message.lower() for keyword in ["fix", "debug", "error"]):
            context_tags.append("debugging")
        elif any(keyword in user_message.lower() for keyword in ["test", "testing"]):
            context_tags.append("testing")
        
        # Remember the conversation
        conversation_id = self.memory.remember_conversation(
            user_message=user_message,
            assistant_response=assistant_response,
            context_tags=context_tags,
            files_referenced=files_referenced,
            tools_used=tools_used,
            metadata=context or {}
        )
        
        # Update current project's knowledge base if applicable
        if self.project_manager.current_workspace:
            self._update_project_knowledge(user_message, assistant_response, context or {})
        
        return conversation_id
    
    def _update_project_knowledge(self, user_message: str, assistant_response: str, context: Dict[str, Any]):
        """Update project-specific knowledge based on interaction"""
        project = self.project_manager.current_workspace.project
        
        # Extract patterns that could become instructions
        if any(keyword in user_message.lower() for keyword in ["always", "never", "remember", "rule"]):
            # This could be a new instruction
            self._suggest_instruction_from_interaction(user_message, assistant_response, project.id)
        
        # Update project bookmarks if files were heavily referenced
        files = context.get("files_referenced", [])
        if len(files) >= 3:  # Multiple files referenced - might be important
            for file_path in files:
                # Auto-bookmark frequently referenced files
                bookmark_name = f"auto_{Path(file_path).stem}"
                self.project_manager.add_bookmark(bookmark_name, file_path)
    
    def _suggest_instruction_from_interaction(self, user_message: str, assistant_response: str, project_id: str):
        """Suggest new instruction based on interaction pattern"""
        # Simple heuristics to extract potential instructions
        instruction_keywords = {
            "always use": InstructionType.CODING_STYLE,
            "never use": InstructionType.CONSTRAINT,
            "must test": InstructionType.TESTING,
            "should deploy": InstructionType.DEPLOYMENT,
            "architecture": InstructionType.ARCHITECTURE
        }
        
        user_lower = user_message.lower()
        
        for keyword, instr_type in instruction_keywords.items():
            if keyword in user_lower:
                # Extract the instruction content (simplified)
                sentences = user_message.split('.')
                for sentence in sentences:
                    if keyword in sentence.lower():
                        # This is a candidate for an instruction
                        title = f"Auto-extracted: {sentence.strip()[:50]}..."
                        content = sentence.strip()
                        
                        # Add as low-priority suggestion
                        self.instruction_manager.add_custom_instruction(
                            project_id=project_id,
                            title=title,
                            content=content,
                            instruction_type=instr_type,
                            scope=InstructionScope.GLOBAL,
                            priority=3,  # Low priority for auto-extracted
                            tags=["auto-extracted", "suggestion"]
                        )
                        break
                break
    
    def create_project_with_memory(self, name: str, base_path: str, template_id: str = None,
                                 instructions: str = "", custom_rules: List[str] = None) -> str:
        """Create project with full memory integration"""
        if template_id:
            # Create from template
            project_id = self.project_manager.create_project_from_template(
                template_id=template_id,
                project_name=name,
                base_path=base_path
            )
        else:
            # Create basic project
            project_id = self.memory.create_project(
                name=name,
                base_path=base_path,
                instructions=instructions,
                custom_rules=custom_rules or []
            )
        
        # Create instruction set with template if specified
        template_ids = [template_id] if template_id else []
        self.instruction_manager.create_instruction_set_for_project(project_id, template_ids)
        
        # Switch to the new project
        self.project_manager.switch_to_project(project_id)
        
        return project_id
    
    def get_project_summary(self, project_id: str = None) -> Dict[str, Any]:
        """Get comprehensive project summary"""
        if not project_id and self.project_manager.current_workspace:
            project_id = self.project_manager.current_workspace.project.id
        
        if not project_id:
            return {}
        
        project = self.memory._load_project(project_id)
        if not project:
            return {}
        
        # Get project context
        project_context = self.project_manager.get_project_context() if project_id == (
            self.project_manager.current_workspace.project.id if self.project_manager.current_workspace else None
        ) else {}
        
        # Get instruction summary
        instruction_summary = self.instruction_manager.generate_instruction_summary(project_id)
        
        # Get recent conversations for this project
        recent_conversations = self.memory.search_memory("", project_only=True, limit=5)
        
        # Get project statistics
        project_stats = self._get_project_statistics(project_id)
        
        return {
            "project": {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "path": project.base_path,
                "created": project.created_at.isoformat(),
                "last_accessed": project.last_accessed.isoformat()
            },
            "workspace": project_context.get("workspace", {}),
            "instructions": {
                "summary": instruction_summary,
                "count": len(self.instruction_manager.instruction_sets.get(project_id, {}).custom_instructions or [])
            },
            "memory": {
                "recent_conversations": len(recent_conversations),
                "total_conversations": project_stats.get("conversation_count", 0)
            },
            "statistics": project_stats,
            "phase_integrations": self.phase_integrations
        }
    
    def _get_project_statistics(self, project_id: str) -> Dict[str, Any]:
        """Get project usage statistics"""
        # Query database for project statistics
        import sqlite3
        
        stats = {
            "conversation_count": 0,
            "file_references": 0,
            "tool_usage": {},
            "most_active_days": [],
            "knowledge_items": 0
        }
        
        try:
            # Conversation statistics
            conn = sqlite3.connect(str(self.memory.db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*), 
                       COUNT(DISTINCT DATE(timestamp)),
                       AVG(LENGTH(user_message) + LENGTH(assistant_response))
                FROM conversations 
                WHERE project_id = ?
            """, (project_id,))
            
            result = cursor.fetchone()
            if result:
                stats["conversation_count"] = result[0] or 0
                stats["active_days"] = result[1] or 0
                stats["avg_conversation_length"] = result[2] or 0
            
            # Tool usage statistics
            cursor.execute("""
                SELECT tools_used, COUNT(*)
                FROM conversations
                WHERE project_id = ? AND tools_used != '[]'
                GROUP BY tools_used
                ORDER BY COUNT(*) DESC
                LIMIT 10
            """, (project_id,))
            
            tool_usage = {}
            for row in cursor.fetchall():
                try:
                    tools = json.loads(row[0])
                    for tool in tools:
                        tool_usage[tool] = tool_usage.get(tool, 0) + row[1]
                except:
                    pass
            
            stats["tool_usage"] = tool_usage
            conn.close()
            
        except Exception as e:
            print(f"Error getting project statistics: {e}")
        
        return stats
    
    def search_project_memory(self, query: str, project_id: str = None, 
                            include_instructions: bool = True) -> Dict[str, Any]:
        """Search through all project memory"""
        if not project_id and self.project_manager.current_workspace:
            project_id = self.project_manager.current_workspace.project.id
        
        if not project_id:
            return {"error": "No project context"}
        
        results = {
            "conversations": [],
            "knowledge": [],
            "instructions": [],
            "files": []
        }
        
        # Search conversations and knowledge
        memory_results = self.memory.search_memory(query, project_only=True, limit=10)
        
        for result in memory_results:
            if result["type"] == "conversation":
                results["conversations"].append(result)
            elif result["type"] == "knowledge":
                results["knowledge"].append(result)
        
        # Search instructions
        if include_instructions:
            instruction_results = self.instruction_manager.search_instructions(project_id, query)
            results["instructions"] = [
                {
                    "title": instr.title,
                    "content": instr.content,
                    "type": instr.type.value,
                    "tags": instr.tags,
                    "priority": instr.priority
                }
                for instr in instruction_results
            ]
        
        # Search project files (if current workspace)
        if (self.project_manager.current_workspace and 
            self.project_manager.current_workspace.project.id == project_id):
            
            project_context = self.project_manager.get_project_context()
            project_files = project_context.get("project_files", [])
            
            # Simple filename search
            matching_files = [
                file for file in project_files
                if query.lower() in file.lower()
            ]
            results["files"] = matching_files[:10]
        
        return results
    
    def export_project_memory(self, project_id: str, export_path: str) -> bool:
        """Export all project memory to file"""
        try:
            project_summary = self.get_project_summary(project_id)
            memory_data = self.search_project_memory("", project_id)
            
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "project_summary": project_summary,
                "memory_data": memory_data,
                "aeonforge_version": "Phase 7+",
                "memory_system_version": "1.0"
            }
            
            export_file = Path(export_path)
            export_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(export_file, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            return True
        
        except Exception as e:
            print(f"Export failed: {e}")
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system memory status"""
        return {
            "memory_system": {
                "active": True,
                "current_session": self.memory.current_session.id if self.memory.current_session else None,
                "cache_sizes": {
                    "conversations": len(self.memory.conversation_cache),
                    "projects": len(self.memory.project_cache),
                    "knowledge": len(self.memory.knowledge_cache)
                }
            },
            "project_manager": {
                "active": True,
                "current_project": (
                    self.project_manager.current_workspace.project.name 
                    if self.project_manager.current_workspace else None
                ),
                "available_templates": len(self.project_manager.project_templates)
            },
            "instruction_manager": {
                "active": True,
                "loaded_instruction_sets": len(self.instruction_manager.instruction_sets),
                "template_instructions": sum(len(instrs) for instrs in self.instruction_manager.template_instructions.values())
            },
            "phase_integrations": self.phase_integrations,
            "data_directory": str(self.data_dir),
            "working_directory": os.getcwd()
        }

# Global instance for easy access
aeonforge_memory = AeonforgeMemoryCore()

def initialize_memory(user_message: str = "", context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Initialize Aeonforge with memory - convenience function"""
    return aeonforge_memory.initialize_session_with_memory(user_message, context)

def remember_interaction(user_message: str, assistant_response: str, context: Dict[str, Any] = None) -> str:
    """Remember interaction - convenience function"""
    return aeonforge_memory.remember_interaction(user_message, assistant_response, context)

def get_current_context() -> Dict[str, Any]:
    """Get current project and memory context"""
    return aeonforge_memory.initialize_session_with_memory()

def main():
    """Test the integration layer"""
    # Initialize memory system
    context = initialize_memory("Hello, I want to start a new React project")
    print(f"Initialized with context: {context.get('available_phases')}")
    
    # Create a project
    project_id = aeonforge_memory.create_project_with_memory(
        name="Test React App",
        base_path="./test_react_app",
        template_id="react-typescript"
    )
    
    print(f"Created project: {project_id}")
    
    # Remember an interaction
    conversation_id = remember_interaction(
        user_message="Create a new React component for user authentication",
        assistant_response="I'll create a TypeScript React component for authentication...",
        context={
            "files_referenced": ["src/components/Auth.tsx", "src/hooks/useAuth.ts"],
            "tools_used": ["Write", "Edit"],
            "tags": ["react", "authentication", "typescript"]
        }
    )
    
    print(f"Remembered conversation: {conversation_id}")
    
    # Get project summary
    summary = aeonforge_memory.get_project_summary()
    print(f"Project summary: {summary['project']['name']}")
    print(f"Instructions available: {summary['instructions']['count']}")
    
    # Search memory
    search_results = aeonforge_memory.search_project_memory("React component")
    print(f"Found {len(search_results['conversations'])} conversation matches")
    print(f"Found {len(search_results['instructions'])} instruction matches")

if __name__ == "__main__":
    main()