import time
from abc import ABC, abstractmethod
from typing import Dict, Any

from models.agent_result import AgentResult


class BaseAgent(ABC):
    """
    Abstract base class for all AI agents.
    Every specialized agent inherits this class.
    """

    def __init__(self, agent_name: str):
        self.agent_name = agent_name

    @abstractmethod
    async def analyze(self, data: Dict[str, Any]) -> AgentResult:
        """
        Each agent implements its own analysis logic.
        """
        pass

    async def execute(self, data: Dict[str, Any]) -> AgentResult:
        """
        Executes the agent and records execution latency.
        """

        start_time = time.perf_counter()

        result = await self.analyze(data)

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        # Always show at least 1 ms
        result.latency_ms = max(1, round(elapsed_ms))

        return result