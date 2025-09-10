/**
 * CodeLensProvider - Shows inline code metrics and quick actions
 */

import * as vscode from 'vscode';
import { AeonforgeService } from '../services/AeonforgeService';

export class AeonforgeCodeLensProvider implements vscode.CodeLensProvider {
    private _onDidChangeCodeLenses = new vscode.EventEmitter<void>();
    public readonly onDidChangeCodeLenses = this._onDidChangeCodeLenses.event;

    constructor(private aeonforgeService: AeonforgeService) {}

    refresh(): void {
        this._onDidChangeCodeLenses.fire();
    }

    async provideCodeLenses(
        document: vscode.TextDocument,
        token: vscode.CancellationToken
    ): Promise<vscode.CodeLens[]> {
        const codeLenses: vscode.CodeLens[] = [];
        
        try {
            // Analyze the document first
            const analysis = await this.aeonforgeService.analyzeCode({
                code: document.getText(),
                language: document.languageId,
                file_path: document.fileName
            });

            // Add file-level metrics at the top
            const firstLine = new vscode.Range(0, 0, 0, 0);
            codeLenses.push(
                new vscode.CodeLens(firstLine, {
                    title: `📊 Quality: ${Math.round(analysis.quality.overall_score)}%`,
                    tooltip: `Overall code quality score: ${analysis.quality.overall_score.toFixed(1)}%`,
                    command: 'aeonforge.showQualityReport',
                    arguments: [document.fileName]
                }),
                new vscode.CodeLens(firstLine, {
                    title: `🔧 Complexity: ${analysis.analysis.complexity_score}`,
                    tooltip: `Code complexity score: ${analysis.analysis.complexity_score}`,
                    command: 'aeonforge.showComplexityDetails',
                    arguments: [document.fileName]
                })
            );

            // Add security warnings if any
            if (analysis.quality.security_score < 80) {
                codeLenses.push(new vscode.CodeLens(firstLine, {
                    title: `🔒 Security Issues (${analysis.quality.security_score.toFixed(0)}%)`,
                    tooltip: 'Click to see security recommendations',
                    command: 'aeonforge.showSecurityIssues',
                    arguments: [document.fileName, analysis.quality.issues]
                }));
            }

            // Add function-level code lenses
            await this.addFunctionCodeLenses(document, analysis, codeLenses);
            
            // Add class-level code lenses
            await this.addClassCodeLenses(document, analysis, codeLenses);
            
            // Add import optimization suggestions
            await this.addImportCodeLenses(document, analysis, codeLenses);

        } catch (error) {
            console.error('CodeLens provider error:', error);
        }

        return codeLenses;
    }

