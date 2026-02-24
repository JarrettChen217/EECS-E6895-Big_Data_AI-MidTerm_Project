"""Tool registry and run_plan executor."""

from typing import Any, Callable


def run_plan(
    plan: dict[str, Any],
    tool_registry: dict[str, Callable[..., dict[str, Any]]],
) -> list[dict[str, Any]]:
    """Execute plan steps in order; return trace (tool, args, result, result_preview)."""
    trace = []
    steps = plan.get("plan", [])

    for step in steps:
        tool_name = step.get("tool")
        args = step.get("args", {})

        if tool_name not in tool_registry:
            trace.append({
                "tool": tool_name,
                "args": args,
                "result": {"error": f"unknown tool '{tool_name}'"},
                "result_preview": "error: unknown tool",
            })
            continue

        try:
            result = tool_registry[tool_name](**args)
        except Exception as e:
            result = {"error": f"Tool execution failed: {str(e)}"}

        result_str = str(result)
        result_preview = result_str if len(result_str) <= 100 else result_str[:100] + "..."

        trace.append({
            "tool": tool_name,
            "args": args,
            "result": result,
            "result_preview": result_preview,
        })

    return trace
