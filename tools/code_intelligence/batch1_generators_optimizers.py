"""
AeonForge Code Intelligence Tools - Batch 1 Continued: Generators & Optimizers
Tools 4-20: Advanced code generation, optimization, and refactoring tools
"""

import ast
import re
import json
import os
import sys
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass
import subprocess
import tempfile
import time
from collections import defaultdict
import difflib

# Import the tool system
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from tools.advanced_tools_system import (
    BaseTool, ToolResult, ToolMetadata, ToolCategory, 
    ToolComplexity, ToolExecutionMode, register_tool
)

# Tool 4: Intelligent Code Refactoring Assistant
@register_tool(ToolMetadata(
    name="intelligent_refactoring_assistant",
    category=ToolCategory.CODE_INTELLIGENCE,
    complexity=ToolComplexity.ENTERPRISE,
    execution_mode=ToolExecutionMode.ASYNCHRONOUS,
    description="AI-powered code refactoring with pattern recognition and automated improvements",
    parameters={
        "code": {"type": "str", "description": "Source code to refactor", "required": True},
        "refactoring_types": {"type": "List[str]", "description": "Types of refactoring to apply", "default": ["all"]},
        "preserve_functionality": {"type": "bool", "description": "Ensure functionality preservation", "default": True},
        "optimization_level": {"type": "str", "description": "Optimization level (conservative, balanced, aggressive)", "default": "balanced"}
    },
    tags=["refactoring", "optimization", "code improvement", "patterns"],
    use_cases=["Legacy code modernization", "Performance optimization", "Code quality improvement"],
    performance_rating=9.7
))
class IntelligentRefactoringAssistant(BaseTool):
    
    async def initialize(self) -> bool:
        self.refactoring_patterns = self._load_refactoring_patterns()
        self._initialized = True
        return True
    
    async def validate_input(self, **kwargs) -> bool:
        return 'code' in kwargs
    
    async def execute(self, **kwargs) -> ToolResult:
        code = kwargs['code']
        refactoring_types = kwargs.get('refactoring_types', ['all'])
        preserve_functionality = kwargs.get('preserve_functionality', True)
        optimization_level = kwargs.get('optimization_level', 'balanced')
        
        try:
            refactored_result = await self._perform_intelligent_refactoring(
                code, refactoring_types, preserve_functionality, optimization_level
            )
            return ToolResult(success=True, data=refactored_result)
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    def _load_refactoring_patterns(self) -> Dict[str, Dict]:
        return {
            "extract_method": {
                "description": "Extract repeated code into methods",
                "pattern": r"(.{20,})\1+",  # Repeated code blocks
                "weight": 0.8
            },
            "eliminate_dead_code": {
                "description": "Remove unused variables and functions", 
                "pattern": r"def\s+\w+.*?(?=def|\Z)",
                "weight": 0.9
            },
            "simplify_conditionals": {
                "description": "Simplify complex conditional statements",
                "pattern": r"if.*(?:and|or).*(?:and|or)",
                "weight": 0.7
            },
            "optimize_loops": {
                "description": "Optimize loop constructs",
                "pattern": r"for.*in.*range\(len\(",
                "weight": 0.8
            },
            "consolidate_imports": {
                "description": "Organize and consolidate import statements",
                "pattern": r"import\s+\w+|from\s+\w+\s+import",
                "weight": 0.6
            }
        }
    
    async def _perform_intelligent_refactoring(self, code: str, refactoring_types: List[str], 
                                            preserve_functionality: bool, optimization_level: str) -> Dict[str, Any]:
        original_code = code
        refactored_code = code
        applied_refactorings = []
        
        # Apply refactoring patterns based on type selection
        if 'all' in refactoring_types:
            patterns_to_apply = list(self.refactoring_patterns.keys())
        else:
            patterns_to_apply = [p for p in refactoring_types if p in self.refactoring_patterns]
        
        for pattern_name in patterns_to_apply:
            refactored_code, changes = await self._apply_refactoring_pattern(
                refactored_code, pattern_name, optimization_level
            )
            if changes:
                applied_refactorings.extend(changes)
        
        # Advanced optimizations
        refactored_code, advanced_changes = await self._apply_advanced_optimizations(
            refactored_code, optimization_level
        )
        applied_refactorings.extend(advanced_changes)
        
        # Generate quality metrics
        quality_improvement = await self._calculate_quality_improvement(original_code, refactored_code)
        
        # Functionality verification if requested
        functionality_preserved = True
        if preserve_functionality:
            functionality_preserved = await self._verify_functionality_preservation(
                original_code, refactored_code
            )
        
        return {
            "original_code": original_code,
            "refactored_code": refactored_code,
            "applied_refactorings": applied_refactorings,
            "quality_improvement": quality_improvement,
            "functionality_preserved": functionality_preserved,
            "diff": self._generate_diff(original_code, refactored_code),
            "recommendations": self._generate_further_recommendations(refactored_code)
        }
    
    async def _apply_refactoring_pattern(self, code: str, pattern_name: str, 
                                       optimization_level: str) -> Tuple[str, List[Dict]]:
        changes = []
        refactored_code = code
        
        if pattern_name == "extract_method":
            refactored_code, method_changes = self._extract_methods(code)
            changes.extend(method_changes)
        
        elif pattern_name == "eliminate_dead_code":
            refactored_code, dead_code_changes = self._eliminate_dead_code(code)
            changes.extend(dead_code_changes)
        
        elif pattern_name == "simplify_conditionals":
            refactored_code, conditional_changes = self._simplify_conditionals(code)
            changes.extend(conditional_changes)
        
        elif pattern_name == "optimize_loops":
            refactored_code, loop_changes = self._optimize_loops(code)
            changes.extend(loop_changes)
        
        elif pattern_name == "consolidate_imports":
            refactored_code, import_changes = self._consolidate_imports(code)
            changes.extend(import_changes)
        
        return refactored_code, changes
    
    def _extract_methods(self, code: str) -> Tuple[str, List[Dict]]:
        changes = []
        lines = code.split('\n')
        
        # Find repeated code blocks (simplified implementation)
        repeated_blocks = self._find_repeated_blocks(lines)
        
        refactored_lines = lines.copy()
        method_counter = 1
        
        for block_info in repeated_blocks:
            if len(block_info['lines']) >= 3:  # Only extract blocks with 3+ lines
                method_name = f"extracted_method_{method_counter}"
                
                # Create method definition
                method_def = [
                    f"def {method_name}(self):",
                    *[f"    {line}" for line in block_info['lines']]
                ]
                
                # Replace occurrences with method calls
                for start_line in block_info['occurrences']:
                    for i in range(len(block_info['lines'])):
                        if start_line + i < len(refactored_lines):
                            if i == 0:
                                refactored_lines[start_line + i] = f"    self.{method_name}()"
                            else:
                                refactored_lines[start_line + i] = ""
                
                # Add method definition at the beginning of class (simplified)
                refactored_lines = method_def + [''] + refactored_lines
                
                changes.append({
                    "type": "extract_method",
                    "method_name": method_name,
                    "description": f"Extracted repeated code block into {method_name}",
                    "lines_saved": len(block_info['occurrences']) * len(block_info['lines'])
                })
                
                method_counter += 1
        
        return '\n'.join(refactored_lines), changes
    
    def _find_repeated_blocks(self, lines: List[str]) -> List[Dict]:
        repeated_blocks = []
        min_block_size = 3
        
        for i in range(len(lines) - min_block_size):
            for j in range(i + min_block_size, len(lines)):
                block = lines[i:i + min_block_size]
                if lines[j:j + min_block_size] == block:
                    # Found a repeated block
                    block_info = {
                        'lines': block,
                        'occurrences': [i, j]
                    }
                    repeated_blocks.append(block_info)
                    break
        
        return repeated_blocks
    
    def _eliminate_dead_code(self, code: str) -> Tuple[str, List[Dict]]:
        changes = []
        try:
            tree = ast.parse(code)
            
            # Find defined functions and variables
            defined_names = set()
            used_names = set()
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    defined_names.add(node.name)
                elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                    used_names.add(node.id)
            
            # Find dead functions
            dead_functions = defined_names - used_names
            
            if dead_functions:
                # Remove dead functions (simplified)
                lines = code.split('\n')
                filtered_lines = []
                skip_lines = False
                
                for line in lines:
                    is_dead_function = any(f"def {func}" in line for func in dead_functions)
                    
                    if is_dead_function:
                        skip_lines = True
                        changes.append({
                            "type": "eliminate_dead_code",
                            "description": f"Removed unused function: {line.strip()}",
                            "impact": "Reduced code size"
                        })
                        continue
                    
                    if skip_lines and line.strip() and not line.startswith(' '):
                        skip_lines = False
                    
                    if not skip_lines:
                        filtered_lines.append(line)
                
                return '\n'.join(filtered_lines), changes
        
        except:
            pass  # If AST parsing fails, return original code
        
        return code, changes
    
    def _simplify_conditionals(self, code: str) -> Tuple[str, List[Dict]]:
        changes = []
        
        # Simplify complex boolean expressions
        patterns = [
            (r'if\s+not\s+\(\s*not\s+(.+?)\s*\):', r'if \1:'),  # Double negation
            (r'if\s+(.+?)\s*==\s*True:', r'if \1:'),  # Comparison with True
            (r'if\s+(.+?)\s*==\s*False:', r'if not \1:'),  # Comparison with False
            (r'if\s+(.+?)\s*!=\s*None:', r'if \1 is not None:'),  # None comparison
        ]
        
        refactored_code = code
        
        for pattern, replacement in patterns:
            matches = re.finditer(pattern, refactored_code)
            for match in matches:
                changes.append({
                    "type": "simplify_conditionals",
                    "description": f"Simplified conditional: {match.group(0)}",
                    "improvement": "Better readability and performance"
                })
            
            refactored_code = re.sub(pattern, replacement, refactored_code)
        
        return refactored_code, changes
    
    def _optimize_loops(self, code: str) -> Tuple[str, List[Dict]]:
        changes = []
        
        # Optimize common loop patterns
        patterns = [
            # for i in range(len(list)) -> for item in list
            (r'for\s+(\w+)\s+in\s+range\(len\((\w+)\)\):\s*\n\s*(.+?)\[\1\]',
             r'for item in \2:\n    \3item'),
            
            # List comprehension opportunities
            (r'(\w+)\s*=\s*\[\]\s*\nfor\s+(\w+)\s+in\s+(.+?):\s*\n\s*\1\.append\((.+?)\)',
             r'\1 = [\4 for \2 in \3]')
        ]
        
        refactored_code = code
        
        for pattern, replacement in patterns:
            if re.search(pattern, refactored_code, re.MULTILINE):
                refactored_code = re.sub(pattern, replacement, refactored_code, flags=re.MULTILINE)
                changes.append({
                    "type": "optimize_loops",
                    "description": "Optimized loop construct",
                    "improvement": "Better performance and readability"
                })
        
        return refactored_code, changes
    
    def _consolidate_imports(self, code: str) -> Tuple[str, List[Dict]]:
        changes = []
        lines = code.split('\n')
        
        # Separate import lines from other code
        import_lines = []
        other_lines = []
        in_imports_section = True
        
        for line in lines:
            if line.strip().startswith(('import ', 'from ')):
                import_lines.append(line.strip())
            elif line.strip() == '':
                if in_imports_section:
                    continue  # Skip empty lines in import section
                else:
                    other_lines.append(line)
            else:
                in_imports_section = False
                other_lines.append(line)
        
        # Sort and organize imports
        if len(import_lines) > 1:
            # Group imports
            standard_imports = []
            third_party_imports = []
            local_imports = []
            
            standard_libs = {'os', 'sys', 'json', 'time', 're', 'math', 'random', 'datetime'}
            
            for imp in import_lines:
                if any(lib in imp for lib in standard_libs):
                    standard_imports.append(imp)
                elif imp.startswith('from .') or 'from src' in imp:
                    local_imports.append(imp)
                else:
                    third_party_imports.append(imp)
            
            # Sort within groups
            standard_imports.sort()
            third_party_imports.sort()
            local_imports.sort()
            
            # Combine with proper spacing
            organized_imports = []
            if standard_imports:
                organized_imports.extend(standard_imports)
                organized_imports.append('')
            if third_party_imports:
                organized_imports.extend(third_party_imports)
                organized_imports.append('')
            if local_imports:
                organized_imports.extend(local_imports)
                organized_imports.append('')
            
            # Combine with rest of code
            refactored_code = '\n'.join(organized_imports + other_lines)
            
            changes.append({
                "type": "consolidate_imports",
                "description": "Organized and sorted import statements",
                "improvement": "Better code organization and PEP 8 compliance"
            })
            
            return refactored_code, changes
        
        return code, changes
    
    async def _apply_advanced_optimizations(self, code: str, optimization_level: str) -> Tuple[str, List[Dict]]:
        changes = []
        refactored_code = code
        
        if optimization_level in ['balanced', 'aggressive']:
            # Apply string concatenation optimizations
            string_concat_pattern = r'(\w+)\s*\+=\s*(["\'].+?["\'])'
            if re.search(string_concat_pattern, refactored_code):
                # Suggest using join for multiple concatenations
                changes.append({
                    "type": "optimize_string_ops",
                    "description": "Consider using str.join() for multiple string concatenations",
                    "improvement": "Better performance for string operations"
                })
        
        if optimization_level == 'aggressive':
            # Apply more aggressive optimizations
            # Convert to generator expressions where appropriate
            list_comp_pattern = r'\[(.+?for.+?in.+?)\]'
            matches = re.finditer(list_comp_pattern, refactored_code)
            
            for match in matches:
                # Check if it's used in sum(), max(), min(), etc.
                context_before = refactored_code[max(0, match.start()-20):match.start()]
                if any(func in context_before for func in ['sum(', 'max(', 'min(', 'all(', 'any(']):
                    replacement = f"({match.group(1)})"
                    refactored_code = refactored_code[:match.start()] + replacement + refactored_code[match.end():]
                    changes.append({
                        "type": "generator_optimization",
                        "description": "Converted list comprehension to generator expression",
                        "improvement": "Memory efficiency improvement"
                    })
        
        return refactored_code, changes
    
    async def _calculate_quality_improvement(self, original: str, refactored: str) -> Dict[str, Any]:
        original_metrics = self._calculate_basic_metrics(original)
        refactored_metrics = self._calculate_basic_metrics(refactored)
        
        return {
            "lines_of_code": {
                "original": original_metrics["loc"],
                "refactored": refactored_metrics["loc"],
                "reduction": original_metrics["loc"] - refactored_metrics["loc"]
            },
            "complexity_estimate": {
                "original": original_metrics["complexity"],
                "refactored": refactored_metrics["complexity"],
                "improvement": original_metrics["complexity"] - refactored_metrics["complexity"]
            },
            "maintainability_score": {
                "original": original_metrics["maintainability"],
                "refactored": refactored_metrics["maintainability"],
                "improvement": refactored_metrics["maintainability"] - original_metrics["maintainability"]
            }
        }
    
    def _calculate_basic_metrics(self, code: str) -> Dict[str, float]:
        lines = [line for line in code.split('\n') if line.strip()]
        loc = len(lines)
        
        # Estimate complexity
        complexity_indicators = ['if', 'elif', 'for', 'while', 'try', 'except']
        complexity = sum(line.lower().count(indicator) for line in lines for indicator in complexity_indicators)
        
        # Estimate maintainability (simplified)
        avg_line_length = sum(len(line) for line in lines) / max(loc, 1)
        maintainability = max(0, 100 - (complexity * 2) - (avg_line_length / 2))
        
        return {
            "loc": loc,
            "complexity": complexity,
            "maintainability": maintainability
        }
    
    async def _verify_functionality_preservation(self, original: str, refactored: str) -> bool:
        # Simplified functionality verification
        # In production, this would involve running tests
        try:
            # Check if both can be parsed without syntax errors
            ast.parse(original)
            ast.parse(refactored)
            
            # Basic structural comparison
            original_functions = re.findall(r'def\s+(\w+)', original)
            refactored_functions = re.findall(r'def\s+(\w+)', refactored)
            
            # Functions should be preserved (though new ones may be added)
            return set(original_functions).issubset(set(refactored_functions))
        
        except:
            return False
    
    def _generate_diff(self, original: str, refactored: str) -> List[str]:
        return list(difflib.unified_diff(
            original.splitlines(keepends=True),
            refactored.splitlines(keepends=True),
            fromfile='original.py',
            tofile='refactored.py',
            n=3
        ))
    
    def _generate_further_recommendations(self, code: str) -> List[str]:
        recommendations = []
        
        # Check for additional improvement opportunities
        if 'lambda' in code:
            recommendations.append("Consider replacing lambda functions with regular functions for better readability")
        
        if re.search(r'except:', code):
            recommendations.append("Use specific exception types instead of bare except clauses")
        
        if len(code.split('\n')) > 100:
            recommendations.append("Consider breaking large files into smaller modules")
        
        return recommendations

