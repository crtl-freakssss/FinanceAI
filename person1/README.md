# Person 1 — Multi-Agent AI Backend

Backend module for **HackVerse 2026 PS-01: Multi-Agent Autonomous Financial Intelligence System for Retail Investors**.

## Overview

This module implements the AI orchestration layer of the project. It executes multiple specialized agents in parallel and generates an explainable investment recommendation for a given stock.

### AI Agents

* **Technical Agent** — RSI, EMA, MACD, momentum, volatility and volume analysis.
* **Fundamental Agent** — Revenue growth, profit growth, PE ratio and RAG-based financial document analysis.
* **Sentiment Agent** — News sentiment scoring and headline analysis.
* **Risk Agent** — Personalized recommendation using user risk tolerance, portfolio exposure and investment horizon.
* **Synthesis Agent** — Combines all agent outputs into one final recommendation.

## Folder Structure

person1/
├── agents/
├── orchestration/
├── models/
├── mock_data/
├── tests/
├── app.py
├── requirements.txt
└── README.md

## Tech Stack

* Python 3.13
* FastAPI
* Pydantic
* AsyncIO
* Pytest

## API Endpoint

### POST `/analyze-stock`

Accepts stock market data, news data, financial fundamentals and user profile information.

Returns:

* Overall recommendation (`BUY`, `HOLD`, `SELL`, `AVOID`)
* Confidence score
* Explainable reasons
* Risk factors
* Source references
* Individual agent outputs
* Performance metrics

## Running Locally

Install dependencies:

```bash
py -m pip install -r requirements.txt
```

Run the backend:

```bash
py -m uvicorn app:app --reload
```

Open Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

## Sample Input

A sample request payload is available in:

```text
mock_data/analysis_input.json
```

## Features

* Multi-agent AI architecture.
* Parallel execution using `asyncio.gather()`.
* Consensus-based recommendation engine.
* Personalized investment risk assessment.
* Explainable AI output with reasons and sources.
* Performance latency metrics for each agent.
