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

import serial

port_name = '/dev/vircom2'
sp = serial.Serial(port_name, 9600, timeout=0.1)

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
dev2=blecontroller.BLEController("ef:23:f5:42:8f:be")#上モータ

speed = utils.rpm2rad_per_sec(10)

dev.enable_action()
dev.set_led(1, 0, 200, 0)
dev.set_speed(speed)
dev.move_to_pos(0.3)
sleep(3)

dev2.enable_action()
dev2.set_led(1, 0, 200, 0)
dev2.set_speed(speed)
dev2.set_max_torque(100)
dev2.move_to_pos(-2.9)

sleep(3)

#キーボード
'''
while True:
    if unix_input_with_timeout() is "a":
        dev.run_forward()
    elif unix_input_with_timeout() is "b":
        dev.run_reverse()
    else:
        dev.stop_motor()
'''

#シリアル入力
while True:
    ret = sp.read()
    print(ret)
    if len(ret) < 1:
        dev.stop_motor()
        dev2.stop_motor()
    else:
        s = ret[0]
        if s == ord("w"): 
            dev2.run_forward()
        elif s == ord("s"):
            dev2.run_reverse()
        elif s == ord("c"):
            dev.run_forward()
        elif s == ord("x"):
            dev.run_reverse()

