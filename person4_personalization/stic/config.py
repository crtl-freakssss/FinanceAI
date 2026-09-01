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
    
    # Updated Design System Tokens (StIC Candy / DM Sans Theme)
    THEME_BG: str = "#fef7ff"
    THEME_SURFACE: str = "#f8eef8"
    THEME_PRIMARY: str = "#e040a0"
    THEME_SECONDARY: str = "#7c52aa"
    THEME_TERTIARY: str = "#0096cc"
    THEME_ERROR: str = "#e53e3e"
    THEME_OUTLINE: str = "#dcc8e0"

stic_config = StICConfig()
