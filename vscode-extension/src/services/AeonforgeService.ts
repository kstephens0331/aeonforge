/**
 * AeonforgeService - Core service for communicating with Aeonforge backend
 */

import axios, { AxiosInstance } from 'axios';
import * as vscode from 'vscode';

export interface CodebaseContext {
    files: FileInfo[];
    structure: ProjectStructure;
    diagnostics: vscode.Diagnostic[];
    activeFile?: string;
    selection?: string;
}

export interface FileInfo {
    path: string;
    language: string;
    content?: string;
    size: number;
    lastModified: Date;
}

export interface ProjectStructure {
    name: string;
    type: string;
    dependencies: Record<string, string>;
    scripts: Record<string, string>;
    structure: string[];
}

export interface AeonforgeResponse {
    message: string;
    agent: string;
    needs_approval?: boolean;
    approval_task?: string;
    approval_details?: string;
    files_created?: string[];
    edits?: CodeEdit[];
}

export interface CodeEdit {
    filePath: string;
    content: string;
    operation: 'create' | 'edit' | 'delete';
    startLine?: number;
    endLine?: number;
}

// New interfaces for multi-language support
export interface CodeAnalysisRequest {
    code: string;
    language?: string;
    file_path?: string;
}

export interface CodeAnalysisResult {
    analysis: {
        language: string;
        syntax_valid: boolean;
        errors: string[];
        warnings: string[];
        complexity_score: number;
        functions: string[];
        classes: string[];
        imports: string[];
        dependencies: string[];
        suggestions: string[];
        structure: Record<string, any>;
    };
    quality: {
        maintainability_score: number;
        readability_score: number;
        performance_score: number;
        security_score: number;
        test_coverage: number;
        documentation_score: number;
        overall_score: number;
        issues: string[];
        suggestions: string[];
    };
}

export interface CodeGenerationRequest {
    description: string;
    language: string;
    context?: Record<string, any>;
}

export interface CodeGenerationResult {
    language: string;
    code: string;
    files: Record<string, string>;
    tests: Record<string, string>;
    documentation: string;
    build_commands: string[];
    run_commands: string[];
}

export interface CodeRefactoringRequest {
    code: string;
    instructions: string;
    language?: string;
    file_path?: string;
}

export interface RefactoringPlan {
    language: string;
    original_code: string;
    refactored_code: string;
    changes: Array<{
        type: string;
        original: any;
        refactored: any;
        description: string;
    }>;
    improvements: string[];
    risks: string[];
    estimated_time: string;
    priority: string;
}

export interface CodeExecutionRequest {
    code: string;
    language?: string;
    file_path?: string;
    input_data?: string;
}

export interface CodeExecutionResult {
    language: string;
    stdout: string;
    stderr: string;
    exit_code: number;
    success: boolean;
}

export interface CodeConversionRequest {
    code: string;
    from_language: string;
    to_language: string;
}

export interface CodeConversionResult {
    from_language: string;
    to_language: string;
    original_code: string;
    converted_code: string;
}

export interface LanguageInfo {
    name: string;
    info: {
        name: string;
        extensions: string[];
        runner: string;
        features: string[];
    };
}

export interface ProjectCreationResult {
    projectName: string;
    projectPath: string;
    filesCreated: string[];
    components: string[];
}

export class AeonforgeService {
    private client: AxiosInstance;
    private conversationId: string;

