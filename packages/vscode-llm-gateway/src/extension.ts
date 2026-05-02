import * as vscode from "vscode";
import { createGatewayController } from "./gatewayController";
import { createVsCodeModelService } from "./modelService";
import {
  buildCopyTokenResult,
  buildStartMessage,
  buildStatusMessage,
  buildStopMessage,
  COPY_TOKEN_ACTION,
  type InfoMessageSpec,
} from "./commandMessages";

const START_COMMAND_ID = "tradingAgentsGateway.start";
const STOP_COMMAND_ID = "tradingAgentsGateway.stop";
const STATUS_COMMAND_ID = "tradingAgentsGateway.status";
const COPY_TOKEN_COMMAND_ID = "tradingAgentsGateway.copyToken";

const gateway = createGatewayController({
  modelService: createVsCodeModelService(vscode.lm, {
    createUserMessage: (content: string) => vscode.LanguageModelChatMessage.User(content),
    createAssistantMessage: (content: string) => vscode.LanguageModelChatMessage.Assistant(content),
    createCancellationSource: () => new vscode.CancellationTokenSource(),
  }),
});

async function showInfoMessage(spec: InfoMessageSpec): Promise<string | undefined> {
  if (spec.actions.length === 0) {
    return vscode.window.showInformationMessage(spec.message);
  }

  return vscode.window.showInformationMessage(spec.message, ...spec.actions);
}

async function copyTokenToClipboard(): Promise<void> {
  const tokenResult = buildCopyTokenResult(gateway.getToken());

  if (!tokenResult.copied || !tokenResult.token) {
    await vscode.window.showInformationMessage(tokenResult.message);
    return;
  }

  await vscode.env.clipboard.writeText(tokenResult.token);
  await vscode.window.showInformationMessage(tokenResult.message);
}

export function activate(context: vscode.ExtensionContext): void {
  const startCommand = vscode.commands.registerCommand(START_COMMAND_ID, async () => {
    const result = await gateway.start();
    const selectedAction = await showInfoMessage(buildStartMessage(result));
    if (selectedAction === COPY_TOKEN_ACTION) {
      await copyTokenToClipboard();
    }
  });

  const stopCommand = vscode.commands.registerCommand(STOP_COMMAND_ID, async () => {
    const result = await gateway.stop("command");
    await showInfoMessage(buildStopMessage(result));
  });

  const statusCommand = vscode.commands.registerCommand(STATUS_COMMAND_ID, async () => {
    const selectedAction = await showInfoMessage(buildStatusMessage(gateway.getStatus()));
    if (selectedAction === COPY_TOKEN_ACTION) {
      await copyTokenToClipboard();
    }
  });

  const copyTokenCommand = vscode.commands.registerCommand(COPY_TOKEN_COMMAND_ID, async () => {
    await copyTokenToClipboard();
  });

  context.subscriptions.push(startCommand, stopCommand, statusCommand, copyTokenCommand);
}

export function deactivate(): Thenable<void> {
  return gateway.stop("deactivate").then(
    () => undefined,
    () => undefined
  );
}
