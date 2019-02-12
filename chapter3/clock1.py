#!/usr/bin/env python3

import datetime
import time
import unicornhathd

# 使用する色の定義
COLOR = (128, 0, 0)

# 0から9とコロンのマッピング
# 横3 x 縦6 = 18ピクセルのフォントを定義
NUMBERS = (
    0b111101101101101111, # 0
    0b110010010010010111, # 1
    0b111001001111100111, # 2
    0b111001111001001111, # 3
    0b100100100101111001, # 4
    0b111100111001001111, # 5
    0b111100100111101111, # 6
    0b111001001001001001, # 7
    0b111101111101101111, # 8
    0b111101111001001111, # 9
    0b000010000000010000, # :
)

# 表示向きの定義(0度)
unicornhathd.rotation(0)

# フォント表示関数の定義
def render_numeric(x, y, number):
    # 行ごとに分割する
    for row_number in range(0, 6):
        try:
            # マッピングから該当行の部分を取得する
            row = NUMBERS[number] >> ((5 - row_number) * 3) & 0b111
        except KeyError:
            return None

        # 列ごとの処理
        for col_number in reversed(range(0, 3)):
            # 該当列のビットが1の場合
            if row & (0b1 << col_number):
                # x位置の算出
                # 指定位置からマイナスをしていくことでunicornHatHDのx軸反転をする
                x_point = x - (2 - col_number)
                # y位置の算出
                y_point = y + row_number
                # ピクセルを追加する
                unicornhathd.set_pixel(x_point, y_point, *COLOR)

# ループ
while True:
    # バッファのクリア
    unicornhathd.clear()

    # 現在時刻の取得
    now = datetime.datetime.now()

    # 時の二桁目がゼロ以外の場合、
    # 二桁目を表示する
    if now.hour >= 10:
        render_numeric(15, 0, now.hour // 10)

    # 時の二桁目を表示する
    render_numeric(12, 0, now.hour % 10)

    # コロンの表示
    # 秒が奇数だった場合のみ表示する
    if now.second % 2:
        # コロンはNUMBERS[10]に格納されている
        render_numeric(9, 0, 10)

    # 分の表示
    render_numeric(6, 0, now.minute // 10)
    render_numeric(2, 0, now.minute % 10)

    # バッファの描写命令
    unicornhathd.show()

    # 0.1秒待つ
    time.sleep(0.1)
