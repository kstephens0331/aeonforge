/**
 * InlineEditProvider - Handles inline code editing with diff preview
 * Provides Claude Code-like inline editing experience
 */

import * as vscode from 'vscode';
import { AeonforgeService, AeonforgeResponse, CodeEdit } from '../services/AeonforgeService';

export class InlineEditProvider {
    constructor(private aeonforgeService: AeonforgeService) {}

    /**
     * Apply code generation results
     */
    async applyCodeGeneration(response: AeonforgeResponse): Promise<void> {
        if (response.edits && response.edits.length > 0) {
            await this.applyCodeEdits(response.edits);
        } else if (response.files_created && response.files_created.length > 0) {
            await this.handleFileCreation(response);
        } else {
            // Show response in a new document
            await this.showInNewDocument(response.message, 'Generated Code');
        }
    }

    /**
     * Apply refactoring results
     */
    async applyRefactoring(editor: vscode.TextEditor, response: AeonforgeResponse): Promise<void> {
        if (response.edits && response.edits.length > 0) {
            await this.applyCodeEdits(response.edits);
        } else {
            // Extract code from response and replace selection
            const codeBlocks = this.extractCodeBlocks(response.message);
            if (codeBlocks.length > 0) {
                await this.replaceSelection(editor, codeBlocks[0]);
            } else {
                vscode.window.showInformationMessage('Refactoring suggestions provided in chat.');
            }
        }
    }

    /**
     * Apply multiple code edits
     */
    private async applyCodeEdits(edits: CodeEdit[]): Promise<void> {
        const config = vscode.workspace.getConfiguration('aeonforge');
        const enableInlineEdits = config.get<boolean>('enableInlineEdits', true);
        const autoSave = config.get<boolean>('autoSave', false);

        if (!enableInlineEdits) {
            // Show edits in diff view instead
            await this.showEditsInDiff(edits);
            return;
        }

        for (const edit of edits) {
            try {
                await this.applyEdit(edit, autoSave);
            } catch (error) {
                vscode.window.showErrorMessage(`Failed to apply edit to ${edit.filePath}: ${error}`);
            }
        }

        vscode.window.showInformationMessage(`✅ Applied ${edits.length} code edit(s)`);
    }

    /**
     * Apply a single code edit
     */
    private async applyEdit(edit: CodeEdit, autoSave: boolean): Promise<void> {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            throw new Error('No workspace folder open');
        }

        const filePath = vscode.Uri.joinPath(workspaceFolder.uri, edit.filePath);

        switch (edit.operation) {
            case 'create':
                await this.createFile(filePath, edit.content);
                break;
            case 'edit':
                await this.editFile(filePath, edit.content, edit.startLine, edit.endLine);
                break;
            case 'delete':
                await this.deleteFile(filePath);
                break;
        }

