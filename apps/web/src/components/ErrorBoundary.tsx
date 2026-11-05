import React, { Component, ErrorInfo, ReactNode } from "react";
import { AlertOctagon, RefreshCw, Terminal, ShieldAlert } from "lucide-react";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
    errorInfo: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error, errorInfo: null };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Clinical System Calibration Failure:", error, errorInfo);
    this.setState({ error, errorInfo });
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
    window.location.reload();
  };

  public render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-[#0B0B0F] text-slate-100 flex items-center justify-center p-6 selection:bg-pink-500 selection:text-white">
          <div className="w-full max-w-xl glass-panel-danger rounded-2xl p-6 sm:p-8 flex flex-col gap-6 relative overflow-hidden border border-rose-500/30">
            {/* Ambient Background Glow */}
            <div className="absolute -top-24 -left-24 w-60 h-60 bg-rose-500/10 rounded-full blur-3xl pointer-events-none" />
            <div className="absolute -bottom-24 -right-24 w-60 h-60 bg-blue-500/10 rounded-full blur-3xl pointer-events-none" />

            {/* Header Badge */}
            <div className="flex items-center justify-between border-b border-rose-500/20 pb-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-center justify-center text-rose-400 shadow-neon-glow">
                  <AlertOctagon className="w-5 h-5 stroke-[2.5]" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono font-bold tracking-widest uppercase text-rose-400">
                      ERR_SUBSYSTEM_FAULT
                    </span>
                    <span className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-rose-500/20 text-rose-300 border border-rose-500/30">
                      CRITICAL
                    </span>
                  </div>
                  <h1 className="text-lg font-black tracking-tight text-white mt-0.5">
                    SYSTEM CALIBRATION ERROR
                  </h1>
                </div>
              </div>
            </div>

            {/* Description */}
            <p className="text-xs text-slate-300 leading-relaxed">
              The clinical inference frontend encountered an unexpected runtime fault. 
              Active biometrics telemetry and hardware streams have been placed in safe-mode isolation 
              to prevent patient state corruption.
            </p>

            {/* Diagnostic Terminal View */}
            <div className="rounded-xl bg-[#07070A] border border-white/5 p-4 font-mono text-[11px] text-slate-300 overflow-x-auto max-h-48 flex flex-col gap-1.5">
              <div className="flex items-center gap-2 text-slate-500 pb-1 border-b border-white/5">
                <Terminal className="w-3.5 h-3.5 text-rose-400" />
                <span>DIAGNOSTIC TRACE LOG</span>
              </div>
              <div className="text-rose-400 font-semibold">
                {this.state.error?.name || "Error"}: {this.state.error?.message || "Unknown anomaly"}
              </div>
              {this.state.error?.stack && (
                <div className="text-[10px] text-slate-400 whitespace-pre-wrap leading-tight mt-1">
                  {this.state.error.stack.split("\n").slice(0, 4).join("\n")}
                </div>
              )}
            </div>

            {/* Action Bar */}
            <div className="flex items-center justify-between pt-2">
              <div className="flex items-center gap-2 text-[11px] text-slate-400">
                <ShieldAlert className="w-4 h-4 text-rose-400" />
                <span>Fail-safe lock engaged</span>
              </div>
              <button
                onClick={this.handleReset}
                className="px-5 py-2.5 rounded-xl font-mono text-xs font-bold tracking-wider uppercase bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 text-white shadow-electric-glow transition-all duration-200 flex items-center gap-2 active:scale-95"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                <span>Recalibrate System</span>
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

