from sqlalchemy import create_engine
from sqlalchemy.dialects import postgresql
from sqlalchemy import Integer, Float

DB_URL = "postgresql+psycopg2://username:password@hostname:5432/dbname"
engine = create_engine(DB_URL)

dtype_map = {
    "depth":            postgresql.ARRAY(Integer),
    "vwc":              postgresql.ARRAY(Float),
    "conductivity":     postgresql.ARRAY(Float),
    "temperature":      postgresql.ARRAY(Float),
    "available_water":  postgresql.ARRAY(Float),
    "salinity":         postgresql.ARRAY(Float),
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
