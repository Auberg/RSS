#!/usr/bin/env python

import time
import utils
# from examples.queue import Queue
# from queue import PriorityQueue
import heapq
#import math

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

        # MAPPING INDEX
        # motor index
        self.left_motor = 4
        self.right_motor = 5
        self.lightbulb = 1
        # analog sensor input index
        self.sonar_sensor = 6
        self.light_sensor_front = 7
        self.light_sensor_rear = 3
        self.left_ir = 4
        self.right_ir = 5
        # digital sensor input index
        self.bumper_left = 1
        self.bumper_right = 0
        self.odomoter = 7
        # Speed setting
        self.left_ratio = 1
        self.base_speed = 100
        self.min_speed = 80
        self.current_speed = self.min_speed
        self.direction = -1 #-1 forward, 1 backward
        self.turn_direction = -1 # -1 turning left, 1 right

        # SENSOR
        # Bumper sensor
        self.bumper_hit = False
        # Light sensor
        self.light_gradient_threshold_percentage = 0.5
        self.light_variance_threshold_percentage = 0.1
        self.light_initial_value_f = -1 # Need this value to be filled
        self.light_initial_value_r = -1 # Need this value to be filled
        self.light_detected_f = False
        self.light_detected_r = False
        self.poi_detected = False
        # IR sensor
        self.ir_threshold_number = 400
        # self.ir_threshold_cm = 400
        self.ir_hit = False
        # Sonar sensor
        self.sonar_threshold = 20
        self.sonar_detect = False
        # Motor setting (Including odomoter)
        self.motor_turn_break_time = 1
        self.motor_turn_angle = -1000 # Angle for turning
        self.odo_change_counter = -1000 # Counter for moving odometer movement --> backward/forward
        self._odo_counter = 0
        self.odo_cur_val = -1
        # self.turn90_odo = 5
        # self.turn180_odo = 10
        # Servo setting
        self.servo_turning_angle = -1

        # OTHER
        self.state = 0
        self.sleep_time = -1
        self.start = False
        # self.q = PriorityQueue()
        self.q = []

    def _test(self):
        #self.mc.setMotor(1, 100)elf.direction) # left back
        #self.mc.setMotor(2, 20)
        # self.mc.setMotor(4, 100)
        #self.mc.setMotor(0,100)
        #self.mc.setMotor(1,100)
        self.light_on()
        # self.mc.setMotor(self.left_motor,-100)
        #self.mc.setMotor(3,100)
        # self.mc.setMotor(self.right_motor,-100)
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
            if not self.start:
                time.sleep(2)
                self.start = True
                self._odo_counter = 0
                if self.light_initial_value_f == -1:
                    self.light_initial_value_f = self.getSensors()[self.light_sensor_front] + 1
                if self.light_initial_value_r == -1:
                    self.light_initial_value_r = self.getSensors()[self.light_sensor_rear] + 1
            # if self.q.empty():
            print('initial value: ', self.light_initial_value_f, self.light_initial_value_r)
            print(self.q)
            if self.q == []:
                self.check_bumper()
                self.check_poi()
                # self.check_ir()
                if self.q == []:
                    print('nothing ahead, forward')
                    heapq.heappush(self.q, (2, time.time(), 0, 1))
                    # self.put((2, time.time(), 0, 1))
            else:
                item = heapq.heappop(self.q)
                print('item: ', item)
                self.state = item[2]
                param = item[3]
                if self.state != -1:
                    self.update_state(self.state, 'Stopping motor')
                    time.sleep(param)
                    self.mc.stopMotors()
                elif self.state == 0:
                    print('forward')
                    self.update_state(self.state, 'Moving forward')
                    self.run()
                elif self.state == 1:
                    self.update_state(self.state, 'Moving backward')
                    self.backward(param)
                elif self.state == 2:
                    self.update_state(self.state, 'Turning count {}'.format(param))
                    self.turn_number(param)
                elif self.state == 3:
                    self.update_state(self.state, 'Turning angle {}'.format(param))
                    self.turn_radius(param)
                elif self.state == 4:
                    self.update_state(self.state, 'Moving servo {}'.format(param))
                    self.servo_move(param)
                elif self.state == 5:
                    time.sleep(param)

    def update_state(self, new_state, extra_info=''):
        if self.state == new_state:
            pass
        else:
            if extra_info != '':
                extra_info = ', ' + extra_info
            self.state = new_state
            print('Change state {} --> {}{}.'.format(self.state, new_state, 'Finish turning'))

