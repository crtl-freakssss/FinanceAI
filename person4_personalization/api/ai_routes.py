"""
Multi-Agent AI Analysis API routes bridging Person 1's FinancialAIGraph orchestrator
into the unified FastAPI backend using the FinancialDataBridge.
"""

from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

import sys
from pathlib import Path

# Ensure repo root and person1 are in sys.path
_repo_root = Path(__file__).resolve().parent.parent.parent
_person1_dir = _repo_root / "person1"
for p in [str(_repo_root), str(_person1_dir)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from data_bridge import (
    FinancialDataBridge,
    data_bridge,
    UserNotFoundError,
    SymbolNotFoundError,
    DataBridgeError,
)

# Robust import of Person 1 graph
try:
    from orchestration.graph import FinancialAIGraph
except ImportError:
    try:
        from person1.orchestration.graph import FinancialAIGraph
    except ImportError:
        FinancialAIGraph = None

ai_router = APIRouter(tags=["Multi-Agent AI Intelligence"])

# Singleton orchestrator graph instance
_last_import_error = None

def get_ai_graph():
    global FinancialAIGraph, _last_import_error
    if FinancialAIGraph is None:
        try:
            import sys
            from pathlib import Path
            _r = Path(__file__).resolve().parent.parent.parent
            _p1 = _r / "person1"
            for _dir in [str(_p1), str(_r)]:
                if _dir not in sys.path:
                    sys.path.insert(0, _dir)
            
            # Ensure models package path includes person1/models
            import models
            _p1_models = str(_p1 / "models")
            if hasattr(models, "__path__") and _p1_models not in models.__path__:
                models.__path__.append(_p1_models)

            from orchestration.graph import FinancialAIGraph as FGraph
            FinancialAIGraph = FGraph
        except Exception as exc:
            _last_import_error = str(exc)
            import logging
            logging.getLogger("ai_routes").error(f"Failed to import FinancialAIGraph: {exc}")
    try:
        return FinancialAIGraph() if FinancialAIGraph is not None else None
    except Exception as exc:
        _last_import_error = f"Instantiation error: {exc}"
        return None






class AIAnalysisRequest(BaseModel):
    user_id: str = Field(..., description="User ID in Person 4 database (e.g. moderate_001)")
    symbol: str = Field(..., description="Stock ticker symbol (e.g. RELIANCE.NS, TCS, AAPL)")
    analysis_type: Optional[str] = Field("full", description="Type of analysis: full, technical, fundamental, sentiment, risk")
    include_rag: Optional[bool] = Field(True, description="Whether to include semantic RAG filing citations")
    include_news: Optional[bool] = Field(True, description="Whether to include live news sentiment")


class AgentSignalOutput(BaseModel):
    agent: str
    signal: str
    confidence: float
    reasons: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    latency_ms: int = 0


class AIAnalysisResponse(BaseModel):
    symbol: str
    requested_symbol: str
    normalized_symbol: str
    user_id: str
    signal: str
    confidence: float
    verdict: str
    key_drivers: List[str] = Field(default_factory=list)
    risk_assessment: List[str] = Field(default_factory=list)
    personalization_note: str = ""
    allocation_suggestion: str = ""
    sources: List[str] = Field(default_factory=list)
    technical: Optional[Dict[str, Any]] = None
    fundamental: Optional[Dict[str, Any]] = None
    sentiment: Optional[Dict[str, Any]] = None
    risk: Optional[Dict[str, Any]] = None
    metrics: Dict[str, Any] = Field(default_factory=dict)
    meta: Dict[str, Any] = Field(default_factory=dict)


@ai_router.post("/ai/analyze", summary="Run Unified Multi-Agent AI Analysis")
async def analyze_stock_ai(request: AIAnalysisRequest):
    """
    Executes the 5-Agent parallel AI investment analysis pipeline for a specified user and stock.
    Automatically fetches market quotes, indicators, news, RAG evidence, and user risk capacity
    via the FinancialDataBridge.
    """
    ai_graph = get_ai_graph()
    if ai_graph is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Multi-Agent AI Engine unavailable: {_last_import_error}",
        )


    # 1. Build unified AI input payload via data bridge
    try:
        unified_input = data_bridge.build_ai_analysis_input(
            user_id=request.user_id,
            symbol=request.symbol,
        )
    except UserNotFoundError as une:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(une),
        )
    except SymbolNotFoundError as sne:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(sne),
        )
    except DataBridgeError as dbe:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Data bridge error: {str(dbe)}",
        )

    # 2. Execute Person 1 FinancialAIGraph asynchronously
    try:
        raw_ai_result = await ai_graph.run(unified_input.model_dump())


        # Enrich response with user ID and symbol metadata
        raw_ai_result["user_id"] = request.user_id
        raw_ai_result["requested_symbol"] = unified_input.requested_symbol
        raw_ai_result["normalized_symbol"] = unified_input.normalized_symbol
        raw_ai_result["signal"] = raw_ai_result.get("overall_signal", "HOLD")
        raw_ai_result["verdict"] = raw_ai_result.get("overall_signal", "HOLD")
        raw_ai_result["key_drivers"] = raw_ai_result.get("key_reasons", [])
        raw_ai_result["risk_assessment"] = raw_ai_result.get("risks", [])
        raw_ai_result["meta"] = unified_input.meta

        return raw_ai_result


    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Multi-agent execution error: {str(exc)}",
        )
 