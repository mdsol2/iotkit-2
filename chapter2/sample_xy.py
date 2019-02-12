#!/usr/bin/env python3
# coding: utf-8
'''
Unicorn HAT HDの全LEDを順番に点灯するサンプル
y座標に応じて色が変化するようにしている
'''

import time
import unicornhathd

while True:
    print('Showing all dot.')

    unicornhathd.clear()

    # Y軸のループ
    for y in range(0, 16):
        # X軸のループ
        for x in range(0, 16):
            # ピクセルのセット
            unicornhathd.set_pixel(x, y, 255-y*15, y*15, 0)
            # 描画を実行
            unicornhathd.show()
            time.sleep(0.5 / 16)

    time.sleep(0.5)
