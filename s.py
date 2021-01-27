# copy/pasting several examples from https://www.geeksforgeeks.org/opencv-python-tutorial/#imagesstart

# ahhhhh, why does opencv flip x/y???

import cv2
import numpy as np
import sys
import argparse
import os
from math import cos, sin

parser = argparse.ArgumentParser(description='Schattenspiel oder so ähnlich')
parser.add_argument('--source', help='select a video source file')

args = parser.parse_args()






def start_video(source):
	global NX, NY, cap, fgbg
	if source:
		print("loading file")
		cap = cv2.VideoCapture(args.source)
	else:
		print("using camera")
		cap = cv2.VideoCapture(0)
	if cap.isOpened() == False:
		raise Exception("Error opening video  file")

	ret, frame = cap.read()
	NY, NX, _ = frame.shape
	print(NX,NY)


	fgbg = cv2.createBackgroundSubtractorMOG2()





def load_config():
	global DRUM_CENTER, DRUM_RADIUS, STICK_POINT
	# where is the drum area?
	DRUM_CENTER = (NX//2, NY//2)
	DRUM_RADIUS = 150
	STICK_POINT = "left"
	if not os.path.isfile("config.txt"):
		print("no config.txt found")
	with open("config.txt") as f:
		for line in f:
			x = line.split("=")
			if len(x) < 2:
				continue
			key, value = x[0].strip(), x[1].strip()
			if key == "drum.x":
				DRUM_CENTER = (int(value), DRUM_CENTER[1])
			elif key == "drum.y":
				DRUM_CENTER = (DRUM_CENTER[0], int(value))
			elif key == "drum.radius":
				DRUM_RADIUS = int(value)
			elif key == "stick.point":
				assert(value in ["left", "right"])
				STICK_POINT = value
			else:
				raise Exception("unknown config key: " + key)


def prepare_drum_mask():
	global drum_mask, DX0, DX1, DY0, DY1

	# some mask...
	drum_mask = np.zeros([NX,NY], dtype=np.int8)
	for i in range(NX):
		for j in range(NY):
			if (i - DRUM_CENTER[0])**2 + (j - DRUM_CENTER[1])**2 < DRUM_RADIUS**2:
				drum_mask[i,j] = 1

	drum_mask = cv2.inRange(drum_mask.T, 0.5, 1.5)

	DX0, DX1 = DRUM_CENTER[0]-DRUM_RADIUS, DRUM_CENTER[0]+DRUM_RADIUS
	DY0, DY1 = DRUM_CENTER[1]-DRUM_RADIUS, DRUM_CENTER[1]+DRUM_RADIUS




start_video(args.source)
load_config()
prepare_drum_mask()


# render output into file?
video = None
#video = cv2.VideoWriter("out.avi", cv2.VideoWriter_fourcc(*'MJPG'), 25, (1920//2, 1080//2))





print("press Q or ESC to quit")

view = None


frame_no = 0

while cap.isOpened():
	ret, frame = cap.read()
	if ret == True:
		fgmask = fgbg.apply(frame)
   
		if frame_no > -80:
			#fg = fgmask * drum_mask.T
			fg = cv2.bitwise_or(fgmask, fgmask, mask=drum_mask)
			lines = cv2.HoughLinesP(fg[DY0:DY1,DX0:DX1], 1, np.pi/18, 300, 100)

			view = np.stack([fgmask, fgmask, fgmask], axis=2)
			view = cv2.circle(view, DRUM_CENTER, DRUM_RADIUS, (180, 50,50), 5)
			
			# argh, implementation got removed... \(T_T)/
			#lsd = cv2.createLineSegmentDetector(0)
			#lines = lsd.detect(fg)
			#print(lines)
			
			if lines is not None:
				x0,y0,x1,y1 = lines[0][0]
				x0,y0,x1,y1 = x0+DX0,y0+DY0,x1+DX0,y1+DY0
				view = cv2.line(view, (x0,y0), (x1,y1), (50,200,200), 8)
				if STICK_POINT == "left":
					if x0 > x1:
						x0,x1 = x1,x0
						y0,y1 = y1,y0
				elif STICK_POINT == "right":
					if x1 > x0:
						x0,x1 = x1,x0
						y0,y1 = y1,y0
				view = cv2.circle(view, (x0,y0), 50, (50,50,250), 20)
#				print(f"{x0}:{y0}     ({len(lines)})")
#			else:
#				print("")
			cv2.imshow('Frame', view)

			# Press Q on keyboard to exit
			if cv2.waitKey(2) & 0xff in [ord('q'), 0x1b]:
				break
		
		if video and view is not None:
			video.write(view[::2,::2,:])
		
		frame_no += 1

	else:
		break

if video:
	video.release()

cap.release()

cv2.destroyAllWindows()

