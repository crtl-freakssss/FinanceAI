import asyncio
import time
from typing import Dict, Any

from agents.technical_agent import TechnicalAgent
from agents.fundamental_agent import FundamentalAgent
from agents.sentiment_agent import SentimentAgent
from agents.risk_agent import RiskAgent
from agents.synthesis_agent import SynthesisAgent
from orchestration.state import OrchestratorState


class FinancialAIGraph:
    """
    Multi-Agent Financial Intelligence Orchestrator

    Pipeline:
        Input
          │
          ├── Technical Agent
          ├── Fundamental Agent
          ├── Sentiment Agent
          └── Risk Agent
               │
        (Runs in Parallel)
               │
        Synthesis Agent
               │
        Final Recommendation
    """

    def __init__(self):
        self.technical_agent = TechnicalAgent()
        self.fundamental_agent = FundamentalAgent()
        self.sentiment_agent = SentimentAgent()
        self.risk_agent = RiskAgent()
        self.synthesis_agent = SynthesisAgent()

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes all agents in parallel and returns the final investment analysis.
        """

        state = OrchestratorState(input_data=input_data)
        symbol = input_data.get("symbol", "UNKNOWN")

        pipeline_start = time.perf_counter()

        try:
            # ---------------------------------------------------
            # Execute all four agents simultaneously
            # ---------------------------------------------------
            (
                technical_result,
                fundamental_result,
                sentiment_result,
                risk_result,
            ) = await asyncio.gather(
                self.technical_agent.execute(input_data),
                self.fundamental_agent.execute(input_data),
                self.sentiment_agent.execute(input_data),
                self.risk_agent.execute(input_data),
            )

            # Save outputs into orchestrator state
            state.technical = technical_result
            state.fundamental = fundamental_result
            state.sentiment = sentiment_result
            state.risk = risk_result

            # ---------------------------------------------------
            # Generate final recommendation
            # ---------------------------------------------------
            final_result = self.synthesis_agent.synthesize(
                symbol=symbol,
                technical=technical_result,
                fundamental=fundamental_result,
                sentiment=sentiment_result,
                risk=risk_result,
            )

            # ---------------------------------------------------
            # Performance Metrics
            # ---------------------------------------------------
            elapsed_ms = (time.perf_counter() - pipeline_start) * 1000
            total_latency = max(1, round(elapsed_ms))

            slowest_agent = max(
                technical_result.latency_ms,
                fundamental_result.latency_ms,
                sentiment_result.latency_ms,
                risk_result.latency_ms,
            )

            state.execution_metrics = {
                "parallel_execution": True,
                "agents_executed": 4,
                "total_latency_ms": total_latency,
                "slowest_agent_ms": slowest_agent,
                "technical_latency_ms": technical_result.latency_ms,
                "fundamental_latency_ms": fundamental_result.latency_ms,
                "sentiment_latency_ms": sentiment_result.latency_ms,
                "risk_latency_ms": risk_result.latency_ms,
            }

            state.final_output = final_result.model_dump()

            response = final_result.model_dump()
            response["metrics"] = state.execution_metrics

            return response

        except Exception as error:
            state.errors["orchestrator"] = str(error)

            elapsed_ms = (time.perf_counter() - pipeline_start) * 1000

            return {
                "symbol": symbol,
                "status": "error",
                "message": "Multi-agent analysis failed.",
                "error": str(error),
                "metrics": {
                    "parallel_execution": False,
                    "agents_executed": 0,
                    "total_latency_ms": max(1, round(elapsed_ms)),
                },
            }