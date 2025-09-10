/**
 * HoverProvider - AI-powered code hover information
 */

import * as vscode from 'vscode';
import { AeonforgeService } from '../services/AeonforgeService';

export class AeonforgeHoverProvider implements vscode.HoverProvider {
    private cache = new Map<string, { hover: vscode.Hover; timestamp: number }>();
    private cacheTimeout = 5 * 60 * 1000; // 5 minutes

    constructor(private aeonforgeService: AeonforgeService) {}

    async provideHover(
        document: vscode.TextDocument,
        position: vscode.Position,
        token: vscode.CancellationToken
    ): Promise<vscode.Hover | undefined> {
        
        const range = document.getWordRangeAtPosition(position);
        if (!range) {
            return undefined;
        }

        const word = document.getText(range);
        const line = document.lineAt(position);
        
        // Generate cache key
        const cacheKey = `${document.fileName}:${position.line}:${word}`;
        const cached = this.cache.get(cacheKey);
        
        if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
            return cached.hover;
        }

        try {
            // Get context around the word
            const contextRange = new vscode.Range(
                Math.max(0, position.line - 3),
                0,
                Math.min(document.lineCount - 1, position.line + 3),
                0
            );
            const context = document.getText(contextRange);
            
            // Analyze the specific element
            const hoverInfo = await this.getHoverInfo(word, context, document.languageId, line.text);
            
            if (hoverInfo) {
                const hover = new vscode.Hover(hoverInfo, range);
                this.cache.set(cacheKey, { hover, timestamp: Date.now() });
                return hover;
            }
            
        } catch (error) {
            console.error('Hover provider error:', error);
        }

