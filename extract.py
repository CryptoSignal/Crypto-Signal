import requests
from bs4 import BeautifulSoup
import csv
import re

#1. url
#2. a -> tag name
#3. attribute -> regex
url = "http://coinmarketcap.com/exchanges/huobi/"
r = requests.get(url)
data = r.text

soup = BeautifulSoup(data, "html.parser")
get_details = soup.find_all("a", href=re.compile('.*hbg.*exchange.*'))

for val in get_details:
    get_val = val.get_text()
    print(get_val)
