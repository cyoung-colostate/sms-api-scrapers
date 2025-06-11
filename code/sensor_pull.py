from irrimax_scraper import main as irrimax_main
from groguru_scraper import main as groguru_main
import datetime

def main():
    """Main function to run the sensor pull scripts."""
    print("Starting sensor pull scripts...")

    end_time = datetime.datetime.now(datetime.timezone.utc).isoformat()

    # Run IrriMAX scraper
    print("Running IrriMAX scraper...")
    irrimax_main(start, end_time)

    # Run GroGuru scraper
    print("Running GroGuru scraper...")
    groguru_main(start, end_time)

    print("Sensor pull completed successfully.")

if (__name__ == "__main__"):
    main()