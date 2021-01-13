#! /usr/bin/env python

import rospy
#import statistics
#from statistics import mean
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist

#================================================#
class SafeTeleop:
	def __init__(self):
		rospy.Subscriber('/scan', LaserScan, self.scan_cb)
#		rospy.Subscriber('/cmd_vel_in', Twist, self.cmd_vel_cb)
		self.pub_cmd = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
		self.scans = LaserScan()
		self.cmd_in = Twist()
		self.cmd_out = Twist()

	def cmd_vel_cb(self, msg):
		self.cmd_in = msg

	def scan_cb(self, msg):
		self.scans = msg

	def update(self):
		n = len(self.scans.ranges)
		ang_inc = self.scans.angle_increment #fonction wiki ros hokuyo node
		milieu = self.scans.angle_max /2 #fonction wiki ros hokuyo node
		portee = 0.8
		sec_dist = 0.5
		kd = 1
		kp = 1.4
		k = 4 #une des roues est moins rapide que l'autre pour tourner
				
		target = False
		#print(self.compteur)
		i = 0
		for item in self.scans.ranges:
					
			if item <= portee:
				dist_target = item
				target = True
				indice_angle_target = i
				break
			else:
				target = False
				i += 1
		
		#	print(i)

		if target:
			
			target_angle = indice_angle_target * ang_inc
			
			print("angle milieu:",milieu) 
			print("angle cible :",target_angle)
			
			if target_angle > milieu : #si l orientation de la cible est a gauche du robot celui tourne a gauche pour la suivre
				Vrot = 1	 		
			elif target_angle < milieu: #si l orientation de la cible est a droite du robot celui tourne a droite pour la suivre
				Vrot = -1*k
			else:
				Vrot = 0 
		
			if dist_target<=portee and dist_target>sec_dist: #lorsque la distance de la cible est comprise entre la distance de securite et la portee du lidar hokuyo
				Vlin = .5
			if dist_target<=sec_dist:
				Vlin = 0
				Vrot = 0

			print("la distance a la cible est :", dist_target)
			
			self.cmd_out.angular.z = Vrot*abs(milieu-target_angle)* kd #il regle la vitesse angulaire
			self.cmd_out.linear.x = Vlin #il avance	
				
			self.cmd_out = self.cmd_in	
		else:
			self.cmd_out.linear.x = 0.0
			self.cmd_out.angular.z = 0.0
		
	

		self.pub_cmd.publish(self.cmd_out)
		
		#========================#


#================================================
rospy.init_node('evitement_node')
node = SafeTeleop()
r = rospy.Rate(10)
while not rospy.is_shutdown():
	node.update()
	r.sleep()

