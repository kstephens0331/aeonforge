/**
 * DiagnosticsCollector - Collects and monitors VS Code diagnostics
 * Helps Aeonforge understand code issues and errors
 */

import * as vscode from 'vscode';

export interface DiagnosticSummary {
    errors: number;
    warnings: number;
    infos: number;
    hints: number;
    totalIssues: number;
    criticalFiles: string[];
}

export class DiagnosticsCollector {
    private diagnosticsMap: Map<string, vscode.Diagnostic[]> = new Map();
    private _onDiagnosticsChanged: vscode.EventEmitter<DiagnosticSummary> = new vscode.EventEmitter<DiagnosticSummary>();
    
    readonly onDiagnosticsChanged: vscode.Event<DiagnosticSummary> = this._onDiagnosticsChanged.event;

    constructor() {
        // Initialize with current diagnostics
        this.collectAllDiagnostics();
    }

    /**
     * Update diagnostics for a specific document
     */
    updateDiagnostics(document: vscode.TextDocument): void {
        const diagnostics = vscode.languages.getDiagnostics(document.uri);
        const filePath = vscode.workspace.asRelativePath(document.uri);
        
        this.diagnosticsMap.set(filePath, diagnostics);
        this.emitDiagnosticsUpdate();
    }

    /**
     * Collect diagnostics from change event
     */
    collectDiagnostics(event: vscode.DiagnosticChangeEvent): void {
        for (const uri of event.uris) {
            const diagnostics = vscode.languages.getDiagnostics(uri);
            const filePath = vscode.workspace.asRelativePath(uri);
            
            if (diagnostics.length > 0) {
                this.diagnosticsMap.set(filePath, diagnostics);
            } else {
                this.diagnosticsMap.delete(filePath);
            }
        }
        
        this.emitDiagnosticsUpdate();
    }

    /**
     * Collect all current diagnostics
     */
    private collectAllDiagnostics(): void {
        this.diagnosticsMap.clear();
        
        const allDiagnostics = vscode.languages.getDiagnostics();
        
        for (const [uri, diagnostics] of allDiagnostics) {
            if (diagnostics.length > 0) {
                const filePath = vscode.workspace.asRelativePath(uri);
                this.diagnosticsMap.set(filePath, diagnostics);
            }
        }
        
        this.emitDiagnosticsUpdate();
    }

    /**
     * Get current diagnostics summary
     */
    getDiagnosticsSummary(): DiagnosticSummary {
        let errors = 0;
        let warnings = 0;
        let infos = 0;
        let hints = 0;
        const criticalFiles: string[] = [];

        for (const [filePath, diagnostics] of this.diagnosticsMap) {
            let fileErrors = 0;
            
            for (const diagnostic of diagnostics) {
                switch (diagnostic.severity) {
                    case vscode.DiagnosticSeverity.Error:
                        errors++;
                        fileErrors++;
                        break;
                    case vscode.DiagnosticSeverity.Warning:
                        warnings++;
                        break;
                    case vscode.DiagnosticSeverity.Information:
                        infos++;
                        break;
                    case vscode.DiagnosticSeverity.Hint:
                        hints++;
                        break;
                }
            }
            
            // Files with multiple errors are considered critical
            if (fileErrors >= 3) {
                criticalFiles.push(filePath);
            }
        }

        return {
            errors,
            warnings,
            infos,
            hints,
            totalIssues: errors + warnings + infos + hints,
            criticalFiles
        };
    }

    /**
     * Get diagnostics for a specific file
     */
    getFileDiagnostics(filePath: string): vscode.Diagnostic[] {
        return this.diagnosticsMap.get(filePath) || [];
    }

    /**
     * Get all diagnostics grouped by severity
     */
    getDiagnosticsBySeverity(): Record<string, Array<{file: string, diagnostic: vscode.Diagnostic}>> {
        const result = {
            errors: [] as Array<{file: string, diagnostic: vscode.Diagnostic}>,
            warnings: [] as Array<{file: string, diagnostic: vscode.Diagnostic}>,
            infos: [] as Array<{file: string, diagnostic: vscode.Diagnostic}>,
            hints: [] as Array<{file: string, diagnostic: vscode.Diagnostic}>
        };

        for (const [filePath, diagnostics] of this.diagnosticsMap) {
            for (const diagnostic of diagnostics) {
                const item = { file: filePath, diagnostic };
                
                switch (diagnostic.severity) {
                    case vscode.DiagnosticSeverity.Error:
                        result.errors.push(item);
                        break;
                    case vscode.DiagnosticSeverity.Warning:
                        result.warnings.push(item);
                        break;
                    case vscode.DiagnosticSeverity.Information:
                        result.infos.push(item);
                        break;
                    case vscode.DiagnosticSeverity.Hint:
                        result.hints.push(item);
                        break;
                }
            }
        }

        return result;
    }

