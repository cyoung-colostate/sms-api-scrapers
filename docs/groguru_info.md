# GroGuru API overview and Notes
The groguru API is a RESTful API that allows users to interact with GroGuru's soil moisture sensors and data. The API provides endpoints for authentication, fetching organization data, site data, device data, and sensor readings.
The API uses JSON for data exchange and requires authentication via a username and password. The API supports various query parameters to filter and sort the data returned.

The `groguru_scraper.py` script is designed to interact with the GroGuru API. It allows users to authenticate, fetch organization and site data, and retrieve sensor readings for a specified site and device. It requires the user to place their credentials in a separate file (`config.py`) to avoid hardcoding sensitive information in the script.


## GroGuru Data Output: Column Descriptions

| Column Name         | Description                                                                 |
|---------------------|-----------------------------------------------------------------------------|
| `timestamp`         | UTC datetime when the measurement was recorded                              |
| `temp_f0`–`temp_f5` | Soil temperature at different depths (°F); typically from shallow to deep   |
| `moisture0`–`moisture5` | Volumetric water content (%) at different soil depths                    |
| `aw0`–`aw5`          | Plant-available water at different depths (unitless index or % based on sensor) |
| `salinity0`–`salinity5` | Soil salinity at various depths (units vary: typically dS/m or mS/cm)   |
| `conductivity0`–`conductivity5` | Electrical conductivity of soil at different depths              |
| `rssi`              | Signal strength of the sensor’s data transmission (dBm)                     |
| `v_bandgap`         | Internal voltage reference value for sensor diagnostics (V)                 |
| `gddEnvelope`       | Growing degree day value or accumulation at time of reading (if reported)   |

> **Note:** The numeric suffix (e.g., `0`, `1`, `2`) typically corresponds to sensor depth. Refer to sensor metadata or the `hardwareSensorLocation` JSON for exact inches (e.g., `moisture0` = 4", `moisture1` = 8", etc.).


## Sensor Depth Mapping (GroGuru AquaCheck Probe)

This section documents how to interpret the sensor indices returned by the GroGuru API based on AquaCheck probe configuration. Each sensor is associated with a depth offset in inches from the soil surface.


| Sensor Index | Sensor Name  | Depth Offset (inches)  | Description        |
|--------------|--------------|------------------------|--------------------|
| 0            | 1            | 4                      | Shallowest sensor  |
| 1            | 2            | 8                      | 2nd sensor         |
| 2            | 3            | 16                     | 3rd sensor         |
| 3            | 4            | 24                     | 4th sensor         |
| 4            | 5            | 32                     | 5th sensor         |
| 5            | 6            | 40                     | Deepest sensor     |


When parsed, the GroGuru data columns (e.g., `moisture0`, `temp_f0`) map to depth values as follows:

| Data Column   | Depth (inches) |
|---------------|----------------|
| moisture0     | 4              |
| moisture1     | 8              |
| moisture2     | 16             |
| moisture3     | 24             |
| moisture4     | 32             |
| moisture5     | 40             |

### Reference Depth

The `referenceDepth` is typically set at **12 inches**, which means the API may align readings to this depth when calculating additional variables or normalized values. However, the raw sensor offsets above reflect actual physical depths from the surface. All renaming and interpretation in this script is based on the `depthOffset` values, not the reference depth.

## Current issues
The REST API only returns the most recent 5 readings for a given date range. This is a limitation of the API and not the script itself. The script currently does not handle pagination or multiple pages of data. See the example output below for a demonstration of this limitation.

> [!NOTE]
> To proceed, I will brute force the collection of all data by iterating through the date range in 1-hour increments. This will allow us to collect all available data points for the specified date range. This is a temporary solution until the API is updated to support pagination or larger data requests. It is not considered a best practice, as it can be fragile depending on sensor reading frequency, but it is a workaround for the current limitations of the API.

# Example output from current groguru_scraper.py

