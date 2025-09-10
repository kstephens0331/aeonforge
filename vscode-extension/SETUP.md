# 🚀 Aeonforge VS Code Extension - Setup Guide

Complete guide to install and test your **Claude Code-like VS Code extension** powered by Aeonforge.

## 📋 Prerequisites

1. **✅ Aeonforge Backend Running**
   ```bash
   cd "C:\Users\usmc3\OneDrive\Documents\Stephens Code Programs\Aeonforge"
   start_backend.bat
   ```
   - Should be accessible at: `http://localhost:8000`
   - Test: `http://localhost:8000/api/health`

2. **✅ Node.js and npm**
   - Node.js 18+ required
   - Check: `node --version && npm --version`

3. **✅ VS Code** (obviously!)

## 🛠️ Installation Steps

### Step 1: Install Dependencies
```bash
cd "C:\Users\usmc3\OneDrive\Documents\Stephens Code Programs\Aeonforge\vscode-extension"
npm install
```

### Step 2: Compile TypeScript
```bash
npm run compile
```

### Step 3: Test the Extension
1. **Open VS Code** in the extension directory:
   ```bash
   code .
   ```

2. **Launch Extension Development Host**:
   - Press `F5` or go to Run & Debug → "Run Extension"
   - This opens a new VS Code window with your extension loaded

3. **Test Basic Functionality**:
   - In the new VS Code window, press `Cmd+Esc` (Mac) or `Ctrl+Esc` (Windows)
   - Should open the Aeonforge chat panel

## ⚙️ Configuration

### Step 1: Configure Extension Settings
In VS Code, go to **Settings** (`Cmd+,` / `Ctrl+,`) and add:

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

### Step 2: Test Backend Connection
1. Open a test project in the Extension Development Host
2. Press `Cmd+Esc` / `Ctrl+Esc` to open Aeonforge chat  
3. Type: "Hello, test connection"
4. Should get response from Aeonforge agents

## 🧪 Testing Guide

### Test 1: Basic Chat Interface
1. **Open Chat**: `Cmd+Esc` / `Ctrl+Esc`
2. **Send Message**: "Analyze this project"
3. **Expected**: Chat opens, message sent, response received

### Test 2: Codebase Analysis
1. **Open a project** with some code files
2. **Click**: "🔍 Analyze Codebase" button in chat
3. **Expected**: Analysis of project structure and files

### Test 3: Code Explanation  
1. **Select some code** in any file
2. **Right-click** → "Explain Code"
3. **Expected**: Detailed explanation appears in chat

### Test 4: Code Refactoring
1. **Select code** to refactor
2. **Right-click** → "Refactor Code"  
3. **Enter instructions**: "Make this more efficient"
4. **Expected**: Refactored code with diff preview

### Test 5: Project Creation
1. **Command Palette**: `Cmd+Shift+P` / `Ctrl+Shift+P`
2. **Run**: "Aeonforge: Create Project"
3. **Describe**: "Create a simple React todo app"
4. **Expected**: New project files created

## 🔧 Troubleshooting

### Issue: Extension Not Loading
**Solutions**:
```bash
# Recompile TypeScript
npm run compile

# Check for compilation errors
npx tsc --noEmit

# Restart VS Code Extension Development Host
```

### Issue: Backend Connection Failed
**Check**:
1. Backend running: `curl http://localhost:8000/api/health`
2. Settings correct: Check `aeonforge.backendUrl`
3. Firewall/proxy issues

### Issue: Chat Panel Not Opening  
**Solutions**:
1. Check keyboard shortcut conflicts
2. Use Command Palette instead: "Aeonforge: Open Chat"
3. Check VS Code Developer Console for errors

### Issue: No Response from Agents
**Check**:
1. Backend logs for errors
2. API keys configured (if needed)
3. Test backend directly with curl

## 📦 Package for Distribution

### Create Extension Package
```bash
# Install packaging tool
npm install -g vsce

# Package extension
vsce package

# Creates: aeonforge-code-1.0.0.vsix
```

### Install Packaged Extension
```bash
# Install in VS Code
code --install-extension aeonforge-code-1.0.0.vsix
```

## 🎯 Usage Examples

### Example 1: Build a Feature
```
User: "Add a login form to this React app"
Aeonforge: *analyzes codebase* → creates components, adds routing, implements auth
```

### Example 2: Fix Errors
```
User: "Fix the TypeScript errors in this file"  
Aeonforge: *analyzes diagnostics* → provides fixes with explanations
```

### Example 3: Code Review
```
User: "Review this function for performance issues"
Aeonforge: *analyzes code* → suggests optimizations with examples
```

## 🔄 Development Workflow

### Making Changes
1. **Edit source files** in `src/`
2. **Recompile**: `npm run compile`  
3. **Reload Extension**: `Cmd+R` / `Ctrl+R` in Extension Development Host
4. **Test changes**

### Debugging
1. **Set breakpoints** in TypeScript source
2. **F5** to launch with debugger
3. **Debug** in Extension Development Host
4. **Check logs** in VS Code Developer Console

## 🌟 Advanced Features

### Custom Commands
Add new commands in `package.json`:
```json
{
  "command": "aeonforge.customFeature",
  "title": "Custom Feature",
  "category": "Aeonforge"
}
```

### Additional Providers
Extend functionality by creating new providers:
- Code Lens Provider
- Hover Provider  
- Completion Provider
- Diagnostic Provider

## 🚀 Deployment Options

### Option 1: Local Installation
- Package with `vsce package`
- Install locally with `code --install-extension`

### Option 2: VS Code Marketplace  
- Publish with `vsce publish`
- Available to all VS Code users

### Option 3: Enterprise Distribution
- Package as `.vsix`
- Distribute through company channels

## ✅ Success Checklist

- [ ] ✅ Backend running and accessible
- [ ] ✅ Extension compiles without errors  
- [ ] ✅ Extension loads in Development Host
- [ ] ✅ Chat panel opens with `Cmd+Esc`/`Ctrl+Esc`
- [ ] ✅ Backend connection works
- [ ] ✅ Can send/receive messages  
- [ ] ✅ Codebase analysis works
- [ ] ✅ Code explanation works
- [ ] ✅ Code refactoring works
- [ ] ✅ Project creation works
- [ ] ✅ Settings configuration works

## 🎉 You Did It!

You now have a **fully functional Claude Code-like VS Code extension** powered by your Aeonforge multi-agent system! 

**Key Achievements**:
- ✅ **Complete VS Code integration**
- ✅ **All Claude Code capabilities** 
- ✅ **Multi-agent backend** 
- ✅ **Local and customizable**
- ✅ **Production-ready code**

**Next Steps**: Use your extension to build amazing projects with the power of Aeonforge's multi-agent system right inside VS Code!