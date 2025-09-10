/**
 * CodebaseAnalyzer - Analyzes and understands the entire codebase
 * Provides Claude Code-like codebase intelligence
 */

import * as vscode from 'vscode';
import * as path from 'path';
import { CodebaseContext, FileInfo, ProjectStructure } from './AeonforgeService';

export interface CodebaseAnalysis {
    overview: string;
    structure: ProjectStructure;
    files: FileInfo[];
    insights: string[];
    recommendations: string[];
}

export class CodebaseAnalyzer {
    private fileCache: Map<string, FileInfo> = new Map();

    /**
     * Analyze the entire workspace
     */
    async analyzeWorkspace(workspaceFolder: vscode.WorkspaceFolder): Promise<CodebaseAnalysis> {
        const files = await this.scanWorkspaceFiles(workspaceFolder);
        const structure = await this.analyzeProjectStructure(workspaceFolder);
        
        return {
            overview: this.generateOverview(structure, files),
            structure,
            files,
            insights: this.generateInsights(structure, files),
            recommendations: this.generateRecommendations(structure, files)
        };
    }

    /**
     * Get context for the current workspace
     */
    async getWorkspaceContext(): Promise<CodebaseContext> {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            throw new Error('No workspace folder open');
        }

        const files = await this.scanWorkspaceFiles(workspaceFolder);
        const structure = await this.analyzeProjectStructure(workspaceFolder);
        const diagnostics = this.collectAllDiagnostics();
        
