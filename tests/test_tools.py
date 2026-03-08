"""Unit tests for platform_chooser and RAG tool."""

import unittest


class TestPlatformChooser(unittest.TestCase):
    """Tests for platform_chooser tool."""

    def test_platform_chooser_returns_ok_with_valid_industry(self):
        from marketing_agent.tools.platform_chooser import platform_chooser

        result = platform_chooser(industry="Health & Fitness", region="US")
        assert result.get("status") == "ok"
        assert "platforms" in result
        assert "audience" in result

    def test_platform_chooser_platforms_non_empty_for_fitness(self):
        from marketing_agent.tools.platform_chooser import platform_chooser

        result = platform_chooser(industry="Health & Fitness", region="US")
        assert len(result.get("platforms", [])) > 0

    def test_platform_chooser_audience_included_when_requested(self):
        from marketing_agent.tools.platform_chooser import platform_chooser

        result = platform_chooser(industry="E-commerce", region="US", include_audience=True)
        assert len(result.get("audience", [])) > 0

    def test_platform_chooser_accepts_empty_industry(self):
        from marketing_agent.tools.platform_chooser import platform_chooser

        result = platform_chooser(industry="", region="US")
        # May return ok with fallback data or error; should not raise
        assert "status" in result


class TestRagTool(unittest.TestCase):
    """Tests for RAG tool (with mock retriever)."""

    def test_make_tool_rag_returns_callable(self):
        from marketing_agent.tools.rag_tool import make_tool_rag
        from unittest.mock import MagicMock

        mock_retriever = MagicMock()
        mock_llm = MagicMock()
        tool = make_tool_rag(mock_retriever, mock_llm)
        assert callable(tool)

    def test_rag_tool_invokes_retriever_and_llm(self):
        from marketing_agent.tools.rag_tool import make_tool_rag
        from unittest.mock import MagicMock
        from langchain_core.documents import Document

        mock_retriever = MagicMock()
        mock_retriever.invoke.return_value = [
            Document(page_content="Policy: no misleading claims.", metadata={"doc_id": "test_1"}),
        ]
        mock_llm = MagicMock()
        mock_llm.generate.return_value = "Based on the policy, avoid misleading claims."

        tool = make_tool_rag(mock_retriever, mock_llm)
        result = tool(question="What are the ad policies?")

        mock_retriever.invoke.assert_called_once_with("What are the ad policies?")
        assert "answer" in result
        assert "evidence" in result
