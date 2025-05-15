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

from typing import List

# ───────────────────────────────────────────────
# 1. SENTEK / IrriMAX Live
# ───────────────────────────────────────────────
IRRIMAX_API_KEY: str = "REPLACE_WITH_YOUR_IRRIMAX_API_KEY"


# ───────────────────────────────────────────────
# 4. AquaSpy AgSpy
# ───────────────────────────────────────────────
AQUASPY_SITE_IDS: List[int] = ["REPLACE_WITH_SITE_ID_1", "REPLACE_WITH_SITE_ID_2"]

# NOTE: While this API does not require authentication, ensure that the siteID 
# values are kept confidential to prevent unauthorized data access.

# ───────────────────────────────────────────────
# 3. GroGuru InSites
# ───────────────────────────────────────────────
GROGURU_USERNAME: str = "REPLACE_WITH_YOUR_EMAIL"
GROGURU_PASSWORD: str = "REPLACE_WITH_YOUR_PASSWORD"


# ───────────────────────────────────────────────
# Optional global settings
# ───────────────────────────────────────────────
# Default timeout (seconds) for all HTTP requests
REQUEST_TIMEOUT: int = 30
