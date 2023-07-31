import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import datetime

import re

startD = datetime.datetime.now()
todayD = str(datetime.date.today())
start = datetime.datetime.now().strftime("%Y-%m-%d")

allLinks = set()
productLinks = []


def findProducts(soup2):
    prod = soup2.find("div", {"id": "main-content"}).find_all("div", {"class": "ci"})
    for ps in prod:
        # print (ps
        if ps.find("a") is None:
            continue
        wholeLink = "https://www.lockslash.com.au" + ps.find("a")['href']
        if wholeLink not in productLinks:
            productLinks.append(wholeLink)


def writeFrame(frame):
    firstCol = ["id", "URL", "Name", "Options", "Price"]
    collist = list(frame.keys())
    for ct in firstCol:
        collist.remove(ct)
    collist.remove(todayD)
    # collist.remove("Unique")

    frame = frame[firstCol + collist + [todayD]]
    frame.to_excel("Lockslash.xlsx", index=False)


def parseData(jsn, url):
    print(jsn['product']["title"])
    results = []
    for ect in jsn['product']['variants']:
        description = ''

        if ect['option1'] != "Default Title":
            description = description + ect['option1']
        if ect['option2'] is not None:
            description = description + "/" + ect['option2']
        if ect['option3'] is not None:
            description = description + "/" + ect['option3']
        results.append(
            {
                "ID": ect['id'],
                "Product ID": ect['product_id'],
                "Name": jsn['product']["title"],
                "Page Link": "https://www.lockslash.com.au" + url,
                "Options": description,
                start + " Price": ect['price'],
                start + " qty": ect['inventory_quantity']
            }
        )
    return results


def process_links(links):
    pattern = r"https://www.lockslash.com.au(.*)"

    for st in links:
        link_ = st['href']

        if link_.startswith("https:"):
            match = re.match(pattern, link_)
            if match:
                result = match.group(1)
                allLinks.add(result)
        else:
            if link_ != "#":
                allLinks.add(link_)


response = requests.get("https://www.lockslash.com.au")
soup = BeautifulSoup(response.text, "html.parser")

menus1 = soup.find("div", {"class": "site-nav__dropdown megamenu text-left"}).find_all("a")
menus2 = soup.find_all("li", {"class": "site-nav__item site-nav__expanded-item site-nav--has-dropdown"})[0].find_all("a")

process_links(menus1)
process_links(menus2)

# print(allLinks, len(allLinks))

for prd in allLinks:
    if "collections" not in prd:
        continue
    page = 1
    while True:
        url_ = "https://www.lockslash.com.au" + prd + "?page=" + str(page)
        res = requests.get(url_)
        # print(f'URL >>> {url_}\nres >>> {res}')
        page = page + 1
        soup2 = BeautifulSoup(res.text, "html.parser")
        products = soup2.find_all("div", {"class": "grid-product__content"})
        if len(products) < 1:
            break
        for ec in products:
            productLinks.append(ec.find("a")['href'])

# print(productLinks, len(productLinks))

try:
    df = pd.read_csv("Lockslash.csv")
    df = df.fillna("")
except:
    df = pd.DataFrame()