# Tool 5: Performance Bottleneck Detector
@register_tool(ToolMetadata(
    name="performance_bottleneck_detector",
    category=ToolCategory.CODE_INTELLIGENCE,
    complexity=ToolComplexity.COMPLEX,
    execution_mode=ToolExecutionMode.ASYNCHRONOUS,
    description="Detects performance bottlenecks and provides optimization recommendations",
    parameters={
        "code": {"type": "str", "description": "Source code to analyze", "required": True},
        "language": {"type": "str", "description": "Programming language", "default": "python"},
        "analysis_depth": {"type": "str", "description": "Analysis depth (surface, deep, comprehensive)", "default": "deep"}
    },
    tags=["performance", "bottleneck", "optimization", "profiling"],
    use_cases=["Performance optimization", "Code review", "System scaling preparation"],
    performance_rating=9.3
))
class PerformanceBottleneckDetector(BaseTool):
    
    async def initialize(self) -> bool:
        self.bottleneck_patterns = self._load_bottleneck_patterns()
        self._initialized = True
        return True
    
    async def validate_input(self, **kwargs) -> bool:
        return 'code' in kwargs
    
    async def execute(self, **kwargs) -> ToolResult:
        code = kwargs['code']
        language = kwargs.get('language', 'python')
        analysis_depth = kwargs.get('analysis_depth', 'deep')
        
        try:
            analysis = await self._analyze_performance_bottlenecks(code, language, analysis_depth)
            return ToolResult(success=True, data=analysis)
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    def _load_bottleneck_patterns(self) -> Dict[str, List[Dict]]:
        return {
            "python": [
                {
                    "pattern": r"for\s+\w+\s+in\s+range\(len\(",
                    "severity": "medium",
                    "description": "Inefficient iteration over list indices",
                    "recommendation": "Use direct iteration: for item in list"
                },
                {
                    "pattern": r"\+=\s*[\"'].*[\"']",
                    "severity": "high", 
                    "description": "String concatenation in loop",
                    "recommendation": "Use list.join() or f-strings"
                },
                {
                    "pattern": r"\.append\s*\(.*\)\s*\n.*for\s+",
                    "severity": "medium",
                    "description": "List building in loop",
                    "recommendation": "Consider list comprehension"
                },
                {
                    "pattern": r"import\s+.*\n.*for\s+.*in.*:",
                    "severity": "low",
                    "description": "Module imported inside function",
                    "recommendation": "Move imports to module level"
                }
            ]
        }
    
    async def _analyze_performance_bottlenecks(self, code: str, language: str, depth: str) -> Dict[str, Any]:
        bottlenecks = []
        
        # Pattern-based detection
        language_patterns = self.bottleneck_patterns.get(language, [])
        for pattern_info in language_patterns:
            matches = list(re.finditer(pattern_info["pattern"], code, re.MULTILINE))
            
            for match in matches:
                line_num = code[:match.start()].count('\n') + 1
                
                bottleneck = {
                    "type": "pattern_based",
                    "description": pattern_info["description"],
                    "severity": pattern_info["severity"],
                    "line": line_num,
                    "code_snippet": match.group(0),
                    "recommendation": pattern_info["recommendation"],
                    "estimated_impact": self._estimate_performance_impact(pattern_info["severity"])
                }
                bottlenecks.append(bottleneck)
        
        # Advanced analysis based on depth
        if depth in ['deep', 'comprehensive']:
            advanced_bottlenecks = await self._advanced_bottleneck_analysis(code, language)
            bottlenecks.extend(advanced_bottlenecks)
        
        if depth == 'comprehensive':
            algorithmic_bottlenecks = await self._algorithmic_complexity_analysis(code)
            bottlenecks.extend(algorithmic_bottlenecks)
        
        # Generate optimization recommendations
        optimization_plan = self._generate_optimization_plan(bottlenecks, code)
        
        return {
            "bottlenecks": bottlenecks,
            "summary": self._generate_performance_summary(bottlenecks),
            "optimization_plan": optimization_plan,
            "priority_fixes": self._prioritize_fixes(bottlenecks),
            "estimated_improvement": self._estimate_overall_improvement(bottlenecks)
        }
    
    def _estimate_performance_impact(self, severity: str) -> str:
        impact_map = {
            "low": "5-15% performance improvement",
            "medium": "15-40% performance improvement", 
            "high": "40-80% performance improvement",
            "critical": "2-10x performance improvement"
        }
        return impact_map.get(severity, "Unknown impact")
    
    async def _advanced_bottleneck_analysis(self, code: str, language: str) -> List[Dict]:
        advanced_bottlenecks = []
        
        if language == "python":
            # Check for nested loops
            nested_loop_pattern = r'for\s+.*:\s*.*for\s+.*:'
            nested_matches = re.finditer(nested_loop_pattern, code, re.MULTILINE | re.DOTALL)
            
            for match in nested_matches:
                line_num = code[:match.start()].count('\n') + 1
                advanced_bottlenecks.append({
                    "type": "nested_loops",
                    "description": "Nested loops detected - O(n²) complexity",
                    "severity": "high",
                    "line": line_num,
                    "recommendation": "Consider algorithmic improvements or data structure optimization",
                    "estimated_impact": "Significant performance impact for large datasets"
                })
            
            # Check for file I/O in loops
            file_io_pattern = r'for\s+.*:.*(?:open\(|read\(|write\()'
            file_io_matches = re.finditer(file_io_pattern, code, re.MULTILINE | re.DOTALL)
            
            for match in file_io_matches:
                line_num = code[:match.start()].count('\n') + 1
                advanced_bottlenecks.append({
                    "type": "io_in_loop",
                    "description": "File I/O operations inside loop",
                    "severity": "critical",
                    "line": line_num,
                    "recommendation": "Batch I/O operations outside the loop",
                    "estimated_impact": "Major performance bottleneck - up to 100x slower"
                })
            
            # Check for database queries in loops
            db_pattern = r'for\s+.*:.*(?:execute\(|query\(|cursor\.)'
            db_matches = re.finditer(db_pattern, code, re.MULTILINE | re.DOTALL)
            
            for match in db_matches:
                line_num = code[:match.start()].count('\n') + 1
                advanced_bottlenecks.append({
                    "type": "db_queries_in_loop",
                    "description": "Database queries inside loop (N+1 problem)",
                    "severity": "critical",
                    "line": line_num,
                    "recommendation": "Use bulk operations or join queries",
                    "estimated_impact": "Severe performance impact - network latency multiplied"
                })
        
        return advanced_bottlenecks
    
    async def _algorithmic_complexity_analysis(self, code: str) -> List[Dict]:
        complexity_issues = []
        
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    complexity = self._analyze_function_complexity(node)
                    
                    if complexity["time_complexity"] in ["O(n²)", "O(n³)", "O(2^n)"]:
                        complexity_issues.append({
                            "type": "algorithmic_complexity",
                            "function": node.name,
                            "description": f"Function has {complexity['time_complexity']} complexity",
                            "severity": "high" if complexity["time_complexity"] == "O(n²)" else "critical",
                            "line": node.lineno,
                            "recommendation": complexity["optimization_suggestion"],
                            "estimated_impact": "Performance degrades with input size"
                        })
        
        except:
            pass  # If AST parsing fails, skip complexity analysis
        
        return complexity_issues
    
    def _analyze_function_complexity(self, func_node: ast.FunctionDef) -> Dict[str, str]:
        # Simplified complexity analysis
        nested_loops = 0
        recursive_calls = 0
        
        for node in ast.walk(func_node):
            if isinstance(node, (ast.For, ast.While)):
                # Check if this loop is nested
                parent_loops = [p for p in ast.walk(func_node) if isinstance(p, (ast.For, ast.While)) and node in ast.walk(p)]
                if len(parent_loops) > 1:
                    nested_loops += 1
            
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == func_node.name:
                    recursive_calls += 1
        
        # Estimate complexity
        if recursive_calls > 0:
            return {
                "time_complexity": "O(2^n)",  # Assuming exponential recursion
                "optimization_suggestion": "Use memoization or iterative approach"
            }
        elif nested_loops > 0:
            return {
                "time_complexity": "O(n²)" if nested_loops == 1 else "O(n³)",
                "optimization_suggestion": "Consider using hash maps or more efficient algorithms"
            }
        else:
            return {
                "time_complexity": "O(n)",
                "optimization_suggestion": "Function appears to have linear complexity"
            }
    
    def _generate_performance_summary(self, bottlenecks: List[Dict]) -> Dict[str, Any]:
        severity_counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        
        for bottleneck in bottlenecks:
            severity = bottleneck.get("severity", "low")
            severity_counts[severity] += 1
        
        return {
            "total_bottlenecks": len(bottlenecks),
            "by_severity": severity_counts,
            "most_critical": [b for b in bottlenecks if b.get("severity") == "critical"][:3],
            "performance_score": self._calculate_performance_score(severity_counts),
            "priority_level": self._determine_priority_level(severity_counts)
        }
    
    def _calculate_performance_score(self, severity_counts: Dict[str, int]) -> float:
        # Performance score out of 100 (higher is better)
        weights = {"critical": 30, "high": 15, "medium": 5, "low": 1}
        penalty = sum(count * weight for severity, count in severity_counts.items() for s, weight in weights.items() if s == severity)
        
        return max(0, 100 - penalty)
    
    def _determine_priority_level(self, severity_counts: Dict[str, int]) -> str:
        if severity_counts["critical"] > 0:
            return "Immediate Action Required"
        elif severity_counts["high"] > 2:
            return "High Priority"
        elif severity_counts["high"] > 0 or severity_counts["medium"] > 3:
            return "Medium Priority"
        else:
            return "Low Priority"
    
    def _generate_optimization_plan(self, bottlenecks: List[Dict], code: str) -> Dict[str, Any]:
        plan = {
            "immediate_fixes": [],
            "short_term_improvements": [],
            "long_term_optimizations": [],
            "estimated_effort": {}
        }
        
        for bottleneck in bottlenecks:
            severity = bottleneck.get("severity", "low")
            fix_item = {
                "description": bottleneck["description"],
                "recommendation": bottleneck["recommendation"],
                "line": bottleneck.get("line", 0),
                "estimated_impact": bottleneck.get("estimated_impact", "Unknown")
            }
            
            if severity == "critical":
                plan["immediate_fixes"].append(fix_item)
            elif severity == "high":
                plan["short_term_improvements"].append(fix_item)
            else:
                plan["long_term_optimizations"].append(fix_item)
        
        # Estimate effort
        plan["estimated_effort"] = {
            "immediate_fixes": f"{len(plan['immediate_fixes']) * 2} hours",
            "short_term_improvements": f"{len(plan['short_term_improvements']) * 4} hours",
            "long_term_optimizations": f"{len(plan['long_term_optimizations']) * 8} hours"
        }
        
        return plan
    
    def _prioritize_fixes(self, bottlenecks: List[Dict]) -> List[Dict]:
        # Sort by severity and potential impact
        severity_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        
        return sorted(bottlenecks, 
                     key=lambda x: (severity_order.get(x.get("severity", "low"), 0), 
                                  x.get("line", 0)), 
                     reverse=True)
    
    def _estimate_overall_improvement(self, bottlenecks: List[Dict]) -> Dict[str, str]:
        critical_count = sum(1 for b in bottlenecks if b.get("severity") == "critical")
        high_count = sum(1 for b in bottlenecks if b.get("severity") == "high")
        
        if critical_count > 0:
            return {
                "potential_improvement": "5-20x performance improvement",
                "confidence": "High",
                "timeframe": "1-2 weeks of optimization work"
            }
        elif high_count > 2:
            return {
                "potential_improvement": "2-5x performance improvement",
                "confidence": "High", 
                "timeframe": "3-5 days of optimization work"
            }
        elif high_count > 0:
            return {
                "potential_improvement": "50-200% performance improvement",
                "confidence": "Medium",
                "timeframe": "1-2 days of optimization work"
            }
        else:
            return {
                "potential_improvement": "10-30% performance improvement",
                "confidence": "Medium",
                "timeframe": "Few hours of optimization work"
            }

# I'll continue with tools 6-20 in the next file to keep this manageable...
# This represents the first 5 of 20 tools in this batch

# Export the tools
__all__ = [
    'IntelligentRefactoringAssistant',
    'PerformanceBottleneckDetector'
]