import requests
import json
from datetime import datetime

def get_hk_official_price():
    url = "https://www.consumer.org.hk/pricewatch/oilwatch/opendata/oilprice.json"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        
        # 尋找 98 無鉛汽油 (Super Unleaded)
        # 官方 JSON 通常按油站排列，我們取第一個有效油站的價格作為參考
        for oil_company in data.get('prices', []):
            if 'Standard Petrol' in oil_company:
                return float(oil_company['Standard Petrol'])
        return 31.79 # 備用
    except Exception as e:
        print(f"HK Error: {e}")
        return 31.79

def get_macau_price():
    # 澳門消委會燃料價格網頁 (以 98 無鉛為例)
    url = "https://www.consumer.gov.mo/Fuel/price/Oil.aspx?lang=zh"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # 尋找表格中第一間油站（通常是參考價）
        # 澳門網頁結構較多 table，這裡建議抓取其「最低價」或「平均價」標籤
        price_tag = soup.find("span", {"id": "ctl00_ContentPlaceHolder1_lbl_MinPrice"})
        if price_tag:
            return float(price_tag.text.strip())
        return 15.09 # 備用數值
    except:
        return 15.09

def get_guangdong_prices():
    url = "https://www.autohome.com.cn/oil"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.encoding = 'gbk' # 汽車之家通常使用 GBK 編碼
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        prices = {"95": 0.0, "98": 0.0}
        
        # 尋找包含「廣東」的表格行
        table = soup.find('table', class_='list-table')
        if table:
            for tr in table.find_all('tr'):
                tds = tr.find_all('td')
                if len(tds) > 0 and '广东' in tds[0].text:
                    # 根據汽車之家目前的表格順序：
                    # tds[0]:地區, tds[1]:92, tds[2]:95, tds[3]:98, tds[4]:0號柴油
                    prices["95"] = float(tds[2].text.strip())
                    prices["98"] = float(tds[3].text.strip())
                    break
        return prices
    except Exception as e:
        print(f"Guangdong (Autohome) Error: {e}")
        return {"95": 9.21, "98": 10.15}

def main():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 整合所有數據
    result = {
        "last_updated": now,
        "items": [
            {
                "region": "香港",
                "price": get_hk_official_price(),
                "currency": "HKD",
                "type": "98無鉛",
                "flag": "🇭🇰",
                "source": "香港消委會 Open Data"
            },
            {
                "region": "澳門",
                "price": get_macau_price(),
                "currency": "MOP",
                "type": "98無鉛",
                "flag": "🇲🇴",
                "source": "澳門消委會"
            },
            {
                "region": "廣東",
                "price": get_china_price(),
                "currency": "CNY",
                "type": "95號",
                "flag": "🇨🇳",
                "source": "廣東油價監測"
            }
        ]
    }

    # 寫入 GitHub Pages 用的 JSON 檔案
    with open("prices.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
    print("Prices updated successfully.")

if __name__ == "__main__":
    main()