    constructor(private baseUrl: string) {
        this.client = axios.create({
            baseURL: baseUrl,
            timeout: 30000,
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        this.conversationId = `vscode_${Date.now()}`;
    }

    /**
     * Test connection to Aeonforge backend
     */
    async testConnection(): Promise<boolean> {
        try {
            const response = await this.client.get('/api/health');
            return response.status === 200;
        } catch (error) {
            console.error('Aeonforge backend connection failed:', error);
            return false;
        }
    }

    /**
     * Send a chat message to Aeonforge agents
     */
    async chat(message: string, context?: CodebaseContext): Promise<AeonforgeResponse> {
        const config = vscode.workspace.getConfiguration('aeonforge');
        const apiKeys = config.get<Record<string, string>>('apiKeys') || {};

        const payload = {
            message,
            conversation_id: this.conversationId,
            api_keys: apiKeys,
            context: context ? this.serializeContext(context) : undefined
        };

        try {
            const response = await this.client.post('/api/chat', payload);
            return response.data;
        } catch (error) {
            throw new Error(`Chat request failed: ${error}`);
        }
    }

    /**
     * Send approval response
     */
    async sendApproval(approved: boolean, approvalId: string): Promise<AeonforgeResponse> {
        const payload = {
            approval_id: approvalId,
            approved,
            conversation_id: this.conversationId
        };

        try {
            const response = await this.client.post('/api/approval', payload);
            return response.data;
        } catch (error) {
            throw new Error(`Approval request failed: ${error}`);
        }
    }

    /**
     * Generate code from description
     */
    async generateCode(description: string, context: CodebaseContext): Promise<AeonforgeResponse> {
        const message = `Generate code: ${description}`;
        return await this.chat(message, context);
    }

    /**
     * Refactor selected code
     */
    async refactorCode(code: string, instructions: string, context: CodebaseContext): Promise<AeonforgeResponse> {
        const message = `Refactor this code with the following instructions: ${instructions}\\n\\nCode to refactor:\\n\`\`\`\\n${code}\\n\`\`\``;
        return await this.chat(message, context);
    }

    /**
     * Explain selected code
     */
    async explainCode(code: string, context: CodebaseContext): Promise<AeonforgeResponse> {
        const message = `Please explain this code in detail:\\n\\n\`\`\`\\n${code}\\n\`\`\``;
        return await this.chat(message, context);
    }

    /**
     * Create a new project
     */
    async createProject(description: string, projectPath: string): Promise<ProjectCreationResult> {
        const config = vscode.workspace.getConfiguration('aeonforge');
        const apiKeys = config.get<Record<string, string>>('apiKeys') || {};

        const payload = {
            message: description,
            conversation_id: `project_${Date.now()}`,
            api_keys: apiKeys,
            project_path: projectPath
        };

        try {
            // First get the project plan
            const planResponse = await this.client.post('/api/chat', payload);
            
            if (planResponse.data.needs_approval) {
                // Auto-approve for project creation
                const approvalResponse = await this.client.post('/api/approval', {
                    approval_id: `auto_${Date.now()}`,
                    approved: true,
                    conversation_id: payload.conversation_id
                });

                return this.parseProjectResult(approvalResponse.data);
            }

            return this.parseProjectResult(planResponse.data);
        } catch (error) {
            throw new Error(`Project creation failed: ${error}`);
        }
    }

    /**
     * Analyze codebase
     */
    async analyzeCodebase(context: CodebaseContext): Promise<AeonforgeResponse> {
        const message = 'Please analyze this codebase and provide insights about its structure, patterns, and potential improvements.';
        return await this.chat(message, context);
    }

    /**
     * Get project insights
     */
    async getProjectInsights(context: CodebaseContext): Promise<AeonforgeResponse> {
        const message = 'Provide detailed insights about this project including architecture, dependencies, code quality, and suggestions for improvement.';
        return await this.chat(message, context);
    }

    /**
     * Fix diagnostics issues
     */
    async fixDiagnostics(diagnostics: vscode.Diagnostic[], context: CodebaseContext): Promise<AeonforgeResponse> {
        const issues = diagnostics.map(d => `${d.severity === vscode.DiagnosticSeverity.Error ? 'Error' : 'Warning'}: ${d.message} (Line ${d.range.start.line + 1})`).join('\\n');
        const message = `Please fix these code issues:\\n\\n${issues}`;
        return await this.chat(message, context);
    }

    private serializeContext(context: CodebaseContext): any {
        return {
            files: context.files.map(f => ({
                path: f.path,
                language: f.language,
                content: f.content?.substring(0, 10000), // Limit content size
                size: f.size
            })),
            structure: context.structure,
            diagnostics: context.diagnostics.length,
            activeFile: context.activeFile,
            selection: context.selection
        };
    }

    private parseProjectResult(response: AeonforgeResponse): ProjectCreationResult {
        // Extract project information from response
        const projectName = this.extractProjectName(response.message);
        const filesCreated = response.files_created || [];
        
        return {
            projectName,
            projectPath: '', // Will be set by caller
            filesCreated,
            components: [] // Extract from response
        };
    }

    private extractProjectName(message: string): string {
        // Extract project name from response message
        const match = message.match(/Project Created.*\`(.+?)\`/);
        return match ? match[1] : 'New Project';
    }

    // Multi-language code analysis methods
    
    /**
     * Analyze code in any programming language
     */
    async analyzeCode(request: CodeAnalysisRequest): Promise<CodeAnalysisResult> {
        try {
            const response = await this.client.post('/api/code/analyze', request);
            return response.data;
        } catch (error) {
            throw new Error(`Code analysis failed: ${error}`);
        }
    }

    /**
     * Generate code in any programming language
     */
    async generateMultiLangCode(request: CodeGenerationRequest): Promise<CodeGenerationResult> {
        try {
            const response = await this.client.post('/api/code/generate', request);
            return response.data;
        } catch (error) {
            throw new Error(`Code generation failed: ${error}`);
        }
    }

    /**
     * Refactor code with detailed analysis and planning
     */
    async createRefactoringPlan(request: CodeRefactoringRequest): Promise<RefactoringPlan> {
        try {
            const response = await this.client.post('/api/code/refactor', request);
            return response.data;
        } catch (error) {
            throw new Error(`Code refactoring failed: ${error}`);
        }
    }

    /**
     * Debug code and get suggestions
     */
    async debugCode(request: CodeAnalysisRequest): Promise<{ language: string; debug_suggestions: string[] }> {
        try {
            const response = await this.client.post('/api/code/debug', request);
            return response.data;
        } catch (error) {
            throw new Error(`Code debugging failed: ${error}`);
        }
    }

    /**
     * Execute code safely
     */
    async executeCode(request: CodeExecutionRequest): Promise<CodeExecutionResult> {
        try {
            const response = await this.client.post('/api/code/execute', request);
            return response.data;
        } catch (error) {
            throw new Error(`Code execution failed: ${error}`);
        }
    }

    /**
     * Convert code between programming languages
     */
    async convertCode(request: CodeConversionRequest): Promise<CodeConversionResult> {
        try {
            const response = await this.client.post('/api/code/convert', request);
            return response.data;
        } catch (error) {
            throw new Error(`Code conversion failed: ${error}`);
        }
    }

    /**
     * Get list of supported programming languages
     */
    async getSupportedLanguages(): Promise<LanguageInfo[]> {
        try {
            const response = await this.client.get('/api/languages');
            return response.data.languages;
        } catch (error) {
            throw new Error(`Failed to get supported languages: ${error}`);
        }
    }

    /**
     * Generate comprehensive code analysis report
     */
    async generateCodeReport(request: CodeAnalysisRequest): Promise<any> {
        try {
            const response = await this.client.post('/api/code/report', request);
            return response.data;
        } catch (error) {
            throw new Error(`Report generation failed: ${error}`);
        }
    }

    /**
     * Analyze current file using multi-language analysis
     */
    async analyzeCurrentFile(): Promise<CodeAnalysisResult | null> {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            return null;
        }

        const document = editor.document;
        const code = document.getText();
        const language = document.languageId;
        const filePath = document.fileName;

        return await this.analyzeCode({ code, language, file_path: filePath });
    }

    /**
     * Refactor selected code or current file
     */
    async refactorSelection(instructions: string): Promise<RefactoringPlan | null> {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            return null;
        }

        const document = editor.document;
        const selection = editor.selection;
        const code = selection.isEmpty ? document.getText() : document.getText(selection);
        const language = document.languageId;
        const filePath = document.fileName;

        return await this.createRefactoringPlan({ code, instructions, language, file_path: filePath });
    }
}