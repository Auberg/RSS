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
        self.left_ratio = 1
        self.base_speed = 100
        self.min_speed = 80
        self.current_speed = self.min_speed
        self.direction = -1 #-1 forward, 1 backward
        # Sensor setting
        self.threshold_sonar = 20
        self.threshold_light = 200
        self.threshold_ir = 400
        self.threshold_turn = 0.5
        self.bumper_hit = False
        self.sonar_detect = False
        # State & servo setting
        self.state = 0
        self.turning_angle = -1
        # Start required
        self.counter = 0
        self.turn_limit = 0

    def _test(self):
        #self.mc.setMotor(1, 100)elf.direction) # left back
        #self.mc.setMotor(2, 20)
        # self.mc.setMotor(4, 100)
        #self.mc.setMotor(0,100)
        #self.mc.setMotor(1,100)
        self.light_on()
        self.mc.setMotor(self.left_motor,-100)
        #self.mc.setMotor(3,100)
        self.mc.setMotor(self.right_motor,-100)
        #self.mc.setMotor(5,100)
        # self.turn_test(90)
    	# self.mc.stopMotors()
    	# time.sleep(2)

    def control(self):
        print('{}\t{}'.format(self.getSensors(), self.getInputs()))
        if self.TEST_MODE:
            self._test()
        else:
            self.light_on()
            if self.state != -1:
                if self.state == 0: # check for situation and move forward
                    self.check_bumper()
                    self.check_sonar()
                    self.check_light()
                    if self.state == 0:
                        self.run()
                if self.state == 1:
                    self.backward()
                if self.state == 2:
                    self.turn_number()
                if self.state == 3:
                    self.mc.stopMotors()
                    self.state = 0
            else:
                self.ms.stopMotors()

            # in the sonar range
            elif self.getSensors()[self.sonar_sensor] <= self.threshold_sonar:
                # self.turn_number(3)
                print('sonar detected')
                self.stop_motion()
                self.backward( )
                self.mc.stopMotors()
            # light sensor detect poi
            elif self.getSensors()[self.light_sensor] >= self.threshold_light:
                print('light detected')
                self.mc.stopMotors()
                self.servo_move(self.final_angle)
            else:
                print('run')
                self.run()

    def check_bumper(self):
        if self.getInputs()[self.bumper_left] == 1 or self.getInputs()[self.bumper_right] == 1:
            print('bumper detected')
            self.mc.stopMotors()
            self.bumper_hit = True
            self.turn_limit = 5
            self.turning_angle = 180
            self.state == 1
        elif self.bumper_hit:
            if self.turn_limit > 0:
                self.state == 1
            elif self.turning_angle != -1:
                self.state == 2
            elif self.turn_limit == 0 and self.turning_angle == -1:
                self.bumper_hit = False
            else:
                print('B02: Undetected error for bumper')
        else:
            print('B01: Undetected error for bumper')

    def check_sonar(self):
        if self.getSensors()[self.sonar_sensor] <= self.threshold_sonar:
            print('sonar detected')
            self.mc.stopMotors()
            self.sonar_detect = True
            self.turn_limit = 3
            self.turning_angle = 180
            self.state == 1
        elif self.sonar_detect:
            if self.turn_limit > 0:
                self.state == 1
            elif self.turning_angle != -1:
                self.state == 2
            elif self.turn_limit == 0 and self.turning_angle == -1:
                self.sonar_detect = False
            else:
                print('S02: Undetected error for Sonar')
        else:
            print('S01: Undetected error for Sonar')

    def turn_radius(self, radius):
        counter = 0
        turn_count = utils.calc_hall_sensor_count_for_turn(radius)
        print(turn_count)
        self.turn_number(turn_count)

    def turn_number(self):
        if self.turn_limit == 0:
            self.turning_angle == -1
            self.state = 0
        else:
            if self.getInputs()[self.odomoter] !=  self.hall_sensor:
                self.hall_sensor = self.getInputs()[self.odomoter]
                self.turn_limit -= 1
            self.mc.setMotor(self.left_motor, self.left_ratio * self.current_speed)
            self.mc.setMotor(self.right_motor, -1 * self.current_speed)

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
        self.current_speed = self.min_speed

    def backward(self, turn_limit=3):
        counter = 0
        while counter <= turn_limit:
            if self.getInputs()[self.odomoter] !=  self.hall_sensor:
                self.hall_sensor = self.getInputs()[self.odomoter]
                counter += 1
            self.mc.setMotor(self.left_motor, -1 * self.left_ratio * self.direction* self.current_speed)
            self.mc.setMotor(self.right_motor, -1 * self.direction* self.current_speed)
        time.sleep(0.3*turn_limit)

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
        left_speed = self.left_ratio * self.current_speed * self.direction
        right_speed = self.current_speed * self.direction
        self.mc.setMotor(self.left_motor, left_speed)
        self.mc.setMotor(self.right_motor, right_speed)

    def light_on(self):
    	self.mc.setMotor(self.lightbulb, 100)

    def servo_move(self, angle):
        self.sc.engage()
        self.sc.setPosition(angle)
        time.sleep(1)

    def vision(self):
        image = self.camera.getFrame()
        self.camera.imshow('Camera', image)
        #pass
