import requests
from geopy.distance import geodesic

def get_nearest_gas_stations_yandex(api_key, latitude, longitude, type_azs):
    base_url = "https://search-maps.yandex.ru/v1/"
    
    params = {
        "apikey": api_key,
        "text": type_azs,
        "lang": "ru_RU",
        "ll": f"{longitude},{latitude}",
        "type": "biz",
        "results": 50 
    }
    
    response = requests.get(base_url, params=params)
    data = response.json()

    gas_stations = []
    for feature in data.get("features", []):
        properties = feature.get("properties", {})
        address = properties.get("CompanyMetaData", {}).get("address", "")
        name = properties.get('name', '')
        coordinates = feature.get("geometry", {}).get("coordinates", [])
        phone = properties.get("CompanyMetaData", {}).get("Phones", [{}])[0].get("formatted", "К сожалению нету номера")
        hours = properties.get("CompanyMetaData", {}).get('Hours', {}).get('text', '')

        dist = geodesic((latitude, longitude), (coordinates[1], coordinates[0])).kilometers

        gas_station_info = {
            "name": name,
            "address": address,
            "coordinates": coordinates,
            "hours": hours,
            "phone": phone,
            "distance": round(dist, 2)
        }
        gas_stations.append(gas_station_info)

    # Сортируем список заправочных станций по расстоянию от ближайшей к дальнейшей
    gas_stations.sort(key=lambda x: x["distance"])

    return gas_stations
