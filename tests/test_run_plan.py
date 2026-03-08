"""Tests for run_plan: executes tools and returns trace."""

import unittest
from unittest.mock import MagicMock


class TestRunPlan(unittest.TestCase):
    """Tests for run_plan executor."""

    def test_run_plan_executes_both_tools(self):
        from marketing_agent.tools import run_plan, platform_chooser

        def mock_rag(question: str, k: int = 3, **kwargs):
            return {"answer": "Policy: no misleading claims.", "evidence": []}

        plan = {
            "plan": [
                {"tool": "platform_chooser", "args": {"industry": "E-commerce", "region": "US"}},
                {"tool": "rag", "args": {"question": "ad policy", "k": 3}},
            ]
        }
        registry = {
            "platform_chooser": platform_chooser,
            "rag": mock_rag,
        }

        trace = run_plan(plan, registry)

        assert len(trace) == 2
        assert trace[0]["tool"] == "platform_chooser"
        assert trace[1]["tool"] == "rag"
        assert trace[0]["result"].get("status") == "ok"
        assert "platforms" in trace[0]["result"]

    def test_run_plan_executes_multiple_rag_steps(self):
        from marketing_agent.tools import run_plan, platform_chooser

        def mock_rag(question: str, k: int = 3, **kwargs):
            return {"answer": f"Policy for: {question[:30]}", "evidence": []}

        plan = {
            "plan": [
                {"tool": "platform_chooser", "args": {"industry": "Health & Fitness", "region": "US"}},
                {"tool": "rag", "args": {"question": "Meta ads policy for health", "k": 3}},
                {"tool": "rag", "args": {"question": "Google Ads policy for fitness", "k": 3}},
            ]
        }
        registry = {
            "platform_chooser": platform_chooser,
            "rag": mock_rag,
        }

        trace = run_plan(plan, registry)

        assert len(trace) == 3
        assert trace[0]["tool"] == "platform_chooser"
        assert trace[1]["tool"] == "rag"
        assert trace[2]["tool"] == "rag"

    def test_run_plan_unknown_tool_yields_error_in_trace(self):
        from marketing_agent.tools import run_plan

        plan = {"plan": [{"tool": "unknown_tool", "args": {}}]}
        registry = {}

        trace = run_plan(plan, registry)

        assert len(trace) == 1
        assert trace[0]["tool"] == "unknown_tool"
        assert "error" in trace[0]["result"]
