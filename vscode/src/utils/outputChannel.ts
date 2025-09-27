import * as vscode from 'vscode';

export class OutputChannelManager {
    private static instance: vscode.OutputChannel;

    static getInstance(): vscode.OutputChannel {
        if (!OutputChannelManager.instance) {
            OutputChannelManager.instance = vscode.window.createOutputChannel('FluxLoop');
        }
        return OutputChannelManager.instance;
    }
}
