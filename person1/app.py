from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any

from orchestration.graph import FinancialAIGraph

app = FastAPI(
    title="Finance AI - Multi-Agent Investment Intelligence",
    version="1.0.0",
    description="HackVerse 2026 PS-01 | Person 1 AI Orchestrator"
)

# -------------------- CORS --------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Change later if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator
graph = FinancialAIGraph()


# -------------------- Request Model --------------------
class AnalysisRequest(BaseModel):
    symbol: str
    market_data: Dict[str, Any]
    news_data: Dict[str, Any]
    fundamental_data: Dict[str, Any]
    user_profile: Dict[str, Any]


# -------------------- Routes --------------------
@app.get("/")
async def root():
    return {
        "message": "Finance AI Multi-Agent Backend Running",
        "agents": [
            "Technical Agent",
            "Fundamental Agent",
            "Sentiment Agent",
            "Risk Agent",
            "Synthesis Agent"
        ]
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "parallel_agents": 4
    }


@app.post("/analyze-stock")
async def analyze_stock(request: AnalysisRequest):
    """
    Main endpoint used by the frontend / orchestrator.
    """
    result = await graph.run(request.model_dump())
    return result


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PERSON1_PORT", "8001"))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
