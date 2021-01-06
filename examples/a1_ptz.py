# -*- coding: utf-8 -*-
"""
Created on Thr Jan 10 09:13:24 2018

@author: takata@innovotion.co.jp
@author: harada@keigan.co.jp
"""

import sys
import pathlib

current_dir = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(current_dir) + '/../') # give 1st priority to the directory where pykeigan exists

from time import sleep
from pykeigan import blecontroller
from pykeigan import utils
from concurrent.futures import ThreadPoolExecutor

import serial

up_pos = 10000
down_pos = 10000

def get_motor_informations():
    global down_pos
    global up_pos
    while True:
        if up:
            m = up.read_motor_measurement()
            up_pos = m.pop("position")
#            print("up_pos:",up_pos)

        if down:
            m = down.read_motor_measurement()
            down_pos = m.pop("position")
            print("down_pos:",down_pos)

        sleep(0.1)

port_name = '/dev/vircom2'
sp = serial.Serial(port_name, 9600)

def get_message(m=''):
    s = sp.read_all()
    c = ''
    if s:
        c = chr(s[0])
        return c
    else:
        return m

up=blecontroller.BLEController("ef:23:f5:42:8f:be")#上モータ
down=blecontroller.BLEController("fe:e1:8c:0a:7d:a0")#下モータ

executor = ThreadPoolExecutor(max_workers=2)
res = executor.submit(get_motor_informations)

up.enable_action()#安全装置。初めてモーターを動作させる場合に必ず必要。
down.enable_action()#安全装置。初めてモーターを動作させる場合に必ず必要。

up.set_speed(0.5)#radian/sec
down.set_speed(0.5)#radian/sec

up.set_acc(0.5)#rpm -> radian/sec
down.set_acc(0.5)#rpm -> radian/sec

up.set_led(1, 0, 200, 0)
down.set_led(1, 0, 200, 0)

up_init_pos = 0.26
down_init_pos = 3.8

up_min_deg = -90
up_max_deg = 45

up_min_pos = utils.deg2rad(up_min_deg) + down_init_pos
up_max_pos = utils.deg2rad(up_max_deg) + down_init_pos

print("up init pos:",up_init_pos)
print("up range:",up_min_pos,up_max_pos)

down_min_deg = -180
down_max_deg = 180

down_min_pos = utils.deg2rad(down_min_deg) + down_init_pos
down_max_pos = utils.deg2rad(down_max_deg) + down_init_pos

print("down init pos:", down_init_pos)
print("down range:",down_min_pos,down_max_pos)

# deg -180 -- 180 
down.move_to_pos(down_init_pos)

while True:
    print(down_pos,down_init_pos)
    if ((down_pos > (down_init_pos - 0.1)) and (down_pos < (down_init_pos + 0.1))):
        break
    sleep(0.1)

# deg -90 -- 45 
up.move_to_pos(up_init_pos)

'''
while True: 
    if (up_pos > up_init_pos - 0.3 and up_pos < up_init_pos + 0.3):
        break
    sleep(0.1)
'''

"""
Exit with key input
"""

print("start")
while True:

    c = get_message()
    
    if c is 'j':
        down.run_forward()
        print("down run forward")
        while True:
            c = get_message("j")
            print("down_max_pos:",down_max_pos)
            if(down_pos > down_max_pos):
                c = ''
                print("stop down run forward limit")
                break
            if c is not 'j':
                print("stop down run forward")
                break
            sleep(0.1)

    if c is 'l':
        down.run_reverse()
        print("down run reverse")
        while True:
            c = get_message("l")
            print("down_min_pos:",down_min_pos)
            if(down_pos < down_min_pos):
                c = ''
                print("stop down run reverse limit")
                break
            if c is not 'l':
                print("stop down run reverse")
                break
            sleep(0.1)

    up.stop_motor()
    down.stop_motor()
     
    sleep(0.2)