Interactive mode:
```bash
(playground2) C:\Users\ansle\OneDrive\Documents\GitHub\sms-api-scrapers\code>python groguru_scraper.py
Authenticating with GroGuru API...
Login successful. User: csu-taps
Fetching organization view...
Successfully fetched organization data.
Available Sites:
 - CSU - ARDEC South Demo / Linear (siteId: 11697)
 - CSU - ARDEC South Demo / Wheel Line (siteId: 11698)
 - CSU - TAPS Farm 04 / Farm 04 (siteId: 12046)
 - CSU - TAPS Farm 05 / Farm 05 (siteId: 12047)
 - CSU - TAPS Farm 06 / Farm 06 (siteId: 12048)
 - CSU - TAPS Farm 07 / Farm 07 (siteId: 12049)
 - CSU - TAPS Farm 09 / Farm 09 (siteId: 12050)
 - CSU - TAPS Farm 12 / Farm 12 (siteId: 12051)
 - CSU - TAPS Farm 13 / Farm 13 (siteId: 12052)
 - CSU - TAPS Farm 16 / Farm 16 (siteId: 12053)
 - CSU - TAPS Farm 19 / Farm 19 - Rep 1 (siteId: 12054)
 - CSU - TAPS Farm 19 / Farm 19 - Rep 2 (siteId: 12055)
 - CSU - TAPS Farm 19 / Farm 19 - Rep 3 (siteId: 12056)
 - CSU - TAPS Farm 20 / Farm 20 (siteId: 12057)
Enter a siteId to fetch readings: 11697
Using twigId (deviceId): 0x634e633131334e70
Enter start date (YYYY-MM-DD): 2025-04-15
Enter end date (YYYY-MM-DD): 2025-04-16
Brute force fetching from 2025-04-15 00:00:00 to 2025-04-16 00:00:00 in 2-hour chunks...
Fetching readings for site 11697 and device 0x634e633131334e70 from 2025-04-15 to 2025-04-15...
Empty DataFrame
Columns: [timestamp]
Index: []
Fetching readings for site 11697 and device 0x634e633131334e70 from 2025-04-15 to 2025-04-15...
Empty DataFrame
Columns: [timestamp]
Index: []
Fetching readings for site 11697 and device 0x634e633131334e70 from 2025-04-15 to 2025-04-15...
Empty DataFrame
Columns: [timestamp]
Index: []
Fetching readings for site 11697 and device 0x634e633131334e70 from 2025-04-15 to 2025-04-15...
Empty DataFrame
Columns: [timestamp]
Index: []
Fetching readings for site 11697 and device 0x634e633131334e70 from 2025-04-15 to 2025-04-15...
Empty DataFrame
Columns: [timestamp]
Index: []
Fetching readings for site 11697 and device 0x634e633131334e70 from 2025-04-15 to 2025-04-15...
Empty DataFrame
Columns: [timestamp]
Index: []
Fetching readings for site 11697 and device 0x634e633131334e70 from 2025-04-15 to 2025-04-15...
Empty DataFrame
Columns: [timestamp]
Index: []
Fetching readings for site 11697 and device 0x634e633131334e70 from 2025-04-15 to 2025-04-15...
Empty DataFrame
Columns: [timestamp]
Index: []
Fetching readings for site 11697 and device 0x634e633131334e70 from 2025-04-15 to 2025-04-15...
Empty DataFrame
Columns: [timestamp]
Index: []
Fetching readings for site 11697 and device 0x634e633131334e70 from 2025-04-15 to 2025-04-15...
Empty DataFrame
Columns: [timestamp]
Index: []
Fetching readings for site 11697 and device 0x634e633131334e70 from 2025-04-15 to 2025-04-15...
Empty DataFrame
Columns: [timestamp]
Index: []
Fetching readings for site 11697 and device 0x634e633131334e70 from 2025-04-15 to 2025-04-16...
                  timestamp  rssi   aw0   aw1   aw2   aw3  ...  temp_f1  temp_f2  temp_f3  temp_f4  temp_f5  v_bandgap
0 2025-04-15 23:00:00+00:00 -61.0  0.51  1.04  1.15  1.28  ...     51.8    50.72    49.28    48.92     48.2       2.35
1 2025-04-15 22:30:00+00:00 -62.0  0.51  1.04  1.15  1.28  ...     51.8    50.72    49.28    48.92     48.2       2.35
2 2025-04-15 22:00:00+00:00 -60.0  0.51  1.04  1.15  1.28  ...     51.8    50.72    49.28    48.56     48.2       2.35
3 2025-04-15 21:30:00+00:00 -62.0  0.51  1.04  1.15  1.28  ...     51.8    50.72    49.28    48.56     48.2       2.35
4 2025-04-15 21:00:00+00:00 -57.0  0.51  1.04  1.15  1.28  ...     51.8    50.72    49.28    48.56     48.2       2.35

[5 rows x 22 columns]
Retrieved 47 rows total.
                  timestamp  rssi   aw0   aw1   aw2   aw3  ...  temp_f1  temp_f2  temp_f3  temp_f4  temp_f5  v_bandgap
0 2025-04-15 00:15:00+00:00 -61.0  0.51  1.04  1.14  1.27  ...    51.44    50.36    48.92    48.20    47.84       2.34
1 2025-04-15 00:45:00+00:00   NaN  0.51  1.04  1.14  1.27  ...    51.44    50.36    48.92    48.56    47.84        NaN
2 2025-04-15 01:15:00+00:00 -61.0  0.52  1.04  1.14  1.28  ...    51.44    50.36    48.92    48.56    47.84       2.34
3 2025-04-15 01:45:00+00:00 -61.0  0.52  1.04  1.14  1.27  ...    51.44    50.36    48.92    48.56    47.84       2.33
4 2025-04-15 02:15:00+00:00 -61.0  0.52  1.04  1.14  1.28  ...    51.44    50.36    48.92    48.56    47.84       2.32

[5 rows x 22 columns]
```

