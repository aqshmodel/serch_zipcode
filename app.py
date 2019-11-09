import requests

zipcode = input('郵便番号は？(ハイフン無し7桁)は？ > ')

response = requests.get(f'http://zipcloud.ibsnet.co.jp/api/search?zipcode={zipcode}')

print(response)  # ステータスコード200が返ってくる 正常値,リクエスト成功
print(response.text)  # 引数に対する結果が返ってくる
