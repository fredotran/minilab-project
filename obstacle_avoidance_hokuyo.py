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
		rospy.Subscriber('/cmd_vel_in', Twist, self.cmd_vel_cb)
		self.pub_cmd = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
		self.scans = LaserScan()
		self.cmd_in = Twist()
		self.cmd_out = Twist()


	def cmd_vel_cb(self, msg):
		self.cmd_in = msg

	def scan_cb(self, msg):
		self.scans = msg

	def update(self):
		safe_drive = True
		for item in self.scans.ranges:
			if item < 0.40:
				safe_drive = False
				break
			else:
				safe_drive = True
		
		#========================#
		if (not safe_drive):
			n = len(self.scans.ranges)

			gauche = self.scans.ranges[0:n//3] #on recupere les valeurs de ranges comprises entre 0 et le tier total des valeurs de ranges
			milieu = self.scans.ranges[n//3:2*n//3] #on recupere les valeurs de ranges comprises entre le tier et le deux-tiers total des valeurs de ranges
			droite = self.scans.ranges[2*n//3:n-1] #on recupere les valeurs de ranges comprises entre deux-tiers et le (total-1) des valeurs de ranges
			
			# calcul des moyennes des distances de gauche
			moy_g = 0
			for i in gauche:
				moy_g += i
				moy_g = moy_g/len(gauche)
			# calcul des moyennes des distances de droite
			moy_d = 0
			for i in droite:
				moy_d+=i
				moy_d = moy_d/len(droite)
				mini = abs(min(gauche))
				
			# recherche de la distance mini détectée
			mini_g = True # par défaut on suppose qu'elle se trouve dans la liste gauche
			
			if mini > abs(min(droite)): # si il existe une distance plus petite à droite on met à jour la distance mini
				mini_g = False
				mini = min(droite)
			
			if mini > min(milieu):  # si il existe une distance plus petite au milieu on met à jour la distance mini
				if min(milieu)*moy_g > min(milieu)*moy_d:   # Si la moyenne des distances à droite est plus petite que la moyenne à gauche, on tourne vers la gauche
					mini_g = False
					mini = min(milieu)
			
			if mini_g: #tourne à droite
				Vrot = 0.6
			else: #tourne à gauche
	  			Vrot = -0.6
			
			if self.cmd_in.linear.x > 0.0:   # pour éviter de percuter un obstacle, le robot s'arrête et effectue une rotation dans la zone la plus libre
				self.cmd_out.linear.x = 0.0
				self.cmd_out.angular.z = Vrot

				 
			else:
				self.cmd_out = self.cmd_in
		else:
			self.cmd_out = self.cmd_in

		self.pub_cmd.publish(self.cmd_out)

#================================================
rospy.init_node('evitement_node')
node = SafeTeleop()
r = rospy.Rate(10)
while not rospy.is_shutdown():
	node.update()
	r.sleep()

