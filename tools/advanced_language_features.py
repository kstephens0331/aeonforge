"""
Advanced Language Features for Aeonforge Phase 5
Complete implementations for code formatting, advanced refactoring, and framework intelligence
"""

import os
import json
import ast
import re
import subprocess
import tempfile
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging
from multi_language_tools import BaseHandler, CodeAnalysis, CodeGeneration

@dataclass
class CodeMetrics:
    """Advanced code metrics"""
    cyclomatic_complexity: int
    maintainability_index: float
    lines_of_code: int
    lines_of_comments: int
    cognitive_complexity: int
    technical_debt_ratio: float
    duplication_percentage: float
    test_coverage: float

@dataclass
class RefactoringResult:
    """Result of advanced refactoring operation"""
    success: bool
    original_code: str
    refactored_code: str
    changes_made: List[str]
    estimated_time_saved: str
    risk_level: str
    rollback_instructions: List[str]

@dataclass
class FrameworkAnalysis:
    """Framework-specific analysis"""
    framework_name: str
    version: Optional[str]
    components: List[str]
    patterns_used: List[str]
    best_practices_violations: List[str]
    security_issues: List[str]
    performance_opportunities: List[str]

class AdvancedPythonHandler(BaseHandler):
    """Advanced Python handler with complete AST analysis"""
    
    def __init__(self):
        super().__init__('python', ['.py', '.pyw'], 'python')
    
    def analyze_code(self, code: str, file_path: str = None) -> CodeAnalysis:
        """Advanced Python code analysis using AST"""
        try:
            tree = ast.parse(code)
            
            # Basic analysis
            functions = []
            classes = []
            imports = []
            decorators = []
            async_functions = []
            comprehensions = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append({
                        'name': node.name,
                        'line': node.lineno,
                        'args': [arg.arg for arg in node.args.args],
                        'decorators': [self._get_decorator_name(d) for d in node.decorator_list],
                        'is_async': False,
                        'returns': ast.unparse(node.returns) if node.returns else None
                    })
                elif isinstance(node, ast.AsyncFunctionDef):
                    async_functions.append({
                        'name': node.name,
                        'line': node.lineno,
                        'is_async': True
                    })
                elif isinstance(node, ast.ClassDef):
                    classes.append({
                        'name': node.name,
                        'line': node.lineno,
                        'bases': [ast.unparse(base) for base in node.bases],
                        'decorators': [self._get_decorator_name(d) for d in node.decorator_list],
                        'methods': self._extract_class_methods(node)
                    })
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    imports.extend(self._extract_imports(node))
                elif isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
                    comprehensions.append({
                        'type': type(node).__name__,
                        'line': node.lineno
                    })
            
            # Calculate advanced metrics
            complexity = self._calculate_cyclomatic_complexity(tree)
            maintainability = self._calculate_maintainability_index(code, complexity)
            
            return CodeAnalysis(
                language='python',
                syntax_valid=True,
                errors=[],
                warnings=self._generate_warnings(tree, code),
                complexity_score=complexity,
                functions=[f['name'] for f in functions],
                classes=[c['name'] for c in classes],
                imports=imports,
                dependencies=self._extract_dependencies(imports),
                suggestions=self._generate_advanced_suggestions(tree, code),
                structure={
                    'functions': functions,
                    'classes': classes,
                    'async_functions': async_functions,
                    'comprehensions': comprehensions,
                    'decorators': decorators,
                    'metrics': {
                        'cyclomatic_complexity': complexity,
                        'maintainability_index': maintainability,
                        'lines_of_code': len([l for l in code.split('\n') if l.strip()]),
                        'lines_of_comments': len([l for l in code.split('\n') if l.strip().startswith('#')])
                    }
                }
            )
            
        except SyntaxError as e:
            return CodeAnalysis(
                language='python',
                syntax_valid=False,
                errors=[f"Syntax error at line {e.lineno}: {e.msg}"],
                warnings=[],
                complexity_score=0,
                functions=[],
                classes=[],
                imports=[],
                dependencies=[],
                suggestions=[],
                structure={}
            )
    
    def generate_code(self, description: str, context: Dict[str, Any] = None) -> CodeGeneration:
        """Advanced Python code generation with framework detection"""
        context = context or {}
        
        # Detect framework requirements
        framework = self._detect_framework_from_description(description)
        
        if framework == 'fastapi':
            return self._generate_fastapi_code(description, context)
        elif framework == 'django':
            return self._generate_django_code(description, context)
        elif framework == 'flask':
            return self._generate_flask_code(description, context)
        elif framework == 'data_science':
            return self._generate_data_science_code(description, context)
        else:
            return self._generate_generic_python_code(description, context)
    
    def format_code(self, code: str) -> str:
        """Format Python code using black"""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp:
                tmp.write(code)
                tmp_path = tmp.name
            
            result = subprocess.run(
                ['black', '--quiet', '--code', code],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                # Fallback to basic formatting
                return self._basic_python_formatting(code)
                
        except (subprocess.CalledProcessError, FileNotFoundError):
            return self._basic_python_formatting(code)
    
    def advanced_refactor(self, code: str, refactor_type: str, **kwargs) -> RefactoringResult:
        """Advanced Python refactoring"""
        try:
            if refactor_type == 'extract_method':
                return self._extract_method(code, kwargs.get('start_line'), kwargs.get('end_line'))
            elif refactor_type == 'rename_variable':
                return self._rename_variable(code, kwargs.get('old_name'), kwargs.get('new_name'))
            elif refactor_type == 'add_type_hints':
                return self._add_type_hints(code)
            elif refactor_type == 'convert_to_async':
                return self._convert_to_async(code, kwargs.get('function_name'))
            elif refactor_type == 'optimize_imports':
                return self._optimize_imports(code)
            else:
                return RefactoringResult(
                    success=False,
                    original_code=code,
                    refactored_code=code,
                    changes_made=[],
                    estimated_time_saved="0 minutes",
                    risk_level="none",
                    rollback_instructions=[]
                )
        except Exception as e:
            return RefactoringResult(
                success=False,
                original_code=code,
                refactored_code=code,
                changes_made=[f"Error: {str(e)}"],
                estimated_time_saved="0 minutes",
                risk_level="high",
                rollback_instructions=[]
            )
    
    def analyze_framework(self, code: str) -> FrameworkAnalysis:
        """Analyze Python framework usage"""
        frameworks = {
            'django': ['django', 'from django', 'models.Model', 'views.View'],
            'flask': ['from flask', 'Flask', '@app.route', 'request.'],
            'fastapi': ['from fastapi', 'FastAPI', '@app.get', '@app.post'],
            'pandas': ['import pandas', 'pd.DataFrame', 'pd.read_'],
            'numpy': ['import numpy', 'np.array', 'np.'],
            'tensorflow': ['import tensorflow', 'tf.', 'keras'],
            'pytorch': ['import torch', 'torch.', 'nn.Module']
        }
        
        detected_framework = None
        confidence = 0
        
        for framework, patterns in frameworks.items():
            matches = sum(1 for pattern in patterns if pattern in code)
            if matches > confidence:
                confidence = matches
                detected_framework = framework
        
        if detected_framework:
            return self._analyze_specific_framework(code, detected_framework)
        else:
            return FrameworkAnalysis(
                framework_name="none",
                version=None,
                components=[],
                patterns_used=[],
                best_practices_violations=[],
                security_issues=[],
                performance_opportunities=[]
            )
    
    # Helper methods for advanced Python analysis
    def _get_decorator_name(self, decorator):
        """Extract decorator name"""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return ast.unparse(decorator)
        elif isinstance(decorator, ast.Call):
            return ast.unparse(decorator.func)
        return str(decorator)
    
    def _extract_class_methods(self, class_node):
        """Extract methods from class"""
        methods = []
        for node in class_node.body:
            if isinstance(node, ast.FunctionDef):
                methods.append({
                    'name': node.name,
                    'line': node.lineno,
                    'is_property': any(self._get_decorator_name(d) == 'property' for d in node.decorator_list),
                    'is_static': any(self._get_decorator_name(d) == 'staticmethod' for d in node.decorator_list),
                    'is_class': any(self._get_decorator_name(d) == 'classmethod' for d in node.decorator_list)
                })
        return methods
    
    def _extract_imports(self, node):
        """Extract import information"""
        imports = []
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ''
            for alias in node.names:
                imports.append(f"{module}.{alias.name}" if module else alias.name)
        return imports
    
    def _extract_dependencies(self, imports: List[str]) -> List[str]:
        """Extract package dependencies from imports"""
        dependencies = []
        for import_item in imports:
            # Extract top-level package name
            if '.' in import_item:
                dependencies.append(import_item.split('.')[0])
            else:
                dependencies.append(import_item)
        return list(set(dependencies))  # Remove duplicates
    
    def _calculate_cyclomatic_complexity(self, tree):
        """Calculate cyclomatic complexity"""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, ast.With):
                complexity += 1
            elif isinstance(node, ast.Assert):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        
        return complexity
    
    def _calculate_maintainability_index(self, code: str, complexity: int) -> float:
        """Calculate maintainability index"""
        lines_of_code = len([l for l in code.split('\n') if l.strip()])
        halstead_volume = lines_of_code * 1.5  # Simplified calculation
        
        # Maintainability Index formula (simplified)
        mi = max(0, (171 - 5.2 * math.log(halstead_volume) - 0.23 * complexity - 16.2 * math.log(lines_of_code)) * 100 / 171)
        return round(mi, 2)
    
    def _generate_warnings(self, tree, code: str) -> List[str]:
        """Generate code warnings"""
        warnings = []
        
        # Check for potential issues
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler) and not node.type:
                warnings.append(f"Line {node.lineno}: Bare except clause - specify exception type")
            elif isinstance(node, ast.Global):
                warnings.append(f"Line {node.lineno}: Global variable usage - consider alternatives")
            elif isinstance(node, ast.Lambda):
                warnings.append(f"Line {node.lineno}: Lambda function - consider named function for readability")
        
        # Check for long lines
        for i, line in enumerate(code.split('\n'), 1):
            if len(line) > 100:
                warnings.append(f"Line {i}: Line too long ({len(line)} chars)")
        
        return warnings
    
    def _generate_advanced_suggestions(self, tree, code: str) -> List[str]:
        """Generate advanced improvement suggestions"""
        suggestions = []
        
        # Analyze patterns
        function_count = len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)])
        class_count = len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)])
        
        if function_count > 10 and class_count == 0:
            suggestions.append("Consider organizing functions into classes for better structure")
        
        # Check for modern Python features
        if 'f"' not in code and 'format(' in code:
            suggestions.append("Consider using f-strings for better readability and performance")
        
        if 'typing' not in code and function_count > 3:
            suggestions.append("Add type hints to improve code documentation and IDE support")
        
        return suggestions
    
    def debug_code(self, code: str, error_message: str = None) -> List[str]:
        """Debug code and suggest fixes"""
        suggestions = []
        
        if error_message:
            if 'ModuleNotFoundError' in error_message:
                module = error_message.split("'")[1] if "'" in error_message else "unknown"
                suggestions.append(f"Install missing module: pip install {module}")
            elif 'SyntaxError' in error_message:
                suggestions.append("Check for missing colons, parentheses, or indentation issues")
            elif 'IndentationError' in error_message:
                suggestions.append("Fix indentation - use consistent spaces or tabs")
            elif 'NameError' in error_message:
                suggestions.append("Check for undefined variables or typos in variable names")
        
        try:
            ast.parse(code)
        except SyntaxError as e:
            suggestions.append(f"Syntax error at line {e.lineno}: {e.msg}")
        
        return suggestions
    
    def refactor_code(self, code: str, instructions: str) -> str:
        """Basic refactoring - use advanced_refactor for more complex operations"""
        if 'add type hints' in instructions.lower():
            return self.advanced_refactor(code, 'add_type_hints').refactored_code
        elif 'add docstrings' in instructions.lower():
            lines = code.split('\n')
            result = []
            for i, line in enumerate(lines):
                result.append(line)
                if line.strip().startswith('def ') or line.strip().startswith('class '):
                    result.append('    """TODO: Add docstring"""')
            return '\n'.join(result)
        return code
    
    def run_code(self, code: str, input_data: str = None) -> Tuple[str, str, int]:
        """Execute Python code"""
        temp_file = self._create_temp_file(code, '.py')
        try:
            return self._run_command(['python', temp_file], input_data)
        finally:
            os.unlink(temp_file)
    
    def _detect_framework_from_description(self, description: str) -> str:
        """Detect framework from description"""
        desc_lower = description.lower()
        
        if any(word in desc_lower for word in ['api', 'rest', 'endpoint', 'fastapi']):
            return 'fastapi'
        elif any(word in desc_lower for word in ['web app', 'django', 'models']):
            return 'django'
        elif any(word in desc_lower for word in ['flask', 'web server']):
            return 'flask'
        elif any(word in desc_lower for word in ['data', 'analysis', 'pandas', 'numpy', 'ml', 'machine learning']):
            return 'data_science'
        else:
            return 'generic'
    
    def _generate_fastapi_code(self, description: str, context: Dict[str, Any]) -> CodeGeneration:
        """Generate FastAPI application code"""
        code = f'''from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI(title="{description}", version="1.0.0")

class Item(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None

# In-memory storage (replace with database)
items = []

@app.get("/")
async def read_root():
    """Root endpoint"""
    return {{"message": "Welcome to {description}"}}

@app.get("/items", response_model=List[Item])
async def get_items():
    """Get all items"""
    return items

@app.get("/items/{{item_id}}", response_model=Item)
async def get_item(item_id: int):
    """Get item by ID"""
    for item in items:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")

@app.post("/items", response_model=Item)
async def create_item(item: Item):
    """Create new item"""
    item.id = len(items) + 1
    items.append(item)
    return item

@app.put("/items/{{item_id}}", response_model=Item)
async def update_item(item_id: int, updated_item: Item):
    """Update existing item"""
    for i, item in enumerate(items):
        if item.id == item_id:
            updated_item.id = item_id
            items[i] = updated_item
            return updated_item
    raise HTTPException(status_code=404, detail="Item not found")

@app.delete("/items/{{item_id}}")
async def delete_item(item_id: int):
    """Delete item"""
    for i, item in enumerate(items):
        if item.id == item_id:
            del items[i]
            return {{"message": "Item deleted successfully"}}
    raise HTTPException(status_code=404, detail="Item not found")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
        
        return CodeGeneration(
            language='python',
            code=code,
            files={
                'main.py': code,
                'requirements.txt': 'fastapi>=0.68.0\nuvicorn[standard]>=0.15.0\npydantic>=1.8.0',
                'Dockerfile': '''FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]'''
            },
            tests={
                'test_main.py': '''import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_create_item():
    item_data = {"name": "Test Item", "description": "Test Description"}
    response = client.post("/items", json=item_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Test Item"'''
            },
            documentation=f"# {description}\n\nFastAPI REST API with CRUD operations\n\n## Features\n- RESTful API endpoints\n- Pydantic models for validation\n- Automatic OpenAPI documentation\n- Type hints throughout\n\n## Usage\n```bash\npip install -r requirements.txt\npython main.py\n```\n\nAPI documentation available at: http://localhost:8000/docs",
            build_commands=['pip install -r requirements.txt'],
            run_commands=['python main.py']
        )
    
    def _generate_data_science_code(self, description: str, context: Dict[str, Any]) -> CodeGeneration:
        """Generate data science code"""
        code = f'''import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import warnings
warnings.filterwarnings('ignore')

# Set style for plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class DataAnalyzer:
    """Data analysis and machine learning pipeline"""
    
    def __init__(self):
        self.data = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.model = None
        self.scaler = StandardScaler()
    
    def load_data(self, file_path: str, target_column: str = None):
        """Load data from CSV file"""
        try:
            self.data = pd.read_csv(file_path)
            print(f"Data loaded successfully! Shape: {{self.data.shape}}")
            self.display_info()
            
            if target_column and target_column in self.data.columns:
                self.prepare_features(target_column)
                
        except Exception as e:
            print(f"Error loading data: {{e}}")
    
    def display_info(self):
        """Display basic information about the dataset"""
        print("\\n=== Dataset Information ===")
        print(f"Shape: {{self.data.shape}}")
        print(f"Columns: {{list(self.data.columns)}}")
        print("\\n=== Data Types ===")
        print(self.data.dtypes)
        print("\\n=== Missing Values ===")
        print(self.data.isnull().sum())
        print("\\n=== Basic Statistics ===")
        print(self.data.describe())
    
    def prepare_features(self, target_column: str):
        """Prepare features for machine learning"""
        # Separate features and target
        X = self.data.drop(columns=[target_column])
        y = self.data[target_column]
        
        # Handle categorical variables
        X = pd.get_dummies(X, drop_first=True)
        
        # Split the data
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        self.X_train = self.scaler.fit_transform(self.X_train)
        self.X_test = self.scaler.transform(self.X_test)
        
        print(f"Features prepared! Training set: {{self.X_train.shape}}")
    
    def explore_data(self):
        """Create exploratory data analysis plots"""
        if self.data is None:
            print("Please load data first!")
            return
        
        # Create subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Exploratory Data Analysis', fontsize=16)
        
        # Distribution of numeric columns
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns[:4]
        for i, col in enumerate(numeric_cols):
            if i < 4:
                row, col_idx = i // 2, i % 2
                axes[row, col_idx].hist(self.data[col], bins=30, alpha=0.7)
                axes[row, col_idx].set_title(f'Distribution of {{col}}')
                axes[row, col_idx].set_xlabel(col)
                axes[row, col_idx].set_ylabel('Frequency')
        
        plt.tight_layout()
        plt.show()
        
        # Correlation heatmap
        if len(numeric_cols) > 1:
            plt.figure(figsize=(10, 8))
            correlation_matrix = self.data[numeric_cols].corr()
            sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0)
            plt.title('Feature Correlation Heatmap')
            plt.show()
    
    def train_model(self, model_type='classification'):
        """Train a machine learning model"""
        if self.X_train is None:
            print("Please prepare features first!")
            return
        
        if model_type == 'classification':
            from sklearn.ensemble import RandomForestClassifier
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        else:
            from sklearn.ensemble import RandomForestRegressor
            self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        
        # Train the model
        self.model.fit(self.X_train, self.y_train)
        
        # Make predictions
        y_pred = self.model.predict(self.X_test)
        
        # Evaluate
        if model_type == 'classification':
            accuracy = accuracy_score(self.y_test, y_pred)
            print(f"Model Accuracy: {{accuracy:.4f}}")
            print("\\nClassification Report:")
            print(classification_report(self.y_test, y_pred))
        else:
            from sklearn.metrics import mean_squared_error, r2_score
            mse = mean_squared_error(self.y_test, y_pred)
            r2 = r2_score(self.y_test, y_pred)
            print(f"Mean Squared Error: {{mse:.4f}}")
            print(f"R² Score: {{r2:.4f}}")
    
    def generate_insights(self):
        """Generate insights from the analysis"""
        insights = []
        
        if self.data is not None:
            insights.append(f"Dataset contains {{self.data.shape[0]}} rows and {{self.data.shape[1]}} columns")
            
            # Missing data insights
            missing_cols = self.data.isnull().sum()
            missing_cols = missing_cols[missing_cols > 0]
            if len(missing_cols) > 0:
                insights.append(f"{{len(missing_cols)}} columns have missing values")
            
            # Data type insights
            numeric_cols = len(self.data.select_dtypes(include=[np.number]).columns)
            categorical_cols = len(self.data.select_dtypes(exclude=[np.number]).columns)
            insights.append(f"{{numeric_cols}} numeric columns, {{categorical_cols}} categorical columns")
        
        return insights

def main():
    """Main analysis pipeline"""
    print("🔍 {description}")
    print("=" * 50)
    
    # Initialize analyzer
    analyzer = DataAnalyzer()
    
    # Example usage (uncomment and modify as needed)
    # analyzer.load_data('your_data.csv', 'target_column')
    # analyzer.explore_data()
    # analyzer.train_model('classification')
    
    print("\\n✅ Data analysis pipeline ready!")
    print("Modify the main() function to load your specific dataset.")

if __name__ == "__main__":
    main()
'''
        
        return CodeGeneration(
            language='python',
            code=code,
            files={
                'data_analyzer.py': code,
                'requirements.txt': '''pandas>=1.3.0
numpy>=1.21.0
matplotlib>=3.4.0
seaborn>=0.11.0
scikit-learn>=1.0.0
jupyter>=1.0.0''',
                'README.md': f'''# {description}

Advanced data analysis and machine learning pipeline.

## Features
- Data loading and preprocessing
- Exploratory data analysis with visualizations
- Machine learning model training and evaluation
- Automated insights generation
- Clean, modular code structure

## Quick Start
```python
from data_analyzer import DataAnalyzer

# Initialize analyzer
analyzer = DataAnalyzer()

# Load your data
analyzer.load_data('your_data.csv', 'target_column')

# Explore the data
analyzer.explore_data()

# Train a model
analyzer.train_model('classification')
```

## Installation
```bash
pip install -r requirements.txt
```
'''
            },
            tests={
                'test_analyzer.py': '''import pytest
import pandas as pd
import numpy as np
from data_analyzer import DataAnalyzer

def test_data_analyzer_initialization():
    analyzer = DataAnalyzer()
    assert analyzer.data is None
    assert analyzer.model is None

def test_data_loading():
    # Create sample data
    sample_data = pd.DataFrame({
        'feature1': np.random.normal(0, 1, 100),
        'feature2': np.random.normal(0, 1, 100),
        'target': np.random.choice([0, 1], 100)
    })
    
    analyzer = DataAnalyzer()
    analyzer.data = sample_data
    
    assert analyzer.data.shape == (100, 3)
    assert 'target' in analyzer.data.columns'''
            },
            documentation=f"# {description}\n\nComprehensive data science pipeline with machine learning capabilities.",
            build_commands=['pip install -r requirements.txt'],
            run_commands=['python data_analyzer.py']
        )
    
    # Implementation of missing refactoring methods
    def _extract_method(self, code: str, start_line: int, end_line: int) -> RefactoringResult:
        """Extract method refactoring"""
        lines = code.split('\n')
        if not start_line or not end_line or start_line >= end_line:
            return RefactoringResult(
                success=False,
                original_code=code,
                refactored_code=code,
                changes_made=["Invalid line range specified"],
                estimated_time_saved="0 minutes",
                risk_level="none",
                rollback_instructions=[]
            )
        
        # Simple extraction - extract lines to new method
        extracted_lines = lines[start_line-1:end_line]
        method_name = "extracted_method"
        new_method = f"\ndef {method_name}():\n    " + "\n    ".join(extracted_lines) + "\n"
        
        # Replace original lines with method call
        lines[start_line-1:end_line] = [f"    {method_name}()"]
        
        # Insert new method before the first function or at the end
        insertion_point = len(lines)
        for i, line in enumerate(lines):
            if line.strip().startswith('def ') or line.strip().startswith('class '):
                insertion_point = i
                break
        
        lines.insert(insertion_point, new_method)
        refactored_code = '\n'.join(lines)
        
        return RefactoringResult(
            success=True,
            original_code=code,
            refactored_code=refactored_code,
            changes_made=[f"Extracted lines {start_line}-{end_line} to method {method_name}"],
            estimated_time_saved="5 minutes",
            risk_level="low",
            rollback_instructions=["Inline the extracted method manually"]
        )
    
    def _rename_variable(self, code: str, old_name: str, new_name: str) -> RefactoringResult:
        """Rename variable refactoring"""
        if not old_name or not new_name:
            return RefactoringResult(
                success=False,
                original_code=code,
                refactored_code=code,
                changes_made=["Old name and new name must be provided"],
                estimated_time_saved="0 minutes",
                risk_level="none",
                rollback_instructions=[]
            )
        
        # Simple find and replace (would need more sophisticated AST-based approach for production)
        import re
        pattern = r'\b' + re.escape(old_name) + r'\b'
        refactored_code = re.sub(pattern, new_name, code)
        
        changes_count = len(re.findall(pattern, code))
        
        return RefactoringResult(
            success=True,
            original_code=code,
            refactored_code=refactored_code,
            changes_made=[f"Renamed {changes_count} occurrences of '{old_name}' to '{new_name}'"],
            estimated_time_saved="2 minutes",
            risk_level="low",
            rollback_instructions=[f"Rename '{new_name}' back to '{old_name}'"]
        )
    
    def _add_type_hints(self, code: str) -> RefactoringResult:
        """Add type hints to functions"""
        try:
            tree = ast.parse(code)
            lines = code.split('\n')
            changes_made = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and not node.returns:
                    # Simple type hint addition - add -> None for functions without return annotation
                    line_idx = node.lineno - 1
                    if line_idx < len(lines):
                        line = lines[line_idx]
                        if ' -> ' not in line and line.strip().endswith(':'):
                            lines[line_idx] = line.replace(':', ' -> None:')
                            changes_made.append(f"Added return type hint to function '{node.name}'")
            
            refactored_code = '\n'.join(lines)
            
            return RefactoringResult(
                success=True,
                original_code=code,
                refactored_code=refactored_code,
                changes_made=changes_made,
                estimated_time_saved="10 minutes",
                risk_level="low",
                rollback_instructions=["Remove '-> None' annotations manually"]
            )
            
        except SyntaxError:
            return RefactoringResult(
                success=False,
                original_code=code,
                refactored_code=code,
                changes_made=["Cannot add type hints to code with syntax errors"],
                estimated_time_saved="0 minutes",
                risk_level="none",
                rollback_instructions=[]
            )
    
    def _convert_to_async(self, code: str, function_name: str) -> RefactoringResult:
        """Convert function to async"""
        if not function_name:
            return RefactoringResult(
                success=False,
                original_code=code,
                refactored_code=code,
                changes_made=["Function name must be provided"],
                estimated_time_saved="0 minutes",
                risk_level="none",
                rollback_instructions=[]
            )
        
        lines = code.split('\n')
        changes_made = []
        
        for i, line in enumerate(lines):
            if f'def {function_name}(' in line:
                lines[i] = line.replace('def ', 'async def ')
                changes_made.append(f"Converted function '{function_name}' to async")
                break
        
        refactored_code = '\n'.join(lines)
        
        return RefactoringResult(
            success=len(changes_made) > 0,
            original_code=code,
            refactored_code=refactored_code,
            changes_made=changes_made,
            estimated_time_saved="3 minutes",
            risk_level="medium",
            rollback_instructions=["Remove 'async' keyword and add 'await' calls where needed"]
        )
    
    def _optimize_imports(self, code: str) -> RefactoringResult:
        """Optimize and sort imports"""
        lines = code.split('\n')
        import_lines = []
        other_lines = []
        changes_made = []
        
        for line in lines:
            if line.strip().startswith(('import ', 'from ')):
                import_lines.append(line.strip())
            else:
                other_lines.append(line)
        
        if import_lines:
            # Sort imports
            import_lines.sort()
            # Remove duplicates
            unique_imports = list(dict.fromkeys(import_lines))
            
            if len(unique_imports) != len(import_lines):
                changes_made.append(f"Removed {len(import_lines) - len(unique_imports)} duplicate imports")
            
            changes_made.append("Sorted imports alphabetically")
            
            # Reconstruct code
            refactored_lines = unique_imports + [''] + other_lines
            refactored_code = '\n'.join(refactored_lines)
        else:
            refactored_code = code
            changes_made = ["No imports found to optimize"]
        
        return RefactoringResult(
            success=len(import_lines) > 0,
            original_code=code,
            refactored_code=refactored_code,
            changes_made=changes_made,
            estimated_time_saved="1 minute",
            risk_level="low",
            rollback_instructions=["Manually revert import order"]
        )