Headless mode:
```bash
(playground2) C:\Users\ansle\OneDrive\Documents\GitHub\sms-api-scrapers\code>python groguru_scraper.py --site 11697 --start 2025-04-16 --end 2025-04-17
Authenticating with GroGuru API...
Login successful. User: csu-taps
Fetching organization view...
Successfully fetched organization data.
Brute force fetching from 2025-04-16 00:00:00 to 2025-04-17 00:00:00 in 2-hour chunks...
Fetching readings for site 11697 and device 0x634e633131334e70 from 2025-04-16 to 2025-04-16...
Empty DataFrame
Columns: [timestamp]
Index: []
Fetching readings for site 11697 and device 0x634e633131334e70 from 2025-04-16 to 2025-04-16...
Empty DataFrame
Columns: [timestamp]
Index: []
Fetching readings for site 11697 and device 0x634e633131334e70 from 2025-04-16 to 2025-04-16...
Empty DataFrame
Columns: [timestamp]
Index: []
Fetching readings for site 11697 and device 0x634e633131334e70 from 2025-04-16 to 2025-04-16...
Empty DataFrame
Columns: [timestamp]
Index: []
Fetching readings for site 11697 and device 0x634e633131334e70 from 2025-04-16 to 2025-04-16...
Empty DataFrame
Columns: [timestamp]
Index: []
Fetching readings for site 11697 and device 0x634e633131334e70 from 2025-04-16 to 2025-04-16...
Empty DataFrame
Columns: [timestamp]
Index: []
Fetching readings for site 11697 and device 0x634e633131334e70 from 2025-04-16 to 2025-04-16...
Empty DataFrame
Columns: [timestamp]
Index: []
Fetching readings for site 11697 and device 0x634e633131334e70 from 2025-04-16 to 2025-04-16...
Empty DataFrame
Columns: [timestamp]
Index: []
Fetching readings for site 11697 and device 0x634e633131334e70 from 2025-04-16 to 2025-04-16...
Empty DataFrame
Columns: [timestamp]
Index: []
Fetching readings for site 11697 and device 0x634e633131334e70 from 2025-04-16 to 2025-04-16...
Empty DataFrame
Columns: [timestamp]
Index: []
Fetching readings for site 11697 and device 0x634e633131334e70 from 2025-04-16 to 2025-04-16...
Empty DataFrame
Columns: [timestamp]
Index: []
Fetching readings for site 11697 and device 0x634e633131334e70 from 2025-04-16 to 2025-04-17...
                  timestamp  rssi  v_bandgap   aw0   aw1   aw2  ...  temp_f0  temp_f1  temp_f2  temp_f3  temp_f4  temp_f5
0 2025-04-16 23:15:00+00:00 -92.0       2.37   NaN   NaN   NaN  ...      NaN      NaN      NaN      NaN      NaN      NaN
1 2025-04-16 22:30:00+00:00 -92.0       2.38  0.53  1.06  1.16  ...    52.88    52.16    51.08    49.64    48.92     48.2
2 2025-04-16 22:00:00+00:00 -89.0       2.38  0.53  1.06  1.16  ...    52.88    52.16    50.72    49.64    48.92     48.2
3 2025-04-16 21:30:00+00:00 -93.0       2.37  0.53  1.06  1.16  ...    52.52    52.16    50.72    49.64    48.92     48.2
4 2025-04-16 21:00:00+00:00 -93.0       2.37  0.53  1.06  1.16  ...    52.52    52.16    50.72    49.64    48.92     48.2

[5 rows x 22 columns]
Retrieved 64 rows total.
                  timestamp  rssi  v_bandgap   aw0   aw1   aw2  ...  temp_f0  temp_f1  temp_f2  temp_f3  temp_f4  temp_f5
0 2025-04-16 00:15:00+00:00 -91.0       2.36   NaN   NaN   NaN  ...      NaN      NaN      NaN      NaN      NaN      NaN
1 2025-04-16 00:30:00+00:00   NaN        NaN  0.51  1.04  1.15  ...    52.16     51.8    50.72    49.28    48.92     48.2
2 2025-04-16 00:45:00+00:00 -92.0       2.36   NaN   NaN   NaN  ...      NaN      NaN      NaN      NaN      NaN      NaN
3 2025-04-16 01:45:00+00:00   NaN        NaN  0.52  1.04  1.15  ...    52.52     51.8    50.72    49.28    48.92     48.2
4 2025-04-16 02:00:00+00:00 -92.0       2.34   NaN   NaN   NaN  ...      NaN      NaN      NaN      NaN      NaN      NaN

[5 rows x 22 columns]
```