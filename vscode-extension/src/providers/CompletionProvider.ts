/**
 * CompletionProvider - AI-powered code completion
 */

import * as vscode from 'vscode';
import { AeonforgeService } from '../services/AeonforgeService';
import { CodebaseAnalyzer } from '../services/CodebaseAnalyzer';

export class AeonforgeCompletionProvider implements vscode.CompletionItemProvider {
    constructor(
        private aeonforgeService: AeonforgeService,
        private codebaseAnalyzer: CodebaseAnalyzer
    ) {}

    async provideCompletionItems(
        document: vscode.TextDocument,
        position: vscode.Position,
        token: vscode.CancellationToken,
        context: vscode.CompletionContext
    ): Promise<vscode.CompletionItem[]> {
        
        // Get context around cursor
        const line = document.lineAt(position);
        const linePrefix = line.text.substring(0, position.character);
        const lineSuffix = line.text.substring(position.character);
        
        // Get surrounding code context
        const startLine = Math.max(0, position.line - 10);
        const endLine = Math.min(document.lineCount - 1, position.line + 10);
        const contextRange = new vscode.Range(startLine, 0, endLine, 0);
        const contextCode = document.getText(contextRange);
        
        try {
            // Analyze current file for better context
            const analysis = await this.aeonforgeService.analyzeCode({
                code: document.getText(),
                language: document.languageId,
                file_path: document.fileName
            });

            // Generate contextual suggestions
            const completions: vscode.CompletionItem[] = [];
            
            // Language-specific completions
            if (document.languageId === 'python') {
                completions.push(...this.getPythonCompletions(linePrefix, analysis));
            } else if (document.languageId === 'javascript' || document.languageId === 'typescript') {
                completions.push(...this.getJavaScriptCompletions(linePrefix, analysis));
            } else if (document.languageId === 'java') {
                completions.push(...this.getJavaCompletions(linePrefix, analysis));
            }
            
            // Add smart suggestions based on context
            completions.push(...this.getContextualSuggestions(linePrefix, contextCode, analysis));
            
            return completions;
            
        } catch (error) {
            console.error('Completion provider error:', error);
            return [];
        }
    }

    private getPythonCompletions(linePrefix: string, analysis: any): vscode.CompletionItem[] {
        const completions: vscode.CompletionItem[] = [];
        
        // Function definition suggestions
        if (linePrefix.trim().startsWith('def ')) {
            const funcCompletion = new vscode.CompletionItem('function_template', vscode.CompletionItemKind.Snippet);
            funcCompletion.insertText = new vscode.SnippetString('${1:function_name}(${2:params}):\n    """${3:Description}\n    \n    Args:\n        ${2:params}: ${4:Description}\n    \n    Returns:\n        ${5:Return description}\n    """\n    ${0:pass}');
            funcCompletion.documentation = 'Complete function with docstring template';
            completions.push(funcCompletion);
        }
        
        // Class definition suggestions
        if (linePrefix.trim().startsWith('class ')) {
            const classCompletion = new vscode.CompletionItem('class_template', vscode.CompletionItemKind.Snippet);
            classCompletion.insertText = new vscode.SnippetString('${1:ClassName}:\n    """${2:Class description}\n    \n    Attributes:\n        ${3:attribute}: ${4:Description}\n    """\n    \n    def __init__(self, ${5:params}):\n        """Initialize ${1:ClassName}\n        \n        Args:\n            ${5:params}: ${6:Description}\n        """\n        ${0:pass}');
            classCompletion.documentation = 'Complete class with docstring template';
            completions.push(classCompletion);
        }
        
        // Import suggestions based on analysis
        if (linePrefix.trim().startsWith('import ') || linePrefix.trim().startsWith('from ')) {
            const commonImports = [
                'requests', 'numpy', 'pandas', 'matplotlib.pyplot', 'json', 'os', 'sys', 'datetime',
                'typing', 'dataclasses', 'pathlib', 'asyncio', 'logging'
            ];
            
            commonImports.forEach(imp => {
                const importCompletion = new vscode.CompletionItem(imp, vscode.CompletionItemKind.Module);
                importCompletion.documentation = `Import ${imp} module`;
                completions.push(importCompletion);
            });
        }
        
        return completions;
    }
    
