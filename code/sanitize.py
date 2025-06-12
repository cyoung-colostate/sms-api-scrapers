import re
import pandas as pd

def sanitize_groguru(groguru_df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert the raw GroGuru DataFrame into a sanitized format suitable for Postgres.
    Columns produced:
      - source: 'groguru'
      - farm: farm column
      - site: site column
      - logger_id: device column
      - timestamp: original timestamp column
      - depth: list of sensor indices (integers)
      - vwc: list of values from moistureX columns, in index order
      - conductivity: list of values from conductivityX columns, in index order
      - temperature: list of values from temp_fX columns, in index order
      - available_water: list of values from awX columns, in index order
      - salinity: list of values from salinityX columns, in index order
    """
    # Patterns for each metric
    moisture_pattern = re.compile(r"^moisture(\d+)$", re.IGNORECASE)
    cond_pattern     = re.compile(r"^conductivity(\d+)$", re.IGNORECASE)
    temp_pattern     = re.compile(r"^temp_f(\d+)$", re.IGNORECASE)
    aw_pattern       = re.compile(r"^aw(\d+)$", re.IGNORECASE)
    salinity_pattern = re.compile(r"^salinity(\d+)$", re.IGNORECASE)

    moisture_info = []
    cond_info     = []
    temp_info     = []
    aw_info       = []
    salinity_info = []

    for col in groguru_df.columns:
        m = moisture_pattern.match(col)
        if m:
            idx = int(m.group(1))
            moisture_info.append((idx, col))
            continue
        m = cond_pattern.match(col)
        if m:
            idx = int(m.group(1))
            cond_info.append((idx, col))
            continue
        m = temp_pattern.match(col)
        if m:
            idx = int(m.group(1))
            temp_info.append((idx, col))
            continue
        m = aw_pattern.match(col)
        if m:
            idx = int(m.group(1))
            aw_info.append((idx, col))
        m = salinity_pattern.match(col)
        if m:
            idx = int(m.group(1))
            salinity_info.append((idx, col))

    # Sort each metric by the sensor index
    moisture_info.sort(key=lambda x: x[0])
    cond_info.sort(key=lambda x: x[0])
    temp_info.sort(key=lambda x: x[0])
    aw_info.sort(key=lambda x: x[0])
    salinity_info.sort(key=lambda x: x[0])

    # Extract lists of column names and indices
    depths = [idx for idx, _ in temp_info]  # use temp indices as depths
    vwc_cols       = [col for _, col in moisture_info]
    cond_cols      = [col for _, col in cond_info]
    temp_cols      = [col for _, col in temp_info]
    aw_cols        = [col for _, col in aw_info]
    salinity_cols  = [col for _, col in salinity_info]

    # Build the clean DataFrame
    clean_df = pd.DataFrame({
        "source":         "groguru",
        "farm":           groguru_df.get("farm", None),
        "site":           groguru_df.get("site", None),
        "logger_id":      groguru_df.get("device", None),
        "timestamp":      pd.to_datetime(groguru_df["timestamp"]),
        "depth":          [depths] * len(groguru_df),
        "vwc":            groguru_df[vwc_cols].values.tolist(),
        "conductivity":   groguru_df[cond_cols].values.tolist(),
        "temperature":    groguru_df[temp_cols].values.tolist(),
        "available_water":groguru_df[aw_cols].values.tolist(),
        "salinity":       groguru_df[salinity_cols].values.tolist()
    })

    return clean_df


def sanitize_irrimax(irrimax_df):
    """
    Convert the raw IrriMax DataFrame into a sanitized format suitable for Postgres.
    Columns produced:
      - source: 'irrimax'
      - farm: None
      - site: None
      - logger_id: logger_id column
      - timestamp: "Date Time" column converted to datetime
      - depth: list of sensor indices (integers)
      - vwc: list of values from moistureX columns, in index order
      - conductivity: list of values from conductivityX columns, in index order
      - temperature: list of values from temp_fX columns, in index order
      - available_water: None
      - salinity: None
    """
    # 1) Extract (index, depth, col) for A, S, T columns
    a_pattern = re.compile(r"^A(\d+)\((\d+)\)$")
    s_pattern = re.compile(r"^S(\d+)\((\d+)\)$")
    t_pattern = re.compile(r"^T(\d+)\((\d+)\)$")

    a_info = []
    s_info = []
    t_info = []

    for col in irrimax_df.columns:
        m = a_pattern.match(col)
        if m:
            idx, depth = int(m.group(1)), int(m.group(2))
            a_info.append((idx, depth, col))
        m = s_pattern.match(col)
        if m:
            idx, depth = int(m.group(1)), int(m.group(2))
            s_info.append((idx, depth, col))
        m = t_pattern.match(col)
        if m:
            idx, depth = int(m.group(1)), int(m.group(2))
            t_info.append((idx, depth, col))

    # 2) Sort by the numeric index
    a_info.sort(key=lambda x: x[0])
    s_info.sort(key=lambda x: x[0])
    t_info.sort(key=lambda x: x[0])

    # 3) Build lists of depths and column names
    depths = [depth for _, depth, _ in a_info]
    vwc_cols = [col for _, _, col in a_info]
    cond_cols = [col for _, _, col in s_info]
    temp_cols = [col for _, _, col in t_info]

    # 4) Construct the new DataFrame
    clean_df = pd.DataFrame({
        "source": "irrimax",
        "farm": None,
        "site": None,
        "logger_id": irrimax_df["logger_id"],
        "timestamp": pd.to_datetime(irrimax_df["Date Time"], format="%Y/%m/%d %H:%M:%S"),
        "depth": [depths] * len(irrimax_df),
        "vwc": irrimax_df[vwc_cols].values.tolist(),
        "conductivity": irrimax_df[cond_cols].values.tolist(),
        "temperature": irrimax_df[temp_cols].values.tolist(),
        "available_water": None,
        "salinity": None
    })
    
    return clean_df