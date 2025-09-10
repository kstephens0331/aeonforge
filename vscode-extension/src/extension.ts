/**
 * Aeonforge VS Code Extension
 * Multi-Agent AI Development System with Claude Code-like capabilities
 */

import * as vscode from 'vscode';
import { AeonforgeService } from './services/AeonforgeService';
import { CodebaseAnalyzer } from './services/CodebaseAnalyzer';
import { InlineEditProvider } from './providers/InlineEditProvider';
import { ChatProvider } from './providers/ChatProvider';
import { DiagnosticsCollector } from './services/DiagnosticsCollector';
import { AeonforgeCompletionProvider } from './providers/CompletionProvider';
import { AeonforgeHoverProvider } from './providers/HoverProvider';
import { AeonforgeCodeLensProvider } from './providers/CodeLensProvider';
import { StatusBarManager } from './services/StatusBarManager';

let aeonforgeService: AeonforgeService;
let codebaseAnalyzer: CodebaseAnalyzer;
let inlineEditProvider: InlineEditProvider;
let chatProvider: ChatProvider;
let diagnosticsCollector: DiagnosticsCollector;
let completionProvider: AeonforgeCompletionProvider;
let hoverProvider: AeonforgeHoverProvider;
let codeLensProvider: AeonforgeCodeLensProvider;
let statusBarManager: StatusBarManager;

