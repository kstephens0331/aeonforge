/**
 * ChatProvider - Manages the chat interface with Aeonforge agents
 * Provides Claude Code-like chat experience
 */

import * as vscode from 'vscode';
import { AeonforgeService, AeonforgeResponse } from '../services/AeonforgeService';
import { CodebaseAnalyzer, CodebaseAnalysis } from '../services/CodebaseAnalyzer';

export interface ChatMessage {
    id: string;
    type: 'user' | 'assistant' | 'system';
    content: string;
    agent?: string;
    timestamp: Date;
    needsApproval?: boolean;
    approvalId?: string;
}

export class ChatProvider implements vscode.TreeDataProvider<ChatMessage> {
    private _onDidChangeTreeData: vscode.EventEmitter<ChatMessage | undefined | null | void> = new vscode.EventEmitter<ChatMessage | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<ChatMessage | undefined | null | void> = this._onDidChangeTreeData.event;

    private chatPanel: vscode.WebviewPanel | undefined;
    private messages: ChatMessage[] = [];

    constructor(
        private aeonforgeService: AeonforgeService,
        private codebaseAnalyzer: CodebaseAnalyzer
    ) {}

    /**
     * Open the main chat panel
     */
    async openChatPanel(): Promise<void> {
        if (this.chatPanel) {
            this.chatPanel.reveal();
            return;
        }

        this.chatPanel = vscode.window.createWebviewPanel(
            'aeonforgeChat',
            '🤖 Aeonforge Assistant',
            vscode.ViewColumn.Beside,
            {
                enableScripts: true,
                retainContextWhenHidden: true,
                localResourceRoots: []
            }
        );

        this.chatPanel.webview.html = this.getChatPanelContent();
        
        // Handle messages from webview
        this.chatPanel.webview.onDidReceiveMessage(async (message) => {
            await this.handleWebviewMessage(message);
        });

        this.chatPanel.onDidDispose(() => {
            this.chatPanel = undefined;
        });

        // Send initial welcome message
        await this.addSystemMessage('🚀 Aeonforge multi-agent development system ready! How can I help you build something amazing?');
    }

    /**
     * Show codebase analysis results
     */
    async showAnalysis(analysis: CodebaseAnalysis): Promise<void> {
        const analysisMessage = `## 🔍 Codebase Analysis Complete

**Project Overview:**
${analysis.overview}

**Key Insights:**
${analysis.insights.map(insight => `• ${insight}`).join('\\n')}

**Recommendations:**
${analysis.recommendations.map(rec => `• ${rec}`).join('\\n')}

**Project Structure:**
\`\`\`
${analysis.structure.structure.slice(0, 20).join('\\n')}
${analysis.structure.structure.length > 20 ? '... and more files' : ''}
\`\`\`

Ready to help you improve this codebase! What would you like to work on?`;

        await this.addAssistantMessage(analysisMessage, 'Senior Developer');
    }

    /**
     * Show code explanation
     */
    async showExplanation(response: AeonforgeResponse): Promise<void> {
        await this.addAssistantMessage(response.message, response.agent);
    }

    /**
     * Handle webview messages
     */
    private async handleWebviewMessage(message: any): Promise<void> {
        switch (message.type) {
            case 'sendMessage':
                await this.handleUserMessage(message.content);
                break;
            case 'sendApproval':
                await this.handleApproval(message.approved, message.approvalId);
                break;
            case 'clearChat':
                this.clearMessages();
                break;
            case 'analyzeCodebase':
                await this.analyzeCurrentCodebase();
                break;
        }
    }

    /**
     * Handle user message
     */
    private async handleUserMessage(content: string): Promise<void> {
        // Add user message to chat
        await this.addUserMessage(content);

        try {
            // Get current workspace context
            const context = await this.codebaseAnalyzer.getWorkspaceContext();
            
            // Send to Aeonforge
            const response = await this.aeonforgeService.chat(content, context);
            
            // Add assistant response
            await this.addAssistantMessage(response.message, response.agent, response.needs_approval, response.approval_task);
            
        } catch (error) {
            await this.addSystemMessage(`❌ Error: ${error}`);
        }
    }

    /**
     * Handle approval response
     */
    private async handleApproval(approved: boolean, approvalId: string): Promise<void> {
        try {
            const response = await this.aeonforgeService.sendApproval(approved, approvalId);
            await this.addAssistantMessage(response.message, response.agent);
        } catch (error) {
            await this.addSystemMessage(`❌ Approval error: ${error}`);
        }
    }

    /**
     * Analyze current codebase
     */
    private async analyzeCurrentCodebase(): Promise<void> {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            await this.addSystemMessage('❌ No workspace folder open');
            return;
        }

