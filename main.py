import asyncio
import httpx
from time import perf_counter
import xml.etree.ElementTree as ET
import openpyxl
import os


async def log_request(request):
    print(f"Request: {request.url!r} {request.method!r}")


async def log_response(response):
    print(f"Response: {response.url!r} {response.status_code!r}")


# Function to cache the XML data to a file
def cache_xml(data):
    with open('exhibitors.xml', 'w') as f:
        f.write(data)


# Function to save exhibitor data to an Excel sheet
def save_to_excel(exhibitors):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Name", "Country Code", "Country", "City", "Postcode", "Email", "Stand Name", "Contacts", "Teaser", "Product Names"])
    for exhibitor in exhibitors:
        contacts = ", ".join([f"{contact['firstName']} {contact['lastName']} - {contact['position']}" for contact in exhibitor['contacts']])
        ws.append([
                exhibitor['name'],
                exhibitor['countryCode'],
                exhibitor['country'],
                exhibitor['city'],
                exhibitor['postcode'],
                exhibitor['email'],
                exhibitor['standName'],
                contacts,
                exhibitor['teaser'] if 'teaser' in exhibitor else 'N/A',
                ", ".join(exhibitor['product_names'] if 'product_names' in exhibitor else 'N/A')
            ])
    wb.save("exhibitors3.xlsx")


async def get_exhibitors(start_result_row):
    url = 'https://live.messebackend.aws.corussoft.de/webservice/search'
    headers = {
        'authority': 'live.messebackend.aws.corussoft.de',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9,en-GB;q=0.8,de;q=0.7,es;q=0.6',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'dnt': '1',
        'origin': 'https://www.fruitlogistica.com',
        'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    }
    params = {'topic': '2022_FRUIT', 'os': 'web',
              'appUrl': 'https://www.fruitlogistica.com/en/trade-visitors/exhibitor-search/#/', 'lang': 'en',
              'apiVersion': '39', 'timezoneOffset': '-240', 'userLang': 'en-US',
              'filterlist': 'entity_orga,entityexcl_evtd', 'startresultrow': str(start_result_row),
              'numresultrows': '25', 'order': 'lexic'}

    async with httpx.AsyncClient(event_hooks={'request': [log_request], 'response': [log_response]}, headers=headers, params=params) as client:
        response = await client.post(url)
        xml_data = response.text
        return xml_data


async def main():
    start_time = perf_counter()
    end_time = None

    exhibitors = []
    start_result_row = 0
    total_exhibitors = 0

    if os.path.exists('exhibitors.xml'):
        print("Using cached data...")
        with open('exhibitors.xml', 'r') as f:
            xml_data = f.read()
            print("Cached data loaded")
    else:
        print("Fetching live data...")
        xml_data = await get_exhibitors(start_result_row)
        print("Caching live data...")
        cache_xml(xml_data)


    root = ET.fromstring(xml_data)
    total_exhibitors = int(root.find('.//entities').attrib.get('count'))

    while start_result_row < total_exhibitors:
        xml_data = await get_exhibitors(start_result_row)
        root = ET.fromstring(xml_data)


        for organization in root.findall('.//organization'):
            exhibitor = {
                'name': organization.attrib.get('name') if 'name' in organization.attrib else 'N/A',
                'countryCode': organization.attrib.get('countryCode') if 'countryCode' in organization.attrib else 'N/A',
                'country': organization.attrib.get('country') if 'country' in organization.attrib else 'N/A',
                'city': organization.attrib.get('city') if 'city' in organization.attrib else 'N/A',
                'postcode': organization.attrib.get('postCode') if 'postCode' in organization.attrib else 'N/A',
                'email': organization.attrib.get('email') if 'email' in organization.attrib else 'N/A',
                'standName': None,  # Initialize standName to None by default
                # Extract contacts
                'contacts': [{
                    'firstName': contact.attrib.get('firstName') if 'firstName' in contact.attrib else 'N/A',
                    'lastName': contact.attrib.get('lastName') if 'lastName' in contact.attrib else 'N/A',
                    'position': contact.attrib.get('position') if 'position' in contact.attrib else 'N/A'
                } for contact in organization.findall('.//contacts/contactPerson')],
                'teaser': organization.find('.//description/teaser').text.strip() if organization.find('.//description/teaser') is not None else 'N/A',
                'product_names': [product.attrib.get('name') for product in organization.findall('.//products/product')]
            }
            # Check if <stand> element exists
            stand_element = organization.find('.//stand')
            if stand_element is not None:
                exhibitor['standName'] = stand_element.attrib.get('standName')


            exhibitors.append(exhibitor)

        start_result_row += 25

    print("Saving to Excel...")
    save_to_excel(exhibitors)

    # Now update the end time
    end_time = perf_counter()

    # print("Exhibitors:", exhibitors)
    print(f"Time taken: {end_time - start_time:.2f} seconds")
    print(f"Total exhibitors: {total_exhibitors}")

if __name__ == '__main__':
    asyncio.run(main())
    print("Done")
