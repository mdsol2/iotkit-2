#!/usr/bin/env python3

# ログ設定
from logging import getLogger, DEBUG, INFO, StreamHandler, Formatter
import os
logger = getLogger(__name__)
handler = StreamHandler()
handler.setFormatter(Formatter('[%(levelname)s] %(asctime)s %(message)s'))
logger.addHandler(handler)

# 環境変数DEBUGがある場合のみデバッグログを出力するようにする
# 開発時は以下のようにして始動する
# $ DEBUG=yes python3 unicorn_enviro.py
if os.environ.get('DEBUG', False):
    logger.setLevel(DEBUG)
else:
    logger.setLevel(INFO)

from PIL import Image, ImageDraw, ImageFont
import unicornhathd
import requests
import math
import time
import datetime

# 参照元のホストとポートの指定
# 継続化するときのことを見据えてホストの直書きは控える
ENVIRO_HOST = os.environ.get('ENVRIO_HOST')
ENVIRO_URL = 'http://{host}/environ'.format(host=ENVIRO_HOST)
COLOR = (200, 0, 0)

logger.debug('request url is %s', ENVIRO_URL)


width, height = unicornhathd.get_shape()
unicornhathd.rotation(0)
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 6)

# httpリクエスト関数
def getEnviro(url, *args, **kwargs):
    r = requests.get(ENVIRO_URL, *args, **kwargs)

    if r.ok and not r.json()['error']:
        return r.json()

# unicornHatHDの画面更新関数
def refreshDisplay(tempture, pressure):
    image = Image.new("RGB", (width, height), (0, 0, 0))
    draw = ImageDraw.Draw(image)

    draw.text((0, -1), '{0:d}℃'.format(tempture), fill=COLOR, font=font)
    draw.text((0, 4), '{0:04d}'.format(pressure), fill=COLOR, font=font)
    draw.text((4, 10), 'hPa', fill=COLOR, font=font)

    unicornhathd.clear()

    # x, yを指定して1ドットずつ描写する
    for x in range(width):
        for y in range(height):
            r, g, b = image.getpixel((x, y))
            # ここの部分でx軸を反転させている
            unicornhathd.set_pixel(width-x-1, y, r, g, b)

    # 現在時刻の秒を基準にドットの点滅をさせる
    if datetime.datetime.now().second % 2:
        unicornhathd.set_pixel(15, 15, *COLOR)
        unicornhathd.set_pixel(15, 14, *COLOR)
        unicornhathd.set_pixel(14, 15, *COLOR)
        unicornhathd.set_pixel(14, 14, *COLOR)

    # 画面のリフレッシュ命令
    unicornhathd.show()

# エラー表示用関数
def renderError():
    image = Image.new("RGB", (width, height), (0, 0, 0))
    draw = ImageDraw.Draw(image)

    draw.text((0, -1), 'ERR', fill=COLOR, font=font)
    draw.text((0, 4), 'OR', fill=COLOR, font=font)
    unicornhathd.clear()

    # x, yを指定して1ドットずつ描写する
    for x in range(width):
        for y in range(height):
            r, g, b = image.getpixel((x, y))
            # ここの部分でx軸を反転させている
            unicornhathd.set_pixel(width-x-1, y, r, g, b)

    # 画面のリフレッシュ命令
    unicornhathd.show()

# メイン関数
def main():
    loop_count = 0
    tempture = 0
    pressure = 0

    while True:
        if loop_count <= 0:
            logger.debug('get environ')

            # http操作時のエラーハンドリング
            try:
                result = getEnviro(ENVIRO_URL)
                tempture = result['results']['tempture']
                pressure = result['results']['pressure']

                # 画面表示用に数値の四捨五入
                tempture = math.floor(tempture)
                pressure = math.floor(pressure)

                logger.debug('OK. tmp: %s, press %s', tempture, pressure)

            # httpリクエストで接続に失敗した場合はこのような例外が発生する
            except requests.exceptions.ConnectionError:
                # ERRORレベルでログ出力
                logger.error('http request failed')
                
                # エラー画面出力
                renderError()
                
                # 60秒待った後にループをやり直す = 再度HTTPリクエストを行う
                time.sleep(60)
                continue

            # その他の例外が起こった際にそれをログに記述し、終了する。
            # 現時点で想定外のエラーが起こった時の問題の特定をスムーズにするため
            except Exception as e:
                logger.exception(e)
                raise e

        refreshDisplay(tempture, pressure)

        # ループのカウントが2048になったらカウントをリセット。
        # カウントが0の時のみhttpリクエストを送るようになっているので、
        # このスパンで数値の更新が起こる
        loop_count += 1
        if loop_count >= 2048:
            loop_count = 0

        time.sleep(0.1)


if __name__ == '__main__':
    logger.info('start script.')

    try:
        main()

    # Ctrol + Cや、終了コールがあった際はこのような例外が発生する。
    except KeyboardInterrupt:
        logger.info('goodbye.')

    # 終了時に画面をクリアする
    finally:
        unicornhathd.off()
