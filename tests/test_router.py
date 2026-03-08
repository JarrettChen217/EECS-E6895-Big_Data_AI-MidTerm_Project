"""Tests for router: route_question returns valid plan with platform_chooser + rag."""

import unittest
from unittest.mock import MagicMock


class TestRouter(unittest.TestCase):
    """Tests for route_question."""

    def test_route_question_returns_plan_with_platform_chooser_and_rag(self):
        from marketing_agent.agent.router import route_question

        mock_llm = MagicMock()
        mock_llm.generate.return_value = '''{
            "plan": [
                {"tool": "platform_chooser", "args": {"industry": "Health & Fitness", "region": "US", "include_audience": true}},
                {"tool": "rag", "args": {"question": "Meta Google TikTok ads policy for health fitness", "k": 5}}
            ]
        }'''

        plan = route_question("I have $5000 for a fitness app", mock_llm)

        assert "plan" in plan
        assert len(plan["plan"]) == 2
        assert plan["plan"][0]["tool"] == "platform_chooser"
        assert plan["plan"][1]["tool"] == "rag"
        assert "industry" in plan["plan"][0]["args"]
        assert "question" in plan["plan"][1]["args"]

    def test_route_question_fallback_when_llm_fails(self):
        from marketing_agent.agent.router import route_question

        mock_llm = MagicMock()
        mock_llm.generate.side_effect = Exception("LLM error")

        plan = route_question("Fitness app budget $3k", mock_llm)

        assert "plan" in plan
        assert len(plan["plan"]) >= 2
        assert plan["plan"][0]["tool"] == "platform_chooser"
        rag_steps = [s for s in plan["plan"] if s["tool"] == "rag"]
        assert len(rag_steps) >= 1
        assert plan["plan"][0]["args"].get("industry")

    def test_route_question_allows_multiple_rag_steps(self):
        from marketing_agent.agent.router import route_question

        mock_llm = MagicMock()
        mock_llm.generate.return_value = '''{
            "plan": [
                {"tool": "platform_chooser", "args": {"industry": "E-commerce", "region": "US"}},
                {"tool": "rag", "args": {"question": "Meta ads policy for e-commerce", "k": 3}},
                {"tool": "rag", "args": {"question": "Google Ads policy for retail", "k": 3}},
                {"tool": "rag", "args": {"question": "TikTok ads policy and brand safety", "k": 3}}
            ]
        }'''

        plan = route_question("E-commerce $10k budget", mock_llm)

        assert len(plan["plan"]) == 4
        assert plan["plan"][0]["tool"] == "platform_chooser"
        rag_steps = [s for s in plan["plan"] if s["tool"] == "rag"]
        assert len(rag_steps) == 3

    def test_cap_rag_steps_limits_to_max(self):
        from marketing_agent.agent.router import _cap_rag_steps

        plan = {
            "plan": [
                {"tool": "platform_chooser", "args": {}},
                {"tool": "rag", "args": {"question": "q1"}},
                {"tool": "rag", "args": {"question": "q2"}},
                {"tool": "rag", "args": {"question": "q3"}},
                {"tool": "rag", "args": {"question": "q4"}},
                {"tool": "rag", "args": {"question": "q5"}},
                {"tool": "rag", "args": {"question": "q6"}},
            ]
        }
        capped = _cap_rag_steps(plan, max_rag=5)
        rag_count = sum(1 for s in capped["plan"] if s["tool"] == "rag")
        assert rag_count == 5
