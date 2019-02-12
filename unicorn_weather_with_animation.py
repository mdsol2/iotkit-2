#!/usr/bin/env python3
# coding: utf-8

"""
    unicorn_weather_with_animation.py
    
    OpenWeatherMapから指定地域の指定時間後の天気を取得し、公式アイコンの代わりに
    unicornhatHDのサンプルにある天気アニメーションを表示するスクリプト
       
   
   必須環境変数は以下の2つ
   
   - WEATHER_CITY 指定地域(Aichi, Nagoya, Sydneyなど)
   - OPENWEATHER_API_KEY  OpenWeatherMapのAPIキー
   
   
   オプショナル環境変数は以下の1つ
   
   - DEBUG デバッグオプション　なにか引数をつけるとデバッグログも表示される
      
      
      
　  必須パッケージ
   - unicornhathd
   - requests
   - pillow
   
   
   
   その他必須ファイル
   このスクリプトと同じディレクトリに公式ライブラリの作例集、weather-icons以下のディレクトリが必要になる。
   https://github.com/pimoroni/unicorn-hat-hd/tree/master/examples/weather-icons
   
   
   起動例:
   ```
   $ WEATHER_CITY=nagoya APIKEY=<OpenWeatherMap API KEY> python3 unicorn_weather_with_animation.py 
   ```
"""

from logging import getLogger
logger = getLogger(__name__)

# nicorn_weather_official_iconから共通部分をインポートする
from unicorn_weather_official_icon import getWeather, filterNearstWeather
from PIL import Image
import datetime
import unicornhathd
import requests
import time
import os

APIKEY = os.environ.get('OPENWEATHER_API_KEY')
CITY = os.environ['WEATHER_CITY']

CYCLE_TIME = 0.5

# アイコンIDと画像との対応表
ICON_TABLE = {
    '01d': 'clear-day.png',
    '01n': 'clear-night.png',
    '02d': 'partly-cloudy-day.png',
    '02n': 'partly-cloudy-night.png',
    '03d': 'cloudy.png',
    '03n': 'cloudy.png',
    '04d': 'cloudy.png',
    '04n': 'cloudy.png',
    '09d': 'rain.png',
    '09n': 'rain.png',
    '10d': 'rain.png',
    '10n': 'rain.png',
    '11d': 'rain.png',
    '11n': 'rain.png',
    '13d': 'snow.png',
    '13n': 'snow.png',
    '50d': 'fog.png',
    '50n': 'fog.png',
    'error': 'error.png'
}

## アニメーション画像のディレクトリを定義する
# このファイルのディレクトリを取得
print(__file__)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# このディレクトリに'weather-icons/icons'のディレクトリを追加する
WEATHER_ICONS_DIRECTORY = os.path.join(CURRENT_DIR, 'weather-icons', 'icons')



width, height = unicornhathd.get_shape()


def drawAnimation(image):
    """
    アニメーション画像の描写関数
    この場合のアニメーション画像はいわゆる動画gifではなく、
    それぞれの画像を横に並べた画像である。
    この横長画像を画面の横幅(16px)ごとに切り取り、
    これを順番に表示してアニメーションさせている。
    """
    for o_x in range(int(image.size[0] / width)):
        for o_y in range(int(image.size[1] / height)):
            valid = False
            for x in range(width):
                for y in range(height):
                    pixel = image.getpixel(((o_x * width) + y, (o_y * height) + x))
                    r, g, b = int(pixel[0]), int(pixel[1]), int(pixel[2])
                    if r or g or b:
                        valid = True
                    unicornhathd.set_pixel(x, y, r, g, b)

            if valid:
                unicornhathd.show()
                time.sleep(CYCLE_TIME)

# メイン関数
def main():
    logger.info(WEATHER_ICONS_DIRECTORY)
    """
    メイン処理
    これをループし続ける。
    基本的な流れはほぼunicorn_weather_official_iconのmain()と同じ
    アイコンを使う代わりにアニメーション画像を表示するようにしている。

    """

    # 現在時刻の取得
    now = datetime.datetime.now()

    # datetimeオブジェクトをUnixTimeに変換し、ターゲット時間を作る
    # ターゲットを2時間先とする
    target_timestamp = now.timestamp() + 60 * 60 * 3

    try:
        # 天気情報の取得
        r = getWeather(CITY, APIKEY)
        
        # リクエスト成功でなかった場合の処理
        if not r.ok:
            # 90秒待ってから関数を終了する。
            # これによりmain()を再稼働させる = リトライ処理
            logger.debug(r.status_code)
            logger.warn('error, weather get fail')
            time.sleep(30 * 3)
            return

        weathers = r.json()['list']

        # ターゲット時間に近い天気情報をフィルタリングする。
        weather = filterNearstWeather(weathers, target_timestamp)
        logger.debug('weather is %s', weather)

        # 対応表からふさわしい画像のファイル名を取得する。
        iconname = ICON_TABLE[weather['weather'][0]['icon']]

        # 予め作っていたアイコンのディレクトリにファイル名を追加し、Pillowでロードする
        logger.debug(os.path.join(WEATHER_ICONS_DIRECTORY, iconname))
        image = Image.open(os.path.join(WEATHER_ICONS_DIRECTORY, iconname))

        if image is None:
            logger.warning("image is None.")
            time.sleep(30 * 3)
            return

    except requests.exceptions.ConnectionError as e:
        logger.exception(e)
        time.sleep(30 * 3)

    except KeyError:
        time.sleep(30 * 3)
        return

    logger.debug('start write icon.')

    for i in range(0, 300):
        drawAnimation(image)




if __name__ == '__main__':
    """
    この書き方をしているのは
    これをライブラリとしてロードできるようにするため。

    https://docs.python.jp/3/library/__main__.html


    """

    # ロガーの設定
    # スクリプトとして動作する場合のみ出力ハンドラを追加する。
    from logging import StreamHandler, INFO, DEBUG, Formatter
    import sys

    # 環境変数DEBUGによってロギングレベルを変更する
    if os.environ.get('DEBUG', None):
        logger.setLevel(DEBUG)
    else:
        logger.setLevel(INFO)

    # StreamHandlerはそのまま標準出力として出力する。
    # つまりprint()と同様の動きをする
    handler = StreamHandler(stream=sys.stdout)
    handler.setFormatter(Formatter('[%(levelname)s] %(asctime)s %(name)s %(message)s'))
    logger.addHandler(handler)

    logger.info('start application.')
    logger.info('city is %s', CITY)

    unicornhathd.brightness(0.5)
    unicornhathd.rotation(90)

    # ここがメイン処理。
    # main()をひたすらループさせる。
    # finally
    try:
        while True:
            main()

    # Ctrl+C時に起きる例外を取得し、エラーメッセージが出ないようにする。
    except KeyboardInterrupt:
        logger.info('detect sigterm. goodbye.')

    # finallyは例外が出ようが出まいが終了時に必ず動作される。
    # ここでは、unicornhathdの終了処理を行わさせている。
    finally:
        unicornhathd.off()

