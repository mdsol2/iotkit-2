#!/usr/bin/env python3
# coding: utf-8
'''
Unicorn HAT HDの全LEDを順番に点灯するサンプル
'''

import time
import unicornhathd

while True:
    print('Showing all dots.')

    unicornhathd.clear()

    for i in range(0, 256):
        # x座標とy座標の計算
        x = i % 16
        y = i // 16
        # ピクセルをセット
        unicornhathd.set_pixel(x, y, 255, 0, 0)
        # 描画を実行
        unicornhathd.show()
        time.sleep(0.5 / 16)

    time.sleep(0.5)
