# copy/pasting several examples from https://www.geeksforgeeks.org/opencv-python-tutorial/#imagesstart

import cv2
import numpy as np
from math import cos, sin

cap = cv2.VideoCapture('/home/michi/Videos/2020-12-19 Shadow Test.mp4')
if cap.isOpened() == False:
	raise Exception("Error opening video  file")

fgbg = cv2.createBackgroundSubtractorMOG2()

# render output into file?
video = None
video = cv2.VideoWriter("out.avi", cv2.VideoWriter_fourcc(*'MJPG'), 25, (1920//2, 1080//2))

# where is the drum area?
DRUM_CENTER = (880,520)
DRUM_RADIUS = 350

# some mask...
drum_mask = np.zeros([1920,1080])#, dtype=int)
for i in range(1920):
	for j in range(1080):
		if (i - DRUM_CENTER[0])**2 + (j - DRUM_CENTER[1])**2 < DRUM_RADIUS**2:
			drum_mask[i,j] = 1

drum_mask = cv2.inRange(drum_mask.T, 0.5, 1.5)

DX0, DX1 = DRUM_CENTER[0]-DRUM_RADIUS, DRUM_CENTER[0]+DRUM_RADIUS
DY0, DY1 = DRUM_CENTER[1]-DRUM_RADIUS, DRUM_CENTER[1]+DRUM_RADIUS

view = None


frame_no = 0

while cap.isOpened():
	ret, frame = cap.read()
	if ret == True:
		fgmask = fgbg.apply(frame)
   
		if frame_no > 80:
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
				if x0 > x1:
					x0,x1 = x1,x0
					y0,y1 = y1,y0
				view = cv2.circle(view, (x0,y0), 50, (50,50,250), 20)
				print(f"{x0}:{y0}     ({len(lines)})")
			else:
				print("")
			cv2.imshow('Frame', view)

			# Press Q on keyboard to exit
			if cv2.waitKey(2) & 0xff == ord('q'):
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

