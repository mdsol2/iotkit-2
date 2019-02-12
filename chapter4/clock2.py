#!/usr/bin/env python3

"""
sudo apt-get install python3 python3-dev python3-pip git python3-rpi.gpio python3-smbus python3-PIL
sudo apt-get install ttf-dejavu
sudo pip3 install unicornhadhd
"""

import datetime
from PIL import Image, ImageDraw, ImageFont
import unicornhathd
import time

COLOR = (200, 0, 0)

width, height = unicornhathd.get_shape()

unicornhathd.rotation(0)

# フォントの定義
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 9)

# 無限ループ
while True:
    # 描写用キャンバスの新規作成
    image = Image.new("RGB", (width, height), (0, 0, 0))
    draw = ImageDraw.Draw(image)

    # 現在時刻の取得
    now = datetime.datetime.now()

    # キャンバスに時、分の描写
    draw.text((0, -1), '{0:02}'.format(now.hour), fill=COLOR, font=font)
    draw.text((0, 8), '{0:02}'.format(now.minute), fill=COLOR, font=font)

    # ここからunicornhatへキャンバス描写作業
    unicornhathd.clear()

    # x, yを指定して1ドットずつ描写する
    for x in range(width):
        for y in range(height):
            r, g, b = image.getpixel((x, y))
            # ここの部分でx軸を反転させている
            unicornhathd.set_pixel(width-x-1, y, r, g, b)

    # コロンの代わりに2x2のドットを描写する
    if now.second % 2:
        unicornhathd.set_pixel(0, height-1, *COLOR)
        unicornhathd.set_pixel(1, height-1, *COLOR)
        unicornhathd.set_pixel(0, height-2, *COLOR)
        unicornhathd.set_pixel(1, height-2, *COLOR)

    # 画面のリフレッシュ命令
    unicornhathd.show()

    time.sleep(0.1)
