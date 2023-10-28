import time
from datetime import datetime

import requests


def main():
    """
    如果您想使用此API，您应该按照以下步骤进行操作。
    """
    # 步骤1：在微博上注册一个应用，并定义常量app key、app secret和redirect_url。
    APP_KEY = '1559422208'
    APP_SECRET = 'e96013d61ffed3f1a86134ebeaab54ba'
    REDIRECT_URL = 'https://api.weibo.com/oauth2/default.html'
    # 步骤2：获取授权URL和代码
    url = f"https://api.weibo.com/oauth2/authorize?response_type=code&client_id={APP_KEY}&redirect_uri={REDIRECT_URL}"
    print(url)
# https://api.weibo.com/oauth2/authorize?response_type=code&client_id=1559422208&redirect_uri=http://192.168.3.154:8080/api/weibo/oauth2
    res = requests.post(
        'https://api.weibo.com/oauth2/access_token',
        params={
            'client_id': APP_KEY,
            'client_secret': APP_SECRET,
            'redirect_uri': REDIRECT_URL,
            'code': input("please input code : "),
            'grant_type': 'authorization_code'
        }
    ).json()
    res['expires_in'] += time.time()

    print(datetime.fromtimestamp(res['expires_in']).strftime('%Y-%m-%d %HH:%MM'))
    print(res)


if __name__ == '__main__':
    main()
