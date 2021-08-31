# -*- coding: utf-8 -*-
import requests
import json
import sys

board_ids = ['JnMfjPf3', 'kl7Pt8pO', 'mpWUf7bp', 'jZMqDNSW', 'VUrZyteN', 'dm8cnGe3', 'GjHIqyQ6', 'nSs3zGWl', '5OafbR0r', 'u3ier36D', 'pEQvKZco', 'lRueC3wU', 'QTsj5KDY', 'xb4FpWY4', 'bJChKs5l', 'TPLdAZUE', 'FLR0nklL', '8Is4Sm1b', 'HHrm8hTv', 'HcV3UEuk',
             'DiFTAjRW', '7rirkDr7', 'WttJfiIy', 'sNZNYg9B', 'hGONfOvF', 'HvBEx94q', 'FXq2KA9o', 'agsntZtr', 'uuKpSADp', '5v20VZ4H', 'IDnyb8dK', 'hjHNbzF3', 'Eudc2Ry2', 'l8QhwO9W', 'Zncjl3AK', 'otlHltDr', 'E2Tya7EY', '3oJHR7tQ', 'Q7EzO09T', 'ENWFGCh2', ]

ret = []

for idx, board_id in enumerate(board_ids):
    url = f'https://api.trello.com/1/boards/{board_id}/cards?filter=open&attachments=cover'
    ret.append(requests.get(url).json()[10:])
    print(f'Done {idx+1}/{len(board_ids)}: {url}')

try:
    filename = sys.argv[1]
except:
    filename = '../data/trello.json'

with open(filename, 'wb') as f:
    f.write(json.dumps(ret, ensure_ascii=False, sort_keys=True).encode('utf8'))