    /**
     * Get top issues that should be addressed first
     */
    getTopIssues(limit: number = 10): Array<{file: string, diagnostic: vscode.Diagnostic, priority: number}> {
        const issues: Array<{file: string, diagnostic: vscode.Diagnostic, priority: number}> = [];
        
        for (const [filePath, diagnostics] of this.diagnosticsMap) {
            for (const diagnostic of diagnostics) {
                let priority = 0;
                
                // Prioritize by severity
                switch (diagnostic.severity) {
                    case vscode.DiagnosticSeverity.Error:
                        priority += 100;
                        break;
                    case vscode.DiagnosticSeverity.Warning:
                        priority += 50;
                        break;
                    case vscode.DiagnosticSeverity.Information:
                        priority += 10;
                        break;
                    case vscode.DiagnosticSeverity.Hint:
                        priority += 5;
                        break;
                }
                
                // Boost priority for common critical issues
                const message = diagnostic.message.toLowerCase();
                if (message.includes('syntax error') || message.includes('unexpected token')) {
                    priority += 50;
                } else if (message.includes('cannot find') || message.includes('undefined')) {
                    priority += 30;
                } else if (message.includes('unused') || message.includes('deprecated')) {
                    priority += 15;
                }
                
                issues.push({ file: filePath, diagnostic, priority });
            }
        }
        
        // Sort by priority (highest first) and return top issues
        return issues
            .sort((a, b) => b.priority - a.priority)
            .slice(0, limit);
    }

    /**
     * Check if there are any critical errors
     */
    hasCriticalErrors(): boolean {
        for (const diagnostics of this.diagnosticsMap.values()) {
            if (diagnostics.some(d => d.severity === vscode.DiagnosticSeverity.Error)) {
                return true;
            }
        }
        return false;
    }

    /**
     * Get diagnostics context for Aeonforge
     */
    getDiagnosticsContext(): any {
        const summary = this.getDiagnosticsSummary();
        const topIssues = this.getTopIssues(5);
        const bySeverity = this.getDiagnosticsBySeverity();
        
        return {
            summary,
            topIssues: topIssues.map(item => ({
                file: item.file,
                line: item.diagnostic.range.start.line + 1,
                message: item.diagnostic.message,
                severity: this.severityToString(item.diagnostic.severity),
                source: item.diagnostic.source,
                priority: item.priority
            })),
            errorFiles: bySeverity.errors.map(e => e.file),
            warningFiles: bySeverity.warnings.map(w => w.file)
        };
    }

    /**
     * Convert severity enum to string
     */
    private severityToString(severity: vscode.DiagnosticSeverity): string {
        switch (severity) {
            case vscode.DiagnosticSeverity.Error: return 'error';
            case vscode.DiagnosticSeverity.Warning: return 'warning';
            case vscode.DiagnosticSeverity.Information: return 'info';
            case vscode.DiagnosticSeverity.Hint: return 'hint';
            default: return 'unknown';
        }
    }

    /**
     * Emit diagnostics update event
     */
    private emitDiagnosticsUpdate(): void {
        const summary = this.getDiagnosticsSummary();
        this._onDiagnosticsChanged.fire(summary);
    }

    /**
     * Clear all diagnostics
     */
    clear(): void {
        this.diagnosticsMap.clear();
        this.emitDiagnosticsUpdate();
    }

    /**
     * Get diagnostic statistics for reporting
     */
    getStatistics(): {
        totalFiles: number;
        filesWithErrors: number;
        filesWithWarnings: number;
        avgIssuesPerFile: number;
        summary: DiagnosticSummary;
    } {
        const summary = this.getDiagnosticsSummary();
        const totalFiles = this.diagnosticsMap.size;
        let filesWithErrors = 0;
        let filesWithWarnings = 0;

        for (const diagnostics of this.diagnosticsMap.values()) {
            if (diagnostics.some(d => d.severity === vscode.DiagnosticSeverity.Error)) {
                filesWithErrors++;
            }
            if (diagnostics.some(d => d.severity === vscode.DiagnosticSeverity.Warning)) {
                filesWithWarnings++;
            }
        }

        return {
            totalFiles,
            filesWithErrors,
            filesWithWarnings,
            avgIssuesPerFile: totalFiles > 0 ? summary.totalIssues / totalFiles : 0,
            summary
        };
    }
}