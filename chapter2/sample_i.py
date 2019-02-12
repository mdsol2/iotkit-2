#!/usr/bin/env python

import time
import unicornhathd

while True:
    print('Showing all dots.')

    unicornhathd.clear()

    for i in range(0, 256):
        x = i % 16
        y = i // 16
        unicornhathd.set_pixel(x, y, 255, 0, 0)
        unicornhathd.show()
        time.sleep(0.5 / 16)

    time.sleep(0.5)
