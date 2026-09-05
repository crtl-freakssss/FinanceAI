/**
 * StIC Terminal Frontend API Client
 * Centralized service layer for communicating with the Unified FastAPI Backend (:8000).
 */

const StICApiClient = (() => {
  // Smart base URL: detects same-origin if on HTTP/HTTPS, falls back to http://127.0.0.1:8000/api/v1
  const detectBaseUrl = () => {
    if (typeof window !== "undefined" && window.STIC_BACKEND_URL) {
      return window.STIC_BACKEND_URL;
    }
    if (typeof window !== "undefined" && window.location && window.location.origin && window.location.origin.startsWith("http")) {
      return `${window.location.origin}/api/v1`;
    }
    return "http://127.0.0.1:8000/api/v1";
  };

  const BASE_URL = detectBaseUrl();
  const DEFAULT_TIMEOUT_MS = 10000;

  /**
   * Helper: Normalize stock symbol according to platform rules
   */
  function normalizeSymbol(symbol) {
    if (!symbol) return "RELIANCE.NS";
    const s = symbol.trim().toUpperCase();
    const INDIAN_ALIASES = {
      "RELIANCE": "RELIANCE.NS",
      "TCS": "TCS.NS",
      "INFY": "INFY.NS",
      "HDFCBANK": "HDFCBANK.NS",
      "ITC": "ITC.NS"
    };
    return INDIAN_ALIASES[s] || s;
  }

  /**
   * Centralized HTTP Request Handler with AbortController timeout
   */
  async function request(path, options = {}) {
    const url = `${BASE_URL}${path}`;
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), options.timeout || DEFAULT_TIMEOUT_MS);

    const headers = {
      "Accept": "application/json",
      "Content-Type": "application/json",
      ...(options.headers || {})
    };

    try {
      const response = await fetch(url, {
        ...options,
        headers,
        signal: controller.signal
      });
      clearTimeout(timeoutId);

      if (!response.ok) {
        let errDetail = `HTTP ${response.status}: ${response.statusText}`;
        try {
          const errJson = await response.json();
          errDetail = errJson.detail || errJson.message || errDetail;
        } catch (_) {}
        const error = new Error(errDetail);
        error.status = response.status;
        throw error;
      }

      return await response.json();
    } catch (err) {
      clearTimeout(timeoutId);
      if (err.name === "AbortError") {
        const timeoutError = new Error(`Request timed out after ${options.timeout || DEFAULT_TIMEOUT_MS}ms`);
        timeoutError.status = 408;
        throw timeoutError;
      }
      throw err;
    }
  }

  return {
    normalizeSymbol,
    getBaseUrl: () => BASE_URL,

    // System Status
    checkHealth: () => request("/health"),
    checkReadiness: () => request("/readiness"),

    // Person 4: User Profile, Portfolio & Risk
    fetchUserProfile: (userId) => request(`/users/${encodeURIComponent(userId)}/profile`),
    fetchUserPortfolio: (userId) => request(`/users/${encodeURIComponent(userId)}/portfolio`),
    fetchPortfolioAnalysis: (userId) => request(`/users/${encodeURIComponent(userId)}/portfolio/analysis`),
    fetchAdvancedRisk: (userId) => request(`/users/${encodeURIComponent(userId)}/portfolio/risk/advanced`),
    fetchUserBehavior: (userId) => request(`/users/${encodeURIComponent(userId)}/behavior`),
    fetchInvestorProfile: (userId) => request(`/users/${encodeURIComponent(userId)}/investor-profile`),
    fetchPersonalizationContext: (userId, symbol, sector = "Energy", marketCap = "LARGE") => {
      const normSym = normalizeSymbol(symbol);
      const params = new URLSearchParams({ sector, market_cap: marketCap });
      return request(`/users/${encodeURIComponent(userId)}/context/${encodeURIComponent(normSym)}?${params}`);
    },

    // Person 2: Market Data, Indicators, News & RAG
    fetchMarketData: (symbol) => request(`/market/${encodeURIComponent(normalizeSymbol(symbol))}`),
    fetchMarketHistory: (symbol, period = "1mo") => {
      const params = new URLSearchParams({ period });
      return request(`/market/${encodeURIComponent(normalizeSymbol(symbol))}/history?${params}`);
    },
    fetchMarketIndicators: (symbol, period = "3mo") => {
      const params = new URLSearchParams({ period });
      return request(`/market/${encodeURIComponent(normalizeSymbol(symbol))}/indicators?${params}`);
    },
    fetchNews: (symbol) => request(`/news/${encodeURIComponent(normalizeSymbol(symbol))}`),
    queryRAG: (query, symbol = null, topK = 3) => {
      const body = {
        query,
        symbol: symbol ? normalizeSymbol(symbol) : null,
        top_k: topK
      };
      return request("/rag/query", {
        method: "POST",
        body: JSON.stringify(body)
      });
    },

    // Person 1: Multi-Agent AI Analysis
    runMultiAgentAnalysis: (userId, symbol, analysisType = "full", includeRag = true, includeNews = true) => {
      const body = {
        user_id: userId,
        symbol: normalizeSymbol(symbol),
        analysis_type: analysisType,
        include_rag: includeRag,
        include_news: includeNews
      };
      return request("/ai/analyze", {
        method: "POST",
        body: JSON.stringify(body),
        timeout: 15000 // 15s timeout for full 5-agent parallel pipeline
      });
    }
  };
})();

// Export globally for browser scripts and module imports
if (typeof window !== "undefined") {
  window.StICApiClient = StICApiClient;
}
if (typeof module !== "undefined" && module.exports) {
  module.exports = StICApiClient;
}
