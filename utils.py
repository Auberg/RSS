import numpy as np
def calc_hall_sensor_count_for_turn(desired_turn_degrees, number_of_magnets=2):
  distance_each_wheel_moves = (desired_turn_degrees/360.0) * 2.0 * np.pi * 4.3
  count = distance_to_hall_sensor_count(distance_each_wheel_moves)
  return count #count should be how many times hall effect sensor changes value to get turn of input degrees.

def hall_sensor_count_to_distance(count):
  #sensor should change value 4 times per revolution of the magnets
  #gearing should make the magnets turn 5 times for each one turn of the wheels
  #wheel radius is 4.3cm
  distance_per_wheel_rotation = 2*np.pi*4.3
  distance_per_magnet_roation = distance_per_wheel_rotation / 5
  distance_per_sensor_value_change = distance_per_magnet_roation / 4
  distance_in_cm = distance_per_sensor_value_change * count
  return distance_in_cm

def distance_to_hall_sensor_count(distance):
  distance_per_wheel_rotation = 2*np.pi*4.3
  distance_per_value_change = distance_per_wheel_rotation / 20.0
  count = distance / distance_per_value_change
  return count

def point(x,y,yaw): #assumed to be measured from origin to lever arm
  goal_position = [4000, 2500, 3000] #placeholder values, replace with actual measurements, 
  robot_arm_height = 10 #placeholder value
  position = [x,y,robot_arm_height]
  orientation = [0,0,yaw] #always start with 0 pitch?
  
  relative_goal_position = goal_positioion - position
  hyp_distance = np.sqrt(relative_goal_position[0]**2 + relative_goal_position[1]**2)
  servo_angle = np.arctan(relative_goal_position[2]/hyp_distance)
  turn_angle = -1 * yaw + np.arctan(relative_goal_position[1]/relative_goal_position[0]) #kind of silly, set up to always turn in one direction. could be better.
  
  return servo_angle, turn_angle
