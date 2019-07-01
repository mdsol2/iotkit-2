#!/usr/bin/env python3
# coding: utf-8

"""
    unicorn_weather_official_icon.py
    
    OpenWeatherMapから指定地域の指定時間後の天気を取得し、公式アイコンを表示させるスクリプト
   
   
   必須環境変数は以下の2つ
   
   - WEATHER_CITY 指定地域(Aichi, Nagoya, Sydneyなど)
   - OPENWEATHER_API_KEY  OpenWeatherMapのAPIキー
   
   
   オプショナル環境変数は以下の1つ
   
   - DEBUG デバッグオプション

   
　  必須パッケージ
   - unicornhathd
   - requests
   - pillow

   

   起動例:
   ```
   $ WEATHER_CITY=nagoya OPENWEATHER_API_KEY=<OpenWeatherMap API KEY> python3 unicorn_weather_official_icon.py 
   ```
"""


from logging import getLogger
logger = getLogger(__name__)

from PIL import Image
from io import BytesIO
import unicornhathd
import datetime
import requests
import os
import sys
import time

APIBASE = 'https://api.openweathermap.org/data/2.5/forecast'
ICON_PATH = 'http://openweathermap.org/img/w'

CITY = os.environ['WEATHER_CITY']
APIKEY = os.environ['OPENWEATHER_API_KEY']


unicornhathd.brightness(0.5)
unicornhathd.rotation(0)

width, height = unicornhathd.get_shape()


def getWeather(city, apikey):
    """
    天気を取得する
    リクエストにAPIKeyと都市をパラメーターに入れる
    
    https://openweathermap.org/forecast5
    """
 
    payload = {
        'APIKEY': APIKEY,
        'q': CITY
    }
    r = requests.get(
        APIBASE,
        params=payload
    )
    return r


def filterNearstWeather(weathers, date):
    """
    openWeatherレスポンスのweatherリストから指定時刻に一番近いものを選択する
    Noneが帰る場合もある
    """
    
    # 計算用のターゲット時間のタイムスタンプを作る。
    # 引数がdatetimeオブジェクトだった場合はそこからunixtimeを取得する
    # それ以外の場合はunixtimeが渡されたとみなす。
    # こうすることで引数dateはunixtime、datetimeオブジェクトのどちらにも対応でき、可用性が上がる
    if isinstance(date, datetime.datetime):
        target_timestamp = date.timestamp()
    else:
        target_timestamp = date

    # 天気予報情報を1つづつ確認してターゲット時間と合致するかを試す
    # 今回の合致条件は、予報の時間がターゲットよりも後かつターゲットから2時間以内であること
    # これを見つけ次第ループ処理を解除する
    weather = None
    for i in weathers:
        if i['dt'] > target_timestamp and abs(i['dt'] - target_timestamp) <= 3600 * 3:
            weather = i
            break

    return weather

def getIconImage(icon):
    """
    openWeatherのアイコンデータを取得する。
    
    やり方としてはHTTPリクエストでpngファイルを取得し、
    PILのimage形式にしてリサイズする。
    
    https://openweathermap.org/weather-conditions
    """
    
    # os.path.joinでアイコンIDにURLと拡張子をくっつける
    # パス周りの操作はなるべくこれを使ったほうが無難
    # https://docs.python.jp/3/library/os.path.html
    path = os.path.join(ICON_PATH, icon + '.png')
    logger.debug('request image from %s', path)

    # requestsを使用してアイコンの取得
    r = requests.get(path)
    
    if r.ok:
        # リクエストが正常終了した場合の処理
        
        # このリクエストではバイナリ（画像）を扱うので、
        # Pillowに渡すときはio.BytesIOを介す必要がある。
        # https://docs.python.jp/3/library/io.html
        image = Image.open(BytesIO(r.content))
        
        # 画像をリサイズし、RGBモードに変換する。
        image.thumbnail((width, height))
        image = image.convert('RGB')

        return image

    logger.warning('fail of image get. %s', path)
    return None

def main():
    """
    メイン処理
    これをループし続ける想定となる
    
    """
    
    # 現在時刻の取得
    now = datetime.datetime.now()
    
    # datetimeオブジェクトをUnixTimeに変換し、ターゲット時間を作る
    # ターゲットを2時間先とする
    target_timestamp = now.timestamp() + 60 * 60 * 2

    try:
        # APIから天気情報を取得
        r = getWeather(CITY, APIKEY)
        
        # リクエストが失敗した場合の処理
        if not r.ok:
            # 90秒待ってから関数を終了する。
            # これによりmain()を再稼働させる = リトライ処理
            logger.debug(r.status)
            logger.warn('error, weather get fail')
            time.sleep(30 * 3)
            return

        # ターゲット時間に近い天気情報をフィルタリングする。
        weathers = r.json()['list']
        weather = filterNearstWeather(weathers, target_timestamp)
        logger.debug('weather is %s', weather)

        image = getIconImage(weather['weather'][0]['icon'])

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

    unicornhathd.clear()

    # x, yを指定して1ドットずつ描写する
    for x in range(width):
        for y in range(height):
            r, g, b = image.getpixel((x, y))
            # ここの部分でx軸を反転させている
            unicornhathd.set_pixel(width-x-1, y, r, g, b)

    unicornhathd.show()

    time.sleep(1800)


if __name__ == '__main__':
    """
    この書き方をしているのは
    これをライブラリとしてロードできるようにするため。
    
    https://docs.python.jp/3/library/__main__.html
    
    
    """

    # ロガーの設定
    # スクリプトとして動作する場合のみ出力ハンドラを追加する。
    from logging import StreamHandler, INFO, DEBUG, Formatter
    
    # 環境変数DEBUGによってロギングレベルを変更する
    if os.environ.get('DEBUG', None):
        logger.setLevel(DEBUG)
    else:
        logger.setLevel(INFO)

    # StreamHandlerはそのまま標準出力として出力する。
    # つまりprint()と同様の動きをする
    handler = StreamHandler(stream=sys.stdout)
    handler.setFormatter(Formatter('[%(levelname)s] %(asctime)s %(message)s'))
    logger.addHandler(handler)

    logger.info('start application. %s', datetime.datetime.now().strftime('%X'))
    logger.info('city is %s', CITY)


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