#################
## Base action ##
#################
    def turn_radius(self, radius):
        if self.motor_turn_angle <=0:
            self.motor_turn_angle = -1000
        else:
            turn_count = utils.calc_hall_sensor_count_for_turn(motor_turn_angle)
            print('Turn count', turn_count)
            self.odo_change_counter = -1000
            self.turn_number(turn_count)

    # can be called with parameter or without
    # normally it should be called with parameter given
    def turn_number(self,number):
        if self.odo_change_counter <= 0:
            self.odo_change_counter = -1000
        else:
            if self.turn_direction * self.odo_change_counter < 0: # negative go the other way aroung (left)
                self.turn_direction *= -1
            if self.getInputs()[self.odomoter] !=  self.odo_cur_val:
                self.odo_cur_val = self.getInputs()[self.odomoter]
                self._odo_counter += 1
                self.odo_change_counter -= 1
            self.mc.setMotor(self.left_motor, self.turn_direction * self.direction * self.left_ratio * self.current_speed)
            self.mc.setMotor(self.right_motor, -1 * self.turn_direction * self.direction * self.current_speed)

    def backward(self, turn_limit):
        if self.odo_change_counter <= 0:
            self.odo_change_counter = -1000
            self.update_state(0, 'Finish moving backward')
        else:
            if self.getInputs()[self.odomoter] !=  self.odo_cur_val:
                self.odo_change_counter -= 1
                self._odo_counter += 1
                self.odo_cur_val = self.getInputs()[self.odomoter]
            self.mc.setMotor(self.left_motor, -1 * self.left_ratio * self.direction* self.current_speed)
            self.mc.setMotor(self.right_motor, -1 * self.direction* self.current_speed)
        # time.sleep(0.3*turn_limit)

    def stop_motion(self):
        print('STOPING THE MOTORS USING MOTION.')
        #slowing down
        self.current_speed = self.min_speed
        self.run()
        time.sleep(0.1)
        print('STOPING THE MOTORS.')
        self.mc.stopMotors()
        time.sleep(1)

    def run(self):
        if self.getInputs()[self.odomoter] !=  self.odo_cur_val:
            self.odo_cur_val = self.getInputs()[self.odomoter]
            self._odo_counter += 1
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
        # self.camera.imshow('Camera', image)
        #pass


###################
## Sensor action ##
###################
    def check_bumper(self):
        # if not self.bumper_hit and (self.getInputs()[self.bumper_left] == 1 or self.getInputs()[self.bumper_right] == 1):
        if self.getInputs()[self.bumper_left] == 1 or self.getInputs()[self.bumper_right] == 1:
            print('bumper detected')
            priority = 0
            self.bumper_hit = True
            heapq.heappush(self.q, (priority, time.time(), -1, 1))
            # self.q.put((priority, time.time(), -1, 1))
            # self.odo_change_counter = 5
            # self.q.put((priority, time.time(), 1, 5))
            heapq.heappush(self.q, (priority, time.time(), 1, 5))
            # self.motor_turn_angle = 90
            # self.q.put((priority, time.time(), 3, 90))
            heapq.heappush(self.q, (priority, time.time(), 3, 90))
            # self.bumper_hit = False
        else:
            # Nothing from bumper
            pass


    def check_poi(self):
        ### Front light sensor check
        if (self.getSensors()[self.light_sensor_front] - self.light_initial_value_f) / self.light_initial_value_f > self.light_gradient_threshold_percentage:
            self.light_detected_f = True
            self.current_speed = self.min_speed
            print('Light Sensor Front gradient detected')
        else:
            if self.light_detected_f:
                print('Returning light sensor rear to initial value')
            self.light_detected_f = False
        ### Rear light ensor check
        if (self.getSensors()[self.light_sensor_rear] - self.light_initial_value_r) / self.light_initial_value_r > self.light_gradient_threshold_percentage:
            self.light_detected_r = True
            print('Light Sensor Rear gradient detected')
        else:
            if self.light_detected_r:
                print('Returning light sensor rear to initial value')
            self.light_detected_r = False
        ### In PoI
        # if not self.poi_detected and self.light_detected_f and self.light_detected_r:
        if self.light_detected_f and self.light_detected_r:
            print('In the PoI')
            priority = 1
            # Define what happened here when we are in the PoI
                # For now stop 1sec, rotate X deg, move the servo, stop 10 sec, rotate 360-X again, stop 1sec DONE
            servo_angle, turn_angle = point(self.x, self.y, self.theta)
            # self.q.put((priority, time.time(), 5, 1))
            heapq.heappush(self.q, (priority, time.time(), 5, 1))
            # self.q.put((priority, time.time(), 3, turn_angle))
            heapq.heappush(self.q, (priority, time.time(), 3, turn_angle))
            # self.q.put((priority, time.time(), 4, servo_angle))
            heapq.heappush(self.q, (priority, time.time(), 4, servo_angle))
            # self.q.put((priority, time.time(), -1, 10))
            heapq.heappush(self.q,(priority, time.time(), -1, 10))
            # self.q.put((priority, time.time(), 3, 360-turn_angle))
            heapq.heappush(self.q, (priority, time.time(), 3, 360-turn_angle))
            # self.q.put((priority, time.time(), -1, 1))
            heapq.heappush(self.q, (priority, time.time(), -1, 1))
        else:
            # Nothing from PoI detection
            pass

        def check_ir(self):
            pass