import math  # Add missing import

# Fix import issue - we need to import from the current directory
try:
    from multi_language_tools import BaseHandler, CodeAnalysis, CodeGeneration
except ImportError:
    # If running from different directory, try relative import
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from multi_language_tools import BaseHandler, CodeAnalysis, CodeGeneration

# Additional language handlers for missing languages
class RHandler(BaseHandler):
    """R programming language handler"""
    
    def __init__(self):
        super().__init__('r', ['.r', '.R'], 'Rscript')
    
    def analyze_code(self, code: str, file_path: str = None) -> CodeAnalysis:
        functions = re.findall(r'(\w+)\s*<-\s*function\s*\(', code)
        libraries = re.findall(r'library\((\w+)\)', code)
        data_objects = re.findall(r'(\w+)\s*<-\s*(?:read\.|data\.frame|c\()', code)
        
        return CodeAnalysis(
            language='r',
            syntax_valid=True,
            errors=[],
            warnings=[],
            complexity_score=len(functions) * 2 + len(data_objects),
            functions=functions,
            classes=[],
            imports=libraries,
            dependencies=libraries,
            suggestions=self._generate_r_suggestions(code),
            structure={'functions': functions, 'libraries': libraries, 'data_objects': data_objects}
        )
    
    def generate_code(self, description: str, context: Dict[str, Any] = None) -> CodeGeneration:
        if 'data analysis' in description.lower() or 'statistics' in description.lower():
            code = f'''# {description}
library(tidyverse)
library(ggplot2)
library(dplyr)

# Load and explore data
load_data <- function(file_path) {{
  data <- read.csv(file_path)
  cat("Data loaded successfully!\\n")
  cat("Dimensions:", dim(data), "\\n")
  return(data)
}}

# Basic statistical analysis
analyze_data <- function(data) {{
  cat("=== Data Summary ===\\n")
  print(summary(data))
  
  cat("\\n=== Data Structure ===\\n")
  str(data)
  
  # Create basic plots
  numeric_cols <- sapply(data, is.numeric)
  if(any(numeric_cols)) {{
    numeric_data <- data[, numeric_cols, drop = FALSE]
    
    # Histogram for first numeric column
    if(ncol(numeric_data) >= 1) {{
      p1 <- ggplot(data, aes(x = numeric_data[,1])) +
        geom_histogram(bins = 30, fill = "skyblue", alpha = 0.7) +
        labs(title = paste("Distribution of", names(numeric_data)[1]),
             x = names(numeric_data)[1], y = "Frequency") +
        theme_minimal()
      print(p1)
    }}
    
    # Correlation plot if multiple numeric columns
    if(ncol(numeric_data) >= 2) {{
      library(corrplot)
      cor_matrix <- cor(numeric_data, use = "complete.obs")
      corrplot(cor_matrix, method = "circle", type = "upper")
    }}
  }}
}}

# Statistical modeling
create_model <- function(data, formula_str) {{
  formula_obj <- as.formula(formula_str)
  model <- lm(formula_obj, data = data)
  
  cat("=== Model Summary ===\\n")
  print(summary(model))
  
  # Diagnostic plots
  par(mfrow = c(2, 2))
  plot(model)
  par(mfrow = c(1, 1))
  
  return(model)
}}

# Main analysis function
main <- function() {{
  cat("🔍 {description}\\n")
  cat(paste(rep("=", 50), collapse = ""), "\\n")
  
  # Example usage (uncomment and modify):
  # data <- load_data("your_data.csv")
  # analyze_data(data)
  # model <- create_model(data, "y ~ x1 + x2")
  
  cat("✅ R analysis pipeline ready!\\n")
}}

# Run main function
if(!interactive()) {{
  main()
}}
'''
        else:
            code = f'''# {description}

# Main function
main <- function() {{
  cat("Hello from R!\\n")
  cat("{description}\\n")
  
  # Add your R code here
}}

# Run main function
main()
'''
        
        return CodeGeneration(
            language='r',
            code=code,
            files={
                'analysis.R': code,
                'install_packages.R': '''# Install required packages
packages <- c("tidyverse", "ggplot2", "dplyr", "corrplot")
install.packages(packages[!packages %in% installed.packages()[,"Package"]])'''
            },
            tests={'test_analysis.R': '# R tests would go here\n# Use testthat package for unit testing'},
            documentation=f"# {description}\n\nR statistical analysis script",
            build_commands=['Rscript install_packages.R'],
            run_commands=['Rscript analysis.R']
        )
    
    def _generate_r_suggestions(self, code: str) -> List[str]:
        suggestions = []
        
        if 'attach(' in code:
            suggestions.append("Avoid using attach() - use data$ or with() instead")
        if 'T' in code or 'F' in code:
            suggestions.append("Use TRUE and FALSE instead of T and F")
        if not re.search(r'library\(tidyverse\)', code) and ('data.frame' in code or 'read.csv' in code):
            suggestions.append("Consider using tidyverse for data manipulation")
        
        return suggestions
    
    def debug_code(self, code: str, error_message: str = None) -> List[str]:
        """Debug R code and suggest fixes"""
        suggestions = []
        if error_message:
            if 'object' in error_message and 'not found' in error_message:
                suggestions.append("Check for undefined variables or misspelled object names")
            elif 'could not find function' in error_message:
                suggestions.append("Check if the required library is loaded or function name is correct")
        return suggestions
    
    def refactor_code(self, code: str, instructions: str) -> str:
        """Basic R code refactoring"""
        if 'pipe' in instructions.lower():
            # Convert to pipe operator %>%
            code = code.replace(')', ' %>%\n  ')
        return code
    
    def run_code(self, code: str, input_data: str = None) -> Tuple[str, str, int]:
        """Execute R code"""
        temp_file = self._create_temp_file(code, '.R')
        try:
            return self._run_command(['Rscript', temp_file], input_data)
        finally:
            os.unlink(temp_file)