        if (autoSave) {
            const document = await vscode.workspace.openTextDocument(filePath);
            await document.save();
        }
    }

    /**
     * Create a new file
     */
    private async createFile(filePath: vscode.Uri, content: string): Promise<void> {
        const workspaceEdit = new vscode.WorkspaceEdit();
        workspaceEdit.createFile(filePath, { overwrite: false });
        workspaceEdit.insert(filePath, new vscode.Position(0, 0), content);
        
        await vscode.workspace.applyEdit(workspaceEdit);
        
        // Open the new file
        const document = await vscode.workspace.openTextDocument(filePath);
        await vscode.window.showTextDocument(document);
    }

    /**
     * Edit existing file
     */
    private async editFile(
        filePath: vscode.Uri, 
        content: string, 
        startLine?: number, 
        endLine?: number
    ): Promise<void> {
        const document = await vscode.workspace.openTextDocument(filePath);
        const workspaceEdit = new vscode.WorkspaceEdit();

        if (startLine !== undefined && endLine !== undefined) {
            // Replace specific lines
            const start = new vscode.Position(startLine, 0);
            const end = new vscode.Position(endLine, document.lineAt(endLine).text.length);
            const range = new vscode.Range(start, end);
            
            workspaceEdit.replace(filePath, range, content);
        } else {
            // Replace entire file content
            const fullRange = new vscode.Range(
                document.positionAt(0),
                document.positionAt(document.getText().length)
            );
            
            workspaceEdit.replace(filePath, fullRange, content);
        }

        await vscode.workspace.applyEdit(workspaceEdit);

        // Show the edited file with diff preview
        await this.showDiffPreview(document, content, startLine, endLine);
    }

    /**
     * Delete file
     */
    private async deleteFile(filePath: vscode.Uri): Promise<void> {
        const choice = await vscode.window.showWarningMessage(
            `Delete file ${vscode.workspace.asRelativePath(filePath)}?`,
            { modal: true },
            'Delete',
            'Cancel'
        );

        if (choice === 'Delete') {
            const workspaceEdit = new vscode.WorkspaceEdit();
            workspaceEdit.deleteFile(filePath);
            await vscode.workspace.applyEdit(workspaceEdit);
        }
    }

    /**
     * Show diff preview for edits
     */
    private async showDiffPreview(
        document: vscode.TextDocument,
        newContent: string,
        startLine?: number,
        endLine?: number
    ): Promise<void> {
        // Create a temporary file with the new content
        const tempUri = vscode.Uri.parse(`untitled:${document.fileName}.new`);
        const tempDocument = await vscode.workspace.openTextDocument(tempUri.with({ 
            scheme: 'untitled'
        }));

        const workspaceEdit = new vscode.WorkspaceEdit();
        workspaceEdit.insert(tempUri, new vscode.Position(0, 0), newContent);
        await vscode.workspace.applyEdit(workspaceEdit);

        // Show diff view
        await vscode.commands.executeCommand(
            'vscode.diff',
            document.uri,
            tempUri,
            `${vscode.workspace.asRelativePath(document.fileName)} ↔ Aeonforge Edit`
        );
    }

    /**
     * Show edits in diff view instead of applying directly
     */
    private async showEditsInDiff(edits: CodeEdit[]): Promise<void> {
        for (const edit of edits) {
            const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
            if (!workspaceFolder) continue;

            const filePath = vscode.Uri.joinPath(workspaceFolder.uri, edit.filePath);
            
            if (edit.operation === 'edit' || edit.operation === 'create') {
                try {
                    let originalDocument: vscode.TextDocument;
                    
                    if (edit.operation === 'create') {
                        // Create empty document for new files
                        const emptyUri = vscode.Uri.parse('untitled:');
                        originalDocument = await vscode.workspace.openTextDocument(emptyUri);
                    } else {
                        originalDocument = await vscode.workspace.openTextDocument(filePath);
                    }

                    await this.showDiffPreview(originalDocument, edit.content);
                } catch (error) {
                    vscode.window.showErrorMessage(`Failed to show diff for ${edit.filePath}: ${error}`);
                }
            }
        }
    }

    /**
     * Handle file creation from response
     */
    private async handleFileCreation(response: AeonforgeResponse): Promise<void> {
        if (!response.files_created || response.files_created.length === 0) return;

        const choice = await vscode.window.showInformationMessage(
            `Aeonforge created ${response.files_created.length} files. Would you like to open the project folder?`,
            'Open Folder',
            'Show Files',
            'Later'
        );

        if (choice === 'Open Folder') {
            // Try to determine project folder from file paths
            const firstFile = response.files_created[0];
            const projectPath = firstFile.split('/')[0];
            
            const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
            if (workspaceFolder) {
                const projectUri = vscode.Uri.joinPath(workspaceFolder.uri, projectPath);
                await vscode.commands.executeCommand('vscode.openFolder', projectUri, true);
            }
        } else if (choice === 'Show Files') {
            // Open first few files
            const filesToShow = response.files_created.slice(0, 3);
            const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
            
            if (workspaceFolder) {
                for (const filePath of filesToShow) {
                    try {
                        const fileUri = vscode.Uri.joinPath(workspaceFolder.uri, filePath);
                        const document = await vscode.workspace.openTextDocument(fileUri);
                        await vscode.window.showTextDocument(document, { preview: false });
                    } catch (error) {
                        console.error(`Failed to open file ${filePath}:`, error);
                    }
                }
            }
        }
    }

    /**
     * Replace selected text in editor
     */
    private async replaceSelection(editor: vscode.TextEditor, newContent: string): Promise<void> {
        const selection = editor.selection;
        
        // Show diff preview first
        const choice = await vscode.window.showInformationMessage(
            'Preview the refactored code?',
            'Preview Diff',
            'Apply Directly',
            'Cancel'
        );

        if (choice === 'Cancel') return;

        if (choice === 'Preview Diff') {
            // Create temp document with the refactored code
            const originalText = editor.document.getText();
            const beforeSelection = editor.document.getText(new vscode.Range(
                new vscode.Position(0, 0),
                selection.start
            ));
            const afterSelection = editor.document.getText(new vscode.Range(
                selection.end,
                editor.document.positionAt(originalText.length)
            ));
            
            const newFullContent = beforeSelection + newContent + afterSelection;
            
            // Show diff
            const tempUri = vscode.Uri.parse(`untitled:${editor.document.fileName}.refactored`);
            const tempDocument = await vscode.workspace.openTextDocument(tempUri);
            
            const workspaceEdit = new vscode.WorkspaceEdit();
            workspaceEdit.insert(tempUri, new vscode.Position(0, 0), newFullContent);
            await vscode.workspace.applyEdit(workspaceEdit);

            await vscode.commands.executeCommand(
                'vscode.diff',
                editor.document.uri,
                tempUri,
                `${vscode.workspace.asRelativePath(editor.document.fileName)} ↔ Refactored`
            );
        } else {
            // Apply directly
            const workspaceEdit = new vscode.WorkspaceEdit();
            workspaceEdit.replace(editor.document.uri, selection, newContent);
            await vscode.workspace.applyEdit(workspaceEdit);
        }
    }

    /**
     * Show content in a new document
     */
    private async showInNewDocument(content: string, title: string): Promise<void> {
        const document = await vscode.workspace.openTextDocument({
            content,
            language: 'markdown'
        });
        
        await vscode.window.showTextDocument(document, {
            preview: false,
            viewColumn: vscode.ViewColumn.Beside
        });
    }

    /**
     * Extract code blocks from markdown-style text
     */
    private extractCodeBlocks(text: string): string[] {
        const codeBlockRegex = /```(?:\\w+)?\\n([\\s\\S]*?)```/g;
        const matches = [];
        let match;
        
        while ((match = codeBlockRegex.exec(text)) !== null) {
            matches.push(match[1].trim());
        }
        
        return matches;
    }
}