#!/usr/bin/env python

import time


class Toddler:
    __version = '2018a'

    def __init__(self, IO):
        print('[Toddler] I am toddler {} playing in a sandbox'.format(Toddler.__version))

        self.camera = IO.camera.initCamera('pi', 'low')
        self.getInputs = IO.interface_kit.getInputs
        self.getSensors = IO.interface_kit.getSensors
        self.mc = IO.motor_control
        self.sc = IO.servo_control
        self.state = 0
        self.hall_sensor = -1
        self.counter = 0

    def control(self):
        print('{}\t{}'.format(self.getSensors(), self.getInputs()))
        #counter = 0
        turn_number = 5
        if self.getInputs()[7] !=  self.hall_sensor:
            self.hall_sensor = self.getInputs()[7]
            self.counter += 1
        if self.counter <= turn_number:
            self.mc.setMotor(2, 70)
            self.mc.setMotor(3, -70)
        else :
            self.mc.stopMotor(2)
            self.mc.stopMotor(3)
            self.counter = 0
            time.sleep(2)
        #print('a')
    	#self.mc.setMotor(0, 100)
    	#self.mc.setMotor(0, 100)
    	#self.mc.setMotor(1, 100)
    	#self.mc.setMotor(2, 100)
    	#self.mc.setMotor(3, 100)
    	#self.mc.setMotor(4, 100)
    	#self.mc.setMotor(5, 100)
    	#counter = 0
    	#limit = 10
    	print(time.time())
	#while counter <= limit:
	#	counter += 1
	#	print(counter)
	#	time.sleep(0.1)
        #self.turn_light()
        #self.mc.setMotor(2, -50 if self.getSensors()[0] >= 30 else 50)
        #self.mc.setMotor(4, -50 if self.getSensors()[0] >= 30 else 50)
	#if self.getSensors()[1] >= 400 :
	#    self.stop()
        #else:
	#    self.run()
        #self.servo_move()


    def stop(self):
        self.mc.stopMotors()
        print('STOPING THE MOTORS.')

    def run(self):
        self.mc.setMotor(2, -40 if self.getSensors()[0] >= 30 else 40)
        self.mc.setMotor(4, -40 if self.getSensors()[0] >= 30 else 40)

    def turn_light(self):
	self.mc.setMotor(1, 100)

    def servo_move(self):
	self.sc.engage()
        self.sc.setPosition(0 if self.getSensors()[0] >= 500 else 180)
        time.sleep(0.05)

    def vision(self):
        image = self.camera.getFrame()
        self.camera.imshow('Camera', image)
        #pass
