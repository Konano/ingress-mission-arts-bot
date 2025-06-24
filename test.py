import requests

HEADERS = {
    "accept": "application/json",
    "accept-language": "en",
    "origin": "https://bannergress.com",
    "priority": "u=1, i",
    "referer": "https://bannergress.com/",
    "sec-ch-ua": '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
}
# resp = requests.get('https://api.bannergress.com/places', params={
#     "used": "true",
#     "collapsePlaces": "true",
#     "query": "Hangzhou",
#     "limit": 9,
#     "offset": 0
# }, headers=HEADERS)

resp = requests.get('https://api.bannergress.com/bnrs', params={
    "orderBy": "created",
    "orderDirection": "DESC",
    "online": "true",
    "placeId": "macao-8e3a",
    "limit": 30,
    "offset": 0
}, headers=HEADERS)

print(len(resp.json()))
