from irrimax_scraper import main as irrimax_main
from groguru_scraper import main as groguru_main

def main():
    """Main function to run the sensor pull scripts."""
    print("Starting sensor pull scripts...")

    # Run IrriMAX scraper
    print("Running IrriMAX scraper...")
    irrimax_main()

    # Run GroGuru scraper
    print("Running GroGuru scraper...")
    groguru_main()

    print("Sensor pull completed successfully.")

if (__name__ == "__main__"):
    main()