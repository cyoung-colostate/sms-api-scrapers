# IrriMAX Sensor Data Column Legend

This table documents the meaning of column headers returned by the IrriMAX Live API when retrieving logger data. Each sensor reading corresponds to a measurement type at a specific depth.

---

## General Columns

| Column        | Description                                               |
|---------------|-----------------------------------------------------------|
| `Date Time`   | Timestamp of the sensor reading (in local site time)      |
| `V1`, `V2`    | Voltage readings from the probe (often supply or upload)  |

---

## Depth-Specific Sensor Columns

Sensor columns are structured as `<Type><Index>(<Depth>)`, for example, `A3(25)` means the third moisture sensor at 25 cm depth.

| Prefix | Sensor Type                              | Units            | Notes                                 |
|--------|------------------------------------------|------------------|---------------------------------------|
| `A`    | Soil Moisture (Volumetric Water Content) | %                | Based on depth (e.g., `A1(5)`)        |
| `S`    | Soil Salinity (Electrical Conductivity)  | µS/cm            | Based on depth (e.g., `S1(5)`)        |
| `T`    | Soil Temperature                         | °C               | Based on depth (e.g., `T1(5)`)        |
| `V`    | Voltage                                  | Volts (V)        | System voltages, not tied to depth    |

---

## Example

| Column     | Meaning                                  |
|------------|-------------------------------------------|
| `A3(25)`   | Moisture reading at 25 cm depth           |
| `S3(25)`   | Salinity reading at 25 cm depth           |
| `T3(25)`   | Temperature reading at 25 cm depth        |
| `V1`       | Probe voltage supply or battery level     |

---

## Notes

- Depths are measured in centimeters (cm), unless otherwise specified by the site configuration.
- Invalid sensor readings may appear as `-1.000` or similar placeholders.
- The exact number of sensors and their depths may vary by probe model.

For API reference, see: [https://www.irrimaxlive.com/help/api.html](https://www.irrimaxlive.com/help/api.html)

# Example Run of the Script in Interactive and Headless Mode
Interactive mode:
```bash
(playground2) C:\Users\ansle\OneDrive\Documents\GitHub\sms-api-scrapers\code>python irrimax_scraper.py
Choose an option:
1. List available loggers
2. Fetch readings for a specific logger
Enter 1 or 2: 2
Enter logger name (case-sensitive): 8A_8
Enter start date (YYYY-MM-DD): 2024-06-10
Enter end date (YYYY-MM-DD): 2024-10-15

Fetching data for logger: 8A_8 (2024-06-10 to 2024-10-15)...
             Date Time      V1      V2     A1(5)     S1(5)  ...    S8(75)    T8(75)    A9(85)    S9(85)  T9(85)
0  2024/06/10 00:00:00  13.735  13.474  16.63106  379.6608  ...  844.3812  17.04999  40.48423  4438.727   16.72
1  2024/06/10 00:30:00  13.769  -1.000  16.62494  376.4792  ...  844.4537  17.04999  40.48423  4438.727   16.72
2  2024/06/10 01:00:00  13.787  -1.000  16.62494  378.4209  ...  844.3812  17.01999  40.49162  4439.438   16.72
3  2024/06/10 01:30:00  13.783  -1.000  16.58220  373.6646  ...  844.0801  16.95001  40.46944  4437.237   16.75
4  2024/06/10 02:00:00  13.707  -1.000  16.60052  373.4932  ...  844.3039  17.00000  40.49162  4422.122   16.72

[5 rows x 30 columns]
```

Headless mode:
```bash
(playground2) C:\Users\ansle\OneDrive\Documents\GitHub\sms-api-scrapers\code>python irrimax_scraper.py 8A_8 2024-06-10 2024-10-15
Fetching data for logger: 8A_8 (2024-06-10 to 2024-10-15)...
             Date Time      V1      V2     A1(5)     S1(5)  ...    S8(75)    T8(75)    A9(85)    S9(85)  T9(85)
0  2024/06/10 00:00:00  13.735  13.474  16.63106  379.6608  ...  844.3812  17.04999  40.48423  4438.727   16.72
1  2024/06/10 00:30:00  13.769  -1.000  16.62494  376.4792  ...  844.4537  17.04999  40.48423  4438.727   16.72
2  2024/06/10 01:00:00  13.787  -1.000  16.62494  378.4209  ...  844.3812  17.01999  40.49162  4439.438   16.72
3  2024/06/10 01:30:00  13.783  -1.000  16.58220  373.6646  ...  844.0801  16.95001  40.46944  4437.237   16.75
4  2024/06/10 02:00:00  13.707  -1.000  16.60052  373.4932  ...  844.3039  17.00000  40.49162  4422.122   16.72

[5 rows x 30 columns]
```