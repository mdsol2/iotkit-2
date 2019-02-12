#!/usr/bin/env python

import time
import unicornhathd

while True:
    print('Showing all dot.')

    unicornhathd.clear()

    for y in range(0, 16):
        for x in range(0, 16):
            unicornhathd.set_pixel(x, y, 255, 0, 0)
            unicornhathd.show()
            time.sleep(0.5 / 16)

    time.sleep(0.5)
