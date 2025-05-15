# AquaSpy AgSpy API Overview

## General Info

The AgSpy API is a simple data API that returns information on moisture and other conditions for agricultural sites (fields) with AgSpy probes. Requests are made via web service, and the response is a JSON object.

The primary unit of management is the **Site**, which corresponds to a plot of land where AgSpy probes are installed. Sites are identified by a unique 4-byte integer value (`SiteID`). This is the only required parameter to retrieve data. The data is not considered sensitive and is retrieved per site, not en masse.

---

## API Endpoints

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


