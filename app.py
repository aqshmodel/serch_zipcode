import requests


def search_address(zipcode):
    response = requests.get(f'http://zipcloud.ibsnet.co.jp/api/search?zipcode={zipcode}')
    results = response.json()['results'][0]
    都道府県 = results["address1"]
    市区町村名 = results["address2"]
    町域名 = results["address3"]
    address = f'{都道府県}{市区町村名}{町域名}'
    return address


def main():
    zipcode = '0287405'
    address = search_address(zipcode)

    print(address)


if __name__ == '__main__':
    main()
