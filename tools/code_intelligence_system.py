"""
Advanced Code Intelligence System for Aeonforge
Provides intelligent code analysis, refactoring, and optimization across all languages
"""

import os
import json
import ast
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
MULTI_LANG_AVAILABLE = False

# Create dummy classes for when not available
class CodeAnalysis:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

class CodeGeneration:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

class DummyMultiLanguageManager:
    def analyze_code(self, code, language=None, file_path=None):
        return CodeAnalysis(
            language=language or "unknown",
            syntax_valid=True,
            errors=[],
            warnings=[],
            complexity_score=1.0,
            functions=[],
            classes=[],
            imports=[],
            dependencies=[],
            suggestions=[],
            structure={}
        )

multi_language_manager = DummyMultiLanguageManager()

try:
    from .multi_language_tools import multi_language_manager as real_manager, CodeAnalysis as RealAnalysis, CodeGeneration as RealGeneration
    multi_language_manager = real_manager
    CodeAnalysis = RealAnalysis
    CodeGeneration = RealGeneration
    MULTI_LANG_AVAILABLE = True
except ImportError:
    try:
        from multi_language_tools import multi_language_manager as real_manager, CodeAnalysis as RealAnalysis, CodeGeneration as RealGeneration
        multi_language_manager = real_manager
        CodeAnalysis = RealAnalysis
        CodeGeneration = RealGeneration
        MULTI_LANG_AVAILABLE = True
    except ImportError:
        pass

@dataclass
class CodeQuality:
    """Code quality metrics"""
    maintainability_score: float
    readability_score: float
    performance_score: float
    security_score: float
    test_coverage: float
    documentation_score: float
    overall_score: float
    issues: List[str]
    suggestions: List[str]

@dataclass
class RefactoringPlan:
    """Detailed refactoring plan"""
    language: str
    original_code: str
    refactored_code: str
    changes: List[Dict[str, Any]]
    improvements: List[str]
    risks: List[str]
    estimated_time: str
    priority: str

