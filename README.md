# Exhibitor Data Fetcher
This Python script fetches exhibitor data from an API endpoint, caches the XML response, parses it, and saves the exhibitor details to an Excel file.

## Requirements
- Python 3.7 or higher
- Required Python libraries: asyncio, httpx, xml.etree.ElementTree, openpyxl

## Installation
### 1. Clone the repository:
`git clone https://github.com/OGNamsta/fruitLogisticaExhibitors.git`

### 2.Install the required dependencies:
`pip install asyncio httpx openpyxl`

## Usage
Run the script by executing the following command:
`python main.py`
The script will fetch exhibitor data from the specified API endpoint, process it, and save the details to an Excel file named exhibitors3.xlsx.

## Description
The `get_exhibitors(start_result_row)` function fetches exhibitor data from the API endpoint asynchronously. It accepts a parameter `start_result_row` to specify the starting index of exhibitors to retrieve.
The `main()`function orchestrates the entire process, including fetching data, parsing XML, processing exhibitor details, and saving them to an Excel file.
Exhibitor details include name, country code, country, city, postcode, email, stand name, contacts, teaser, and product names.
The script caches XML responses to minimize API requests for subsequent runs.
Event hooks are used to log HTTP requests and responses for debugging purposes.

## Licence
This project is licensed under the MIT License - see the [LICENCE](https://github.com/OGNamsta/fruitLogisticaExhibitors/blob/master/MIT_Licence.txt) file for details.
