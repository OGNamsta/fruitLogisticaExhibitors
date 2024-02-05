import asyncio
import httpx
from time import perf_counter
import xml.etree.ElementTree as ET


async def log_request(request):
    print(f"Request: {request.url!r} {request.method!r}")


async def log_response(response):
    print(f"Response: {response.url!r} {response.status_code!r}")


async def get_exhibitors():
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
    params = {
        'topic': '2022_FRUIT',
        'os': 'web',
        'appUrl': 'https://www.fruitlogistica.com/en/trade-visitors/exhibitor-search/#/',
        'lang': 'en',
        'apiVersion': '39',
        'timezoneOffset': '-240',
        'userLang': 'en-US',
        'filterlist': 'entity_orga,entityexcl_evtd',
        'startresultrow': '0',
        'numresultrows': '25',
        'order': 'lexic',
    }

    async with httpx.AsyncClient(event_hooks={'request': [log_request], 'response': [log_response]}, headers=headers, params=params) as client:
        response = await client.post(url)
        data = response.text
        # print(data)
        # exhibitors = data['result']['exhibitors']
        return data


async def main():
    start_time = perf_counter()
    end_time = perf_counter()
    exhibitors = await get_exhibitors()
    root = ET.fromstring(exhibitors)

    for organization in root.findall('.//organization'):
        name = organization.attrib.get('name')
        country_code = organization.attrib.get('countryCode')
        country = organization.attrib.get('country')
        city = organization.attrib.get('city')
        postcode = organization.attrib.get('postCode')
        email = organization.attrib.get('email')
        stand_name = organization.find('.//stand').attrib.get('standName')

        # Extract contacts
        contacts = organization.find('.//contacts')
        contact_persons = []
        for contact in contacts.findall('.//contactPerson'):
            contact_person = {
                'firstName': contact.attrib.get('firstName'),
                'lastName': contact.attrib.get('lastName'),
                'position': contact.attrib.get('position')
            }
            contact_persons.append(contact_person)

        # Print or process the extracted data
        print(f"Name: {name}")
        print(f"Country Code: {country_code}")
        print(f"Country: {country}")
        print(f"City: {city}")
        print(f"Postcode: {postcode}")
        print(f"Email: {email}")
        print(f"Stand Name: {stand_name}")
        print("Contacts:")
        for contact_person in contact_persons:
            print(f" - {contact_person['firstName']} {contact_person['lastName']}, {contact_person['position']}")

    # print("Exhibitors:", exhibitors)
    print(f"Time taken: {end_time - start_time:.2f} seconds")



if __name__ == '__main__':
    asyncio.run(main())
