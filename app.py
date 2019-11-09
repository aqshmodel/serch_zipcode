import requests

zipcode = '0287405'

response = requests.get(f'http://zipcloud.ibsnet.co.jp/api/search?zipcode={zipcode}')

# print(response)  # ステータスコード200が返ってくる 正常値,リクエスト成功
# print(response.text)  # 引数に対する結果が返ってくる
data = response.json()  # 引数に対する結果が返ってくる
results = data['results'][0]
都道府県 = results["address1"]
市区町村名 = results["address2"]
町域名 = results["address3"]

print(f'{都道府県}{市区町村名}{町域名}')