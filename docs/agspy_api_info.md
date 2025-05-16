# AquaSpy AgSpy API Overview
> [!NOTE]
> 🛑 **TL;DR**: Integration is paused due to lack of in-season probes. Site IDs must be hardcoded, and no sensor data can be retrieved until AquaSpy hardware is deployed and activated in-season.


### AquaSpy Integration Note

While AquaSpy exposes structured data over a web service, it does **not provide a conventional REST API**. The platform relies on fixed URLs with known site IDs, returns JSON embedded inside XML, and does not support authenticated user-based access or site discovery. We treat this as a static data feed rather than a dynamic, queryable API (e.g., no resource discovery, no user-level auth, no POST methods).


---

## ⚠️ AquaSpy API Integration Status

The AquaSpy API integration is currently **on hold** due to deployment and platform constraints. Below is a summary of the current issues preventing full functionality:

---

### ❌ Current Limitations

1. **No Sensors Currently Deployed**
   - None of the monitored sites have AquaSpy sensors actively installed.
   - As a result, `InSeason = False` and `CurrentFieldSeasonID = null` for all known `siteID`s.
   - This prevents any historical or real-time sensor data from being accessed via the API.

2. **Season Dependency for Data Access**
   - The AquaSpy API requires that a site be marked as `InSeason = True` and have a valid `CurrentFieldSeasonID` to access:
     - `GetSeasonApiData` – full seasonal time series
     - `GetSeasonDifferentialApiData` – incremental updates
   - `GetSeasonApiData` returns `null` if no `CurrentFieldSeasonID` exists.
   - `GetSeasonDifferentialApiData` cannot run without a valid timestamp from an in-season probe.

3. **Site ID Discovery is Manual**
   - The API provides **no method to list all `siteID`s** accessible by a user.
   - Site IDs must be known in advance and manually entered in the script.
   - This is unlike other platforms (e.g., IrriMAX or GroGuru) that support logger/site discovery via authenticated API calls.

---

### ✅ Resolution Path (When Sensors Are Active)

When AquaSpy sensors are deployed and a season is defined via the AquaSpy dealer portal:

- `get_site_metadata(site_id)` will return a valid `CurrentFieldSeasonID`.
- `get_season_data(season_id)` and `get_differential_data(season_id, timestamp)` will return valid time-series data.

Until that point, the AquaSpy script will remain functional for metadata retrieval only, with data methods inactive.

---

### TODO

- Revisit AquaSpy integration after sensor deployment and in-season activation.
- Explore automation options for `siteID` discovery through internal records or support contact.

## Example of Problem
```python
In [8]: # all sesnor IDs
   ...: site_ids = [33853, 33856, 30759, 33857, 33858, 33859, 30756, 33860,
   ...:             33861, 33862, 34533, 33863, 30757, 33854, 33855, 30758]
   ...:
   ...: for sid in site_ids:
   ...:     try:
   ...:         m = get_site_metadata(sid)
   ...:         if m["CurrentFieldSeasonID"]:
   ...:             print(f"✅ Site {sid} ({m['SiteDesc']}): SeasonID = {m['CurrentFieldSeasonID']}")
   ...:         else:
   ...:             print(f"⛔ Site {sid} ({m['SiteDesc']}): No Season ID")
   ...:     except Exception as e:
   ...:         print(f"⚠️ Site {sid} failed: {e}")
   ...:
⛔ Site 33853 (Farm 1 - 4D - Block II): No Season ID
⛔ Site 33856 (Farm 12 - 1D - Block II): No Season ID
⛔ Site 30759 (Farm 14 - TAPS 2023): No Season ID
⛔ Site 33857 (Farm 16 - 10E - Block II): No Season ID
⛔ Site 33858 (Farm 17 - 8E - Block II): No Season ID
⛔ Site 33859 (Farm 19 - 4E - Block II): No Season ID
⛔ Site 30756 (Farm 2 - TAPS 2023): No Season ID
⛔ Site 33860 (Farm 21 - 1C - Block II): No Season ID
⛔ Site 33861 (Farm 25 - 1E - Block II): No Season ID
⛔ Site 33862 (Farm 26 - 7D - Block II): No Season ID
⛔ Site 34533 (Farm 28 - 7H - Block R): No Season ID
⛔ Site 33863 (Farm 29 - 8H - Block R): No Season ID
⛔ Site 30757 (Farm 3 - TAPS 2023): No Season ID
⛔ Site 33854 (Farm 6 - 10D - Block II): No Season ID
⛔ Site 33855 (Farm 7 - 3E - Block II): No Season ID
⛔ Site 30758 (Farm 8 - TAPS 2023): No Season ID
```

