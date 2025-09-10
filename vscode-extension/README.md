# 🤖 Aeonforge Code - VS Code Extension

Multi-Agent AI Development System with **Claude Code-like capabilities** powered by your local Aeonforge backend.

## ✨ Features

### 🎯 Core Capabilities
- **🔍 Full Codebase Intelligence** - Understands your entire project structure and dependencies
- **💬 Natural Language Chat** - Describe what you want to build in plain English  
- **✏️ Inline Code Editing** - Direct file edits with diff preview like Claude Code
- **🤖 Multi-Agent System** - Project Manager, Senior Developer, and specialist agents
- **⚡ Instant Access** - `Cmd+Esc` (Mac) / `Ctrl+Esc` (Windows/Linux) to open chat

### 🛠️ Development Tools
- **📊 Project Analysis** - Complete codebase analysis and insights
- **🔧 Code Refactoring** - AI-powered code improvements with context awareness
- **📝 Code Explanation** - Detailed explanations of selected code
- **🏗️ Project Creation** - Build complete projects from descriptions
- **🔍 Diagnostic Integration** - Automatic error detection and fixing suggestions

### 🎨 Interface Features
- **📱 Modern Chat Interface** - Beautiful, responsive chat panel
- **👀 Diff Preview** - See changes before applying them
- **🎛️ Customizable Settings** - Configure backend URL, API keys, and behavior
- **📋 Context Menus** - Right-click actions for common tasks
- **🔗 Deep VS Code Integration** - Works with existing VS Code features

## 🚀 Getting Started

### Prerequisites
1. **Aeonforge Backend Running** - Make sure your Aeonforge backend is running on `http://localhost:8000`
2. **SerpAPI Key** (optional) - For web search functionality

### Installation

1. **Install the Extension**
   ```bash
   cd vscode-extension
   npm install
   npm run compile
   ```

2. **Configure Settings**
   Open VS Code settings and configure:
   ```json
   {
     "aeonforge.backendUrl": "http://localhost:8000",
     "aeonforge.apiKeys": {
       "serpapi": "your-serpapi-key-here"
     },
     "aeonforge.enableInlineEdits": true,
     "aeonforge.autoSave": false
   }
   ```

3. **Start Using Aeonforge**
   - Press `Cmd+Esc` (Mac) or `Ctrl+Esc` (Windows/Linux) to open chat
   - Or use the Command Palette: `Aeonforge: Open Chat`

## 📖 Usage Guide

### 🎪 Main Chat Interface
- **Open Chat**: `Cmd+Esc` / `Ctrl+Esc`
- **Analyze Codebase**: Click "🔍 Analyze Codebase" button
- **Natural Conversations**: Ask questions about your code or describe what you want to build

### 🔧 Context Menu Actions
- **Right-click selected code** → "Explain Code" or "Refactor Code"
- **Right-click in Explorer** → "Analyze Codebase"

### ⌨️ Command Palette Commands
- `Aeonforge: Open Chat` - Open main chat interface
- `Aeonforge: Analyze Codebase` - Analyze current project
- `Aeonforge: Generate Code` - Generate code from description
- `Aeonforge: Create Project` - Create new project from description

### 💡 Example Usage

1. **Code Explanation**
   - Select code → Right-click → "Explain Code"
   - Get detailed explanations with context

2. **Code Refactoring**
   - Select code → Right-click → "Refactor Code" 
   - Describe how you want it improved

3. **Project Creation**
   - Command Palette → "Aeonforge: Create Project"
   - Describe your project: "Build a React app with TypeScript and Tailwind"

4. **Codebase Analysis**
   - Command Palette → "Aeonforge: Analyze Codebase"
   - Get insights, recommendations, and project overview

## ⚙️ Configuration

### Extension Settings

| Setting | Description | Default |
|---------|-------------|---------|
| `aeonforge.backendUrl` | URL of Aeonforge backend | `http://localhost:8000` |
| `aeonforge.apiKeys` | API keys for external services | `{}` |
| `aeonforge.enableInlineEdits` | Enable inline editing with diff preview | `true` |
| `aeonforge.autoSave` | Auto-save files after edits | `false` |

### API Keys Configuration
```json
{
  "aeonforge.apiKeys": {
    "serpapi": "your-serpapi-key-here"
  }
}
```

## 🏗️ Architecture

### Core Components
- **AeonforgeService** - Communication with backend API
- **CodebaseAnalyzer** - Full project understanding and analysis
- **ChatProvider** - Interactive chat interface with agents  
- **InlineEditProvider** - Code editing with diff preview
- **DiagnosticsCollector** - Error detection and monitoring

### Multi-Agent System
- **Project Manager** - Planning and coordination
- **Senior Developer** - Code implementation and review
- **Specialists** - Domain-specific expertise (AI, blockchain, security)

## 🔧 Development

### Building from Source
```bash
git clone <repository>
cd vscode-extension
npm install
npm run compile
```

### Running in Development
1. Open in VS Code
2. Press F5 to launch Extension Development Host
3. Test the extension in the new VS Code window

### Package for Distribution
```bash
npm install -g vsce
vsce package
```

## 🤝 Comparison to Claude Code

| Feature | Claude Code | Aeonforge Code |
|---------|-------------|----------------|
| **Codebase Intelligence** | ✅ | ✅ |
| **Inline Editing** | ✅ | ✅ |
| **Diff Preview** | ✅ | ✅ |
| **Chat Interface** | ✅ | ✅ |
| **Project Creation** | ✅ | ✅ |
| **Multi-Agent System** | ❌ | ✅ |
| **Local Backend** | ❌ | ✅ |
| **Customizable** | ❌ | ✅ |
| **Self-Hosted** | ❌ | ✅ |

## 🛠️ Troubleshooting

### Backend Connection Issues
1. Ensure Aeonforge backend is running: `http://localhost:8000/api/health`
2. Check `aeonforge.backendUrl` setting
3. Verify no firewall blocking the connection

### Extension Not Loading
1. Check VS Code Developer Console for errors
2. Ensure TypeScript compilation succeeded: `npm run compile`
3. Restart VS Code

### Chat Not Responding
1. Check backend logs for errors
2. Verify API keys are configured correctly
3. Test backend directly with curl

## 📝 License

This project is part of the Aeonforge Multi-Agent Development System.

## 🤖 About Aeonforge

Aeonforge is a comprehensive multi-agent AI development system that provides:
- **Phase 1**: Core agent framework with AutoGen
- **Phase 2**: Multi-agent collaboration
- **Phase 3**: Web interface and API
- **Phase 4**: VS Code integration (this extension)

Built with the philosophy of **no simulated data** - everything is real, functional, and production-ready.