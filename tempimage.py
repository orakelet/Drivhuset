# import the necessary packages
import uuid
import os
import time

class TempImage:
	def __init__(self, basePath="/home/pi/OneDrive/Ute", ext=".jpg"):
		# construct the file path
		dateString = time.strftime("%Y%m%d-%H%M%S")
		self.path = "{base_path}/{date_String}{ext}".format(base_path=basePath,
			date_String=dateString, ext=ext)

	def cleanup(self):
		# remove the file
		os.remove(self.path)
