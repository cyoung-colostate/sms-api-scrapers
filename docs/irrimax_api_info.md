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