headers = {
    'authority': 'www.lockslash.com.au',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,uk;q=0.6,vi;q=0.5,pt;q=0.4,ka;q=0.3',
    'cache-control': 'max-age=0',
    # 'cookie': 'secure_customer_sig=; _cmp_a=%7B%22purposes%22%3A%7B%22a%22%3Atrue%2C%22p%22%3Atrue%2C%22m%22%3Atrue%2C%22t%22%3Atrue%7D%2C%22display_banner%22%3Afalse%2C%22merchant_geo%22%3A%22AU%22%2C%22sale_of_data_region%22%3Afalse%7D; _y=611e84e7-b111-42f7-933e-f946b4ced787; _shopify_y=611e84e7-b111-42f7-933e-f946b4ced787; _orig_referrer=; _landing_page=%2F; xgen_user_id=1q9bfbt0pi8lkjhb8vz; cart=e0f3862be12473a1f3f3f884312abbda; _gid=GA1.3.504189798.1690361030; xgen_ab_info={"testing_group_name":"Inactive"}; _gcl_au=1.1.387859844.1690361031; _shg_user_id=d2196ea2-3304-4f89-9bc0-b530ca4c962a; messagemedia_shown=1; _s=5e402e31-f970-499e-88fb-84d538fa6c2a; _shopify_s=5e402e31-f970-499e-88fb-84d538fa6c2a; _shopify_sa_p=; yotpo_pixel=b2448b09-5ccc-4849-b3b6-b8eb76bc6ba4; _sp_ses.6392=*; shopify_pay_redirect=pending; xgen_session_id=d3aa2514-a153-4c15-bb6b-bc80c276817e; xgen_meta_data={"access_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjdXN0b21lcl9pZCI6IjVlYjNhNTE3YmI0MTcwMzcxNmFmY2FkMjFiNTIyN2E3IiwiZXhwIjoxNjkwNTY4MzQzLCJ1c2VyX2lkIjoiMXE5YmZidDBwaThsa2poYjh2eiJ9.3Yp4dGFPCfemMHcy-cWJfI3f4aIYDkuOwL_-NDNp58s","expiration_date":"2023-07-28T18:19:03","customer_id":"5eb3a517bb41703716afcad21b5227a7","user_type":"return_user","stale":false}; _shg_session_id=54f5deb0-3e10-4ac5-8e74-d6d80912405f; cart_currency=NZD; cart_sig=d05b70b6ecc9ca2937a001b970b5475a; localization=NZ; _shopify_sa_t=2023-07-28T06%3A23%3A32.358Z; _ga=GA1.1.2088805231.1690361030; _ga_Y1SQQJT64D=GS1.1.1690525145.4.1.1690525412.57.0.0; cart_ts=1690525407; cart_ver=gcp-us-east1%3A13; _ga_ZH6QRMX9WH=GS1.1.1690525147.4.1.1690525412.0.0.0; __kla_id=eyIkcmVmZXJyZXIiOnsidHMiOjE2OTAzNjEwMzAsInZhbHVlIjoiIiwiZmlyc3RfcGFnZSI6Imh0dHBzOi8vd3d3LmxvY2tzbGFzaC5jb20uYXUvIn0sIiRsYXN0X3JlZmVycmVyIjp7InRzIjoxNjkwNTI1NDEzLCJ2YWx1ZSI6IiIsImZpcnN0X3BhZ2UiOiJodHRwczovL3d3dy5sb2Nrc2xhc2guY29tLmF1LyJ9fQ==; keep_alive=5380b615-facc-4a11-9515-24c50030c9bd; dynamic_checkout_shown_on_cart=1; _sp_id.6392=b515ff09657f7adc.1690361029.3.1690525422.1690439684',
    'if-none-match': 'W/"cacheable:120e6038594aef82544f7e8091485610"',
    'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
}

cookies = {
    'cart_currency': 'NZD',
    'localization': 'NZ',
}

s = requests.Session()
s.headers.update(headers)
s.cookies.update(cookies)

newproduct = oldprd = foundPrd = 0
numofProds = len(productLinks)

for i, ec in enumerate(productLinks):

    rs = s.get("https://www.lockslash.com.au" + ec + ".json")
    data = parseData(json.loads(rs.text), ec)
    foundPrd = foundPrd + 1

    for h in data:

        try:
            trt = df.loc[
                (df['ID'] == h['id']) &
                (df['Product ID'] == h['product_id']) &
                (df['Name'] == h['Name']) &
                (df['Options'] == h['Options']) &
                (df['Page Link'] == h['Page Link'])
            ]
        except:
            trt = pd.DataFrame()

        if not trt.empty:
            oldprd = oldprd + 1
            df.loc[
                (df['ID'] == h['id']) &
                (df['Product ID'] == h['product_id']) &
                (df['Name'] == h['Name']) &
                (df['Options'] == h['Options']) &
                (df['Page Link'] == h['Page Link']),
                [start + " Price"]] = h[start + " Price"]
            df.loc[
                (df['ID'] == h['id']) &
                (df['Product ID'] == h['product_id']) &
                (df['Name'] == h['Name']) &
                (df['Options'] == h['Options']) &
                (df['Page Link'] == h['Page Link']),
                [start + " qty"]] = h[start + " qty"]
        else:
            newproduct = newproduct + 1
            df = df._append(h, ignore_index=True)

    file_name = f"{start}_Lockslash.csv"
    df.to_csv(file_name, index=False)

result = f'''
\n{start}\n
New products >>> {newproduct},
old products >>> {oldprd},
found products in this run >>> {foundPrd}/{numofProds}
=======================================\n
File {file_name} saved! \n
=======================================
'''
print(result)
