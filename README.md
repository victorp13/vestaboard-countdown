# Vestaboard Countdown
 
 ⚠ **Important**: To run this, you need a config file. See the bottom of this README for more information. 

## The Goal
My goal was to create a countdown on our new Vestaboard. I wanted to be able to set the date and time of the event and have the countdown display the days until the event. I also wanted to find a way for my family members to easily modify the list of events and their dates without my direct involvement.

<div align="center">
<img src="img/featured_vestaboard.jpg">
</div>

## The Solution
Vestaboard has a local API that allows you to update the contents of the board. I created a cron job that runs once a day and loads the content of a Google Sheet. The Google Sheet contains the list of events and their dates. The cron job then updates the Vestaboard with the countdown in number of days until each event.

So step-by-step:
- Google sheet with list of events and their dates
- Python script that reads the Google sheet and calls the local API
- Cron job that runs the Python script once a day

<div align="center">
<img src="img/vestaboard-architecture.png">
</div>

### Vestaboard API
First things first: Vestaboard also has a cloud-based API, but I like to use local APIs as much as possible. This removes reliance on Vestaboard's servers and allows me to update the board even if their services are down. The API is very simple and allows you to read and write the contents of the board. The API is documented here: https://docs.vestaboard.com/local.

To make use of the Local API, you have to request an API token using [this form](https://www.vestaboard.com/local-api). You will then have to wait for an approval email from Vestaboard with the local API token in it, in plain text. I find this manual process a bit silly: The cloud-based API credentials *can* be created in the developer portal but the local API requires a manual request. Perhaps this manual process is temporary: I hope Vestaboard will add the ability to create and maintain local API credentials in the developer portal. 

⚠ **Warning:** Remember to keep your local API token secret. Consider deleting the e-mail containing it.

### Google Sheet
To allow my family members to update the list of events, I created a Google Sheet that they have access to. The sheet contains the list of events and their dates, a flag to switch on and off the display of these events, and a message to display with a flag as well.

<div align="center">
<img src="img/vestaboard-sheet.png">
</div>

Sheets can be published to the web and can be accessed using a public URL. To do this, go to the `File` menu, then `Share` and `Publish to web`. Then on the dialog that opens just click "Publish" as the default settings are fine. A URL will be generated that you can use to access the sheet.

<div align="center">
<img src="img/vestaboard-publish-to-web.png">
</div>

After publishing the sheet, you can revising the same dialog and select `Comma-separated values (.csv)` as the format. This will generate a URL that you can use to access the sheet in CSV format. This is the URL that I use in my Python script.


<div align="center">
<img src="img/vestaboard-publish-dialog.png">
</div>

### Python script
I am using Python to create the cron job. It calls the published Google Sheet and reads its contents. Then I iterate over the lines and form a list of events (and an optional message). The total number of lines that can be displayed is six, so I append empty lines if needed. 

The Vestaboard local API expects not simply ASCII lines but instead only accepts a string like this with [specific character codes](https://docs.vestaboard.com/characters):
```
[[4, 1, 25, 19, 0, 20, 9, 12, 12, 50, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
[0, 0, 6, 1, 25, 0, 32, 0, 0, 0, 0, 0, 0, 29, 34, 0, 0, 0, 0, 0, 0, 0], 
[0, 0, 12, 21, 3, 1, 19, 0, 27, 30, 0, 0, 27, 27, 27, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 4, 9, 19, 14, 5, 25, 0, 0, 0, 0, 27, 35, 32, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 12, 15, 22, 5, 0, 9, 19, 0, 20, 8, 5, 0, 13, 5, 19, 19, 1, 7, 5, 0, 0]]
```

To build up these lines I make use of the Python library [Vestaboard](https://github.com/ShaneSutro/Vestaboard) and specifically its `convertLine` method. This method takes a string and converts it to the correct character codes. I then use the `urllib.request` [library](https://docs.python.org/3/library/urllib.request.html#module-urllib.request) to call the Vestaboard local API and update the board. I would have used the Vestaboard library, but it does not support the local API (yet).

### Cron Job
Finally, I created a CRON job that runs the Python script once a day. I am using crontab on my local Intel NUC.

I also created a Flask app that allows me to run the script on-demand. This allows me to update the board without waiting for the cron job to run.

### Config file
You will need to add a config.py file with the following contents:

```
googlesheets_url='https://docs.google.com/spreadsheets/<really_long_string>/pub?output=csv'
vestaboard_ip='<local_ip_of_vestaboard>'
vestaboard_key='<local_api_key>'
```
Mind that you pick the CSV format of the Google Sheet. 