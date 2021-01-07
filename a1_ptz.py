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

up_init_pos = 0.26
down_init_pos = -0

TIMEOUT = 300 # milli

port_name = '/dev/vircom2'
sp = serial.Serial(port_name, 9600)

def get_motor_informations():
    global down_pos,up_pos
    global down_init_pos,up_init_pos
    global sp
    while True:
        if up:
            m = up.read_motor_measurement()
            up_pos = m.pop("position")
            #print("up_pos:",up_pos)

        if down:
            m = down.read_motor_measurement()
            down_pos = m.pop("position")
            #print("down_pos:",down_pos)

        down_deg = utils.rad2deg(down_pos - down_init_pos)      
        up_deg = utils.rad2deg(up_pos - up_init_pos)      
        sp.write(bytes(str(int(down_deg)) + "," + str(int(up_deg)) + "\n",'UTF-8'))

        sleep(0.05)

def get_message():
    s = sp.read_all()
    c = ''
    if s:
        c = chr(s[0])
    return c

def send_message():
    global down_pos
    global up_pos
    down_pos_str = str(down_pos)
    up_pos_str = str(up_pos)
    send_str = "down:" + down_pos + " up:" + up_pos
    sp.write(send_str.encode('utf-8'))
   
import time
def current_milli_time():
    return int(round(time.time() * 1000))



print("connect up motor")
up=blecontroller.BLEController("ef:23:f5:42:8f:be")#上モータ
print("connect down motor")
down=blecontroller.BLEController("fe:e1:8c:0a:7d:a0")#下モータ

executor = ThreadPoolExecutor(max_workers=2)
res = executor.submit(get_motor_informations)

up.enable_action()#安全装置。初めてモーターを動作させる場合に必ず必要。
down.enable_action()#安全装置。初めてモーターを動作させる場合に必ず必要。

up.set_speed(0.5)#radian/sec
down.set_speed(0.5)#radian/sec

up.set_acc(0.5)#rpm -> radian/sec
down.set_acc(0.5)#rpm -> radian/sec

up.set_max_torque(10.0)
down.set_max_torque(10.0)

up.set_led(1, 0, 200, 0)
down.set_led(1, 0, 200, 0)

up_min_deg = -45
up_max_deg = 90

up_min_pos = utils.deg2rad(up_min_deg) + up_init_pos
up_max_pos = utils.deg2rad(up_max_deg) + up_init_pos

print("up init pos:",up_init_pos)
print("up range:",up_min_pos,up_max_pos)

down_min_deg = -120
down_max_deg = 120

down_min_pos = utils.deg2rad(down_min_deg) + down_init_pos
down_max_pos = utils.deg2rad(down_max_deg) + down_init_pos

print("down init pos:", down_init_pos)
print("down range:",down_min_pos,down_max_pos)

def init_pos():
    error = 0.1
    global down_pos,up_pos
    global down_init_pos,up_init_pos

    print("start init pos")

    down.move_to_pos(down_init_pos)
    while True:
        if ((down_pos > (down_init_pos - error)) and (down_pos < (down_init_pos + error))):
            break
        sleep(0.1)

    up.move_to_pos(up_init_pos)
    while True: 
        if (up_pos > up_init_pos - error and up_pos < up_init_pos + error):
            break
        sleep(0.1)

    print("finish init pos")

init_pos()
print("control enable")
while True:
    #a:init i:up k:down j:left l:right

    c = get_message()

    if c is 'a':
        init_pos()

    if c is 'i':
        if(up_pos < up_max_pos):
            up.run_forward()
            print("up run forward")
            start_time = current_milli_time()
            while True:
                time_diff = current_milli_time() - start_time
                #print(time_diff)
                if (time_diff > TIMEOUT):
                    print("time out")
                    c = ''
                    break

                c = get_message()

                if c is 'i':
                    start_time = current_milli_time()

                #print("up_max_pos:",up_max_pos)
                if(up_pos > up_max_pos):
                    c = ''
                    print("stop up run forward limit")
                    break
                if (c is not 'i') and (c is not ''):
                    print("stop up run forward")
                    break
                sleep(0.05)

    if c is 'k':
        if(up_pos > up_min_pos):
            up.run_reverse()
            print("up run reverse")
            start_time = current_milli_time()
            while True:
                time_diff = current_milli_time() - start_time
                #print(time_diff)
                if (time_diff > TIMEOUT):
                    print("time out")
                    c = ''
                    break

                c = get_message()

                if c is 'k':
                    start_time = current_milli_time()

                #print("up_min_pos:",up_min_pos)
                if(up_pos < up_min_pos):
                    c = ''
                    print("stop up run reverse limit")
                    break
                if (c is not 'k') and (c is not ''):
                    print("stop up run reverse")
                    break
                sleep(0.05)



    
    if c is 'j':
        if(down_pos < down_max_pos):
            down.run_forward()
            print("down run forward")
            start_time = current_milli_time()
            while True:
                time_diff = current_milli_time() - start_time
                #print(time_diff)
                if (time_diff > TIMEOUT):
                    print("time out")
                    c = ''
                    break

                c = get_message()

                if c is 'j':
                    start_time = current_milli_time()

                #print("down_max_pos:",down_max_pos)
                if(down_pos > down_max_pos):
                    c = ''
                    print("stop down run forward limit")
                    break
                if (c is not 'j') and (c is not ''):
                    print("stop down run forward")
                    break
                sleep(0.05)

    if c is 'l':
        if(down_pos > down_min_pos):
            down.run_reverse()
            print("down run reverse")
            start_time = current_milli_time()
            while True:
                time_diff = current_milli_time() - start_time
                #print(time_diff)
                if (time_diff > TIMEOUT):
                    print("time out")
                    c = ''
                    break

                c = get_message()

                if c is 'l':
                    start_time = current_milli_time()

                #print("down_min_pos:",down_min_pos)
                if(down_pos < down_min_pos):
                    c = ''
                    print("stop down run reverse limit")
                    break
                if (c is not 'l') and (c is not ''):
                    print("stop down run reverse")
                    break
                sleep(0.05)

    up.stop_motor()
    down.stop_motor()
     
    sleep(0.1)



