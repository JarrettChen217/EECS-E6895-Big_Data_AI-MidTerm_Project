"""Agent: router, synthesizer, and run_agent."""

from marketing_agent.agent.run import run_agent
from marketing_agent.agent.router import route_question
from marketing_agent.agent.synthesizer import synthesize_answer

__all__ = ["run_agent", "route_question", "synthesize_answer"]
