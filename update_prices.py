import requests
import json
import statistics
from bs4 import BeautifulSoup
from datetime import datetime

def get_hk_price():
    # 香港消委會官方 JSON
    url = "https://www.consumer.org.hk/pricewatch/oilwatch/opendata/oilprice.json"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        # 提取 98 無鉛 (Super Unleaded) 參考價
        for oil in data.get('prices', []):
            if 'super_unleaded' in oil and oil['super_unleaded']:
                return float(oil['super_unleaded'])
        return 31.79
    except:
        return 31.79

def get_macau_cash_min():
    # 澳門消委會現金優惠 API
    url = "https://www.consumer.gov.mo/api02/api/fuel/getBounsData/cn?category=001&sid=fuel_next_app"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        
        cash_prices = []
        if 'data' in data:
            for item in data['data']:
                # 篩選：BonusCode 為 0003 (現金)，且針對 98 無鉛 (通常 fuel_id 為 3)
                if item.get('BonusCode') == "0003":
                    # bouns_order 欄位即為折扣後價格
                    price = float(item.get('bouns_order', 0))
                    if price > 0:
                        cash_prices.append(price)
        
        return min(cash_prices) if cash_prices else 12.59
    except Exception as e:
        print(f"Macau API Error: {e}")
        return 12.59

def get_guangdong_prices():
    # 汽車之家廣東油價
    url = "https://www.autohome.com.cn/oil"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.encoding = 'gbk'
        soup = BeautifulSoup(resp.text, 'html.parser')
        prices = {"95": 9.21, "98": 10.15}
        
        table = soup.find('table', class_='list-table')
        if table:
            for tr in table.find_all('tr'):
                tds = tr.find_all('td')
                if len(tds) > 0 and '广东' in tds[0].text:
                    prices["95"] = float(tds[2].text.strip())
                    prices["98"] = float(tds[3].text.strip())
                    break
        return prices
    except:
        return {"95": 9.21, "98": 10.15}

def main():
    hk = get_hk_price()
    mo = get_macau_cash_min()
    gd = get_guangdong_prices()
    
    result = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "items": [
            {"region": "香港", "price": hk, "currency": "HKD", "type": "98無鉛", "flag": "🇭🇰", "note": "零售參考價"},
            {"region": "澳門", "price": mo, "currency": "MOP", "type": "98無鉛", "flag": "🇲🇴", "note": "全城最平現金價"},
            {"region": "珠海", "price": gd["95"], "currency": "CNY", "type": "95號", "flag": "🇨🇳", "note": "廣東零售價"},
            {"region": "珠海", "price": gd["98"], "currency": "CNY", "type": "98號", "flag": "🇨🇳", "note": "廣東零售價"}
        ]
    }

    with open("prices.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
    print("Success: prices.json has been updated.")

if __name__ == "__main__":
    main()
