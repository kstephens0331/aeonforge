/**
 * StatusBarManager - Manages VS Code status bar integration
 */

import * as vscode from 'vscode';
import { AeonforgeService } from './AeonforgeService';

export class StatusBarManager {
    private statusBarItem: vscode.StatusBarItem;
    private analysisStatusItem: vscode.StatusBarItem;
    private qualityStatusItem: vscode.StatusBarItem;
    private connectionStatusItem: vscode.StatusBarItem;

    constructor(private aeonforgeService: AeonforgeService) {
        // Main Aeonforge status item
        this.statusBarItem = vscode.window.createStatusBarItem(
            vscode.StatusBarAlignment.Left, 
            100
        );
        this.statusBarItem.command = 'aeonforge.openChat';
        this.statusBarItem.tooltip = 'Click to open Aeonforge Chat';
        
        // Analysis status item
        this.analysisStatusItem = vscode.window.createStatusBarItem(
            vscode.StatusBarAlignment.Left,
            99
        );
        this.analysisStatusItem.command = 'aeonforge.analyzeCurrentFile';
        this.analysisStatusItem.tooltip = 'Click to analyze current file';
        
        // Code quality indicator
        this.qualityStatusItem = vscode.window.createStatusBarItem(
            vscode.StatusBarAlignment.Left,
            98
        );
        this.qualityStatusItem.command = 'aeonforge.showQualityReport';
        
        // Connection status
        this.connectionStatusItem = vscode.window.createStatusBarItem(
            vscode.StatusBarAlignment.Right,
            100
        );
        this.connectionStatusItem.command = 'aeonforge.checkConnection';
        
        this.initializeStatusBar();
        this.startPeriodicUpdates();
        this.setupEventListeners();
    }

    private initializeStatusBar(): void {
        // Set initial status
        this.statusBarItem.text = '🤖 Aeonforge';
        this.statusBarItem.backgroundColor = undefined;
        this.statusBarItem.show();
        
        this.analysisStatusItem.text = '$(search) Analyze';
        this.analysisStatusItem.show();
        
        this.updateConnectionStatus();
        this.updateCurrentFileStatus();
    }

    private setupEventListeners(): void {
        // Update status when active editor changes
        vscode.window.onDidChangeActiveTextEditor(() => {
            this.updateCurrentFileStatus();
        });
        
        // Update status when text document changes
        vscode.workspace.onDidChangeTextDocument((event) => {
            const activeEditor = vscode.window.activeTextEditor;
            if (activeEditor && event.document === activeEditor.document) {
                this.scheduleAnalysisUpdate();
            }
        });
        
        // Update status when configuration changes
        vscode.workspace.onDidChangeConfiguration((event) => {
            if (event.affectsConfiguration('aeonforge')) {
                this.updateConnectionStatus();
            }
        });
    }

    private scheduleAnalysisUpdate(): void {
        // Debounce analysis updates
        clearTimeout((this as any).analysisTimeout);
        (this as any).analysisTimeout = setTimeout(() => {
            this.updateCurrentFileStatus();
        }, 2000);
    }

    private startPeriodicUpdates(): void {
        // Update connection status every 30 seconds
        setInterval(() => {
            this.updateConnectionStatus();
        }, 30000);
        
        // Update file analysis every 5 minutes for active file
        setInterval(() => {
            this.updateCurrentFileStatus();
        }, 300000);
    }

    private async updateConnectionStatus(): Promise<void> {
        try {
            // Test connection to backend
            const languages = await this.aeonforgeService.getSupportedLanguages();
            
            this.connectionStatusItem.text = `$(check) Aeonforge (${languages.length} langs)`;
            this.connectionStatusItem.backgroundColor = undefined;
            this.connectionStatusItem.tooltip = `Connected to Aeonforge backend\nSupported languages: ${languages.length}`;
            this.connectionStatusItem.show();
            
            // Update main status to indicate connection
            this.statusBarItem.backgroundColor = undefined;
            
        } catch (error) {
            this.connectionStatusItem.text = '$(error) Aeonforge Offline';
            this.connectionStatusItem.backgroundColor = new vscode.ThemeColor('statusBarItem.errorBackground');
            this.connectionStatusItem.tooltip = `Connection failed: ${error}`;
            this.connectionStatusItem.show();
            
            // Update main status to indicate disconnection
            this.statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.warningBackground');
            this.statusBarItem.tooltip = 'Aeonforge backend is offline - click to retry';
        }
    }

    private async updateCurrentFileStatus(): Promise<void> {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            this.analysisStatusItem.hide();
            this.qualityStatusItem.hide();
            return;
        }

        const document = editor.document;
        const language = document.languageId;
        