        return {
            files,
            structure,
            diagnostics,
            activeFile: vscode.window.activeTextEditor?.document.fileName,
            selection: this.getActiveSelection()
        };
    }

    /**
     * Get context for a specific file
     */
    async getFileContext(document: vscode.TextDocument): Promise<CodebaseContext> {
        const workspaceFolder = vscode.workspace.getWorkspaceFolder(document.uri);
        if (!workspaceFolder) {
            throw new Error('File is not in a workspace');
        }

        const fileInfo: FileInfo = {
            path: vscode.workspace.asRelativePath(document.fileName),
            language: document.languageId,
            content: document.getText(),
            size: document.getText().length,
            lastModified: new Date()
        };

        const relatedFiles = await this.findRelatedFiles(document);
        const structure = await this.analyzeProjectStructure(workspaceFolder);
        const diagnostics = vscode.languages.getDiagnostics(document.uri);

        return {
            files: [fileInfo, ...relatedFiles],
            structure,
            diagnostics,
            activeFile: document.fileName,
            selection: this.getActiveSelection()
        };
    }

    /**
     * Scan all files in workspace
     */
    private async scanWorkspaceFiles(workspaceFolder: vscode.WorkspaceFolder): Promise<FileInfo[]> {
        const files: FileInfo[] = [];
        const exclude = this.getExcludePatterns();
        
        // Find all relevant files
        const filePattern = '**/*.{ts,js,tsx,jsx,py,java,cpp,c,cs,go,rs,php,rb,swift,kt}';
        const foundFiles = await vscode.workspace.findFiles(
            filePattern,
            `{${exclude.join(',')}}`,
            1000 // Limit to prevent overwhelming
        );

        for (const fileUri of foundFiles) {
            const document = await vscode.workspace.openTextDocument(fileUri);
            const relativePath = vscode.workspace.asRelativePath(fileUri);
            
            const fileInfo: FileInfo = {
                path: relativePath,
                language: document.languageId,
                content: this.shouldIncludeContent(fileUri) ? document.getText() : undefined,
                size: document.getText().length,
                lastModified: new Date()
            };

            files.push(fileInfo);
            this.fileCache.set(relativePath, fileInfo);
        }

        return files;
    }

    /**
     * Analyze project structure
     */
    private async analyzeProjectStructure(workspaceFolder: vscode.WorkspaceFolder): Promise<ProjectStructure> {
        const rootPath = workspaceFolder.uri.fsPath;
        const projectName = path.basename(rootPath);
        
        // Try to detect project type and dependencies
        const packageJsonUri = vscode.Uri.file(path.join(rootPath, 'package.json'));
        const requirementsUri = vscode.Uri.file(path.join(rootPath, 'requirements.txt'));
        const cargoUri = vscode.Uri.file(path.join(rootPath, 'Cargo.toml'));
        const pomUri = vscode.Uri.file(path.join(rootPath, 'pom.xml'));

        let projectType = 'unknown';
        let dependencies: Record<string, string> = {};
        let scripts: Record<string, string> = {};

        try {
            // Check for Node.js project
            const packageDoc = await vscode.workspace.openTextDocument(packageJsonUri);
            const packageJson = JSON.parse(packageDoc.getText());
            projectType = 'nodejs';
            dependencies = { ...packageJson.dependencies, ...packageJson.devDependencies };
            scripts = packageJson.scripts || {};
        } catch {
            try {
                // Check for Python project
                await vscode.workspace.openTextDocument(requirementsUri);
                projectType = 'python';
            } catch {
                try {
                    // Check for Rust project  
                    await vscode.workspace.openTextDocument(cargoUri);
                    projectType = 'rust';
                } catch {
                    try {
                        // Check for Java project
                        await vscode.workspace.openTextDocument(pomUri);
                        projectType = 'java';
                    } catch {
                        // Unknown project type
                    }
                }
            }
        }

        const structure = await this.generateDirectoryStructure(workspaceFolder);

        return {
            name: projectName,
            type: projectType,
            dependencies,
            scripts,
            structure
        };
    }

    /**
     * Generate directory structure
     */
    private async generateDirectoryStructure(workspaceFolder: vscode.WorkspaceFolder): Promise<string[]> {
        const structure: string[] = [];
        const exclude = this.getExcludePatterns();
        
        const allFiles = await vscode.workspace.findFiles(
            '**/*',
            `{${exclude.join(',')}}`,
            500
        );

        for (const fileUri of allFiles) {
            const relativePath = vscode.workspace.asRelativePath(fileUri);
            structure.push(relativePath);
        }

        return structure.sort();
    }

    /**
     * Find files related to the current file
     */
    private async findRelatedFiles(document: vscode.TextDocument): Promise<FileInfo[]> {
        const relatedFiles: FileInfo[] = [];
        const currentDir = path.dirname(document.fileName);
        const baseName = path.basename(document.fileName, path.extname(document.fileName));

        // Find files in same directory
        const pattern = `${currentDir}/**/*.{ts,js,tsx,jsx,py,java,cpp,c,cs}`;
        const foundFiles = await vscode.workspace.findFiles(pattern, null, 10);

        for (const fileUri of foundFiles) {
            if (fileUri.fsPath === document.fileName) continue;

            const doc = await vscode.workspace.openTextDocument(fileUri);
            const content = doc.getText();
            
            // Check if files are related (imports, references, etc.)
            if (this.areFilesRelated(document.getText(), content, baseName)) {
                relatedFiles.push({
                    path: vscode.workspace.asRelativePath(fileUri),
                    language: doc.languageId,
                    content,
                    size: content.length,
                    lastModified: new Date()
                });
            }
        }

        return relatedFiles;
    }

    /**
     * Check if two files are related
     */
    private areFilesRelated(currentContent: string, otherContent: string, baseName: string): boolean {
        // Simple heuristic - check for imports or references
        const importPatterns = [
            `import.*${baseName}`,
            `from.*${baseName}`,
            `require.*${baseName}`,
            `#include.*${baseName}`
        ];

        return importPatterns.some(pattern => 
            new RegExp(pattern, 'i').test(currentContent) || 
            new RegExp(pattern, 'i').test(otherContent)
        );
    }

    /**
     * Collect all diagnostics from workspace
     */
    private collectAllDiagnostics(): vscode.Diagnostic[] {
        const allDiagnostics: vscode.Diagnostic[] = [];
        
        vscode.languages.getDiagnostics().forEach(([uri, diagnostics]) => {
            allDiagnostics.push(...diagnostics);
        });

        return allDiagnostics;
    }

    /**
     * Get currently selected text
     */
    private getActiveSelection(): string | undefined {
        const editor = vscode.window.activeTextEditor;
        if (!editor || editor.selection.isEmpty) return undefined;
        
        return editor.document.getText(editor.selection);
    }

    /**
     * Generate overview of the project
     */
    private generateOverview(structure: ProjectStructure, files: FileInfo[]): string {
        const totalFiles = files.length;
        const totalLines = files.reduce((sum, f) => sum + (f.content?.split('\\n').length || 0), 0);
        const languages = [...new Set(files.map(f => f.language))];

        return `Project: ${structure.name} (${structure.type})
Files: ${totalFiles}
Lines of code: ~${totalLines}
Languages: ${languages.join(', ')}
Dependencies: ${Object.keys(structure.dependencies).length}`;
    }

    /**
     * Generate insights about the project
     */
    private generateInsights(structure: ProjectStructure, files: FileInfo[]): string[] {
        const insights: string[] = [];
        
        // Analyze project complexity
        if (files.length > 100) {
            insights.push('Large codebase with significant complexity');
        } else if (files.length > 20) {
            insights.push('Medium-sized project with moderate complexity');
        } else {
            insights.push('Small to medium project');
        }

        // Analyze languages used
        const languages = [...new Set(files.map(f => f.language))];
        if (languages.length > 3) {
            insights.push('Multi-language project - may benefit from better organization');
        }

        // Analyze dependencies
        const depCount = Object.keys(structure.dependencies).length;
        if (depCount > 50) {
            insights.push('Heavy dependency usage - monitor for security and maintenance');
        }

        return insights;
    }

    /**
     * Generate recommendations
     */
    private generateRecommendations(structure: ProjectStructure, files: FileInfo[]): string[] {
        const recommendations: string[] = [];
        
        // Check for common files
        const hasReadme = files.some(f => f.path.toLowerCase().includes('readme'));
        if (!hasReadme) {
            recommendations.push('Consider adding a README.md file for documentation');
        }

        const hasTests = files.some(f => f.path.toLowerCase().includes('test'));
        if (!hasTests) {
            recommendations.push('Consider adding unit tests for better code quality');
        }

        // Check for large files
        const largeFiles = files.filter(f => f.size > 1000);
        if (largeFiles.length > 0) {
            recommendations.push('Some files are quite large - consider refactoring into smaller modules');
        }

        return recommendations;
    }

    /**
     * Get file exclusion patterns
     */
    private getExcludePatterns(): string[] {
        return [
            'node_modules/**',
            '.git/**',
            'dist/**',
            'build/**',
            'out/**',
            '.vscode/**',
            '**/*.min.js',
            '**/*.map',
            '.DS_Store',
            'Thumbs.db',
            '__pycache__/**',
            '*.pyc',
            '.pytest_cache/**',
            'target/**',
            'bin/**',
            'obj/**'
        ];
    }

    /**
     * Should include file content in analysis
     */
    private shouldIncludeContent(fileUri: vscode.Uri): boolean {
        const filePath = fileUri.fsPath;
        const size = filePath.length;
        
        // Skip very large files
        if (size > 50000) return false;
        
        // Skip binary files
        const binaryExtensions = ['.jpg', '.png', '.gif', '.pdf', '.zip', '.exe', '.dll'];
        const ext = path.extname(filePath).toLowerCase();
        
        return !binaryExtensions.includes(ext);
    }
}