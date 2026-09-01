from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from models.agent_result import AgentResult


class OrchestratorState(BaseModel):
    """
    Shared state passed between all agents and the synthesis engine.
    """

    # Original request data (from Person 2 / frontend)
    input_data: Dict[str, Any]

    # Individual agent outputs
    technical: Optional[AgentResult] = None
    fundamental: Optional[AgentResult] = None
    sentiment: Optional[AgentResult] = None
    risk: Optional[AgentResult] = None

    # Final synthesis output
    final_output: Optional[Dict[str, Any]] = None

    # Metrics
    execution_metrics: Dict[str, Any] = Field(default_factory=dict)

    # Debug / logging
    errors: Dict[str, str] = Field(default_factory=dict)

    class Config:
        populate_by_name = True