import requests

response = requests.get('http://zipcloud.ibsnet.co.jp/api/search?zipcode=0287405')

print(response)  # ステータスコード200が返ってくる 正常値,リクエスト成功
print(response.text)  # 引数に対する結果が返ってくる

