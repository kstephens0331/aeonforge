"""
Aeonforge Instruction Manager - Project-Specific Instructions and Rules
Manages custom instructions, rules, and context for individual projects
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Union
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

from .memory_system import MemorySystem

class InstructionType(Enum):
    """Types of instructions"""
    CODING_STYLE = "coding_style"
    ARCHITECTURE = "architecture"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    WORKFLOW = "workflow"
    BUSINESS_RULE = "business_rule"
    CONSTRAINT = "constraint"
    PREFERENCE = "preference"

class InstructionScope(Enum):
    """Scope of instruction application"""
    GLOBAL = "global"  # Applies to entire project
    DIRECTORY = "directory"  # Applies to specific directory
    FILE_TYPE = "file_type"  # Applies to specific file types
    COMPONENT = "component"  # Applies to specific components

@dataclass
class Instruction:
    """Individual instruction or rule"""
    id: str
    title: str
    content: str
    type: InstructionType
    scope: InstructionScope
    scope_target: str  # Directory path, file pattern, component name
    priority: int  # 1-10, higher is more important
    active: bool
    examples: List[str]
    exceptions: List[str]
    created_at: datetime
    last_modified: datetime
    created_by: str  # 'user', 'assistant', 'template'
    tags: List[str]
    metadata: Dict[str, Any]

@dataclass
class InstructionSet:
    """Collection of instructions for a project"""
    project_id: str
    project_name: str
    base_instructions: str
    custom_instructions: List[Instruction]
    inherited_templates: List[str]
    global_overrides: Dict[str, Any]
    context_variables: Dict[str, str]
    last_updated: datetime

@dataclass
class ContextualInstruction:
    """Instruction with resolved context"""
    instruction: Instruction
    applies_to_current_context: bool
    context_match_score: float
    resolved_content: str
    active_examples: List[str]

class InstructionManager:
    """Manages project-specific instructions and rules"""
    
    def __init__(self, memory_system: MemorySystem):
        self.memory = memory_system
        self.instruction_sets: Dict[str, InstructionSet] = {}
        self.template_instructions: Dict[str, List[Instruction]] = {}
        
        # Load built-in instruction templates
        self._load_instruction_templates()
    
    def _load_instruction_templates(self):
        """Load built-in instruction templates"""
        
        # React TypeScript Instructions
        react_instructions = [
            Instruction(
                id="react-functional-components",
                title="Use Functional Components",
                content="Always use functional components with React hooks instead of class components. Use arrow function syntax for consistency.",
                type=InstructionType.CODING_STYLE,
                scope=InstructionScope.FILE_TYPE,
                scope_target="*.tsx,*.jsx",
                priority=9,
                active=True,
                examples=[
                    "const MyComponent: React.FC<Props> = ({ title }) => { return <div>{title}</div>; };",
                    "const useCustomHook = () => { const [state, setState] = useState(); return { state, setState }; };"
                ],
                exceptions=["Legacy components that haven't been migrated yet"],
                created_at=datetime.now(),
                last_modified=datetime.now(),
                created_by="template",
                tags=["react", "components", "hooks"],
                metadata={"framework": "react"}
            ),
            
            Instruction(
                id="typescript-strict-types",
                title="Strict TypeScript Typing",
                content="Use strict TypeScript types. Avoid 'any' type. Define interfaces for all props and state. Use generics where appropriate.",
                type=InstructionType.CODING_STYLE,
                scope=InstructionScope.FILE_TYPE,
                scope_target="*.ts,*.tsx",
                priority=10,
                active=True,
                examples=[
                    "interface Props { title: string; onClick: () => void; }",
                    "type ApiResponse<T> = { data: T; status: number; message?: string; }"
                ],
                exceptions=["Third-party library types that are not well-defined"],
                created_at=datetime.now(),
                last_modified=datetime.now(),
                created_by="template",
                tags=["typescript", "types", "interfaces"],
                metadata={"language": "typescript"}
            ),
            
            Instruction(
                id="component-testing",
                title="Component Testing Requirements",
                content="Every component must have corresponding unit tests. Test user interactions, prop variations, and error states.",
                type=InstructionType.TESTING,
                scope=InstructionScope.FILE_TYPE,
                scope_target="*.tsx",
                priority=8,
                active=True,
                examples=[
                    "test('renders component with title', () => { render(<Component title='test' />); expect(screen.getByText('test')).toBeInTheDocument(); });",
                    "test('handles click events', () => { const onClick = jest.fn(); render(<Component onClick={onClick} />); fireEvent.click(screen.getByRole('button')); expect(onClick).toHaveBeenCalled(); });"
                ],
                exceptions=["Simple presentation components with no logic"],
                created_at=datetime.now(),
                last_modified=datetime.now(),
                created_by="template",
                tags=["testing", "components", "unit-tests"],
                metadata={"testing_framework": "vitest"}
            )
        ]
        
        # Python FastAPI Instructions
        python_instructions = [
            Instruction(
                id="async-await-pattern",
                title="Use Async/Await for I/O Operations",
                content="Use async/await for all database operations, external API calls, and file I/O. Never use blocking operations in async contexts.",
                type=InstructionType.CODING_STYLE,
                scope=InstructionScope.FILE_TYPE,
                scope_target="*.py",
                priority=10,
                active=True,
                examples=[
                    "async def get_user(db: AsyncSession, user_id: int) -> User: return await db.get(User, user_id)",
                    "async def call_external_api() -> dict: async with httpx.AsyncClient() as client: return await client.get('/api/data')"
                ],
                exceptions=["Synchronous utility functions that don't perform I/O"],
                created_at=datetime.now(),
                last_modified=datetime.now(),
                created_by="template",
                tags=["python", "async", "performance"],
                metadata={"framework": "fastapi"}
            ),
            
            Instruction(
                id="pydantic-validation",
                title="Use Pydantic Models for Validation",
                content="Use Pydantic models for all request/response validation. Define clear field types, constraints, and examples.",
                type=InstructionType.ARCHITECTURE,
                scope=InstructionScope.DIRECTORY,
                scope_target="app/models",
                priority=9,
                active=True,
                examples=[
                    "class UserCreate(BaseModel): email: EmailStr; name: str = Field(..., min_length=1, max_length=100)",
                    "class UserResponse(BaseModel): id: int; email: str; created_at: datetime; class Config: from_attributes = True"
                ],
                exceptions=["Internal data structures that don't cross API boundaries"],
                created_at=datetime.now(),
                last_modified=datetime.now(),
                created_by="template",
                tags=["python", "validation", "api"],
                metadata={"library": "pydantic"}
            ),
            
            Instruction(
                id="dependency-injection",
                title="Use Dependency Injection",
                content="Use FastAPI's dependency injection system for database sessions, authentication, and shared services. Never create global connections.",
                type=InstructionType.ARCHITECTURE,
                scope=InstructionScope.DIRECTORY,
                scope_target="app/api",
                priority=8,
                active=True,
                examples=[
                    "async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:",
                    "@app.get('/users/{user_id}') async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):"
                ],
                exceptions=["Simple utility endpoints that don't require dependencies"],
                created_at=datetime.now(),
                last_modified=datetime.now(),
                created_by="template",
                tags=["fastapi", "dependency-injection", "architecture"],
                metadata={"pattern": "dependency_injection"}
            )
        ]
        
        self.template_instructions = {
            "react-typescript": react_instructions,
            "python-fastapi": python_instructions
        }
    
    def create_instruction_set_for_project(self, project_id: str, template_ids: List[str] = None) -> InstructionSet:
        """Create instruction set for a project"""
        project = self.memory._load_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        # Start with base instructions from project
        instruction_set = InstructionSet(
            project_id=project_id,
            project_name=project.name,
            base_instructions=project.instructions,
            custom_instructions=[],
            inherited_templates=template_ids or [],
            global_overrides={},
            context_variables={
                "project_name": project.name,
                "project_path": project.base_path,
                "current_date": datetime.now().strftime("%Y-%m-%d")
            },
            last_updated=datetime.now()
        )
        
        # Add template instructions
        if template_ids:
            for template_id in template_ids:
                if template_id in self.template_instructions:
                    for template_instruction in self.template_instructions[template_id]:
                        # Create copy with new ID for project
                        project_instruction = Instruction(
                            id=f"{project_id}_{template_instruction.id}",
                            title=template_instruction.title,
                            content=template_instruction.content,
                            type=template_instruction.type,
                            scope=template_instruction.scope,
                            scope_target=template_instruction.scope_target,
                            priority=template_instruction.priority,
                            active=template_instruction.active,
                            examples=template_instruction.examples.copy(),
                            exceptions=template_instruction.exceptions.copy(),
                            created_at=datetime.now(),
                            last_modified=datetime.now(),
                            created_by="template",
                            tags=template_instruction.tags.copy(),
                            metadata=template_instruction.metadata.copy()
                        )
                        instruction_set.custom_instructions.append(project_instruction)
        
        self.instruction_sets[project_id] = instruction_set
        self._save_instruction_set(instruction_set)
        
        return instruction_set
    
    def add_custom_instruction(self, project_id: str, title: str, content: str,
                             instruction_type: InstructionType, scope: InstructionScope,
                             scope_target: str = "", priority: int = 5,
                             examples: List[str] = None, tags: List[str] = None) -> str:
        """Add custom instruction to project"""
        instruction_set = self._get_or_create_instruction_set(project_id)
        
        instruction_id = f"{project_id}_{len(instruction_set.custom_instructions)}_{int(datetime.now().timestamp())}"
        
        instruction = Instruction(
            id=instruction_id,
            title=title,
            content=content,
            type=instruction_type,
            scope=scope,
            scope_target=scope_target,
            priority=priority,
            active=True,
            examples=examples or [],
            exceptions=[],
            created_at=datetime.now(),
            last_modified=datetime.now(),
            created_by="user",
            tags=tags or [],
            metadata={}
        )
        
        instruction_set.custom_instructions.append(instruction)
        instruction_set.last_updated = datetime.now()
        
        self._save_instruction_set(instruction_set)
        
        return instruction_id
    
    def update_instruction(self, project_id: str, instruction_id: str, **updates) -> bool:
        """Update existing instruction"""
        instruction_set = self.instruction_sets.get(project_id)
        if not instruction_set:
            return False
        
        instruction = None
        for instr in instruction_set.custom_instructions:
            if instr.id == instruction_id:
                instruction = instr
                break
        
        if not instruction:
            return False
        
        # Update fields
        for field, value in updates.items():
            if hasattr(instruction, field):
                setattr(instruction, field, value)
        
        instruction.last_modified = datetime.now()
        instruction_set.last_updated = datetime.now()
        
        self._save_instruction_set(instruction_set)
        
        return True
    
    def deactivate_instruction(self, project_id: str, instruction_id: str) -> bool:
        """Deactivate an instruction without deleting it"""
        return self.update_instruction(project_id, instruction_id, active=False)
    
    def get_contextual_instructions(self, project_id: str, current_file: str = "",
                                  current_directory: str = "", file_type: str = "") -> List[ContextualInstruction]:
        """Get instructions relevant to current context"""
        instruction_set = self.instruction_sets.get(project_id)
        if not instruction_set:
            return []
        
        contextual_instructions = []
        
        for instruction in instruction_set.custom_instructions:
            if not instruction.active:
                continue
            
            # Calculate context relevance
            applies_to_context = self._instruction_applies_to_context(
                instruction, current_file, current_directory, file_type
            )
            
            match_score = self._calculate_context_match_score(
                instruction, current_file, current_directory, file_type
            )
            
            # Resolve context variables in content
            resolved_content = self._resolve_context_variables(
                instruction.content, instruction_set.context_variables
            )
            
            contextual_instruction = ContextualInstruction(
                instruction=instruction,
                applies_to_current_context=applies_to_context,
                context_match_score=match_score,
                resolved_content=resolved_content,
                active_examples=instruction.examples
            )
            
            contextual_instructions.append(contextual_instruction)
        
        # Sort by priority and relevance
        contextual_instructions.sort(
            key=lambda x: (x.instruction.priority, x.context_match_score),
            reverse=True
        )
        
        return contextual_instructions
    
    def _instruction_applies_to_context(self, instruction: Instruction, current_file: str,
                                      current_directory: str, file_type: str) -> bool:
        """Check if instruction applies to current context"""
        if instruction.scope == InstructionScope.GLOBAL:
            return True
        
        elif instruction.scope == InstructionScope.FILE_TYPE:
            if not instruction.scope_target:
                return True
            patterns = instruction.scope_target.split(',')
            for pattern in patterns:
                pattern = pattern.strip()
                if file_type and pattern.endswith(file_type):
                    return True
                if current_file and self._matches_pattern(current_file, pattern):
                    return True
        
        elif instruction.scope == InstructionScope.DIRECTORY:
            if not instruction.scope_target:
                return True
            target_dir = instruction.scope_target.strip()
            if current_directory.startswith(target_dir) or current_file.startswith(target_dir):
                return True
        
        elif instruction.scope == InstructionScope.COMPONENT:
            # Would need more sophisticated component detection
            return instruction.scope_target.lower() in current_file.lower()
        
        return False
    
    def _calculate_context_match_score(self, instruction: Instruction, current_file: str,
                                     current_directory: str, file_type: str) -> float:
        """Calculate how well instruction matches current context"""
        score = 0.0
        
        # Base score from priority
        score += instruction.priority / 10.0
        
        # Scope specificity bonus
        if instruction.scope == InstructionScope.FILE_TYPE:
            score += 0.3
        elif instruction.scope == InstructionScope.DIRECTORY:
            score += 0.2
        elif instruction.scope == InstructionScope.COMPONENT:
            score += 0.4
        
        # Tag matching
        if instruction.tags:
            file_name_lower = current_file.lower() if current_file else ""
            tag_matches = sum(1 for tag in instruction.tags if tag.lower() in file_name_lower)
            score += (tag_matches / len(instruction.tags)) * 0.2
        
        # Exact pattern matching bonus
        if instruction.scope == InstructionScope.FILE_TYPE and instruction.scope_target:
            patterns = instruction.scope_target.split(',')
            for pattern in patterns:
                if current_file and self._matches_pattern(current_file, pattern.strip()):
                    score += 0.3
                    break
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _matches_pattern(self, filename: str, pattern: str) -> bool:
        """Check if filename matches pattern (supports wildcards)"""
        import fnmatch
        return fnmatch.fnmatch(filename, pattern)
    
    def _resolve_context_variables(self, content: str, variables: Dict[str, str]) -> str:
        """Resolve context variables in instruction content"""
        resolved_content = content
        
        for var_name, var_value in variables.items():
            placeholder = f"{{{{{var_name}}}}}"
            resolved_content = resolved_content.replace(placeholder, var_value)
        
        return resolved_content
    
    def _get_or_create_instruction_set(self, project_id: str) -> InstructionSet:
        """Get existing or create new instruction set"""
        if project_id in self.instruction_sets:
            return self.instruction_sets[project_id]
        
        return self.create_instruction_set_for_project(project_id)
    
    def _save_instruction_set(self, instruction_set: InstructionSet):
        """Save instruction set to file"""
        project = self.memory._load_project(instruction_set.project_id)
        if not project:
            return
        
        instructions_dir = Path(project.base_path) / ".aeonforge"
        instructions_dir.mkdir(exist_ok=True)
        
        instructions_file = instructions_dir / "instructions.json"
        
        # Convert to serializable format
        data = {
            "project_id": instruction_set.project_id,
            "project_name": instruction_set.project_name,
            "base_instructions": instruction_set.base_instructions,
            "custom_instructions": [asdict(instr) for instr in instruction_set.custom_instructions],
            "inherited_templates": instruction_set.inherited_templates,
            "global_overrides": instruction_set.global_overrides,
            "context_variables": instruction_set.context_variables,
            "last_updated": instruction_set.last_updated.isoformat()
        }
        
        # Handle datetime serialization
        for instr_data in data["custom_instructions"]:
            instr_data["created_at"] = instr_data["created_at"].isoformat()
            instr_data["last_modified"] = instr_data["last_modified"].isoformat()
            instr_data["type"] = instr_data["type"].value
            instr_data["scope"] = instr_data["scope"].value
        
        with open(instructions_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_instruction_set_from_file(self, project_id: str) -> Optional[InstructionSet]:
        """Load instruction set from file"""
        project = self.memory._load_project(project_id)
        if not project:
            return None
        
        instructions_file = Path(project.base_path) / ".aeonforge" / "instructions.json"
        if not instructions_file.exists():
            return None
        
        try:
            with open(instructions_file, 'r') as f:
                data = json.load(f)
            
            # Parse instructions
            custom_instructions = []
            for instr_data in data.get("custom_instructions", []):
                instruction = Instruction(
                    id=instr_data["id"],
                    title=instr_data["title"],
                    content=instr_data["content"],
                    type=InstructionType(instr_data["type"]),
                    scope=InstructionScope(instr_data["scope"]),
                    scope_target=instr_data["scope_target"],
                    priority=instr_data["priority"],
                    active=instr_data["active"],
                    examples=instr_data["examples"],
                    exceptions=instr_data["exceptions"],
                    created_at=datetime.fromisoformat(instr_data["created_at"]),
                    last_modified=datetime.fromisoformat(instr_data["last_modified"]),
                    created_by=instr_data["created_by"],
                    tags=instr_data["tags"],
                    metadata=instr_data["metadata"]
                )
                custom_instructions.append(instruction)
            
            instruction_set = InstructionSet(
                project_id=data["project_id"],
                project_name=data["project_name"],
                base_instructions=data["base_instructions"],
                custom_instructions=custom_instructions,
                inherited_templates=data["inherited_templates"],
                global_overrides=data["global_overrides"],
                context_variables=data["context_variables"],
                last_updated=datetime.fromisoformat(data["last_updated"])
            )
            
            self.instruction_sets[project_id] = instruction_set
            return instruction_set
        
        except Exception as e:
            print(f"Failed to load instructions: {e}")
            return None
    
    def generate_instruction_summary(self, project_id: str, current_context: str = "") -> str:
        """Generate a summary of active instructions for current context"""
        contextual_instructions = self.get_contextual_instructions(project_id, current_context)
        
        if not contextual_instructions:
            return "No specific instructions found for this project."
        
        summary_parts = []
        
        # Group by type
        by_type = {}
        for ctx_instr in contextual_instructions:
            if ctx_instr.applies_to_current_context:
                instr_type = ctx_instr.instruction.type
                if instr_type not in by_type:
                    by_type[instr_type] = []
                by_type[instr_type].append(ctx_instr)
        
        for instr_type, instructions in by_type.items():
            summary_parts.append(f"\n**{instr_type.value.replace('_', ' ').title()} Guidelines:**")
            
            for ctx_instr in sorted(instructions, key=lambda x: x.instruction.priority, reverse=True):
                instr = ctx_instr.instruction
                summary_parts.append(f"• {instr.title}: {ctx_instr.resolved_content}")
                
                if instr.examples and len(instr.examples) > 0:
                    summary_parts.append(f"  Example: {instr.examples[0]}")
        
        return "\n".join(summary_parts) if summary_parts else "No active instructions for current context."
    
    def search_instructions(self, project_id: str, query: str) -> List[Instruction]:
        """Search instructions by content"""
        instruction_set = self.instruction_sets.get(project_id)
        if not instruction_set:
            return []
        
        query_lower = query.lower()
        matching_instructions = []
        
        for instruction in instruction_set.custom_instructions:
            if (query_lower in instruction.title.lower() or
                query_lower in instruction.content.lower() or
                any(query_lower in tag.lower() for tag in instruction.tags) or
                any(query_lower in example.lower() for example in instruction.examples)):
                matching_instructions.append(instruction)
        
        return matching_instructions

def main():
    """Test the instruction manager"""
    from memory_system import MemorySystem
    
    memory = MemorySystem()
    instruction_manager = InstructionManager(memory)
    
    # Create a test project
    project_id = memory.create_project(
        name="Test React Project",
        base_path="/test/react-project",
        instructions="Build a React application with TypeScript"
    )
    
    # Create instruction set with template
    instruction_set = instruction_manager.create_instruction_set_for_project(
        project_id, 
        template_ids=["react-typescript"]
    )
    
    # Add custom instruction
    instruction_manager.add_custom_instruction(
        project_id=project_id,
        title="Use Redux for State Management",
        content="Use Redux Toolkit for complex state management. Create slices for different feature domains.",
        instruction_type=InstructionType.ARCHITECTURE,
        scope=InstructionScope.DIRECTORY,
        scope_target="src/store",
        priority=7,
        examples=["const userSlice = createSlice({ name: 'user', initialState, reducers: {...} })"],
        tags=["redux", "state-management"]
    )
    
    # Get contextual instructions
    contextual = instruction_manager.get_contextual_instructions(
        project_id, 
        current_file="src/components/UserProfile.tsx"
    )
    
    print(f"Found {len(contextual)} relevant instructions")
    
    # Generate summary
    summary = instruction_manager.generate_instruction_summary(project_id, "src/components/UserProfile.tsx")
    print("Instruction Summary:")
    print(summary)

if __name__ == "__main__":
    main()