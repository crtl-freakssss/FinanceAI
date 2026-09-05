"""
StIC Integration Configuration
Manages environment settings and connection parameters for the StIC integration layer.
"""

import os

class StICConfig:
    """Configuration class for StIC adapter and MCP tools."""
    
    PERSON4_API_URL: str = os.getenv("PERSON4_API_URL", "http://localhost:8000")
    STIC_API_URL: str = os.getenv("STIC_API_URL", "http://localhost:8080")
    STIC_PROJECT_ID: str = os.getenv("STIC_PROJECT_ID", "15879964569093521067")
    STIC_PROJECT_TITLE: str = "SI Terminal Intelligence Platform"
    
    # Updated Design System Tokens (StIC Dark High-Precision Intelligence Theme)
    THEME_BG: str = "#051424"
    THEME_SURFACE: str = "#122131"
    THEME_PRIMARY: str = "#2dd4bf"
    THEME_PRIMARY_BRIGHT: str = "#57f1db"
    THEME_SECONDARY: str = "#10b981"
    THEME_TERTIARY: str = "#ffced0"
    THEME_ERROR: str = "#f43f5e"
    THEME_OUTLINE: str = "#3c4a46"



stic_config = StICConfig()
