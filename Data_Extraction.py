import pandas as pd
import os
import sys
import json

f = open('./Data/335982.json', 'r', encoding='utf-8')
data = json.load(f)
info = data['innings']
print(info)
match_date = info['dates'][0]
print(match_date)
data.get('meta',{})
print(data['meta'])

