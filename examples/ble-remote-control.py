# -*- coding: utf-8 -*-
"""
Created on Thr Jan 10 09:13:24 2018

@author: takata@innovotion.co.jp
@author: harada@keigan.co.jp
"""

import sys
import pathlib

import sys
import select

def unix_input_with_timeout(prompt='', timeout=0.1):
    sys.stdout.write(prompt)
    sys.stdout.flush()
    (ready, _, _) = select.select([sys.stdin], [], [], timeout)
    if ready:
        return sys.stdin.readline().rstrip('\n')
    else:
        return 0

current_dir = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(current_dir) + '/../') # give 1st priority to the directory where pykeigan exists

from time import sleep
from pykeigan import blecontroller
from pykeigan import utils

dev=blecontroller.BLEController("fe:e1:8c:0a:7d:a0")#下モータ
#dev2=blecontroller.BLEController("ef:23:f5:42:8f:be")#上モータ

speed = utils.rpm2rad_per_sec(10)
dev.enable_action()
dev.set_led(1, 0, 200, 0)
dev.set_speed(speed)
dev.move_to_pos(0.3)

speed = utils.rpm2rad_per_sec(3)


while True:
    if unix_input_with_timeout() is "a":
        dev.run_forward()
    elif unix_input_with_timeout() is "b":
        dev.run_reverse()
    else:
        dev.stop_motor()
