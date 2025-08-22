import requests
from django.shortcuts import render
from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth
from django.conf import settings


def get_geocode(address_data):
    address = ' '.join(filter(None, [
        address_data.get('COUNTRY'),
        address_data.get('PROVINCE'),
        address_data.get('REGION'),
        address_data.get('CITY'),
        address_data.get('ADDRESS_1')
    ]))

    if not address:
        return None

    api_key = settings.YANDEX_MAPS_API_KEY

    try:
        response = requests.get(f'https://geocode-maps.yandex.ru/v1/?apikey={api_key}&geocode={address}&format=json')
        response.raise_for_status()
        data = response.json()

        position = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
        return [float(coord) for coord in position.split(' ')[::-1]]
    except Exception:
        return None


@main_auth(on_cookies=True)
def map(request):
    bx24 = request.bitrix_user_token
    points = []
    points_with_coords = []

    try:
        companies = bx24.call_list_method('crm.company.list', {'select': ['ID', 'TITLE']})
        companies_dict = {company['ID']: company for company in companies}


        addresses = bx24.call_list_method('crm.address.list', {
            'filter': {'ENTITY_TYPE_ID': 4}
        })

        for address in addresses:
            company_id = address['ENTITY_ID']
            if company_id in companies_dict:
                company_data = companies_dict[company_id]

                geocode = get_geocode(address)

                address_parts = [
                    address.get('COUNTRY'),
                    address.get('PROVINCE'),
                    address.get('REGION'),
                    address.get('CITY'),
                    address.get('ADDRESS_1')
                ]
                address_str = ', '.join(filter(None, address_parts))


                point = {
                    'id': company_id,
                    'title': company_data.get('TITLE', 'No Name'),
                    'address': address_str,
                    'has_address': bool(address_str),
                    'geocode': {'latitude': geocode[0], 'longitude': geocode[1]} if geocode else None
                }

                points.append(point)
                if geocode:
                    points_with_coords.append(point)

    except Exception as e:
        return render(request, 'map.html', {
            'error': str(e),
            'points': [],
            'points_with_coords': [],
            'points_without_coords': 0,
            'yandex_api_key': settings.YANDEX_MAPS_API_KEY
        })

    points_without_coords = len(points) - len(points_with_coords)

    return render(request, 'map.html', {
        'points': points,
        'points_with_coords': points_with_coords,
        'points_without_coords': points_without_coords,
        'yandex_api_key': settings.YANDEX_MAPS_API_KEY
    })