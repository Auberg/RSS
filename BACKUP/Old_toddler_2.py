#!/usr/bin/env python

import time
import utils
import math

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
        self.left_motor = 4
        self.right_motor = 5
        self.lightbulb = 2
        # digital sensor input index
        self.bumper_left = 1
        self.bumper_right = 0
        self.odomoter = 7
        # digital sensor input index
        self.sonar_sensor = 6
        self.light_sensor = 7
        self.left_ir = 4
        self.right_ir = 5
        # Speed setting
        self.left_ratio = 1
        self.base_speed = 100
        self.min_speed = 100
        self.current_speed = self.min_speed
        self.direction =1 #-1 forward, 1 backward
        # Sensor setting
        self.threshold_sonar = 20
        #self.threshold_light = 200
	self.threshold_light = 140
        self.threshold_ir = 400
        self.threshold_turn = 0.5
        # State & servo setting
        self.state = 0
        self.stateArray = [0,1,2,3]
        self.final_angle = 90
        # Start required
        self.hall_sensor = -1
        self.counter = 0
	self.back_counter = 0
	self.hit_wall = 0
	self.able_to_run = True
	self.light_on()

    def _test(self):
        #self.mc.setMotor(1, 100)elf.direction) # left back
        #self.mc.setMotor(0, 100)
        #self.mc.setMotor(1, 100)
        #self.mc.setMotor(2, 100)
        #self.mc.setMotor(3, 100)
      	#self.mc.setMotor(4, 100)
        #self.mc.setMotor(5, 100)
	#self.turn_radius(180-40)
	#x = 180
	#self.light_on()
        #self.part3_test(0,0,90)
	#self.turn_radius(90)
	self.light_on()
	if self.able_to_run:
		if self.getSensors()[self.light_sensor] >= self.threshold_light:
			print('light detected')
			self.mc.stopMotors()
			self.able_to_run = False
		else:
			self.run()
	pass

    def control(self):
        print('{}\t{}'.format(self.getSensors(), self.getInputs()))
        if self.TEST_MODE:
            self._test()
        else:
            self.light_on()
    	    if self.able_to_run:
    		    if self.getSensors()[self.light_sensor] >= self.threshold_light:
    		        print('light detected')
			        self.able_to_run = False
    		        self.mc.stopMotors()
    		        #self.part3_test( 0, 0, 90)
    		    elif self.hit_wall >= 1 :
    			self.backward(turn_limit=10)
    		    elif self.getInputs()[self.bumper_left] == 1 or self.getInputs()[self.bumper_right] == 1:
    		        print('bumper detected')
                    self.hit_wall = 1
    		    #self.mc.setMotor(1, -50 if self.getSensors()[0] >= 30 else 50)
                elif self.getSensors()[self.sonar_sensor] <= self.threshold_sonar:
    		        # self.turn_number(3)
    		        print('sonar detected')
    			#self.hit_wall = 1
                else:
    		        print('run')
    		        self.run()
            else:
                print('cannot run')

    def turn_radius(self, radius):

        turn_count = utils.calc_hall_sensor_count_for_turn(radius)
        print(turn_count)
        self.turn_number("Turn Count = " + str(turn_count))

    def turn_number(self, turn_number):
        if self.counter <= turn_number:
            if self.getInputs()[self.odomoter] !=  self.hall_sensor:
                self.hall_sensor = self.getInputs()[self.odomoter]
                self.counter += 1
            self.mc.setMotor(self.left_motor, self.direction * self.current_speed)
            self.mc.setMotor(self.right_motor, self.direction * -1 * self.current_speed)
	else :
	    self.hit_wall = 0
	    self.counter = 0
	    self.back_counter = 0
	    self.mc.stopMotors()

    def turn(self):
        self.current_sbackwardpeed = self.min_speed
        if self.getSensors()[self.right_ir] <= self.threshold_ir: # turn right
            self.mc.setMotor(self.left_motor, -1 * self.left_ratio * self.current_speed * self.direction) # left backward
            self.mc.setMotor(self.right_motor, self.current_speed * self.direction) # right forward
            time.sleep(self.threshold_turn)
        elif self.getSensors()[self.left_ir] <= self.threshold_ir: # turn left
            self.mc.setMotor(self.left_motor, self.left_ratio * self.current_speed * self.direction) # left forward
            self.mc.setMotor(self.right_motor, -1 * self.current_speed * self.direction) # right backward
            time.sleep(self.threshold_turn)
        else: # turn 180
            self.mc.setMotor(self.left_motor, -1 * self.left_ratio * self.current_speed * self.direction) # left backward
            self.mc.setMotor(self.right_motor, self.current_speed * self.direction) # right forward
            time.sleep(2*self.threshold_turn)
        self.current_speed = self.base_speed

    def backward(self, turn_limit=3):
        if self.back_counter <= turn_limit:
            if self.getInputs()[self.odomoter] !=  self.hall_sensor:
                self.hall_sensor = self.getInputs()[self.odomoter]
                self.back_counter += 1
            self.mc.setMotor(self.left_motor, self.direction * -1 * self.current_speed)
            self.mc.setMotor(self.right_motor, self.direction * -1 * self.current_speed)
	else :
	    self.mc.stopMotors()


    def stop_motion(self):
        print('STOPING THE MOTORS USING MOTION.')
        #slowing down
        self.current_speed =self.min_speed
        self.run()
        time.sleep(0.15)
        print('STOPING THE MOTORS.')
        self.mc.stopMotors()
        time.sleep(1)

    def run(self):
        self.mc.setMotor(self.left_motor, self.left_ratio * self.current_speed * self.direction)
        self.mc.setMotor(self.right_motor, self.current_speed * self.direction)
        #testing stright direction
        #time.sleep(0.85)
        #self.mc.stopMotors()
        #time.sleep(0.15)


    def alt_backwards(self):
	self.mc.setMotor(self.left_motor,self.direction * -1 * self.current_speed)
        self.mc.setMotor(self.right_motor,self.direction * -1 * self.current_speed)

    def light_on(self):
    	self.mc.setMotor(self.lightbulb, 100)

    def servo_move(self, angle):
        self.sc.engage()
        self.sc.setPosition(angle)


    def vision(self):
        image = self.camera.getFrame()
        self.camera.imshow('Camera', image)
        #pass

    def part3_test(self, x, y, orientation):
        servo_angle, turn_angle, direction = utils.point(x,y,orientation)
	print(servo_angle* 180/ math.pi)
	print( turn_angle )
	self.turn_radius(turn_angle)
        self.servo_move(180 - servo_angle* 180/ math.pi)