        try {
            const analysis = await this.codebaseAnalyzer.analyzeWorkspace(workspaceFolder);
            await this.showAnalysis(analysis);
        } catch (error) {
            await this.addSystemMessage(`❌ Analysis failed: ${error}`);
        }
    }

    /**
     * Add user message
     */
    private async addUserMessage(content: string): Promise<void> {
        const message: ChatMessage = {
            id: Date.now().toString(),
            type: 'user',
            content,
            timestamp: new Date()
        };

        this.messages.push(message);
        await this.sendMessageToWebview(message);
    }

    /**
     * Add assistant message
     */
    private async addAssistantMessage(content: string, agent?: string, needsApproval?: boolean, approvalTask?: string): Promise<void> {
        const message: ChatMessage = {
            id: Date.now().toString(),
            type: 'assistant',
            content,
            agent,
            timestamp: new Date(),
            needsApproval,
            approvalId: needsApproval ? `approval_${Date.now()}` : undefined
        };

        this.messages.push(message);
        await this.sendMessageToWebview(message);
    }

    /**
     * Add system message
     */
    private async addSystemMessage(content: string): Promise<void> {
        const message: ChatMessage = {
            id: Date.now().toString(),
            type: 'system',
            content,
            timestamp: new Date()
        };

        this.messages.push(message);
        await this.sendMessageToWebview(message);
    }

    /**
     * Send message to webview
     */
    private async sendMessageToWebview(message: ChatMessage): Promise<void> {
        if (this.chatPanel) {
            await this.chatPanel.webview.postMessage({
                type: 'newMessage',
                message
            });
        }
    }

    /**
     * Clear all messages
     */
    private clearMessages(): void {
        this.messages = [];
        if (this.chatPanel) {
            this.chatPanel.webview.postMessage({
                type: 'clearMessages'
            });
        }
    }

    /**
     * Get chat panel HTML content
     */
    private getChatPanelContent(): string {
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aeonforge Assistant</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
            margin: 0;
            padding: 0;
            background: var(--vscode-editor-background);
            color: var(--vscode-editor-foreground);
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        .header {
            padding: 16px;
            background: var(--vscode-titleBar-activeBackground);
            border-bottom: 1px solid var(--vscode-panel-border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .header h1 {
            margin: 0;
            font-size: 18px;
            font-weight: 600;
        }
        
        .header-actions {
            display: flex;
            gap: 8px;
        }
        
        .btn {
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: none;
            padding: 8px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            transition: background-color 0.2s;
        }
        
        .btn:hover {
            background: var(--vscode-button-hoverBackground);
        }
        
        .btn-secondary {
            background: var(--vscode-button-secondaryBackground);
            color: var(--vscode-button-secondaryForeground);
        }
        
        .btn-secondary:hover {
            background: var(--vscode-button-secondaryHoverBackground);
        }
        
        .chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }
        
        .message {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        
        .message-header {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 12px;
            opacity: 0.8;
        }
        
        .message-content {
            background: var(--vscode-input-background);
            padding: 12px 16px;
            border-radius: 8px;
            border: 1px solid var(--vscode-input-border);
            line-height: 1.5;
        }
        
        .message.user .message-content {
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            margin-left: 20%;
        }
        
        .message.assistant .message-content {
            background: var(--vscode-editor-inactiveSelectionBackground);
        }
        
        .message.system .message-content {
            background: var(--vscode-notificationToast-border);
            font-style: italic;
            text-align: center;
        }
        
        .agent-badge {
            background: var(--vscode-badge-background);
            color: var(--vscode-badge-foreground);
            padding: 2px 6px;
            border-radius: 12px;
            font-size: 10px;
            font-weight: 500;
        }
        
        .approval-section {
            margin-top: 12px;
            padding: 12px;
            background: var(--vscode-notificationWarning-background);
            border: 1px solid var(--vscode-notificationWarning-border);
            border-radius: 6px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .approval-buttons {
            display: flex;
            gap: 8px;
        }
        
        .btn-approve {
            background: var(--vscode-testing-iconPassed);
            color: white;
        }
        
        .btn-reject {
            background: var(--vscode-testing-iconFailed);
            color: white;
        }
        
        .input-section {
            padding: 16px;
            border-top: 1px solid var(--vscode-panel-border);
            background: var(--vscode-input-background);
        }
        
        .input-container {
            display: flex;
            gap: 8px;
            align-items: flex-end;
        }
        
        .input-field {
            flex: 1;
            background: var(--vscode-input-background);
            border: 1px solid var(--vscode-input-border);
            color: var(--vscode-input-foreground);
            padding: 12px;
            border-radius: 6px;
            resize: vertical;
            min-height: 20px;
            max-height: 120px;
            font-family: inherit;
            font-size: 14px;
        }
        
        .input-field:focus {
            outline: none;
            border-color: var(--vscode-focusBorder);
        }
        
        pre {
            background: var(--vscode-textCodeBlock-background);
            padding: 12px;
            border-radius: 4px;
            overflow-x: auto;
            border: 1px solid var(--vscode-input-border);
        }
        
        code {
            background: var(--vscode-textCodeBlock-background);
            padding: 2px 4px;
            border-radius: 2px;
            font-family: 'Courier New', monospace;
        }
        
        .loading {
            display: flex;
            align-items: center;
            gap: 8px;
            opacity: 0.7;
            font-style: italic;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .spinner {
            width: 16px;
            height: 16px;
            border: 2px solid var(--vscode-progressBar-background);
            border-top: 2px solid var(--vscode-button-background);
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 Aeonforge Assistant</h1>
        <div class="header-actions">
            <button class="btn btn-secondary" onclick="analyzeCodebase()">🔍 Analyze Codebase</button>
            <button class="btn btn-secondary" onclick="clearChat()">🗑️ Clear</button>
        </div>
    </div>
    
    <div class="chat-container" id="chatContainer">
        <!-- Messages will be inserted here -->
    </div>
    
    <div class="input-section">
        <div class="input-container">
            <textarea 
                id="messageInput" 
                class="input-field" 
                placeholder="Ask me anything about your code, or describe what you want to build..."
                rows="1"
            ></textarea>
            <button class="btn" onclick="sendMessage()" id="sendBtn">Send</button>
        </div>
    </div>

    <script>
        const vscode = acquireVsCodeApi();
        let isLoading = false;

        // Auto-resize textarea
        document.getElementById('messageInput').addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 120) + 'px';
        });

        // Send message on Enter (Shift+Enter for new line)
        document.getElementById('messageInput').addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (!message || isLoading) return;
            
            vscode.postMessage({
                type: 'sendMessage',
                content: message
            });
            
            input.value = '';
            input.style.height = 'auto';
            setLoading(true);
        }

        function sendApproval(approved, approvalId) {
            vscode.postMessage({
                type: 'sendApproval',
                approved: approved,
                approvalId: approvalId
            });
        }

        function clearChat() {
            document.getElementById('chatContainer').innerHTML = '';
            vscode.postMessage({ type: 'clearChat' });
        }

        function analyzeCodebase() {
            vscode.postMessage({ type: 'analyzeCodebase' });
        }

        function setLoading(loading) {
            isLoading = loading;
            const sendBtn = document.getElementById('sendBtn');
            
            if (loading) {
                sendBtn.innerHTML = '<div class="spinner"></div>';
                sendBtn.disabled = true;
            } else {
                sendBtn.innerHTML = 'Send';
                sendBtn.disabled = false;
            }
        }

        function addMessage(message) {
            const container = document.getElementById('chatContainer');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message ' + message.type;
            
            let agentBadge = '';
            if (message.agent) {
                agentBadge = '<span class="agent-badge">' + message.agent + '</span>';
            }
            
            let approvalSection = '';
            if (message.needsApproval) {
                approvalSection = \`
                    <div class="approval-section">
                        <div>
                            <strong>🤖 Agent approval required</strong>
                            <div style="font-size: 12px; margin-top: 4px;">The agent wants to proceed with this task. Do you approve?</div>
                        </div>
                        <div class="approval-buttons">
                            <button class="btn btn-approve" onclick="sendApproval(true, '\${message.approvalId}')">✅ Approve</button>
                            <button class="btn btn-reject" onclick="sendApproval(false, '\${message.approvalId}')">❌ Reject</button>
                        </div>
                    </div>
                \`;
            }
            
            messageDiv.innerHTML = \`
                <div class="message-header">
                    <span>\${message.type === 'user' ? '👤 You' : message.type === 'assistant' ? '🤖 Assistant' : '🔧 System'}</span>
                    \${agentBadge}
                    <span>\${new Date(message.timestamp).toLocaleTimeString()}</span>
                </div>
                <div class="message-content">
                    \${formatMessageContent(message.content)}
                    \${approvalSection}
                </div>
            \`;
            
            container.appendChild(messageDiv);
            container.scrollTop = container.scrollHeight;
            
            setLoading(false);
        }

        function formatMessageContent(content) {
            // Basic markdown-like formatting
            content = content.replace(/\`\`\`([\\s\\S]*?)\`\`\`/g, '<pre><code>$1</code></pre>');
            content = content.replace(/\`([^`]+)\`/g, '<code>$1</code>');
            content = content.replace(/\\*\\*([^*]+)\\*\\*/g, '<strong>$1</strong>');
            content = content.replace(/\\*([^*]+)\\*/g, '<em>$1</em>');
            content = content.replace(/\\n/g, '<br>');
            
            return content;
        }

        // Listen for messages from extension
        window.addEventListener('message', event => {
            const message = event.data;
            
            switch (message.type) {
                case 'newMessage':
                    addMessage(message.message);
                    break;
                case 'clearMessages':
                    document.getElementById('chatContainer').innerHTML = '';
                    break;
            }
        });
    </script>
</body>
</html>`;
    }

    // TreeDataProvider implementation
    getTreeItem(element: ChatMessage): vscode.TreeItem {
        const treeItem = new vscode.TreeItem(
            element.content.substring(0, 50) + (element.content.length > 50 ? '...' : ''),
            vscode.TreeItemCollapsibleState.None
        );
        
        treeItem.tooltip = element.content;
        treeItem.description = element.agent || element.type;
        
        return treeItem;
    }

    getChildren(element?: ChatMessage): Thenable<ChatMessage[]> {
        if (!element) {
            return Promise.resolve(this.messages);
        }
        return Promise.resolve([]);
    }
}