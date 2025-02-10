# Usko Market Watcher

This Python script uses Selenium to monitor item listings on the Usko Pazar website and notify you via Slack when items are sold.  It also provides a simple Tkinter GUI for displaying watched and sold items.

## Features

* Monitors user listings on Usko Pazar.
* Sends Slack notifications for sold items.
* Displays watched and sold items in a GUI.
* Supports both "sell" and "buy" modes.

## Requirements

* Python 3
* Selenium
* Slack SDK
* Tkinter (usually included with Python)
* Chrome browser and ChromeDriver (matching your Chrome version)

## Installation

1.  Clone the repository:

    ```bash
    git clone https://github.com/ikaganacar1/UskoPazar-WebScrapper.git
    ```

2.  Install the required Python packages:

    ```bash
    pip install selenium slack_sdk
    ```

3.  Download Slack to your mobile phone and get a api key.

## Configuration

1.  Put the essensial data to `config.json` file in the same directory as the script with the following structure:

    ```json
    {
      "config": {
        "slack_api_key": "YOUR_SLACK_API_TOKEN",
        "slack_channel_name": "YOUR_SLACK_CHANNEL_NAME",
        "slack_bot_name": "YOUR_SLACK_BOT_NAME",
        "update_frequency": 90  // Update frequency in seconds
      }
    }
    ```




## Notes

*   The script uses headless Chrome for monitoring.
*   Make sure the username you enter is correct.
*   The update frequency is in seconds. Adjust it as needed.
*   The script assumes the structure of the Usko Pazar website remains consistent.  Changes to the website may require updates to the script.

## Contributing

Contributions are welcome!  Please open an issue or submit a pull request.
