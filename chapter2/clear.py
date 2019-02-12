#!/usr/bin/env python3
# coding: utf-8
'''
Unicorn HAT HDのLEDマトリックスをリセットするプログラム
'''

import time
import unicornhathd

# バッファーをクリアして
unicornhathd.clear()
# 描画を実行
unicornhathd.show()