    private getJavaScriptCompletions(linePrefix: string, analysis: any): vscode.CompletionItem[] {
        const completions: vscode.CompletionItem[] = [];
        
        // Function suggestions
        if (linePrefix.includes('function ') || linePrefix.includes('=>')) {
            const asyncFuncCompletion = new vscode.CompletionItem('async_function', vscode.CompletionItemKind.Snippet);
            asyncFuncCompletion.insertText = new vscode.SnippetString('async ${1:functionName}(${2:params}) {\n    try {\n        ${0:// Implementation}\n    } catch (error) {\n        console.error(error);\n        throw error;\n    }\n}');
            asyncFuncCompletion.documentation = 'Async function with error handling';
            completions.push(asyncFuncCompletion);
        }
        
        // React component suggestions
        if (linePrefix.includes('const ') && linePrefix.includes('=')) {
            const reactComponent = new vscode.CompletionItem('react_component', vscode.CompletionItemKind.Snippet);
            reactComponent.insertText = new vscode.SnippetString('const ${1:ComponentName} = ({ ${2:props} }) => {\n    return (\n        <div>\n            ${0:// Component content}\n        </div>\n    );\n};\n\nexport default ${1:ComponentName};');
            reactComponent.documentation = 'React functional component template';
            completions.push(reactComponent);
        }
        
        return completions;
    }
    
    private getJavaCompletions(linePrefix: string, analysis: any): vscode.CompletionItem[] {
        const completions: vscode.CompletionItem[] = [];
        
        // Method suggestions
        if (linePrefix.trim().includes('public ') || linePrefix.trim().includes('private ')) {
            const methodCompletion = new vscode.CompletionItem('method_template', vscode.CompletionItemKind.Snippet);
            methodCompletion.insertText = new vscode.SnippetString('/**\n * ${3:Description}\n * @param ${4:param} ${5:Description}\n * @return ${6:Return description}\n */\n${1:public} ${2:returnType} ${7:methodName}(${4:param}) {\n    ${0:// Implementation}\n}');
            methodCompletion.documentation = 'Java method with JavaDoc';
            completions.push(methodCompletion);
        }
        
        return completions;
    }
    
    private getContextualSuggestions(linePrefix: string, contextCode: string, analysis: any): vscode.CompletionItem[] {
        const completions: vscode.CompletionItem[] = [];
        
        // Error handling suggestions
        if (linePrefix.includes('try') || linePrefix.includes('catch') || linePrefix.includes('except')) {
            const errorHandling = new vscode.CompletionItem('error_handling', vscode.CompletionItemKind.Snippet);
            errorHandling.insertText = new vscode.SnippetString('try {\n    ${1:// Code that might throw}\n} catch (${2:error}) {\n    console.error(\'${3:Error message}:\', ${2:error});\n    ${0:// Error handling}\n}');
            errorHandling.documentation = 'Complete error handling block';
            completions.push(errorHandling);
        }
        
        // Logging suggestions
        if (linePrefix.includes('log') || linePrefix.includes('console')) {
            const logCompletion = new vscode.CompletionItem('log_debug', vscode.CompletionItemKind.Snippet);
            logCompletion.insertText = new vscode.SnippetString('console.log(\'${1:Debug}: ${2:message}\', ${3:variable});');
            logCompletion.documentation = 'Debug logging statement';
            completions.push(logCompletion);
        }
        
        // Test suggestions
        if (contextCode.includes('test') || contextCode.includes('describe') || contextCode.includes('it(')) {
            const testCompletion = new vscode.CompletionItem('test_case', vscode.CompletionItemKind.Snippet);
            testCompletion.insertText = new vscode.SnippetString('it(\'${1:should do something}\', async () => {\n    // Arrange\n    ${2:const expected = true;}\n    \n    // Act\n    ${3:const result = await someFunction();}\n    \n    // Assert\n    ${4:expect(result).toBe(expected);}\n});');
            testCompletion.documentation = 'Test case with AAA pattern';
            completions.push(testCompletion);
        }
        
        return completions;
    }
}