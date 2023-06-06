from djitellopy import Tello
import cv2
import numpy as np

#Callback for trackbar function
def callback(x):
	pass

#Connecting to drone
drone = Tello()
#drone.connect()
#Window
height = 500
width = 500
deadzone = 100
#Define the initial speed
in_speed = 60
#Area
area_min = 3000
area_centro1 = 10000
area_centro2 = 25000

#HSV initial values
H_min = 98  #0
H_max = 125  #180
S_min = 100  #0
S_max = 255  #255
V_min = 70   #0
V_max = 255  #255
hsv_min = np.array([H_min, S_min, V_min]) 
hsv_max = np.array([H_max, S_max, V_min])
#direccion de tracking
direccion = 0
#Drone speeds
drone.left_right_velocity = 0
drone.for_back_velocity = 0
drone.up_down_velocity = 0
drone.yaw_velocity = 0
#Initializing camera stream
#drone.streamoff()
#drone.streamon()

#Obtener contornos
def getContours (img,img_tracking):
	contours, hierachy=cv2.findContours(img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
	global direccion
	mylistC = []
	mylistArea = []

	for c in contours:
		#calcular area
		area= cv2.contourArea(c)
		#print(area)
		if(area>area_min):
			per = cv2.arcLength(c,True)
			approx = cv2.approxPolyDP(c, 0.02*per, True)
			x, y, w, h = cv2.boundingRect(approx)
			cx = int (x + (w/2))
			cy = int (y + (h/2))
			area = w*h
			mylistC.append([cx,cy])
			mylistArea.append(area)
			#mostrar imagen
			cv2.drawContours(img_tracking, [c], -1,(255,0,255),thickness=3)
			cv2.putText(img_tracking, 'cx: ' + str(cx), (width-495,height-480),cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 255, 0),2)
			cv2.putText(img_tracking, 'cy: ' + str(cy), (width-495,height-450),cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 255, 0),2)
			cv2.circle(img_tracking,(cx,cy),5,(255,0,0),cv2.FILLED)
			cv2.line(img_tracking, ((width//2),(height//2)), (cx,cy),(0, 0, 255), 2)
			
			#control de movimiento
			if cx<((width//2)-deadzone) and cy>((height//2)-deadzone) and cy<((height//2)+deadzone):
				cv2.rectangle(img_tracking,(0,((height//2)-deadzone)),((width//2)-deadzone,(height//2)+deadzone),(0,0,255),cv2.FILLED)
				direccion= 1
			elif cx>((width//2)+deadzone) and cy>((height//2)-deadzone) and cy<((height//2)+deadzone):
				cv2.rectangle(img_tracking,((width//2)+deadzone,((height//2)-deadzone)),(width,(height//2)+deadzone),(0,0,255),cv2.FILLED)
				direccion=2
			elif cy<((height//2)-deadzone) and cx>((width//2)-deadzone) and cx<((width//2)+deadzone):
				cv2.rectangle(img_tracking,((width//2)-deadzone,0),((width//2)+deadzone,(height//2)-deadzone),(0,0,255),cv2.FILLED)
				direccion= 3
			elif cy>((height//2)+deadzone) and cx>((width//2)-deadzone) and cx<((width//2)+deadzone):
				cv2.rectangle(img_tracking,((width//2)-deadzone,(height//2)+deadzone),((width//2)+deadzone,height),(0,0,255),cv2.FILLED)
				direccion=4

			elif area < area_centro1:
				direccion=5
			elif area > area_centro1 and area < area_centro2:
				direccion=6
			elif area > area_centro2:
				direccion=7
		else:
			direccion = 0
	
	#trazar lineas
	cv2.line(img_tracking,((width//2)-deadzone,0),((width//2)-deadzone,width),(255,255,0),2)
	cv2.line(img_tracking,((width//2)+deadzone,0),((width//2)+deadzone,width),(255,255,0),2)
	cv2.line(img_tracking,(0,(height//2)-deadzone),(height,(height//2)-deadzone),(255,255,0),2)
	cv2.line(img_tracking,(0,(height//2)+deadzone),(height,(height//2)+deadzone),(255,255,0),2)
	cv2.circle(img_tracking,(height//2,width//2),5,(255,0,0),cv2.FILLED)

	if len(mylistArea)!= 0:
		i=mylistArea.index(max(mylistArea))
		return (img_tracking , [mylistC[i],mylistArea[i]])
	else:
		return img_tracking, [[0,0],0]
	

def teclado(key):
	lr, fb, ud, yv = 0, 0, 0, 0

	if key == 119: #w
		fb = speed	 
	elif key == 115: #s
		fb = -speed

	if key == 97: #a
		lr = -speed
	elif key == 100: #d
		lr = speed

	if key == 82: #up
		ud = speed
	elif key == 84: #down
		ud = -speed
	
	if key == 81: #left
		yv = -speed
	elif key == 83: #right
		yv = speed 

	if key == 116: #t
		drone.takeoff()
	elif key== 108: #l
		drone.land()

	if key == 122: #z
		drone.flip_forward()
	elif key== 120: #x
		drone.flip_back()
	if key == 99: #c
		drone.flip_left()
	elif key== 118: #v
		drone.flip_right()
	
	drone.send_rc_control(lr, fb, ud, yv)
		
capture = cv2.VideoCapture(0)
#Create and configure a window for Trackbar
cv2.namedWindow('Trackbar')
cv2.resizeWindow('Trackbar',(height,width))
#Create the trackbar for the speed value
cv2.createTrackbar('Speed', 'Trackbar', 0, 100, callback)
cv2.createTrackbar('H min', 'Trackbar', 0, 180, callback)
cv2.createTrackbar('H max', 'Trackbar', 0, 180, callback)
cv2.createTrackbar('S min', 'Trackbar', 0, 255, callback)
cv2.createTrackbar('S max', 'Trackbar', 0, 255, callback)
cv2.createTrackbar('V min', 'Trackbar', 0, 255, callback)
cv2.createTrackbar('V max', 'Trackbar', 0, 255, callback)
#Set initial values for the speed
cv2.setTrackbarPos('Speed','Trackbar', in_speed)
cv2.setTrackbarPos('H min','Trackbar', H_min)
cv2.setTrackbarPos('H max','Trackbar', H_max)
cv2.setTrackbarPos('S min','Trackbar', S_min)
cv2.setTrackbarPos('S max','Trackbar', S_max)
cv2.setTrackbarPos('V min','Trackbar', V_min)
cv2.setTrackbarPos('V max','Trackbar', V_max)

def main():
	print("main program inicialized")
	i=0
	while True:
		#Obtaining a new frame --- return,ImageName = capture.read() --- return = 0 no frame recieved
		#From webcam
		ret, img = capture.read()

		#From Tello
		#frame_read = drone.get_frame_read()
		#img = frame_read.frame

		img = cv2.flip(img,1)
		img = cv2.resize(img,(height,width))
		img_tracking = img.copy()
		
		#Reading HSV and speed from trackbar
		global speed
		speed = cv2.getTrackbarPos('Speed', 'Trackbar')
		H_max = cv2.getTrackbarPos('H max', 'Trackbar')
		H_min = cv2.getTrackbarPos('H min', 'Trackbar')
		S_max = cv2.getTrackbarPos('S max', 'Trackbar')
		S_min = cv2.getTrackbarPos('S min', 'Trackbar')
		V_max = cv2.getTrackbarPos('V max', 'Trackbar')
		V_min = cv2.getTrackbarPos('V min', 'Trackbar')

		#Convert to HSV Color Space
		hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
		#Mask color
		hsv_min = np.array([H_min, S_min, V_min]) 
		hsv_max = np.array([H_max, S_max, V_max])
		mask = cv2.inRange(hsv_img, hsv_min, hsv_max)
		mask = cv2.erode(mask,None,iterations=3)
		mask = cv2.dilate(mask,None,iterations=3)
		result = cv2.bitwise_and(img,img,mask = mask) 
	
		#Getting contours and object position
		imgBlur = cv2.GaussianBlur(result,(7,7),1)
		imgGray = cv2.cvtColor(imgBlur,cv2.COLOR_BGR2GRAY)
		imgCanny = cv2.Canny(imgGray,166, 171)
		
		img, info = getContours(imgGray,img_tracking)

		print("Center: ", info[0], "Area: ", info[1])
		#Writing in the image.... cv2.putText(ImageName, text, location, font, scale, color, thickness)
		cv2.putText(img_tracking, "speed: "+str(speed) ,(width-120,height-480),cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0,255,0),2)

		#moviendo el drone
		if direccion ==1:
			drone.yaw_velocity = speed
			cv2.putText(img_tracking, 'R L', (width-495,height-50),cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 255, 0),2)
		elif direccion == 2:
			drone.yaw_velocity= -speed
			cv2.putText(img_tracking, 'R R', (width-495,height-50),cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 255, 0),2)
		elif direccion == 3:
			drone.up_down_velocity= speed
			cv2.putText(img_tracking, 'UP', (width-495,height-50),cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 255, 0),2)
		elif direccion == 4:
			drone.up_down_velocity= -speed
			cv2.putText(img_tracking, 'DOWN', (width-495,height-50),cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 255, 0),2)
		elif direccion == 5:
			drone.for_back_velocity = speed
			cv2.putText(img_tracking, 'Forward', (width-495,height-10),cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 255, 0),2)
		elif direccion == 6:
			drone.left_right_velocity = 0
			drone.for_back_velocity = 0
			drone.up_down_velocity = 0 
			drone.yaw_velocity = 0
			cv2.putText(img_tracking, 'Area in the range', (width-495,height-10),cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 255, 0),2)
		elif direccion == 7:
			drone.for_back_velocity = -speed
			cv2.putText(img_tracking, 'Back', (width-495,height-10),cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 255, 0),2)
		else:
			drone.left_right_velocity = 0
			drone.for_back_velocity = 0
			drone.up_down_velocity = 0 
			drone.yaw_velocity = 0
			cv2.putText(img_tracking, 'STOP', (width-495,height-50),cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 255, 0),2)

		drone.send_rc_control(drone.left_right_velocity, drone.for_back_velocity, drone.up_down_velocity, drone.yaw_velocity)
		#window
		mask = cv2.cvtColor(mask,cv2.COLOR_GRAY2BGR)
		hor = np.hstack([img,mask,result])
		#hor1 = np.hstack([result,img_tracking])
		#ver = np.vstack([hor,hor1]) 
		cv2.imshow("Frame",hor)
		#cv2.imshow("Image",img_tracking)
		key=cv2.waitKey(50) & 0xFF
		#print(key)

		teclado(key)

		#Moving the Tello drone
		if key == 113: #q
			cv2.destroyAllWindows()
			break
		
try:
	main()

except KeyboardInterrupt:
	print('KeyboardInterrupt exception is caught')
	print("landing")
	#drone.land()
	cv2.destroyAllWindows()

else:
	print('No exceptions are caught')
