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
# Demo key:
#IRRIMAX_API_KEY: str = "56ba75ce-af38-4f10-9147-6f0d9ec82b12"


# ───────────────────────────────────────────────
# 2. AquaSpy (AgSpy API)
#    Site-level access — username/password required
# ───────────────────────────────────────────────
AQUASPY_USERNAME: str = "REPLACE_WITH_YOUR_AQUASPY_USERNAME"
AQUASPY_PASSWORD: str = "REPLACE_WITH_YOUR_AQUASPY_PASSWORD"


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
