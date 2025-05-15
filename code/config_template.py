"""
config_template.py
-------------------------------------------------
Private credentials for the soil-moisture API collectors.

RENAME this file to `config.py` and keep it out of version control
(already referenced in .gitignore).

Populate the placeholders below with your own keys / credentials.
Only include the variables you need for the platforms you use.

-------------------------------------------------
"""

# ───────────────────────────────────────────────
# 1. SENTEK / IrriMAX Live
# ───────────────────────────────────────────────
IRRIMAX_API_KEY: str = "REPLACE_WITH_YOUR_IRRIMAX_API_KEY"


# ───────────────────────────────────────────────
# 2. AquaSpy (AgSpy)
#    Choose whichever auth method your account uses.
# ───────────────────────────────────────────────
# If your AquaSpy account uses a token:
# AQUASPY_API_TOKEN: str = "REPLACE_WITH_YOUR_AQUASPY_TOKEN"

# …or, if it requires user credentials:
# AQUASPY_USERNAME: str = "REPLACE_WITH_YOUR_AQUASPY_USERNAME"
# AQUASPY_PASSWORD: str = "REPLACE_WITH_YOUR_AQUASPY_PASSWORD"


# ───────────────────────────────────────────────
# 3. GroGuru InSites
#    The API can be accessed either with OAuth‑style
#    client credentials *or* a static API key.
# ───────────────────────────────────────────────
# OAuth flow (preferred):
# GROGURU_CLIENT_ID: str     = "REPLACE_WITH_YOUR_GROGURU_CLIENT_ID"
# GROGURU_CLIENT_SECRET: str = "REPLACE_WITH_YOUR_GROGURU_CLIENT_SECRET"
# GROGURU_USERNAME: str      = "REPLACE_WITH_YOUR_GROGURU_USERNAME"
# GROGURU_PASSWORD: str      = "REPLACE_WITH_YOUR_GROGURU_PASSWORD"

# …or static key:
# GROGURU_API_KEY: str = "REPLACE_WITH_YOUR_GROGURU_API_KEY"


# ───────────────────────────────────────────────
# Optional global settings
# ───────────────────────────────────────────────
# Default timeout (seconds) for all HTTP requests
REQUEST_TIMEOUT: int = 30