export function activate(context: vscode.ExtensionContext) {
    console.log('🚀 Aeonforge Code extension is now active!');

    // Initialize core services
    const config = vscode.workspace.getConfiguration('aeonforge');
    const backendUrl = config.get<string>('backendUrl') || 'http://localhost:8000';
    
    aeonforgeService = new AeonforgeService(backendUrl);
    codebaseAnalyzer = new CodebaseAnalyzer();
    inlineEditProvider = new InlineEditProvider(aeonforgeService);
    chatProvider = new ChatProvider(aeonforgeService, codebaseAnalyzer);
    diagnosticsCollector = new DiagnosticsCollector();
    
    // Initialize new providers
    completionProvider = new AeonforgeCompletionProvider(aeonforgeService, codebaseAnalyzer);
    hoverProvider = new AeonforgeHoverProvider(aeonforgeService);
    codeLensProvider = new AeonforgeCodeLensProvider(aeonforgeService);
    statusBarManager = new StatusBarManager(aeonforgeService);

    // Register chat panel provider
    const chatViewProvider = vscode.window.createTreeView('aeonforgeChat', {
        treeDataProvider: chatProvider
    });

    // Main command: Open Aeonforge Chat (Cmd+Esc / Ctrl+Esc)
    const openChatCommand = vscode.commands.registerCommand('aeonforge.openChat', async () => {
        await chatProvider.openChatPanel();
    });

    // Analyze entire codebase
    const analyzeCodebaseCommand = vscode.commands.registerCommand('aeonforge.analyzeCodebase', async () => {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            vscode.window.showErrorMessage('No workspace folder open');
            return;
        }

        vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: "🔍 Analyzing codebase with Aeonforge...",
            cancellable: false
        }, async (progress) => {
            try {
                const analysis = await codebaseAnalyzer.analyzeWorkspace(workspaceFolder);
                await chatProvider.showAnalysis(analysis);
                vscode.window.showInformationMessage('✅ Codebase analysis complete!');
            } catch (error) {
                vscode.window.showErrorMessage(`Analysis failed: ${error}`);
            }
        });
    });

    // Generate code from description
    const generateCodeCommand = vscode.commands.registerCommand('aeonforge.generateCode', async () => {
        const description = await vscode.window.showInputBox({
            prompt: 'Describe what you want to build',
            placeHolder: 'e.g., Create a REST API for user management'
        });

        if (!description) return;

        vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: "🤖 Generating code with Aeonforge...",
            cancellable: false
        }, async () => {
            try {
                const context = await codebaseAnalyzer.getWorkspaceContext();
                const result = await aeonforgeService.generateCode(description, context);
                await inlineEditProvider.applyCodeGeneration(result);
                vscode.window.showInformationMessage('✅ Code generation complete!');
            } catch (error) {
                vscode.window.showErrorMessage(`Code generation failed: ${error}`);
            }
        });
    });

    // Refactor selected code  
    const refactorCodeCommand = vscode.commands.registerCommand('aeonforge.refactorCode', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor || editor.selection.isEmpty) {
            vscode.window.showErrorMessage('Please select code to refactor');
            return;
        }

        const selectedText = editor.document.getText(editor.selection);
        const instructions = await vscode.window.showInputBox({
            prompt: 'How would you like to refactor this code?',
            placeHolder: 'e.g., Extract into reusable functions, optimize performance'
        });

        if (!instructions) return;

        vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: "🔧 Refactoring code...",
            cancellable: false
        }, async () => {
            try {
                const context = await codebaseAnalyzer.getFileContext(editor.document);
                const result = await aeonforgeService.refactorCode(selectedText, instructions, context);
                await inlineEditProvider.applyRefactoring(editor, result);
            } catch (error) {
                vscode.window.showErrorMessage(`Refactoring failed: ${error}`);
            }
        });
    });

    // Explain selected code
    const explainCodeCommand = vscode.commands.registerCommand('aeonforge.explainCode', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor || editor.selection.isEmpty) {
            vscode.window.showErrorMessage('Please select code to explain');
            return;
        }

        const selectedText = editor.document.getText(editor.selection);
        
        try {
            const context = await codebaseAnalyzer.getFileContext(editor.document);
            const explanation = await aeonforgeService.explainCode(selectedText, context);
            await chatProvider.showExplanation(explanation);
        } catch (error) {
            vscode.window.showErrorMessage(`Code explanation failed: ${error}`);
        }
    });

    // Create new project
    const createProjectCommand = vscode.commands.registerCommand('aeonforge.createProject', async () => {
        const description = await vscode.window.showInputBox({
            prompt: 'Describe the project you want to create',
            placeHolder: 'e.g., Build a React app with TypeScript and Tailwind CSS'
        });

        if (!description) return;

        const folderUri = await vscode.window.showOpenDialog({
            canSelectFiles: false,
            canSelectFolders: true,
            canSelectMany: false,
            openLabel: 'Select Project Location'
        });

        if (!folderUri) return;

        vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: "🏗️ Creating project with Aeonforge...",
            cancellable: false
        }, async () => {
            try {
                const projectPath = folderUri[0].fsPath;
                const result = await aeonforgeService.createProject(description, projectPath);
                
                // Open the new project
                const projectUri = vscode.Uri.file(result.projectPath);
                await vscode.commands.executeCommand('vscode.openFolder', projectUri);
                
                vscode.window.showInformationMessage(`✅ Project created: ${result.projectName}`);
            } catch (error) {
                vscode.window.showErrorMessage(`Project creation failed: ${error}`);
            }
        });
    });

    // Monitor file changes and diagnostics
    const fileWatcher = vscode.workspace.onDidChangeTextDocument((event) => {
        diagnosticsCollector.updateDiagnostics(event.document);
    });

    const diagnosticWatcher = vscode.languages.onDidChangeDiagnostics((event) => {
        diagnosticsCollector.collectDiagnostics(event);
    });

    // Register language providers
    const supportedLanguages = [
        'python', 'javascript', 'typescript', 'java', 'cpp', 'csharp',
        'go', 'rust', 'php', 'ruby', 'swift', 'kotlin', 'html', 'css',
        'sql', 'shellscript', 'powershell'
    ];
    
    const completionDisposable = vscode.languages.registerCompletionItemProvider(
        supportedLanguages,
        completionProvider,
        '.', '('
    );
    
    const hoverDisposable = vscode.languages.registerHoverProvider(
        supportedLanguages,
        hoverProvider
    );
    
    const codeLensDisposable = vscode.languages.registerCodeLensProvider(
        supportedLanguages,
        codeLensProvider
    );

    // Register additional multi-language commands
    const analyzeCurrentFileCommand = vscode.commands.registerCommand('aeonforge.analyzeCurrentFile', async () => {
        try {
            statusBarManager.showProgress('Analyzing file...');
            const result = await aeonforgeService.analyzeCurrentFile();
            
            if (result) {
                statusBarManager.showSuccess('Analysis complete');
                const message = `**Code Quality**: ${Math.round(result.quality.overall_score)}%\n**Complexity**: ${result.analysis.complexity_score}\n**Functions**: ${result.analysis.functions.length}\n**Classes**: ${result.analysis.classes.length}`;
                vscode.window.showInformationMessage(message);
            } else {
                vscode.window.showWarningMessage('No active file to analyze');
            }
        } catch (error) {
            statusBarManager.showError('Analysis failed');
            vscode.window.showErrorMessage(`Analysis failed: ${error}`);
        }
    });

    const convertCodeCommand = vscode.commands.registerCommand('aeonforge.convertCode', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No active editor');
            return;
        }

        const selection = editor.selection;
        const code = selection.isEmpty ? editor.document.getText() : editor.document.getText(selection);
        const fromLanguage = editor.document.languageId;

        const targetLanguages = ['python', 'javascript', 'typescript', 'java', 'cpp', 'csharp', 'go', 'rust'];
        const toLanguage = await vscode.window.showQuickPick(
            targetLanguages.filter(lang => lang !== fromLanguage),
            { placeHolder: 'Convert to which language?' }
        );

        if (!toLanguage) return;

        try {
            statusBarManager.showProgress('Converting code...');
            const result = await aeonforgeService.convertCode({
                code,
                from_language: fromLanguage,
                to_language: toLanguage
            });

            // Show converted code in new document
            const newDoc = await vscode.workspace.openTextDocument({
                content: result.converted_code,
                language: toLanguage
            });
            await vscode.window.showTextDocument(newDoc);
            statusBarManager.showSuccess('Code converted');

        } catch (error) {
            statusBarManager.showError('Conversion failed');
            vscode.window.showErrorMessage(`Code conversion failed: ${error}`);
        }
    });

    const executeCodeCommand = vscode.commands.registerCommand('aeonforge.executeCode', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No active editor');
            return;
        }

        const selection = editor.selection;
        const code = selection.isEmpty ? editor.document.getText() : editor.document.getText(selection);
        const language = editor.document.languageId;

        try {
            statusBarManager.showProgress('Executing code...');
            const result = await aeonforgeService.executeCode({
                code,
                language,
                file_path: editor.document.fileName
            });

            // Show output in new document
            const outputContent = `Exit Code: ${result.exit_code}\n\nSTDOUT:\n${result.stdout}\n\nSTDERR:\n${result.stderr}`;
            const outputDoc = await vscode.workspace.openTextDocument({
                content: outputContent,
                language: 'plaintext'
            });
            await vscode.window.showTextDocument(outputDoc, vscode.ViewColumn.Beside);
            
            if (result.success) {
                statusBarManager.showSuccess('Code executed');
            } else {
                statusBarManager.showError('Execution failed');
            }

        } catch (error) {
            statusBarManager.showError('Execution failed');
            vscode.window.showErrorMessage(`Code execution failed: ${error}`);
        }
    });

    const explainHoverCommand = vscode.commands.registerCommand('aeonforge.explainHover', async (args) => {
        const { word, context, type } = JSON.parse(args);
        
        try {
            const message = `Explain this ${type}: ${word}\n\nContext:\n${context}`;
            await chatProvider.sendMessage(message);
            await chatProvider.openChatPanel();
        } catch (error) {
            vscode.window.showErrorMessage(`Explanation failed: ${error}`);
        }
    });

    // Quality report commands
    const showQualityReportCommand = vscode.commands.registerCommand('aeonforge.showQualityReport', async (fileName?) => {
        try {
            const editor = vscode.window.activeTextEditor;
            if (!editor && !fileName) {
                vscode.window.showErrorMessage('No active file to analyze');
                return;
            }

            const document = editor?.document;
            const code = document ? document.getText() : '';
            const language = document ? document.languageId : '';
            const filePath = fileName || document?.fileName || '';

            const report = await aeonforgeService.generateCodeReport({
                code,
                language,
                file_path: filePath
            });

            // Show report in webview or new document
            const reportContent = JSON.stringify(report, null, 2);
            const reportDoc = await vscode.workspace.openTextDocument({
                content: reportContent,
                language: 'json'
            });
            await vscode.window.showTextDocument(reportDoc, vscode.ViewColumn.Beside);

        } catch (error) {
            vscode.window.showErrorMessage(`Quality report failed: ${error}`);
        }
    });

    // Set context for views
    vscode.commands.executeCommand('setContext', 'aeonforge:enabled', true);

    // Register all disposables
    context.subscriptions.push(
        openChatCommand,
        analyzeCodebaseCommand, 
        generateCodeCommand,
        refactorCodeCommand,
        explainCodeCommand,
        createProjectCommand,
        analyzeCurrentFileCommand,
        convertCodeCommand,
        executeCodeCommand,
        explainHoverCommand,
        showQualityReportCommand,
        chatViewProvider,
        fileWatcher,
        diagnosticWatcher,
        completionDisposable,
        hoverDisposable,
        codeLensDisposable,
        statusBarManager
    );

    // Show welcome message
    vscode.window.showInformationMessage(
        '🤖 Aeonforge Code is ready! Press Cmd+Esc (Mac) or Ctrl+Esc (Windows/Linux) to start.',
        'Open Chat'
    ).then((selection) => {
        if (selection === 'Open Chat') {
            vscode.commands.executeCommand('aeonforge.openChat');
        }
    });
}

export function deactivate() {
    console.log('🔄 Aeonforge Code extension deactivated');
}