class CodeIntelligenceEngine:
    """Advanced code intelligence and analysis engine"""
    
    def __init__(self):
        self.analysis_history = []
        self.refactoring_patterns = self._load_refactoring_patterns()
        self.security_rules = self._load_security_rules()
        
    def _load_refactoring_patterns(self) -> Dict[str, Any]:
        """Load common refactoring patterns for each language"""
        return {
            'python': {
                'long_function': {'max_lines': 50, 'suggestion': 'Break into smaller functions'},
                'deep_nesting': {'max_depth': 4, 'suggestion': 'Use early returns or extract methods'},
                'magic_numbers': {'pattern': r'\b\d+\b', 'suggestion': 'Use named constants'},
                'duplicate_code': {'min_similarity': 0.8, 'suggestion': 'Extract common functionality'}
            },
            'javascript': {
                'var_usage': {'pattern': r'\bvar\s', 'suggestion': 'Use const or let instead of var'},
                'callback_hell': {'max_nested': 3, 'suggestion': 'Use async/await or promises'},
                'global_variables': {'pattern': r'^\s*\w+\s*=', 'suggestion': 'Avoid global variables'},
                'jquery_usage': {'pattern': r'\$\(', 'suggestion': 'Consider modern alternatives to jQuery'}
            },
            'java': {
                'god_class': {'max_methods': 20, 'suggestion': 'Break into smaller classes'},
                'long_parameter_list': {'max_params': 5, 'suggestion': 'Use parameter objects'},
                'static_imports': {'pattern': r'import static', 'suggestion': 'Use sparingly to avoid confusion'}
            }
        }
    
    def _load_security_rules(self) -> Dict[str, Any]:
        """Load security analysis rules"""
        return {
            'python': [
                {'pattern': r'eval\(', 'severity': 'high', 'message': 'Avoid eval() - security risk'},
                {'pattern': r'exec\(', 'severity': 'high', 'message': 'Avoid exec() - security risk'},
                {'pattern': r'pickle\.loads?\(', 'severity': 'medium', 'message': 'Pickle can execute arbitrary code'},
                {'pattern': r'shell=True', 'severity': 'high', 'message': 'Shell injection vulnerability'},
                {'pattern': r'password\s*=\s*[\'"][^\'"]+[\'"]', 'severity': 'high', 'message': 'Hardcoded password detected'}
            ],
            'javascript': [
                {'pattern': r'eval\(', 'severity': 'high', 'message': 'Avoid eval() - security risk'},
                {'pattern': r'innerHTML\s*=', 'severity': 'medium', 'message': 'XSS vulnerability - use textContent'},
                {'pattern': r'document\.write\(', 'severity': 'medium', 'message': 'Avoid document.write - XSS risk'},
                {'pattern': r'setTimeout\([\'"][^\'"]+[\'"]', 'severity': 'medium', 'message': 'Avoid string-based setTimeout'}
            ],
            'sql': [
                {'pattern': r'SELECT\s+\*\s+FROM.*\+.*', 'severity': 'high', 'message': 'SQL injection vulnerability'},
                {'pattern': r'WHERE.*=.*\+', 'severity': 'high', 'message': 'Potential SQL injection'},
                {'pattern': r'DROP\s+TABLE', 'severity': 'medium', 'message': 'Destructive operation detected'}
            ]
        }
    
    def analyze_code_quality(self, code: str, language: str = None, file_path: str = None) -> CodeQuality:
        """Comprehensive code quality analysis"""
        if not language:
            language = multi_language_manager.detect_language(code, file_path)
        
        # Get basic analysis
        basic_analysis = multi_language_manager.analyze_code(code, language, file_path)
        
        # Calculate quality metrics
        maintainability = self._calculate_maintainability(code, language, basic_analysis)
        readability = self._calculate_readability(code, language)
        performance = self._calculate_performance_score(code, language)
        security = self._calculate_security_score(code, language)
        test_coverage = self._estimate_test_coverage(code, language)
        documentation = self._calculate_documentation_score(code, language)
        
        overall = (maintainability + readability + performance + security + documentation) / 5
        
        # Generate issues and suggestions
        issues = self._identify_code_issues(code, language, basic_analysis)
        suggestions = self._generate_improvement_suggestions(code, language, basic_analysis)
        
        return CodeQuality(
            maintainability_score=maintainability,
            readability_score=readability,
            performance_score=performance,
            security_score=security,
            test_coverage=test_coverage,
            documentation_score=documentation,
            overall_score=overall,
            issues=issues,
            suggestions=suggestions
        )
    
    def _calculate_maintainability(self, code: str, language: str, analysis: CodeAnalysis) -> float:
        """Calculate maintainability score based on complexity, structure, etc."""
        score = 100.0
        
        # Penalize high complexity
        if analysis.complexity_score > 50:
            score -= min(30, (analysis.complexity_score - 50) * 0.5)
        
        # Penalize long functions (language-specific)
        if language == 'python':
            functions = re.findall(r'def\s+\w+.*?(?=def|\Z)', code, re.DOTALL)
            for func in functions:
                lines = len(func.split('\n'))
                if lines > 50:
                    score -= min(10, (lines - 50) * 0.1)
        
        # Penalize deep nesting
        max_indent = 0
        for line in code.split('\n'):
            if line.strip():
                indent = len(line) - len(line.lstrip())
                max_indent = max(max_indent, indent)
        
        if language in ['python']:
            max_depth = max_indent // 4
        else:
            max_depth = max_indent // 2
            
        if max_depth > 6:
            score -= min(15, (max_depth - 6) * 2)
        
        return max(0, min(100, score))
    
    def _calculate_readability(self, code: str, language: str) -> float:
        """Calculate readability score"""
        score = 100.0
        lines = code.split('\n')
        
        # Check for comments
        comment_lines = 0
        if language == 'python':
            comment_lines = len([l for l in lines if l.strip().startswith('#') or '"""' in l])
        elif language in ['javascript', 'java', 'cpp']:
            comment_lines = len([l for l in lines if '//' in l or '/*' in l])
        
        total_lines = len([l for l in lines if l.strip()])
        comment_ratio = comment_lines / max(1, total_lines)
        
        if comment_ratio < 0.1:
            score -= 20
        elif comment_ratio > 0.3:
            score -= 10
        
        # Check line length
        long_lines = len([l for l in lines if len(l) > 100])
        if long_lines > total_lines * 0.1:
            score -= 15
        
        # Check for meaningful variable names
        if language == 'python':
            vars_found = re.findall(r'\b[a-z_][a-z0-9_]*\s*=', code)
            short_vars = [v for v in vars_found if len(v.split('=')[0].strip()) < 3]
            if len(short_vars) > len(vars_found) * 0.3:
                score -= 10
        
        return max(0, min(100, score))
    
    def _calculate_performance_score(self, code: str, language: str) -> float:
        """Calculate performance score"""
        score = 100.0
        
        # Language-specific performance checks
        if language == 'python':
            # Check for inefficient patterns
            if 'for i in range(len(' in code:
                score -= 10
            if re.search(r'\+\s*=\s*.*\[.*\]', code):  # List concatenation in loop
                score -= 15
            if 'global ' in code:
                score -= 5
                
        elif language == 'javascript':
            # Check for inefficient DOM operations
            if 'getElementById' in code and code.count('getElementById') > 3:
                score -= 10
            if 'innerHTML' in code:
                score -= 5
            if re.search(r'for\s*\(.*\.length', code):  # Length in loop condition
                score -= 5
                
        elif language == 'sql':
            # Check for inefficient queries
            if 'SELECT *' in code.upper():
                score -= 15
            if 'WHERE' not in code.upper() and 'SELECT' in code.upper():
                score -= 10
        
        return max(0, min(100, score))
    
    def _calculate_security_score(self, code: str, language: str) -> float:
        """Calculate security score"""
        score = 100.0
        
        if language in self.security_rules:
            for rule in self.security_rules[language]:
                if re.search(rule['pattern'], code, re.IGNORECASE):
                    if rule['severity'] == 'high':
                        score -= 25
                    elif rule['severity'] == 'medium':
                        score -= 10
                    else:
                        score -= 5
        
        return max(0, min(100, score))
    
    def _estimate_test_coverage(self, code: str, language: str) -> float:
        """Estimate test coverage based on code structure"""
        if language == 'python':
            functions = len(re.findall(r'def\s+\w+', code))
            test_functions = len(re.findall(r'def\s+test_\w+', code))
            return min(100, (test_functions / max(1, functions)) * 100)
        
        elif language == 'javascript':
            functions = len(re.findall(r'function\s+\w+|const\s+\w+\s*=.*=>', code))
            test_functions = len(re.findall(r'test\(|it\(|describe\(', code))
            return min(100, (test_functions / max(1, functions)) * 50)  # Less aggressive for JS
        
        return 50.0  # Default estimate
    
    def _calculate_documentation_score(self, code: str, language: str) -> float:
        """Calculate documentation score"""
        score = 100.0
        
        if language == 'python':
            functions = re.findall(r'def\s+\w+.*?:', code)
            classes = re.findall(r'class\s+\w+.*?:', code)
            docstrings = len(re.findall(r'""".*?"""', code, re.DOTALL))
            
            total_items = len(functions) + len(classes)
            if total_items > 0:
                doc_ratio = docstrings / total_items
                if doc_ratio < 0.5:
                    score -= 30
                elif doc_ratio < 0.8:
                    score -= 15
        
        elif language in ['javascript', 'java']:
            functions = len(re.findall(r'function\s+\w+|public\s+.*\s+\w+\s*\(', code))
            jsdoc_comments = len(re.findall(r'/\*\*.*?\*/', code, re.DOTALL))
            
            if functions > 0:
                doc_ratio = jsdoc_comments / functions
                if doc_ratio < 0.3:
                    score -= 25
        
        return max(0, min(100, score))
    
    def _identify_code_issues(self, code: str, language: str, analysis: CodeAnalysis) -> List[str]:
        """Identify specific code issues"""
        issues = []
        
        # Add syntax errors
        issues.extend(analysis.errors)
        
        # Language-specific issues
        if language in self.refactoring_patterns:
            patterns = self.refactoring_patterns[language]
            
            for issue_type, config in patterns.items():
                if issue_type == 'long_function' and language == 'python':
                    functions = re.findall(r'def\s+(\w+).*?(?=def|\Z)', code, re.DOTALL)
                    for func in functions:
                        if len(func.split('\n')) > config['max_lines']:
                            issues.append(f"Function is too long (>{config['max_lines']} lines)")
                
                elif 'pattern' in config:
                    if re.search(config['pattern'], code):
                        issues.append(f"{issue_type}: {config['suggestion']}")
        
        # Security issues
        if language in self.security_rules:
            for rule in self.security_rules[language]:
                if re.search(rule['pattern'], code, re.IGNORECASE):
                    issues.append(f"Security: {rule['message']}")
        
        return issues
    
    def _generate_improvement_suggestions(self, code: str, language: str, analysis: CodeAnalysis) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []
        
        # Quality-based suggestions
        quality = self.analyze_code_quality(code, language)
        
        if quality.maintainability_score < 70:
            suggestions.append("Consider breaking down complex functions and reducing nesting")
        
        if quality.readability_score < 70:
            suggestions.append("Add more comments and use more descriptive variable names")
        
        if quality.performance_score < 70:
            suggestions.append("Review performance bottlenecks and optimize critical paths")
        
        if quality.security_score < 80:
            suggestions.append("Address security vulnerabilities and follow secure coding practices")
        
        if quality.test_coverage < 80:
            suggestions.append("Increase test coverage by adding more unit tests")
        
        if quality.documentation_score < 70:
            suggestions.append("Add more documentation, docstrings, and inline comments")
        
        # Language-specific suggestions
        if language == 'python':
            if 'import *' in code:
                suggestions.append("Avoid wildcard imports - import specific modules/functions")
            if re.search(r'except:', code):
                suggestions.append("Use specific exception types instead of bare except clauses")
        
        elif language == 'javascript':
            if 'var ' in code:
                suggestions.append("Use 'const' or 'let' instead of 'var'")
            if '==' in code and '===' not in code:
                suggestions.append("Use strict equality (===) instead of loose equality (==)")
        
        return suggestions
    
    def create_refactoring_plan(self, code: str, instructions: str, language: str = None, file_path: str = None) -> RefactoringPlan:
        """Create a detailed refactoring plan"""
        if not language:
            language = multi_language_manager.detect_language(code, file_path)
        
        # Get current analysis
        analysis = multi_language_manager.analyze_code(code, language, file_path)
        quality = self.analyze_code_quality(code, language)
        
        # Generate refactored code
        refactored = multi_language_manager.refactor_code(code, instructions, language, file_path)
        
        # Analyze changes
        changes = self._analyze_code_changes(code, refactored, language)
        improvements = self._identify_improvements(quality, refactored, language)
        risks = self._assess_refactoring_risks(code, refactored, language)
        
        # Estimate time and priority
        estimated_time = self._estimate_refactoring_time(changes, language)
        priority = self._determine_priority(quality, improvements)
        
        return RefactoringPlan(
            language=language,
            original_code=code,
            refactored_code=refactored,
            changes=changes,
            improvements=improvements,
            risks=risks,
            estimated_time=estimated_time,
            priority=priority
        )
    
    def _analyze_code_changes(self, original: str, refactored: str, language: str) -> List[Dict[str, Any]]:
        """Analyze the differences between original and refactored code"""
        changes = []
        
        orig_lines = original.split('\n')
        refact_lines = refactored.split('\n')
        
        # Simple diff analysis
        if len(orig_lines) != len(refact_lines):
            changes.append({
                'type': 'line_count_change',
                'original': len(orig_lines),
                'refactored': len(refact_lines),
                'description': f"Line count changed from {len(orig_lines)} to {len(refact_lines)}"
            })
        
        # Check for structural changes
        if language == 'python':
            orig_functions = len(re.findall(r'def\s+\w+', original))
            refact_functions = len(re.findall(r'def\s+\w+', refactored))
            
            if orig_functions != refact_functions:
                changes.append({
                    'type': 'function_count_change',
                    'original': orig_functions,
                    'refactored': refact_functions,
                    'description': f"Function count changed from {orig_functions} to {refact_functions}"
                })
        
        return changes
    
    def _identify_improvements(self, original_quality: CodeQuality, refactored_code: str, language: str) -> List[str]:
        """Identify improvements from refactoring"""
        refactored_quality = self.analyze_code_quality(refactored_code, language)
        improvements = []
        
        if refactored_quality.overall_score > original_quality.overall_score:
            improvements.append(f"Overall code quality improved by {refactored_quality.overall_score - original_quality.overall_score:.1f} points")
        
        if refactored_quality.maintainability_score > original_quality.maintainability_score:
            improvements.append("Maintainability improved")
        
        if refactored_quality.readability_score > original_quality.readability_score:
            improvements.append("Readability improved")
        
        if refactored_quality.security_score > original_quality.security_score:
            improvements.append("Security improved")
        
        return improvements
    
    def _assess_refactoring_risks(self, original: str, refactored: str, language: str) -> List[str]:
        """Assess potential risks of refactoring"""
        risks = []
        
        # Check for major structural changes
        orig_analysis = multi_language_manager.analyze_code(original, language)
        refact_analysis = multi_language_manager.analyze_code(refactored, language)
        
        if len(orig_analysis.functions) != len(refact_analysis.functions):
            risks.append("Function signatures may have changed - check API compatibility")
        
        if len(orig_analysis.classes) != len(refact_analysis.classes):
            risks.append("Class structure changed - verify inheritance and usage")
        
        # Check for removed dependencies
        removed_deps = set(orig_analysis.dependencies) - set(refact_analysis.dependencies)
        if removed_deps:
            risks.append(f"Dependencies removed: {', '.join(removed_deps)}")
        
        return risks
    
    def _estimate_refactoring_time(self, changes: List[Dict[str, Any]], language: str) -> str:
        """Estimate time required for refactoring"""
        base_time = 30  # minutes
        
        for change in changes:
            if change['type'] == 'line_count_change':
                diff = abs(change['refactored'] - change['original'])
                base_time += diff * 2  # 2 minutes per line change
            elif change['type'] == 'function_count_change':
                base_time += abs(change['refactored'] - change['original']) * 15  # 15 min per function
        
        if base_time < 60:
            return f"{base_time} minutes"
        elif base_time < 480:
            return f"{base_time // 60} hours"
        else:
            return f"{base_time // 480} days"
    
    def _determine_priority(self, quality: CodeQuality, improvements: List[str]) -> str:
        """Determine refactoring priority"""
        if quality.overall_score < 50 or quality.security_score < 60:
            return "HIGH"
        elif quality.overall_score < 70 or len(improvements) > 3:
            return "MEDIUM"
        else:
            return "LOW"
    
    def generate_code_report(self, code: str, language: str = None, file_path: str = None) -> Dict[str, Any]:
        """Generate comprehensive code analysis report"""
        if not language:
            language = multi_language_manager.detect_language(code, file_path)
        
        basic_analysis = multi_language_manager.analyze_code(code, language, file_path)
        quality_analysis = self.analyze_code_quality(code, language, file_path)
        
        return {
            'file_info': {
                'language': language,
                'file_path': file_path,
                'lines_of_code': len([l for l in code.split('\n') if l.strip()]),
                'total_lines': len(code.split('\n'))
            },
            'structure': {
                'functions': basic_analysis.functions,
                'classes': basic_analysis.classes,
                'imports': basic_analysis.imports,
                'complexity_score': basic_analysis.complexity_score
            },
            'quality_metrics': asdict(quality_analysis),
            'recommendations': {
                'immediate_fixes': [issue for issue in quality_analysis.issues if 'Security:' in issue],
                'improvements': quality_analysis.suggestions[:5],
                'next_steps': self._generate_next_steps(quality_analysis)
            }
        }
    
    def _generate_next_steps(self, quality: CodeQuality) -> List[str]:
        """Generate actionable next steps"""
        steps = []
        
        if quality.security_score < 80:
            steps.append("1. Address security vulnerabilities immediately")
        
        if quality.test_coverage < 70:
            steps.append("2. Add comprehensive unit tests")
        
        if quality.maintainability_score < 70:
            steps.append("3. Refactor complex functions and reduce coupling")
        
        if quality.documentation_score < 70:
            steps.append("4. Add documentation and improve comments")
        
        if quality.performance_score < 70:
            steps.append("5. Profile and optimize performance bottlenecks")
        
        return steps

# Global instance
code_intelligence = CodeIntelligenceEngine()

def analyze_code_quality(code: str, language: str = None, file_path: str = None) -> CodeQuality:
    """Convenience function for code quality analysis"""
    return code_intelligence.analyze_code_quality(code, language, file_path)

def create_refactoring_plan(code: str, instructions: str, language: str = None, file_path: str = None) -> RefactoringPlan:
    """Convenience function for refactoring planning"""
    return code_intelligence.create_refactoring_plan(code, instructions, language, file_path)

def generate_code_report(code: str, language: str = None, file_path: str = None) -> Dict[str, Any]:
    """Convenience function for code analysis reports"""
    return code_intelligence.generate_code_report(code, language, file_path)