"""End-to-end tests: simulate user input and run_agent (with mocked LLM)."""

import pytest
from unittest.mock import MagicMock, patch


class TestRunAgentE2E:
    """E2E tests for run_agent with mocked LLM and retriever."""

    def test_run_agent_returns_final_answer(self):
        from marketing_agent.agent.run import run_agent, _build_tool_registry
        from marketing_agent.tools import platform_chooser

        mock_llm = MagicMock()
        mock_llm.generate.side_effect = [
            # Router response
            '''{"plan": [
                {"tool": "platform_chooser", "args": {"industry": "Health & Fitness", "region": "US"}},
                {"tool": "rag", "args": {"question": "Meta Google TikTok ads policy for health", "k": 5}}
            ]}''',
            # Synthesizer response
            "## 1. Platform Selection\nMeta and Google...",
        ]

        def mock_rag(question, k=3, **kwargs):
            return {"answer": "Avoid misleading health claims.", "evidence": [{"doc_id": "meta_policy"}]}

        with patch("marketing_agent.agent.run.get_llm", return_value=mock_llm):
            with patch("marketing_agent.agent.run._build_tool_registry") as mock_build:
                mock_build.return_value = {
                    "platform_chooser": platform_chooser,
                    "rag": mock_rag,
                }
                result = run_agent(
                    "I have $5000 for a fitness app targeting young adults",
                    llm=mock_llm,
                    retriever=object(),
                )

        assert "final_answer" in result
        assert "plan" in result
        assert "trace" in result

    def test_run_agent_fallback_plan_when_router_fails(self):
        from marketing_agent.agent.run import run_agent
        from marketing_agent.tools import platform_chooser

        mock_llm = MagicMock()
        mock_llm.generate.side_effect = [
            "invalid json {{{",  # Router fails
            "## 1. Platform Selection\nRecommend Meta...",  # Synthesizer
        ]

        def mock_rag(question, k=3, **kwargs):
            return {"answer": "Policy info.", "evidence": []}

        with patch("marketing_agent.agent.run.get_llm", return_value=mock_llm):
            with patch("marketing_agent.agent.run._build_tool_registry") as mock_build:
                mock_build.return_value = {
                    "platform_chooser": platform_chooser,
                    "rag": mock_rag,
                }
                result = run_agent(
                    "Fitness app $5k",
                    llm=mock_llm,
                    retriever=object(),
                )

        assert "final_answer" in result
        assert "plan" in result
        assert len(result.get("plan", [])) == 2
