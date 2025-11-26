# Energy Tariff for Home Assistant

**Energy Tariff** is a custom Home Assistant integration designed to provide accurate, real-time energy pricing for your Energy Dashboard.

While built with **DTE Energy's Time-of-Day (3 p.m. - 7 p.m.)** plan in mind, it is fully configurable to support various Time-of-Use (TOU) or Fixed Rate plans from other utility providers.

## Features

* **Time-of-Use (TOU) Support**: Define peak and off-peak hours to match your utility's schedule.

* **Seasonal Rates**: Automatically switches between Summer and Winter rates based on your configuration.

* **Holiday & Weekend Logic**: Built-in support (using the `holidays` library) to automatically apply off-peak rates on weekends and major US holidays.

* **Fixed Rate Mode**: Simple configuration for flat-rate energy plans.

* **Energy Dashboard Ready**: Creates a sensor entity compatible with the "Use an entity with current price" option in Home Assistant's Energy Dashboard.

## Installation

### Option 1: HACS (Recommended)

1. Open HACS in Home Assistant.

2. Go to "Integrations" > Top right menu > "Custom repositories".

3. Add `https://github.com/mxbleau/ha-energy-tariff` with the category **Integration**.

4. Click **Download** on the "Energy Tariff" card.

5. Restart Home Assistant.

### Option 2: Manual Installation

1. Download the latest release.

2. Extract the zip file and copy the `custom_components/energy_tariff` folder into your Home Assistant's `config/custom_components/` directory.

3. Restart Home Assistant.

## Configuration

1. Navigate to **Settings** > **Devices & Services**.

2. Click **+ Add Integration**.

3. Search for **Energy Tariff**.

4. Follow the configuration wizard:

   * **Strategy**: Choose between "Fixed Rate" or "Time of Use".

   * **Time of Use Settings**:

     * Define your Peak Start and End times (e.g., 15:00 to 19:00).

     * Select your Summer months.

     * Enter your specific rates for Summer Peak, Summer Off-Peak, Winter Peak, and Winter Off-Peak.

     * Enable/Disable weekend and holiday off-peak overrides.

### Setting up the Energy Dashboard

Once the integration is added:

1. Go to **Settings** > **Dashboards** > **Energy**.

2. Find your **Grid Consumption** source and click the pencil icon to edit.

3. Under **Grid consumption price**, select **Use an entity with current price**.

4. Select the sensor created by this integration (e.g., `sensor.my_energy_rate`).

5. Click **Save**.

## Example: DTE Energy Time-of-Day (3 p.m. - 7 p.m.)

To match the DTE Time-of-Day plan:

* **Peak Start**: `15:00`

* **Peak End**: `19:00`

* **Summer Months**: June, July, August, September

* **Weekends Off-Peak**: Checked

* **Holidays Off-Peak**: Checked

*Note: Rates should be entered as dollars per kWh (e.g., 0.2339).*

## Credits

This project uses the [python-holidays](https://github.com/dr-prodigy/python-holidays) library to accurately determine holiday schedules.

[releases]: https://github.com/mxbleau/ha-energy-tariff/releases