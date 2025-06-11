"""
irrimax_interactive.py
Created by A.J. Brown
Agricultural Data Scientist
CSU Agricultural Water Quality Program
Ansley.Brown@colostate.edu
---------------------------
This script uses Python to interact with the IrriMAX Live API v1.9 to retrieve soil 
sensor data for use in WISE Pro. Supports both interactive and headless (server) use.

URL: https://www.irrimaxlive.com/help/api.html
Example Call: https://www.irrimaxlive.com/api/?cmd=getreadings&name=Soybeans%201&from=20110911000000&key=APIKEYHERE


Data units:
Sensor columns are structured as `<Type><Index>(<Depth>)`, for example, `A3(25)` means the third moisture sensor at 25 cm depth.

| Prefix | Sensor Type                              | Units            | Notes                                 |
|--------|------------------------------------------|------------------|---------------------------------------|
| `A`    | Soil Moisture (Volumetric Water Content) | %                | Based on depth (e.g., `A1(5)`)        |
| `S`    | Soil Salinity (Electrical Conductivity)  | µS/cm            | Based on depth (e.g., `S1(5)`)        |
| `T`    | Soil Temperature                         | °C               | Based on depth (e.g., `T1(5)`)        |
| `V`    | Voltage                                  | Volts (V)        | System voltages, not tied to depth    |

"""
import requests
from datetime_helpers import valid_start, valid_end
import logging
from irrimax_methods import get_loggers, get_readings

logger = logging.getLogger(__name__)

session = requests.Session()
  
def run_interactive():
    """Interactive console mode."""
    logger.info("Choose an option:")
    logger.info("1. List available loggers")
    logger.info("2. Fetch readings for a specific logger")
    choice = input("Enter 1 or 2: ").strip()

    if choice == "1":
        loggers = get_loggers()
        logger.info("\nAvailable Loggers:")
        for lg in loggers:
            logger.info(f" - {lg['name']}")
    elif choice == "2":
        logger_name = input("Enter logger name (case-sensitive): ").strip()

        while True:
            start_str = input("Enter start date or datetime (YYYY-MM-DD[THH:MM:SS]): ").strip()
            end_str   = input("Enter end   date or datetime (YYYY-MM-DD[THH:MM:SS]): ").strip()

            try:
                from_date = valid_start(start_str)
                to_date   = valid_end(end_str)
                logger.info(f"\nFetching data for logger: {logger_name} ({from_date.date()} to {to_date.date()})...")
                df = get_readings(logger_name, from_date, to_date)

                if df.empty:
                    logger.info("No data found for the given date range.")
                    retry = input("Try a new date range? (y/n): ").strip().lower()
                    if retry != "y":
                        logger.info("Exiting.")
                        break
                else:
                    logger.info(df.head())
                    break

            except ValueError as ve:
                logger.error(f"Date Error: {ve}")
            except Exception as e:
                logger.error(f"Error: {e}")
                break
    else:
        logger.error("Invalid selection. Exiting.")

if __name__ == "__main__":
    run_interactive()