        // Check if language is supported
        try {
            const supportedLanguages = await this.aeonforgeService.getSupportedLanguages();
            const isSupported = supportedLanguages.some(lang => 
                lang.info.extensions.some(ext => document.fileName.endsWith(ext))
            );
            
            if (!isSupported) {
                this.analysisStatusItem.text = `$(info) ${language} (unsupported)`;
                this.analysisStatusItem.tooltip = 'Language not supported by Aeonforge';
                this.analysisStatusItem.show();
                this.qualityStatusItem.hide();
                return;
            }
            
            // Show analyzing status
            this.analysisStatusItem.text = `$(loading~spin) Analyzing ${language}...`;
            this.analysisStatusItem.show();
            
            // Perform analysis
            const analysis = await this.aeonforgeService.analyzeCode({
                code: document.getText(),
                language: language,
                file_path: document.fileName
            });
            
            // Update analysis status
            this.analysisStatusItem.text = `$(search) ${language} (${analysis.analysis.functions.length}f, ${analysis.analysis.classes.length}c)`;
            this.analysisStatusItem.tooltip = `Functions: ${analysis.analysis.functions.length}, Classes: ${analysis.analysis.classes.length}, Complexity: ${analysis.analysis.complexity_score}`;
            
            // Update quality status
            const qualityScore = Math.round(analysis.quality.overall_score);
            const qualityIcon = this.getQualityIcon(qualityScore);
            const qualityColor = this.getQualityColor(qualityScore);
            
            this.qualityStatusItem.text = `${qualityIcon} ${qualityScore}%`;
            this.qualityStatusItem.backgroundColor = qualityColor;
            this.qualityStatusItem.tooltip = this.buildQualityTooltip(analysis.quality);
            this.qualityStatusItem.show();
            
            // Show issues count if any
            if (analysis.quality.issues.length > 0) {
                this.statusBarItem.text = `🤖 Aeonforge (${analysis.quality.issues.length} issues)`;
                this.statusBarItem.tooltip = `Aeonforge - ${analysis.quality.issues.length} code issues detected`;
            } else {
                this.statusBarItem.text = '🤖 Aeonforge';
                this.statusBarItem.tooltip = 'Aeonforge - No issues detected';
            }
            
        } catch (error) {
            this.analysisStatusItem.text = `$(error) Analysis failed`;
            this.analysisStatusItem.tooltip = `Failed to analyze ${language}: ${error}`;
            this.analysisStatusItem.backgroundColor = new vscode.ThemeColor('statusBarItem.errorBackground');
            this.qualityStatusItem.hide();
        }
    }

    private getQualityIcon(score: number): string {
        if (score >= 90) return '$(check-all)';
        if (score >= 75) return '$(check)';
        if (score >= 60) return '$(warning)';
        if (score >= 40) return '$(error)';
        return '$(alert)';
    }

    private getQualityColor(score: number): vscode.ThemeColor | undefined {
        if (score >= 75) return undefined; // Default
        if (score >= 60) return new vscode.ThemeColor('statusBarItem.warningBackground');
        return new vscode.ThemeColor('statusBarItem.errorBackground');
    }

    private buildQualityTooltip(quality: any): string {
        const lines = [
            `Code Quality: ${quality.overall_score.toFixed(1)}%`,
            '',
            `📐 Maintainability: ${quality.maintainability_score.toFixed(0)}%`,
            `📖 Readability: ${quality.readability_score.toFixed(0)}%`,
            `⚡ Performance: ${quality.performance_score.toFixed(0)}%`,
            `🔒 Security: ${quality.security_score.toFixed(0)}%`,
            `🧪 Test Coverage: ${quality.test_coverage.toFixed(0)}%`,
            `📝 Documentation: ${quality.documentation_score.toFixed(0)}%`
        ];
        
        if (quality.issues.length > 0) {
            lines.push('', '⚠️ Issues:');
            quality.issues.slice(0, 3).forEach((issue: string) => {
                lines.push(`  • ${issue}`);
            });
            
            if (quality.issues.length > 3) {
                lines.push(`  • ... and ${quality.issues.length - 3} more`);
            }
        }
        
        lines.push('', 'Click for detailed report');
        return lines.join('\n');
    }

    public showProgress(message: string, task?: Thenable<any>): void {
        this.statusBarItem.text = `$(loading~spin) ${message}`;
        
        if (task) {
            task.finally(() => {
                // Reset to normal status after task completion
                setTimeout(() => {
                    this.updateCurrentFileStatus();
                }, 1000);
            });
        }
    }

    public showError(message: string, duration = 5000): void {
        const originalText = this.statusBarItem.text;
        const originalBg = this.statusBarItem.backgroundColor;
        
        this.statusBarItem.text = `$(error) ${message}`;
        this.statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.errorBackground');
        
        setTimeout(() => {
            this.statusBarItem.text = originalText;
            this.statusBarItem.backgroundColor = originalBg;
        }, duration);
    }

    public showSuccess(message: string, duration = 3000): void {
        const originalText = this.statusBarItem.text;
        const originalBg = this.statusBarItem.backgroundColor;
        
        this.statusBarItem.text = `$(check) ${message}`;
        this.statusBarItem.backgroundColor = undefined;
        
        setTimeout(() => {
            this.statusBarItem.text = originalText;
            this.statusBarItem.backgroundColor = originalBg;
        }, duration);
    }

    public updateAnalysisProgress(stage: string, progress?: number): void {
        let text = `$(loading~spin) ${stage}`;
        if (progress !== undefined) {
            text += ` (${Math.round(progress)}%)`;
        }
        this.analysisStatusItem.text = text;
    }

    public dispose(): void {
        this.statusBarItem.dispose();
        this.analysisStatusItem.dispose();
        this.qualityStatusItem.dispose();
        this.connectionStatusItem.dispose();
    }
}