class ScalaHandler(BaseHandler):
    """Scala programming language handler"""
    
    def __init__(self):
        super().__init__('scala', ['.scala'], 'scala')
    
    def analyze_code(self, code: str, file_path: str = None) -> CodeAnalysis:
        functions = re.findall(r'def\s+(\w+)\s*\[?[^\]]*\]?\s*\(', code)
        classes = re.findall(r'class\s+(\w+)', code)
        objects = re.findall(r'object\s+(\w+)', code)
        imports = re.findall(r'import\s+([^\s\n]+)', code)
        traits = re.findall(r'trait\s+(\w+)', code)
        
        return CodeAnalysis(
            language='scala',
            syntax_valid=True,
            errors=[],
            warnings=[],
            complexity_score=len(functions) + len(classes) * 2 + len(objects),
            functions=functions,
            classes=classes + objects + traits,
            imports=imports,
            dependencies=imports,
            suggestions=[],
            structure={'functions': functions, 'classes': classes, 'objects': objects, 'traits': traits}
        )
    
    def generate_code(self, description: str, context: Dict[str, Any] = None) -> CodeGeneration:
        code = f'''// {description}
object Main extends App {{
  
  // Main application logic
  def main(): Unit = {{
    println("Hello from Scala!")
    println("{description}")
    
    // Add your Scala code here
  }}
  
  // Helper functions
  def processData[T](data: List[T]): List[T] = {{
    data.filter(_ != null)
  }}
  
  // Example case class
  case class Item(id: Int, name: String, value: Double)
  
  // Example trait
  trait Processor[T] {{
    def process(item: T): T
  }}
  
  // Run main function
  main()
}}
'''
        
        return CodeGeneration(
            language='scala',
            code=code,
            files={
                'Main.scala': code,
                'build.sbt': '''name := "scala-project"
version := "0.1"
scalaVersion := "2.13.8"

libraryDependencies ++= Seq(
  "org.scalatest" %% "scalatest" % "3.2.9" % Test
)'''
            },
            tests={'MainTest.scala': '''import org.scalatest.flatspec.AnyFlatSpec
import org.scalatest.matchers.should.Matchers

class MainTest extends AnyFlatSpec with Matchers {
  "Main" should "process data correctly" in {
    val data = List(1, 2, 3)
    Main.processData(data) shouldEqual data
  }
}'''},
            documentation=f"# {description}\n\nScala application",
            build_commands=['sbt compile'],
            run_commands=['sbt run']
        )
    
    def debug_code(self, code: str, error_message: str = None) -> List[str]:
        """Debug Scala code and suggest fixes"""
        suggestions = []
        if error_message:
            if 'not found: value' in error_message:
                suggestions.append("Check for undefined variables or imports")
            elif 'type mismatch' in error_message:
                suggestions.append("Check variable types and function signatures")
        return suggestions
    
    def refactor_code(self, code: str, instructions: str) -> str:
        """Basic Scala code refactoring"""
        return code
    
    def run_code(self, code: str, input_data: str = None) -> Tuple[str, str, int]:
        """Execute Scala code"""
        temp_file = self._create_temp_file(code, '.scala')
        try:
            return self._run_command(['scala', temp_file], input_data)
        finally:
            os.unlink(temp_file)

