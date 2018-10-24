#!/usr/bin/env python

import time
import utils

class Toddler:
    __version = '2018a'


    def __init__(self, IO):
        print('[Toddler] I am toddler {} playing in a sandbox'.format(Toddler.__version))

        self.TEST_MODE = False
        self.camera = IO.camera.initCamera('pi', 'low')
        self.getInputs = IO.interface_kit.getInputs
        self.getSensors = IO.interface_kit.getSensors
        self.mc = IO.motor_control
        self.sc = IO.servo_control
        # motor index
        self.left_motor = 2
        self.right_motor = 4
        self.lightbulb = 1
        # digital sensor input index
        self.bumper_left = 1
        self.bumper_right = 2
        self.odomoter = 7
        # digital sensor input index
        self.sonar_sensor = 0
        self.light_sensor = 1
        self.left_ir = 2
        self.left_ir = 3
        # Speed setting
        self.base_speed = 85
        self.current_speed = self.base_speed
        self.min_speed = 70
        self.direction = -1 #-1 forward, 1 backward
        # Sensor setting
        self.threshold_sonar = 20
        self.threshold_light = 200
        self.threshold_ir = 400
        self.threshold_turn = 0.5
        # State & servo setting
        self.state = 0
        self.final_angle = 90
        # Start required

        self.light_on()

        self.hall_sensor = -1
        self.counter = 0

    def _test(self):
        #self.mc.setMotor(1, 100)elf.direction) # left back
        #self.mc.setMotor(2, 20)
        # self.mc.setMotor(4, 100)
        #self.mc.setMotor(0,100)
        #self.mc.setMotor(1,100)
        self.mc.setMotor(2,100)
        #self.mc.setMotor(3,100)
        self.mc.setMotor(4,100)
        #self.mc.setMotor(5,100)
        # self.turn_test(90)
    	# self.mc.stopMotors()
    	# time.sleep(2)

    def turn_test(self, radius):
        counter = 0
        turn_count = utils.calc_hall_sensor_count_for_turn(radius)
        print(turn_count)
        self.turn_number(turn_count)

    def turn_number(self, turn_number):
        counter = 0
        while counter <= turn_number:
            if self.getInputs()[self.odomoter] !=  self.hall_sensor:
                self.hall_sensor = self.getInputs()[self.odomoter]
                counter += 1
            self.mc.setMotor(self.left_motor, self.current_speed)
            self.mc.setMotor(self.right_motor, -1 * self.current_speed)

    def control(self):
        print('{}\t{}'.format(self.getSensors(), self.getInputs()))
        if self.TEST_MODE:
            self._test()
        else:
            if self.getInputs()[self.bumper_left] == 1 or self.getInputs()[self.bumper_right] == 1:
                print('bumper detected')
                self.stop_motion()
                self.backward()
                self.turn_test(90)
            #self.mc.setMotor(1, -50 if self.getSensors()[0] >= 30 else 50)
        elif self.getSensors()[self.sonar_sensor] <= self.threshold_sonar:
                # self.turn_number(3)
                print('sonar detected')
                pass
            elif self.getSensors()[self.light_sensor] >= self.threshold_light:
                print('light detected')
                self.stop()
                self.servo_move(self.final_angle)
            else:
                print('run')
                self.run()

    def turn(self):
        self.current_sbackwardpeed = self.min_speed
        if self.getSensors()[self.left_ir] >= 30: # turn right
            self.mc.setMotor(self.left_motor, -1 * self.current_speed * self.direction) # left backward
            self.mc.setMotor(self.right_motor, self.current_speed * self.direction) # right forward
            time.sleep(self.threshold_turn)
        elif self.getSensors()[self.right_ir] >= 30: # turn left
            self.mc.setMotor(self.left_motor, self.current_speed * self.direction) # left forward
            self.mc.setMotor(self.right_motor, -1 * self.current_speed * self.direction) # right backward
            time.sleep(self.threshold_turn)
        else: # turn 180
            self.mc.setMotor(self.left_motor, -1 * self.current_speed * self.direction) # left backward
            self.mc.setMotor(self.right_motor, self.current_speed * self.direction) # right forward
            time.sleep(2 * self.threshold_turn)
        self.current_speed = self.base_speed

    def backward(self, turn_number=3):
        counter = 0
        while counter <= turn_number:
            if self.getInputs()[self.odomoter] !=  self.hall_sensor:
                self.hall_sensor = self.getInputs()[self.odomoter]
                counter += 1
            self.mc.setMotor(self.left_motor, -1*self.direction* self.current_speed)
            self.mc.setMotor(self.right_motor, -1*self.direction* self.current_speed)

    def stop(self):
        self.mc.stopMotors()
        print('STOPING THE MOTORS.')

    def stop_motion(self):
        self._slow_motion()
        time.sleep(0.5)
        self.mc.stopMotors()
        time.sleep(0.5)
        print('STOPING THE MOTORS USING MOTION.')

    def _slow_motion(self):
        self.current_speed =self.min_speed
        self.run()

    def run(self):
        self.mc.setMotor(self.left_motor, self.current_speed * self.direction)
        self.mc.setMotor(self.right_motor, self.current_speed * self.direction)

    def light_on(self):
    	self.mc.setMotor(self.lightbulb, 100)

    def servo_move(self, angle):
        self.sc.engage()
        self.sc.setPosition(angle)
        time.sleep(0.1)

    def vision(self):
        image = self.camera.getFrame()
        self.camera.imshow('Camera', image)
        #pass
