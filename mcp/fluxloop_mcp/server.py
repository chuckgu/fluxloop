"""Entry point for the Fluxloop MCP stdio server (minimal stub)."""

from __future__ import annotations

import argparse
import asyncio
import sys
from dataclasses import dataclass
from typing import Any, Dict, Optional

from msgspec import ValidationError
from msgspec import json as msgjson

from .tools import (
    AnalyzeRepositoryTool,
    DetectFrameworksTool,
    FAQTool,
    GenerateIntegrationStepsTool,
    ProposeEditPlanTool,
    RunIntegrationWorkflowTool,
    ValidateEditPlanTool,
)


@dataclass
class MCPConfig:
    """Runtime configuration for the MCP server."""

    name: str = "fluxloop"
    version: str = "0.0.1"


class ToolError(Exception):
    """Structured error raised when tool invocation fails."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class ToolRegistry:
    """Simple tool registry used for early wiring tests."""

    def __init__(self) -> None:
        self._analyze_repository = AnalyzeRepositoryTool()
        self._faq = FAQTool()
        self._detect_frameworks = DetectFrameworksTool()
        self._generate_steps = GenerateIntegrationStepsTool()
        self._propose_plan = ProposeEditPlanTool()
        self._validate_plan = ValidateEditPlanTool()
        self._workflow = RunIntegrationWorkflowTool()

    async def dispatch(self, request: Dict[str, Any]) -> Dict[str, Any]:
        tool = request.get("tool")
        if tool == "handshake":
            return {
                "tool": "handshake",
                "data": {
                    "name": "fluxloop",
                    "version": "0.0.1",
                    "capabilities": [
                        "analyze_repository",
                        "faq",
                        "detect_frameworks",
                        "generate_integration_steps",
                        "propose_edit_plan",
                        "validate_edit_plan",
                        "run_integration_workflow",
                    ],
                },
            }

        if tool == "faq":
            query = request.get("query", "")
            return {"tool": "faq", "data": self._faq.query(str(query))}
        if tool == "analyze_repository":
            return {
                "tool": "analyze_repository",
                "data": self._analyze_repository.analyze(request),
            }
        if tool == "detect_frameworks":
            return {"tool": "detect_frameworks", "data": self._detect_frameworks.detect(request)}
        if tool == "generate_integration_steps":
            return {
                "tool": "generate_integration_steps",
                "data": self._generate_steps.generate(request),
            }
        if tool == "propose_edit_plan":
            return {
                "tool": "propose_edit_plan",
                "data": self._propose_plan.propose(request),
            }
        if tool == "validate_edit_plan":
            return {
                "tool": "validate_edit_plan",
                "data": self._validate_plan.validate(request),
            }
        if tool == "run_integration_workflow":
            return {
                "tool": "run_integration_workflow",
                "data": self._workflow.run(request),
            }

        raise ToolError("unknown_tool", f"Unknown tool '{tool}'")


class MCPServer:
    """Minimal stdio loop for early experimentation.

    The implementation intentionally keeps the protocol surface tiny: every inbound JSON line must
    encode an object containing `tool` and tool-specific payloads. Responses are newline-delimited
    JSON objects that mirror the request ID if provided.
    """

    def __init__(self, config: Optional[MCPConfig] = None) -> None:
        self.config = config or MCPConfig()
        self.registry = ToolRegistry()

    async def run_stdio(self) -> None:
        """Continuously read JSON objects from stdin and emit replies to stdout."""

        loop = asyncio.get_running_loop()

        async def _readline() -> str:
            return await loop.run_in_executor(None, sys.stdin.readline)

        while True:
            raw_line = await _readline()
            if raw_line == "":
                # stdin closed
                break

            raw_line = raw_line.strip()
            if not raw_line:
                continue

            try:
                payload = msgjson.decode(raw_line)
                if not isinstance(payload, dict):
                    raise TypeError("Decoded payload is not a JSON object")
            except (ValidationError, TypeError) as exc:
                self._write(self._error_response(None, "invalid_payload", str(exc)))
                continue

            request_id = payload.get("id")
            try:
                result = await self.registry.dispatch(payload)
                data = result.get("data")
                if isinstance(data, dict) and data.get("error"):
                    raise ToolError("tool_error", data["error"])
                self._write(self._success_response(request_id, result))
            except ToolError as exc:
                self._write(self._error_response(request_id, exc.code, exc.message))
            except Exception as exc:  # noqa: BLE001 - surface unexpected failures
                self._write(self._error_response(request_id, "internal_error", str(exc)))

    def _write(self, message: Dict[str, Any]) -> None:
        sys.stdout.write(msgjson.encode(message).decode() + "\n")
        sys.stdout.flush()

    def _success_response(self, request_id: Optional[Any], result: Dict[str, Any]) -> Dict[str, Any]:
        response = {
            "type": "response",
            "result": result,
        }
        if request_id is not None:
            response["id"] = request_id
        return response

    def _error_response(
        self, request_id: Optional[Any], code: str, message: str
    ) -> Dict[str, Any]:
        response = {
            "type": "error",
            "error": {"code": code, "message": message},
        }
        if request_id is not None:
            response["id"] = request_id
        return response


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fluxloop MCP server skeleton")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Execute a single FAQ query via --query and exit (bypasses stdio loop).",
    )
    parser.add_argument(
        "--query",
        type=str,
        default="",
        help="FAQ query to run when --once is supplied.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> None:
    """Console script entry point."""

    args = parse_args(argv)
    server = MCPServer()

    async def _runner() -> None:
        if args.once:
            try:
                result = await server.registry.dispatch({"tool": "faq", "query": args.query})
                data = result.get("data")
                if isinstance(data, dict) and data.get("error"):
                    raise ToolError("tool_error", data["error"])
                server._write(server._success_response(None, result))
            except ToolError as exc:
                server._write(server._error_response(None, exc.code, exc.message))
            except Exception as exc:  # noqa: BLE001
                server._write(server._error_response(None, "internal_error", str(exc)))
        else:
            await server.run_stdio()

    asyncio.run(_runner())


if __name__ == "__main__":
    main()

