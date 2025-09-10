"""
Aeonforge Project Manager - Isolated Project Contexts and Folder Management
Provides project-specific environments with dedicated instructions and context
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime
import fnmatch
import uuid

from .memory_system import MemorySystem, ProjectContext

@dataclass
class ProjectTemplate:
    """Project template definition"""
    id: str
    name: str
    description: str
    directory_structure: Dict[str, Any]
    default_files: Dict[str, str]  # filename -> content
    instructions: str
    custom_rules: List[str]
    required_tools: List[str]
    file_patterns: List[str]
    environment_variables: Dict[str, str]

@dataclass
class ProjectWorkspace:
    """Active project workspace"""
    project: ProjectContext
    active_files: Set[str]
    bookmarks: Dict[str, str]  # name -> file_path
    quick_commands: Dict[str, str]  # command -> action
    custom_snippets: Dict[str, str]  # trigger -> code
    file_watcher_patterns: List[str]
    last_build_time: Optional[datetime]
    dependencies: Dict[str, Any]

class ProjectManager:
    """Manages project contexts and isolated environments"""
    
    def __init__(self, data_dir: str = "memory_data", workspace_dir: str = "workspaces"):
        self.data_dir = Path(data_dir)
        self.workspace_dir = Path(workspace_dir)
        
        # Ensure directories exist
        self.data_dir.mkdir(exist_ok=True)
        self.workspace_dir.mkdir(exist_ok=True)
        
        # Memory system integration
        self.memory = MemorySystem(str(self.data_dir))
        
        # Project state
        self.current_workspace: Optional[ProjectWorkspace] = None
        self.project_templates: Dict[str, ProjectTemplate] = {}
        self.active_watchers: Dict[str, Any] = {}
        
        # Load built-in templates
        self._load_builtin_templates()
        
        # Load existing projects
        self._discover_existing_projects()
    
    def _load_builtin_templates(self):
        """Load built-in project templates"""
        
        # React TypeScript Project Template
        react_ts_template = ProjectTemplate(
            id="react-typescript",
            name="React TypeScript Project",
            description="Modern React project with TypeScript, Vite, and testing setup",
            directory_structure={
                "src": {
                    "components": {},
                    "hooks": {},
                    "services": {},
                    "types": {},
                    "utils": {},
                    "styles": {}
                },
                "public": {},
                "tests": {
                    "__mocks__": {},
                    "components": {},
                    "utils": {}
                },
                "docs": {}
            },
            default_files={
                "package.json": """{
  "name": "{{project_name}}",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "test": "vitest",
    "lint": "eslint src --ext ts,tsx",
    "type-check": "tsc --noEmit"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@vitejs/plugin-react": "^4.0.0",
    "typescript": "^5.0.0",
    "vite": "^4.4.0",
    "vitest": "^0.34.0"
  }
}""",
                "tsconfig.json": """{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}""",
                "vite.config.ts": """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
})""",
                "src/main.tsx": """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './styles/index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)""",
                "src/App.tsx": """import React from 'react'

function App() {
  return (
    <div className="App">
      <header>
        <h1>{{project_name}}</h1>
        <p>Welcome to your new React TypeScript project!</p>
      </header>
    </div>
  )
}

export default App""",
                ".gitignore": """node_modules
dist
.env.local
.env.development.local
.env.test.local
.env.production.local
npm-debug.log*
yarn-debug.log*
yarn-error.log*"""
            },
            instructions="""This is a React TypeScript project. Follow these guidelines:

1. Use functional components with hooks
2. Implement proper TypeScript typing for all props and state
3. Use CSS modules or styled-components for styling
4. Write tests for all components using Vitest and React Testing Library
5. Follow React best practices for component composition
6. Use custom hooks for reusable logic
7. Implement proper error boundaries
8. Use React.memo for performance optimization when needed""",
            custom_rules=[
                "Always use TypeScript strict mode",
                "Prefer composition over inheritance",
                "Use meaningful component and variable names",
                "Implement accessibility features",
                "Write comprehensive unit tests",
                "Use ESLint and Prettier for code formatting",
                "Follow React Hooks rules",
                "Optimize bundle size and performance"
            ],
            required_tools=["npm", "typescript", "vite"],
            file_patterns=["*.tsx", "*.ts", "*.css", "*.json"],
            environment_variables={"NODE_ENV": "development"}
        )
        
        # Python FastAPI Project Template
        python_api_template = ProjectTemplate(
            id="python-fastapi",
            name="Python FastAPI Project",
            description="FastAPI project with async support, database integration, and testing",
            directory_structure={
                "app": {
                    "api": {
                        "endpoints": {},
                        "dependencies": {}
                    },
                    "core": {},
                    "models": {},
                    "services": {},
                    "utils": {}
                },
                "tests": {
                    "api": {},
                    "services": {},
                    "utils": {}
                },
                "docs": {},
                "scripts": {}
            },
            default_files={
                "requirements.txt": """fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
sqlalchemy==2.0.23
alembic==1.13.1
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2""",
                "app/main.py": """from fastapi import FastAPI
from app.api.endpoints import router
from app.core.config import settings

app = FastAPI(
    title="{{project_name}}",
    description="API for {{project_name}}",
    version="1.0.0"
)

app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to {{project_name}} API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)""",
                "app/core/config.py": """from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "{{project_name}}"
    debug: bool = False
    database_url: str = "sqlite:///./app.db"
    
    class Config:
        env_file = ".env"

settings = Settings()""",
                ".gitignore": """__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
.env
.pytest_cache/
*.db
.coverage"""
            },
            instructions="""This is a FastAPI Python project. Follow these guidelines:

1. Use async/await for all database and external API calls
2. Implement proper Pydantic models for request/response validation
3. Use dependency injection for database sessions and authentication
4. Write comprehensive tests with pytest and httpx
5. Follow RESTful API design principles
6. Implement proper error handling and logging
7. Use SQLAlchemy for database operations
8. Implement API versioning and documentation""",
            custom_rules=[
                "Use type hints for all functions and variables",
                "Follow PEP 8 style guidelines",
                "Use async database operations",
                "Implement proper exception handling",
                "Write docstrings for all functions and classes",
                "Use environment variables for configuration",
                "Implement request/response logging",
                "Use proper HTTP status codes"
            ],
            required_tools=["python", "pip", "uvicorn"],
            file_patterns=["*.py", "*.pyi", "*.json", "*.yaml", "*.yml"],
            environment_variables={"PYTHONPATH": ".", "DEBUG": "true"}
        )
        
        self.project_templates = {
            react_ts_template.id: react_ts_template,
            python_api_template.id: python_api_template
        }
    
    def create_project_from_template(self, template_id: str, project_name: str, 
                                   base_path: str, custom_vars: Dict[str, str] = None) -> str:
        """Create a new project from template"""
        if template_id not in self.project_templates:
            raise ValueError(f"Template {template_id} not found")
        
        template = self.project_templates[template_id]
        project_path = Path(base_path) / project_name
        
        # Create project directory
        project_path.mkdir(parents=True, exist_ok=True)
        
        # Create directory structure
        self._create_directory_structure(project_path, template.directory_structure)
        
        # Create default files
        variables = {"project_name": project_name}
        if custom_vars:
            variables.update(custom_vars)
        
        for file_path, content in template.default_files.items():
            full_path = project_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Replace template variables
            processed_content = content
            for var, value in variables.items():
                processed_content = processed_content.replace(f"{{{{{var}}}}}", str(value))
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(processed_content)
        
        # Create project in memory system
        project_id = self.memory.create_project(
            name=project_name,
            base_path=str(project_path),
            description=f"Project created from template: {template.name}",
            instructions=template.instructions,
            custom_rules=template.custom_rules,
            file_patterns=template.file_patterns
        )
        
        # Create workspace configuration
        workspace_config = {
            "template_id": template_id,
            "environment_variables": template.environment_variables,
            "required_tools": template.required_tools,
            "bookmarks": {},
            "quick_commands": self._get_default_commands(template),
            "custom_snippets": {}
        }
        
        workspace_config_path = project_path / ".aeonforge" / "workspace.json"
        workspace_config_path.parent.mkdir(exist_ok=True)
        
        with open(workspace_config_path, 'w') as f:
            json.dump(workspace_config, f, indent=2)
        
        return project_id
    
    def _create_directory_structure(self, base_path: Path, structure: Dict[str, Any]):
        """Recursively create directory structure"""
        for name, contents in structure.items():
            dir_path = base_path / name
            dir_path.mkdir(exist_ok=True)
            
            if isinstance(contents, dict) and contents:
                self._create_directory_structure(dir_path, contents)
    
    def _get_default_commands(self, template: ProjectTemplate) -> Dict[str, str]:
        """Get default quick commands for template"""
        commands = {}
        
        if template.id == "react-typescript":
            commands = {
                "dev": "npm run dev",
                "build": "npm run build",
                "test": "npm run test",
                "lint": "npm run lint",
                "install": "npm install"
            }
        elif template.id == "python-fastapi":
            commands = {
                "dev": "uvicorn app.main:app --reload",
                "test": "pytest",
                "install": "pip install -r requirements.txt",
                "migrate": "alembic upgrade head",
                "shell": "python -m app.main"
            }
        
        return commands
    
    def load_project_workspace(self, project_id: str) -> Optional[ProjectWorkspace]:
        """Load project workspace"""
        project = self.memory._load_project(project_id)
        if not project:
            return None
        
        workspace_config_path = Path(project.base_path) / ".aeonforge" / "workspace.json"
        workspace_config = {}
        
        if workspace_config_path.exists():
            with open(workspace_config_path, 'r') as f:
                workspace_config = json.load(f)
        
        workspace = ProjectWorkspace(
            project=project,
            active_files=set(),
            bookmarks=workspace_config.get('bookmarks', {}),
            quick_commands=workspace_config.get('quick_commands', {}),
            custom_snippets=workspace_config.get('custom_snippets', {}),
            file_watcher_patterns=workspace_config.get('file_watcher_patterns', ['**/*.py', '**/*.ts', '**/*.tsx']),
            last_build_time=None,
            dependencies=workspace_config.get('dependencies', {})
        )
        
        return workspace
    
    def switch_to_project(self, project_id: str) -> bool:
        """Switch to project workspace"""
        workspace = self.load_project_workspace(project_id)
        if not workspace:
            return False
        
        # Switch memory system to project
        self.memory.switch_to_project(project_id)
        
        # Set current workspace
        self.current_workspace = workspace
        
        # Change working directory
        os.chdir(workspace.project.base_path)
        
        # Set environment variables
        workspace_config_path = Path(workspace.project.base_path) / ".aeonforge" / "workspace.json"
        if workspace_config_path.exists():
            with open(workspace_config_path, 'r') as f:
                config = json.load(f)
                env_vars = config.get('environment_variables', {})
                for key, value in env_vars.items():
                    os.environ[key] = value
        
        return True
    
    def get_project_context(self) -> Dict[str, Any]:
        """Get current project context"""
        if not self.current_workspace:
            return {}
        
        project = self.current_workspace.project
        
        # Get project files
        project_files = self._scan_project_files(project.base_path, project.file_patterns)
        
        # Get recent activity
        memory_context = self.memory.get_context_for_current_session()
        
        return {
            'project': {
                'id': project.id,
                'name': project.name,
                'description': project.description,
                'path': project.base_path,
                'instructions': project.instructions,
                'custom_rules': project.custom_rules,
                'file_count': len(project_files)
            },
            'workspace': {
                'active_files': list(self.current_workspace.active_files),
                'bookmarks': self.current_workspace.bookmarks,
                'quick_commands': self.current_workspace.quick_commands,
                'custom_snippets': self.current_workspace.custom_snippets
            },
            'memory_context': memory_context,
            'project_files': project_files[:50]  # Limit for performance
        }
    
    def _scan_project_files(self, base_path: str, patterns: List[str]) -> List[str]:
        """Scan project files matching patterns"""
        base = Path(base_path)
        files = []
        
        for pattern in patterns:
            for file_path in base.rglob(pattern):
                if file_path.is_file() and not self._should_ignore_file(file_path):
                    relative_path = str(file_path.relative_to(base))
                    files.append(relative_path)
        
        return sorted(files)
    
    def _should_ignore_file(self, file_path: Path) -> bool:
        """Check if file should be ignored"""
        ignore_patterns = [
            "node_modules/**",
            ".git/**",
            "__pycache__/**",
            "*.pyc",
            ".pytest_cache/**",
            "dist/**",
            "build/**",
            ".venv/**",
            "venv/**"
        ]
        
        for pattern in ignore_patterns:
            if fnmatch.fnmatch(str(file_path), pattern):
                return True
        
        return False
    
    def add_bookmark(self, name: str, file_path: str) -> bool:
        """Add file bookmark"""
        if not self.current_workspace:
            return False
        
        self.current_workspace.bookmarks[name] = file_path
        self._save_workspace_config()
        return True
    
    def add_quick_command(self, name: str, command: str) -> bool:
        """Add quick command"""
        if not self.current_workspace:
            return False
        
        self.current_workspace.quick_commands[name] = command
        self._save_workspace_config()
        return True
    
    def add_code_snippet(self, trigger: str, code: str) -> bool:
        """Add custom code snippet"""
        if not self.current_workspace:
            return False
        
        self.current_workspace.custom_snippets[trigger] = code
        self._save_workspace_config()
        return True
    
    def _save_workspace_config(self):
        """Save workspace configuration"""
        if not self.current_workspace:
            return
        
        workspace_config = {
            "bookmarks": self.current_workspace.bookmarks,
            "quick_commands": self.current_workspace.quick_commands,
            "custom_snippets": self.current_workspace.custom_snippets,
            "file_watcher_patterns": self.current_workspace.file_watcher_patterns,
            "dependencies": self.current_workspace.dependencies
        }
        
        config_path = Path(self.current_workspace.project.base_path) / ".aeonforge" / "workspace.json"
        config_path.parent.mkdir(exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(workspace_config, f, indent=2)
    
    def _discover_existing_projects(self):
        """Discover existing projects with .aeonforge directories"""
        # This would scan common project locations for existing Aeonforge projects
        pass
    
    def get_available_templates(self) -> List[Dict[str, Any]]:
        """Get list of available project templates"""
        return [
            {
                'id': template.id,
                'name': template.name,
                'description': template.description,
                'required_tools': template.required_tools,
                'file_patterns': template.file_patterns
            }
            for template in self.project_templates.values()
        ]
    
    def clone_project_from_git(self, git_url: str, project_name: str, base_path: str) -> Optional[str]:
        """Clone project from Git and set up Aeonforge workspace"""
        try:
            import subprocess
            
            project_path = Path(base_path) / project_name
            
            # Clone repository
            subprocess.run(['git', 'clone', git_url, str(project_path)], check=True)
            
            # Auto-detect project type and set up workspace
            template_id = self._detect_project_type(project_path)
            
            # Create project in memory system
            project_id = self.memory.create_project(
                name=project_name,
                base_path=str(project_path),
                description=f"Cloned from {git_url}",
                instructions="Follow the project's existing conventions and README instructions.",
                file_patterns=["**/*"]
            )
            
            # Create workspace configuration
            workspace_config = {
                "template_id": template_id,
                "git_url": git_url,
                "bookmarks": {},
                "quick_commands": self._detect_project_commands(project_path),
                "custom_snippets": {}
            }
            
            workspace_config_path = project_path / ".aeonforge" / "workspace.json"
            workspace_config_path.parent.mkdir(exist_ok=True)
            
            with open(workspace_config_path, 'w') as f:
                json.dump(workspace_config, f, indent=2)
            
            return project_id
        
        except Exception as e:
            print(f"Failed to clone project: {e}")
            return None
    
    def _detect_project_type(self, project_path: Path) -> Optional[str]:
        """Auto-detect project type from files"""
        if (project_path / "package.json").exists():
            package_json_path = project_path / "package.json"
            with open(package_json_path) as f:
                package_data = json.load(f)
                if "react" in package_data.get("dependencies", {}):
                    return "react-typescript"
        
        if (project_path / "requirements.txt").exists() or (project_path / "pyproject.toml").exists():
            # Check for FastAPI
            for file_path in project_path.rglob("*.py"):
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(1000)  # Read first 1000 chars
                    if "fastapi" in content.lower():
                        return "python-fastapi"
        
        return None
    
    def _detect_project_commands(self, project_path: Path) -> Dict[str, str]:
        """Detect common project commands"""
        commands = {}
        
        if (project_path / "package.json").exists():
            with open(project_path / "package.json") as f:
                package_data = json.load(f)
                scripts = package_data.get("scripts", {})
                for script_name, script_command in scripts.items():
                    commands[script_name] = f"npm run {script_name}"
        
        if (project_path / "Makefile").exists():
            # Parse Makefile for targets (simplified)
            commands["make"] = "make"
        
        if (project_path / "requirements.txt").exists():
            commands["install"] = "pip install -r requirements.txt"
        
        return commands

def main():
    """Test the project manager"""
    manager = ProjectManager()
    
    # List available templates
    templates = manager.get_available_templates()
    print("Available templates:")
    for template in templates:
        print(f"  - {template['name']}: {template['description']}")
    
    # Create a project from template
    project_id = manager.create_project_from_template(
        template_id="react-typescript",
        project_name="my-react-app",
        base_path="./test_projects"
    )
    
    print(f"Created project with ID: {project_id}")
    
    # Switch to project
    if manager.switch_to_project(project_id):
        print("Switched to project successfully")
        
        # Get project context
        context = manager.get_project_context()
        print(f"Project context: {context['project']['name']}")
        print(f"Available commands: {list(context['workspace']['quick_commands'].keys())}")

if __name__ == "__main__":
    main()