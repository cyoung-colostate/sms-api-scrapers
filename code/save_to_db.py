from sqlalchemy.dialects import postgresql
from sqlalchemy import Integer, Float
from db import engine

dtype_map = {
    "depth":            postgresql.ARRAY(Integer),
    "vwc":              postgresql.ARRAY(Float),
    "conductivity":     postgresql.ARRAY(Float),
    "temperature":      postgresql.ARRAY(Float),
    "available_water":  postgresql.ARRAY(Float),
    "salinity":         postgresql.ARRAY(Float),
    "is_metric":        postgresql.BOOLEAN,
    # the rest will be inferred (TEXT, TIMESTAMP, etc.)
}

def save_to_db(df):
    df.to_sql(
        name="sensor_data",
        con=engine,
        if_exists="append",
        index=False,
        dtype=dtype_map,
    )