class DartHandler(BaseHandler):
    """Dart programming language handler (Flutter)"""
    
    def __init__(self):
        super().__init__('dart', ['.dart'], 'dart')
    
    def analyze_code(self, code: str, file_path: str = None) -> CodeAnalysis:
        functions = re.findall(r'(?:void|int|String|bool|double|Future<\w+>|Widget)\s+(\w+)\s*\(', code)
        classes = re.findall(r'class\s+(\w+)', code)
        imports = re.findall(r'import\s+[\'"]([^\'"]+)[\'"]', code)
        widgets = re.findall(r'(?:StatelessWidget|StatefulWidget|Widget)', code)
        
        return CodeAnalysis(
            language='dart',
            syntax_valid=True,
            errors=[],
            warnings=[],
            complexity_score=len(functions) + len(classes) * 2,
            functions=functions,
            classes=classes,
            imports=imports,
            dependencies=imports,
            suggestions=self._generate_dart_suggestions(code),
            structure={'functions': functions, 'classes': classes, 'widgets': len(widgets)}
        )
    
    def generate_code(self, description: str, context: Dict[str, Any] = None) -> CodeGeneration:
        if 'flutter' in description.lower() or 'mobile' in description.lower():
            code = f'''import 'package:flutter/material.dart';

void main() {{
  runApp(MyApp());
}}

class MyApp extends StatelessWidget {{
  @override
  Widget build(BuildContext context) {{
    return MaterialApp(
      title: '{description}',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        visualDensity: VisualDensity.adaptivePlatformDensity,
      ),
      home: MyHomePage(title: '{description}'),
    );
  }}
}}

class MyHomePage extends StatefulWidget {{
  MyHomePage({{Key? key, required this.title}}) : super(key: key);
  
  final String title;

  @override
  _MyHomePageState createState() => _MyHomePageState();
}}

class _MyHomePageState extends State<MyHomePage> {{
  int _counter = 0;

  void _incrementCounter() {{
    setState(() {{
      _counter++;
    }});
  }}

  @override
  Widget build(BuildContext context) {{
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            Text(
              'You have pushed the button this many times:',
            ),
            Text(
              '$_counter',
              style: Theme.of(context).textTheme.headline4,
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _incrementCounter,
        tooltip: 'Increment',
        child: Icon(Icons.add),
      ),
    );
  }}
}}
'''
            files = {
                'lib/main.dart': code,
                'pubspec.yaml': f'''name: flutter_app
description: {description}
version: 1.0.0+1

environment:
  sdk: ">=2.17.0 <3.0.0"

dependencies:
  flutter:
    sdk: flutter
  cupertino_icons: ^1.0.2

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^2.0.0

flutter:
  uses-material-design: true''',
                'android/app/build.gradle': '''def localProperties = new Properties()
def localPropertiesFile = rootProject.file('local.properties')
if (localPropertiesFile.exists()) {
    localPropertiesFile.withReader('UTF-8') { reader ->
        localProperties.load(reader)
    }
}

def flutterRoot = localProperties.getProperty('flutter.sdk')
if (flutterRoot == null) {
    throw new GradleException("Flutter SDK not found. Define location with flutter.sdk in the local.properties file.")
}

android {
    compileSdkVersion 31
    
    defaultConfig {
        applicationId "com.example.flutter_app"
        minSdkVersion 16
        targetSdkVersion 31
        versionCode 1
        versionName "1.0"
    }
}'''
            }
        else:
            code = f'''// {description}

void main() {{
  print('Hello from Dart!');
  print('{description}');
  
  // Example function
  var result = calculateSum([1, 2, 3, 4, 5]);
  print('Sum: $result');
}}

int calculateSum(List<int> numbers) {{
  return numbers.fold(0, (a, b) => a + b);
}}

class Example {{
  String name;
  
  Example(this.name);
  
  void greet() {{
    print('Hello, $name!');
  }}
}}
'''
            files = {
                'main.dart': code,
                'pubspec.yaml': '''name: dart_app
description: Dart console application
version: 1.0.0

environment:
  sdk: ">=2.17.0 <3.0.0"

dev_dependencies:
  test: ^1.16.0'''
            }
        
        return CodeGeneration(
            language='dart',
            code=code,
            files=files,
            tests={'test/main_test.dart': '''import 'package:test/test.dart';

void main() {
  test('calculate sum', () {
    // Add your tests here
    expect(2 + 2, equals(4));
  });
}'''},
            documentation=f"# {description}\n\nDart application",
            build_commands=['dart pub get'],
            run_commands=['dart main.dart'] if 'flutter' not in description.lower() else ['flutter run']
        )
    
    def debug_code(self, code: str, error_message: str = None) -> List[str]:
        """Debug Dart code and suggest fixes"""
        suggestions = []
        if error_message:
            if 'Undefined name' in error_message:
                suggestions.append("Check for undefined variables or incorrect imports")
            elif 'type' in error_message and 'is not a subtype' in error_message:
                suggestions.append("Check variable types and casts")
        return suggestions
    
    def refactor_code(self, code: str, instructions: str) -> str:
        """Basic Dart code refactoring"""
        return code
    
    def run_code(self, code: str, input_data: str = None) -> Tuple[str, str, int]:
        """Execute Dart code"""
        temp_file = self._create_temp_file(code, '.dart')
        try:
            return self._run_command(['dart', temp_file], input_data)
        finally:
            os.unlink(temp_file)
    
    def _generate_dart_suggestions(self, code: str) -> List[str]:
        suggestions = []
        
        if 'var ' in code and not 'final ' in code and not 'const ' in code:
            suggestions.append("Consider using 'final' or 'const' for immutable variables")
        if 'print(' in code and 'flutter' in code.lower():
            suggestions.append("Use debugPrint() instead of print() in Flutter apps")
        if 'StatefulWidget' in code and '@override' not in code:
            suggestions.append("Add @override annotations for better code clarity")
        
        return suggestions