    private async addFunctionCodeLenses(
        document: vscode.TextDocument,
        analysis: any,
        codeLenses: vscode.CodeLens[]
    ): Promise<void> {
        const text = document.getText();
        const language = document.languageId;
        
        // Find functions based on language
        let functionRegex: RegExp;
        let functionNameIndex = 1;
        
        if (language === 'python') {
            functionRegex = /^(\s*)def\s+(\w+)\s*\([^)]*\):/gm;
            functionNameIndex = 2;
        } else if (language === 'javascript' || language === 'typescript') {
            functionRegex = /^(\s*)(?:function\s+(\w+)\s*\([^)]*\)|const\s+(\w+)\s*=\s*\([^)]*\)\s*=>|(\w+)\s*\([^)]*\)\s*{)/gm;
            functionNameIndex = 2;
        } else if (language === 'java') {
            functionRegex = /^(\s*)(?:public|private|protected)?\s*(?:static)?\s*\w+\s+(\w+)\s*\([^)]*\)\s*{/gm;
            functionNameIndex = 2;
        } else {
            return; // Unsupported language for function detection
        }

        let match;
        while ((match = functionRegex.exec(text)) !== null) {
            const functionName = match[functionNameIndex] || match[3] || match[4];
            if (!functionName) continue;

            const startPos = document.positionAt(match.index);
            const range = new vscode.Range(startPos.line, 0, startPos.line, 0);
            
            // Estimate function complexity
            const functionEnd = this.findFunctionEnd(text, match.index, language);
            const functionBody = text.substring(match.index, functionEnd);
            const complexity = this.calculateFunctionComplexity(functionBody);
            
            // Add complexity lens
            if (complexity > 5) {
                codeLenses.push(new vscode.CodeLens(range, {
                    title: `🔥 Complex (${complexity})`,
                    tooltip: `Function complexity: ${complexity} (consider refactoring)`,
                    command: 'aeonforge.refactorFunction',
                    arguments: [functionName, startPos]
                }));
            }
            
            // Add test lens if no tests found
            if (!this.hasTests(functionName, text)) {
                codeLenses.push(new vscode.CodeLens(range, {
                    title: `🧪 Generate Tests`,
                    tooltip: `Generate unit tests for ${functionName}`,
                    command: 'aeonforge.generateTests',
                    arguments: [functionName, functionBody, startPos]
                }));
            }
            
            // Add documentation lens if no docs
            if (!this.hasDocumentation(functionBody, language)) {
                codeLenses.push(new vscode.CodeLens(range, {
                    title: `📝 Add Docs`,
                    tooltip: `Generate documentation for ${functionName}`,
                    command: 'aeonforge.generateDocs',
                    arguments: [functionName, functionBody, startPos]
                }));
            }
        }
    }

    private async addClassCodeLenses(
        document: vscode.TextDocument,
        analysis: any,
        codeLenses: vscode.CodeLens[]
    ): Promise<void> {
        const text = document.getText();
        const language = document.languageId;
        
        let classRegex: RegExp;
        
        if (language === 'python') {
            classRegex = /^(\s*)class\s+(\w+).*:/gm;
        } else if (language === 'javascript' || language === 'typescript') {
            classRegex = /^(\s*)class\s+(\w+)/gm;
        } else if (language === 'java') {
            classRegex = /^(\s*)(?:public\s+)?class\s+(\w+)/gm;
        } else {
            return;
        }

        let match;
        while ((match = classRegex.exec(text)) !== null) {
            const className = match[2];
            const startPos = document.positionAt(match.index);
            const range = new vscode.Range(startPos.line, 0, startPos.line, 0);
            
            // Count methods in class
            const classEnd = this.findClassEnd(text, match.index, language);
            const classBody = text.substring(match.index, classEnd);
            const methodCount = this.countMethods(classBody, language);
            
            if (methodCount > 10) {
                codeLenses.push(new vscode.CodeLens(range, {
                    title: `⚠️ Large Class (${methodCount} methods)`,
                    tooltip: `Class has ${methodCount} methods - consider splitting`,
                    command: 'aeonforge.suggestClassRefactoring',
                    arguments: [className, startPos]
                }));
            }
            
            // Add interface extraction suggestion for TypeScript
            if (language === 'typescript' && methodCount > 3) {
                codeLenses.push(new vscode.CodeLens(range, {
                    title: `🔧 Extract Interface`,
                    tooltip: `Extract interface from ${className}`,
                    command: 'aeonforge.extractInterface',
                    arguments: [className, classBody, startPos]
                }));
            }
        }
    }

    private async addImportCodeLenses(
        document: vscode.TextDocument,
        analysis: any,
        codeLenses: vscode.CodeLens[]
    ): Promise<void> {
        if (analysis.analysis.imports.length === 0) return;
        
        // Find unused imports
        const text = document.getText();
        const unusedImports = this.findUnusedImports(text, analysis.analysis.imports, document.languageId);
        
        if (unusedImports.length > 0) {
            const firstLine = new vscode.Range(0, 0, 0, 0);
            codeLenses.push(new vscode.CodeLens(firstLine, {
                title: `🧹 Clean Imports (${unusedImports.length} unused)`,
                tooltip: `Remove ${unusedImports.length} unused imports`,
                command: 'aeonforge.cleanImports',
                arguments: [document.fileName, unusedImports]
            }));
        }
        
        // Suggest import organization
        if (analysis.analysis.imports.length > 5) {
            const firstLine = new vscode.Range(0, 0, 0, 0);
            codeLenses.push(new vscode.CodeLens(firstLine, {
                title: `📋 Organize Imports`,
                tooltip: 'Sort and organize import statements',
                command: 'aeonforge.organizeImports',
                arguments: [document.fileName]
            }));
        }
    }

    private findFunctionEnd(text: string, startIndex: number, language: string): number {
        // Simple heuristic - find next function or class declaration
        let nextDefRegex: RegExp;
        
        if (language === 'python') {
            nextDefRegex = /^(def|class)\s+/gm;
        } else if (language === 'javascript' || language === 'typescript') {
            nextDefRegex = /^(function|class|\w+\s*\(|const\s+\w+\s*=)/gm;
        } else {
            nextDefRegex = /^(public|private|protected|class)/gm;
        }
        
        nextDefRegex.lastIndex = startIndex + 1;
        const nextMatch = nextDefRegex.exec(text);
        
        return nextMatch ? nextMatch.index : text.length;
    }

    private findClassEnd(text: string, startIndex: number, language: string): number {
        // Similar to findFunctionEnd but for classes
        let nextClassRegex: RegExp;
        
        if (language === 'python') {
            nextClassRegex = /^class\s+/gm;
        } else {
            nextClassRegex = /^class\s+/gm;
        }
        
        nextClassRegex.lastIndex = startIndex + 1;
        const nextMatch = nextClassRegex.exec(text);
        
        return nextMatch ? nextMatch.index : text.length;
    }

    private calculateFunctionComplexity(functionBody: string): number {
        let complexity = 1;
        
        // Count control flow statements
        const controlFlowKeywords = ['if', 'else', 'elif', 'for', 'while', 'try', 'catch', 'except', 'switch', 'case'];
        controlFlowKeywords.forEach(keyword => {
            const regex = new RegExp(`\\b${keyword}\\b`, 'gi');
            const matches = functionBody.match(regex) || [];
            complexity += matches.length;
        });
        
        return complexity;
    }

    private countMethods(classBody: string, language: string): number {
        let methodRegex: RegExp;
        
        if (language === 'python') {
            methodRegex = /^\s*def\s+\w+/gm;
        } else if (language === 'javascript' || language === 'typescript') {
            methodRegex = /^\s*\w+\s*\(/gm;
        } else {
            methodRegex = /^\s*(public|private|protected)?\s*\w+\s+\w+\s*\(/gm;
        }
        
        const matches = classBody.match(methodRegex) || [];
        return matches.length;
    }

    private hasTests(functionName: string, text: string): boolean {
        const testPatterns = [
            `test_${functionName}`,
            `test${functionName}`,
            `${functionName}Test`,
            `describe('${functionName}'`,
            `describe("${functionName}"`,
            `it('${functionName}'`,
            `it("${functionName}"`
        ];
        
        return testPatterns.some(pattern => text.includes(pattern));
    }

    private hasDocumentation(functionBody: string, language: string): boolean {
        if (language === 'python') {
            return /""".*?"""/s.test(functionBody) || /'''.*?'''/s.test(functionBody);
        } else if (language === 'javascript' || language === 'typescript') {
            return /\/\*\*.*?\*\//s.test(functionBody);
        } else if (language === 'java') {
            return /\/\*\*.*?\*\//s.test(functionBody);
        }
        
        return false;
    }

    private findUnusedImports(text: string, imports: string[], language: string): string[] {
        const unusedImports: string[] = [];
        
        imports.forEach(imp => {
            // Extract the actual module/variable name from import statement
            let importName = imp;
            if (language === 'python') {
                // Handle "from x import y" and "import x as y"
                const fromMatch = imp.match(/from\s+[\w.]+\s+import\s+(\w+)/);
                const asMatch = imp.match(/import\s+[\w.]+\s+as\s+(\w+)/);
                const simpleMatch = imp.match(/import\s+([\w.]+)/);
                
                if (fromMatch) importName = fromMatch[1];
                else if (asMatch) importName = asMatch[1];
                else if (simpleMatch) importName = simpleMatch[1].split('.')[0];
            }
            
            // Check if the import is used in the code
            const usageRegex = new RegExp(`\\b${importName}\\b`, 'g');
            const matches = text.match(usageRegex) || [];
            
            // If only found once (the import itself), it's unused
            if (matches.length <= 1) {
                unusedImports.push(imp);
            }
        });
        
        return unusedImports;
    }
}