        return undefined;
    }

    private async getHoverInfo(
        word: string,
        context: string,
        language: string,
        line: string
    ): Promise<vscode.MarkdownString | undefined> {
        
        // Language-specific hover information
        const hoverContent = new vscode.MarkdownString();
        hoverContent.isTrusted = true;
        
        // Determine what kind of element this is
        const elementType = this.detectElementType(word, context, language, line);
        
        switch (elementType) {
            case 'function':
                return await this.getFunctionHoverInfo(word, context, language);
            case 'variable':
                return await this.getVariableHoverInfo(word, context, language);
            case 'class':
                return await this.getClassHoverInfo(word, context, language);
            case 'method':
                return await this.getMethodHoverInfo(word, context, language);
            case 'module':
                return await this.getModuleHoverInfo(word, language);
            default:
                return await this.getGeneralHoverInfo(word, context, language);
        }
    }

    private detectElementType(word: string, context: string, language: string, line: string): string {
        const lineContext = line.toLowerCase();
        
        // Function detection
        if (language === 'python') {
            if (context.includes(`def ${word}(`)) return 'function';
            if (context.includes(`class ${word}(`)) return 'class';
            if (lineContext.includes('import') && lineContext.includes(word)) return 'module';
        } else if (language === 'javascript' || language === 'typescript') {
            if (context.includes(`function ${word}(`)) return 'function';
            if (context.includes(`const ${word} =`) || context.includes(`let ${word} =`)) return 'variable';
            if (context.includes(`class ${word}`)) return 'class';
            if (lineContext.includes('.') && lineContext.includes(word)) return 'method';
        } else if (language === 'java') {
            if (context.includes(`class ${word}`)) return 'class';
            if (context.includes(`${word}(`)) return 'method';
        }
        
        // Method call detection
        if (line.includes('.') && line.includes(`${word}(`)) return 'method';
        
        // Variable detection (basic heuristic)
        if (context.includes(`${word} =`) || context.includes(`= ${word}`)) return 'variable';
        
        return 'unknown';
    }

    private async getFunctionHoverInfo(word: string, context: string, language: string): Promise<vscode.MarkdownString> {
        const hover = new vscode.MarkdownString();
        
        // Extract function signature from context
        const functionRegex = new RegExp(`(def|function|public|private)?\\s*${word}\\s*\\([^)]*\\)`, 'i');
        const match = context.match(functionRegex);
        const signature = match ? match[0] : `${word}()`;
        
        hover.appendCodeblock(signature, language);
        hover.appendMarkdown(`\n**Function**: \`${word}\`\n\n`);
        
        // Try to extract docstring or comments
        const docstring = this.extractDocumentation(word, context, language);
        if (docstring) {
            hover.appendMarkdown(docstring);
        } else {
            hover.appendMarkdown(`*AI Analysis*: Function \`${word}\` - Click to get detailed explanation`);
            hover.appendMarkdown(`\n\n[📖 Explain Function](command:aeonforge.explainHover?${encodeURIComponent(JSON.stringify({ word, context, type: 'function' }))})`);
        }
        
        // Add complexity analysis
        const complexity = this.estimateComplexity(context, word);
        if (complexity > 1) {
            hover.appendMarkdown(`\n\n**Complexity**: ${this.getComplexityDescription(complexity)}`);
        }
        
        return hover;
    }

    private async getVariableHoverInfo(word: string, context: string, language: string): Promise<vscode.MarkdownString> {
        const hover = new vscode.MarkdownString();
        
        hover.appendMarkdown(`**Variable**: \`${word}\`\n\n`);
        
        // Try to infer type from context
        const inferredType = this.inferVariableType(word, context, language);
        if (inferredType) {
            hover.appendCodeblock(inferredType, language);
        }
        
        hover.appendMarkdown(`*Click for AI analysis*\n\n`);
        hover.appendMarkdown(`[🔍 Analyze Variable](command:aeonforge.explainHover?${encodeURIComponent(JSON.stringify({ word, context, type: 'variable' }))})`);
        
        return hover;
    }

    private async getClassHoverInfo(word: string, context: string, language: string): Promise<vscode.MarkdownString> {
        const hover = new vscode.MarkdownString();
        
        hover.appendMarkdown(`**Class**: \`${word}\`\n\n`);
        
        // Extract class signature
        const classRegex = new RegExp(`class\\s+${word}[^{]*`, 'i');
        const match = context.match(classRegex);
        if (match) {
            hover.appendCodeblock(match[0], language);
        }
        
        // Count methods and properties
        const methods = this.countClassMethods(word, context, language);
        if (methods > 0) {
            hover.appendMarkdown(`\n**Methods**: ${methods}\n`);
        }
        
        hover.appendMarkdown(`\n[📚 Class Documentation](command:aeonforge.explainHover?${encodeURIComponent(JSON.stringify({ word, context, type: 'class' }))})`);
        
        return hover;
    }

    private async getMethodHoverInfo(word: string, context: string, language: string): Promise<vscode.MarkdownString> {
        const hover = new vscode.MarkdownString();
        
        hover.appendMarkdown(`**Method**: \`${word}()\`\n\n`);
        hover.appendMarkdown(`*AI-powered method analysis*\n\n`);
        hover.appendMarkdown(`[⚡ Explain Method](command:aeonforge.explainHover?${encodeURIComponent(JSON.stringify({ word, context, type: 'method' }))})`);
        
        return hover;
    }

    private async getModuleHoverInfo(word: string, language: string): Promise<vscode.MarkdownString> {
        const hover = new vscode.MarkdownString();
        
        hover.appendMarkdown(`**Module**: \`${word}\`\n\n`);
        
        // Common module descriptions
        const moduleDescriptions: Record<string, string> = {
            'os': 'Operating system interface utilities',
            'sys': 'System-specific parameters and functions',
            'json': 'JSON encoder and decoder',
            'requests': 'HTTP library for Python',
            'numpy': 'Numerical computing library',
            'pandas': 'Data analysis and manipulation library',
            'matplotlib': 'Plotting library',
            'react': 'JavaScript library for building user interfaces',
            'express': 'Web application framework for Node.js',
            'axios': 'Promise-based HTTP client'
        };
        
        const description = moduleDescriptions[word.toLowerCase()];
        if (description) {
            hover.appendMarkdown(description);
        } else {
            hover.appendMarkdown(`*Third-party or custom module*`);
        }
        
        hover.appendMarkdown(`\n\n[📖 Module Docs](command:aeonforge.explainHover?${encodeURIComponent(JSON.stringify({ word, context: '', type: 'module' }))})`);
        
        return hover;
    }

    private async getGeneralHoverInfo(word: string, context: string, language: string): Promise<vscode.MarkdownString> {
        const hover = new vscode.MarkdownString();
        
        hover.appendMarkdown(`**Symbol**: \`${word}\`\n\n`);
        hover.appendMarkdown(`*AI Analysis Available*\n\n`);
        hover.appendMarkdown(`[🤖 Get AI Explanation](command:aeonforge.explainHover?${encodeURIComponent(JSON.stringify({ word, context, type: 'general' }))})`);
        
        return hover;
    }

    private extractDocumentation(word: string, context: string, language: string): string | null {
        if (language === 'python') {
            // Look for docstrings
            const docstringRegex = new RegExp(`def\\s+${word}[^:]*:\\s*"""([^"]+)"""`, 's');
            const match = context.match(docstringRegex);
            return match ? match[1].trim() : null;
        } else if (language === 'javascript' || language === 'typescript') {
            // Look for JSDoc comments
            const jsdocRegex = new RegExp(`\\/\\*\\*([^*]+)\\*\\/\\s*function\\s+${word}`, 's');
            const match = context.match(jsdocRegex);
            return match ? match[1].trim() : null;
        }
        
        return null;
    }

    private inferVariableType(word: string, context: string, language: string): string | null {
        if (language === 'python') {
            if (context.includes(`${word} = [`)) return 'List';
            if (context.includes(`${word} = {`)) return 'Dict';
            if (context.includes(`${word} = "`)) return 'str';
            if (context.includes(`${word} = '`)) return 'str';
            if (context.includes(`${word} = True`) || context.includes(`${word} = False`)) return 'bool';
        } else if (language === 'javascript' || language === 'typescript') {
            if (context.includes(`${word} = [`)) return 'Array';
            if (context.includes(`${word} = {`)) return 'Object';
            if (context.includes(`${word} = "`)) return 'string';
            if (context.includes(`${word} = '`)) return 'string';
            if (context.includes(`${word} = true`) || context.includes(`${word} = false`)) return 'boolean';
        }
        
        return null;
    }

    private estimateComplexity(context: string, functionName: string): number {
        let complexity = 1;
        
        // Count control flow statements
        const controlFlowKeywords = ['if', 'else', 'elif', 'for', 'while', 'try', 'catch', 'except', 'switch', 'case'];
        controlFlowKeywords.forEach(keyword => {
            const regex = new RegExp(`\\b${keyword}\\b`, 'gi');
            const matches = context.match(regex) || [];
            complexity += matches.length;
        });
        
        return complexity;
    }

    private getComplexityDescription(complexity: number): string {
        if (complexity <= 5) return `Low (${complexity})`;
        if (complexity <= 10) return `Medium (${complexity}) ⚠️`;
        return `High (${complexity}) ⚠️⚠️`;
    }

    private countClassMethods(className: string, context: string, language: string): number {
        if (language === 'python') {
            const methodRegex = /def\s+\w+\s*\(/g;
            const matches = context.match(methodRegex) || [];
            return matches.length;
        } else if (language === 'javascript' || language === 'typescript') {
            const methodRegex = /\w+\s*\([^)]*\)\s*{/g;
            const matches = context.match(methodRegex) || [];
            return matches.length;
        }
        
        return 0;
    }
}