## API Documentation
[https://agspy.aquaspy.com/apioverview](https://agspy.aquaspy.com/apioverview)

**Web Service URL:**  
`https://agspy.aquaspy.com/Proxies/SiteService.asmx`

### Web Methods:
- `GetSiteApiData?siteID={siteID}`
- `GetSeasonApiData?fieldSeasonID={currentFieldSeasonID}`
- `GetSeasonDifferentialApiData?fieldSeasonID={currentFieldSeasonID}&referenceTimestamp={referenceTimestamp}`

---

## `GetSiteApiData` Method

Returns the current status and conditions for a specific `siteID`.

- Response: a JSON object with both site-level and season-level information.
- The JSON object is structured as follows (the underlying .NET C# data type of the value stands in for the actual value below, encased in brackets):
  
```json
 
{

    // Site-level information

    "SiteID": [int],                                // The unique identifier for the Site
    "SiteDesc": "[string]",                         // Site name/description
    "Latitude": [double],
    "Longitude": [double],
    "LocaleCode": "[string]",                       // The state (or similar foreign political territory) code for the Site
    "SubLocaleName": "[string]",                    // The county (or similar foreign political territory) name
    "SurveyInfo": "[string]",                       // Land parcel identifier
    "SoilType": "[string]",     
    "InSeason": [boolean],                          // Indicates if a crop is currently planted
    "HasEquipment": [boolean],                      // Indicates if an AgSpy probe is currently installed at/registered to the Site
    "IsSuspended": [boolean],                       // Indicates if a paid subscription is not associated with the Site
    "RegionName": "[string]",                       // The name of the Dealer managing the Site's "subscriber" (customer)
    "CustomerName": "[string]",                     // The name of the Customer who owns the Site
    "CurrentFieldSeasonID": [int?],                 // Unique identifier for the Site's current growing season (if any)
    "TimeZoneInfoID": "[string]",                   // The time zone the Site is located within
    "SensorInterval": [int],                        // The distance between probe sensors; in cm or inches
    "DepthUnit": "[string]".                        // Linear measurement unit; cm or " (inches)
 
    /****** BEGIN Season-level information; only provided if InSeason == true ******/

    "PlantDate": "[datetime]",
    "Duration": [int],                              // The duration of the season, in days
    "ProjectedHarvestDate": "[datetime]",           // PlantDate + Duration
    "CropType": "[string]",
    "UseAutomation": [boolean],                     // Indicates that automated refill estimation is in use
    "RootDepthSensorIndex": [int?],                 // The lowest sensor (if any) on which roots have been detected
    "MoistureLevel": "[string]",                    // Description of current soil moisture
    "MoisturePercentage": [int?],                   // % of total possible moisture available for root consumption
    "DaysToEmpty": [int?],                          // Days until MoisturePercentage = 0
    "LastIrrigationDate": "[datetime?]",
    "LastIrrigationDepthSensorIndex": [int?],       // The lowest sensor on which irrigation was last detected
    "InstallDepth": [int],                          // Depth of top active sensor (in cm or inches)
    "LastReportedTimestamp": "[datetime?]",         // Last receipt of data transmitted by the comm tower
    "CurrentSeasonDay": [int],                      // Number of days since plant date
    "SummaryFullPoint": [double?],                  // Current aggregate full point
    "UseManualFullPoint": [boolean],                // Indicates that the manual FP supplants the summary FP
    "ManualFullPoint": [double],                    // Manually assigned full point
    "UpperActiveSensorIndex": [int],                // Index of top sensor actively included in monitoring
    "LowerActiveSensorIndex": [int],                // Index of bottom sensor actively included in monitoring
    "ActiveRootZoneSensorIndex": [int],             // Sensor index of lowest sensor included in the Active Root Zone
    "MoisturePercentage": [double?],                // % of total moisture available in the Active Root Zone*
    "MoisturePercentageAllSensors": [double?],      // % of total possible moisture available across all active sensors
    "MoisturePercentagePrior": [double?],           // % of total possible moisture available 24 hours prior to last data
    "OptimumUpper": [double],                       // % specifying upper limit of optimum band
    "OptimumLower": [double],                       // % specifying lower limit of optimum band

    "MoistureValues": [double[]],                   // Array of the most recent individual sensor moisture values
    "EcValues": [double[]],                         // Array of the most recent individual sensor Ec values
    "TemperatureValues": [double[]],                // Array of the most recent individual sensor temperature values

    "LastWeatherInformationTimestamp": "[datetime?]",   // The timestamp of the most recently reported CT weather sensor data (if available)
    "LastAirTemperature": [double?],                    // The most recent air temperature reading
    "AirTemperature24HourMinimum": [double?],           // The low air temp. in the last 24 hours
    "AirTemperature24HourMaximum": [double?],           // The high air temp in the last 24 hours
    "LastHumidity": [double?],                          // The most recent relative humidity reading (%)
    "Humidity24HourMinimum": [double?],                 // The low relative humidity reading (%) in the last 24 hours
    "Humidity24HourMaximum": [double?],                 // The high relative humidity reading (%) in the last 24 hours
    "Precipitation24HourTotal": [double?],              // Total precipitation in the last 24 hours (CT rain gauge)
    "CumulativePrecipitation": [double?],               // Season-to-date cumulative precipitation (CT rain gauge)
    "GrowingDegreeDays24HourTotal": [double?],          // Growing degree days accumulated in the last 24 hours
    "GrowingDegreeDaysSeasonTotal": [double?],          // Growing degree days accumulated in the season-to-date

    "SeasonEvents": [                               // Array of events which have occurred during the season
        {
            "EventType": "[string]",                // Text description of the type of event
            "AutomationEventType": "[string]",      // If EventType == "Automation", the event sub-type (IrrigationDetection, etc.)
            "EventDate": "[datetime]",              // Date of the event
            "EventTime": "[TimeSpan]",              // Time of day of the event (adjusted to site's timezone)
            "EventData": "[string]",                // Text description of event details
            "Comment": "[string]"                   // Supplemental information provided manually by users
        },
        …
    ],

    "ProbeProductCode": "[string]",                 // Probe model number
    "ProbeDSN": "[string]",                         // Probe serial number
    "GatewayProductCode": "[string]",               // Comm tower model number
    "GatewayDSN": "[string]",                       // Comm tower serial number
    "FirmwareVersion": [int?],                      // Comm tower firmware version #

    /****** END Season-level information ******/

    "ReplyTimestamp": "[datetime]"                  // UTC timestamp of this response

}
```

**Notes:**

- Indices are zero-based

- Sensor depths and moisture percentages are in customer’s preferred units (`DepthUnit`).

- % values are expressed as fractional values between 0.0 and 1.0.

- Root Depth and Last Irrigation Depth can be calculated as follows from `RootDepthSensorIndex` and `LastIrrigationDepthSensorIndex`, provided these are not null, as follows:

```bash
((RootDepthSensorIndex - UpperActiveSensorIndex) * SensorInterval) + InstallDepth
((LastIrrigationDepthSensorIndex - UpperActiveSensorIndex) * SensorInterval) + InstallDepth
```

## `GetSeasonApiData` and `GetSeasonDifferentialApiData` Methods

These methods retrieve **historical sensor data** for the current season of an AgSpy Site.

- Both require the `fieldSeasonID` parameter, which is obtained from the `CurrentFieldSeasonID` field in the `GetSiteApiData` response.
- **`GetSeasonApiData`** returns **all** sensor readings since the beginning of the season. Use it once to initialize your data store.
- **`GetSeasonDifferentialApiData`** returns **only new readings** after a given timestamp. Use it repeatedly for incremental updates.

### Response Structure (shared by both methods):

```json
{
    "Success": [boolean],                           // Indicates if the call was successful
    "HasPublicMessage": [boolean],                  
    "Messages": [string[]],                         // Provides info about exception, if encountered
    "Data": {
        "SiteID": [int],                            
        "FieldSeasonID": [int],
        "ReferenceTimestamp": "[datetime?]",
        "MaxReadTimestampUTC": "[datetime]",        // The timestamp of the most recent sensor readings
        "SeasonData": [                             // An array of sets of readings
            {
                "[datetime]": {                     // The timestamp of a set of readings
                    "M": [double[]],                // The moisture values of the reading, indexed from top to bottom sensor
                    "E": [double[]],                // The Ec values of the reading
                    "T": [double[]],                // The temperature values of the reading
                    "SM": [double],                 // The moisture summary value (%)
                    "SE": [double]                  // The Ec summary value
                }
            },
            ...
        ]
    }
}
```

### Notes:

- **Keys inside `SeasonData`** are timestamps (`datetime`) of the reading.

- Each reading block includes:
  - `"M"`: Moisture readings (top to bottom sensor)
  - `"E"`: Electrical conductivity (EC) values
  - `"T"`: Temperature values
  - `"SM"`: Moisture summary (%)
  - `"SE"`: EC summary value

- **Truncated arrays**: The arrays for `"M"`, `"E"`, and `"T"` will **only include active sensors**, meaning sensors above ground or otherwise excluded will not appear.

- **Incremental updating**:  
  Use the value from `MaxReadTimestampUTC` as your `referenceTimestamp` in subsequent calls to `GetSeasonDifferentialApiData`. This ensures only new data is pulled.

- **URL encoding required**:  
  `referenceTimestamp` must be URL-encoded when used in request parameters (e.g., convert `:` to `%3A`).

- **First call strategy**:  
  - Use `GetSeasonApiData` **once** to retrieve full season history.
  - Then switch to `GetSeasonDifferentialApiData` for all **future incremental pulls**.

---


