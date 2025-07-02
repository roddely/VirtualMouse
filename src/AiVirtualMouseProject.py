import cv2
import mediapipe as mp
import time
import handTrackingModule as htm
import numpy as np
import autopy
import pyautogui

cap = cv2.VideoCapture(0)
########################################
wCam, hCam = 640, 480
frameR = 100  # Frame Reduction for faster processing
smoothening = 7  # Smoothing factor for mouse movement  
########################################
prevX, prevY = 0, 0  # Previous mouse coordinates
currX, currY = 0, 0  # Current mouse coordinates

cap.set(3, wCam)
cap.set(4, hCam)

scale = None
cTime = 0
pTime = 0
win_tab_btn = False  # Track if Win+Tab is pressed

# Variables for fist detection
previouseTime = 0
fistTime = 0 # Time when fist was detected
handState = "open" 
fist_at_the_same_time = False  # Track if fist is detected at the same time

#Variables for swipe up and down
previousePos = []
detector = htm.HandDetector(maxHands=1)
wScreen, hScreen = autopy.screen.size()  # Get screen size
mouse_down = False  # Track mouse button state

# Variable to skip the block of code
skip_block = False 

while True:
    cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Image", 1280, 960)  # Resize the window to match camera resolution
    cv2.setWindowProperty("Image", cv2.WND_PROP_TOPMOST, 1) # Make the window always on top
    # Find Hand Landmarks
    success, img = cap.read()
    img, found = detector.findHands(img)
    lmList, bbox, handType = detector.findPosition(img)

    #Detect the scale of bbox
    
    scale = detector.get_bbox_scale(bbox)
    # Check which fingers are up
    fingers = detector.fingerUp(lmList, handType)
    # print(fingers)
    cv2.rectangle(img, (frameR, frameR - 30), (wCam - frameR, hCam - frameR - 30), (0, 0, 255), 2)
    #Scroll up and down with thumb and index finger (fist hand)
    if fingers[0] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
        length, img, lineInfo = detector.findDistance(4, 8, img)
        if length < 30*scale:
            if len(previousePos) == 0:
                previousePos.append(lmList[8][1])  # Store the x-axis position of the index finger
                previousePos.append(lmList[8][2])  # Store the y-axis position of the index finger
            if lmList[8][1] < previousePos[0]:
                pyautogui.keyDown('shift') 
                pyautogui.scroll(100)  # Scroll left
                pyautogui.keyUp('shift')
            if lmList[8][1] > previousePos[0]:
                pyautogui.keyDown('shift')
                pyautogui.scroll(-100)  # Scroll right
                pyautogui.keyUp('shift')
            if lmList[8][2] < previousePos[1]: 
                pyautogui.scroll(100)  # Scroll up
            if lmList[8][2] > previousePos[1]:
                pyautogui.scroll(-100)  # Scroll down

            skip_block = True  # Skip the rest of the code in this iteration
        else:
            skip_block = False
            previousePos.clear()  # Clear the previous position if the fingers are not close enough
    
    # print(skip_block)
                
    # Moving mode
    if fingers[1] == 1 and skip_block == False:
        x1, y1 = lmList[8][1], lmList[8][2]
        x2, y2 = lmList[12][1], lmList[12][2]
        # Convert Coordinates
        x3 = np.interp(x1, (frameR, wCam-frameR), (0, wScreen))
        y3 = np.interp(y1, (frameR, hCam-frameR), (0, hScreen))
        # Smoothen Values
        currX = prevX + (x3 - prevX) / smoothening
        currY = prevY + (y3 - prevY) / smoothening
        # Move Mouse
        autopy.mouse.move(currX, currY)
        cv2.circle(img, (x1, y1), 15, (0, 255, 255), cv2.FILLED)

        prevX, prevY = currX, currY  # Update previous coordinates
    # Clicking mode (index and middle fingers up)
    if fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 1 and skip_block == False:
        #Find distance between index and middle finger
        length, img, lineInfo = detector.findDistance(8, 12, img)
        #If distance is short enough, click mouse
        if length < 30* scale:
            cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
            autopy.mouse.click(button=autopy.mouse.Button.LEFT)
    # Only index and middle fingers up: toggle mode
    if fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0 and fingers[4] == 0 and skip_block == False:
        # Find distance between fingers
        length, img, lineInfo = detector.findDistance(8, 12, img)
        # Click mouse if distance is short enough
        if length < 30* scale:
            cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
            if not mouse_down:
                autopy.mouse.toggle(autopy.mouse.Button.LEFT, True)
                mouse_down = True     
        else:
            if mouse_down:
                autopy.mouse.toggle(autopy.mouse.Button.LEFT, False)
                mouse_down = False
    #Right click: thumb and index (open hand)
    if fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 1 and skip_block == False:
        length, img, lineInfo = detector.findDistance(4, 5, img)
        thumb_angel = detector.findAngel(
                (lmList[4][1], lmList[4][2]),  # Tip of thumb
                (lmList[3][1], lmList[3][2]),  # PIP of thumb
                (lmList[2][1], lmList[2][2])   # MCP of thumb   
            )
        # print(length)
        if length < 50* scale and thumb_angel < 150:
            cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 0, 255), cv2.FILLED)
            autopy.mouse.click(button=autopy.mouse.Button.RIGHT)

    #Fist hand - open hand (minimize all windows)
    if fistTime == 0:
        fistTime = time.time()
    if fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 1 and (time.time() - fistTime > 0.5):
        handState = "open"
        skip_block = False  # Reset skip block when hand is open
        if previouseTime!= 0:
            fistTime = previouseTime  # Reset fist time when hand is open
        previouseTime = time.time()
        fist_at_the_same_time = True
        # print(handState)
        # print(time.time() - fistTime)
    if fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0 and handState == "open" and found == True:
        fist_at_the_same_time = False
        skip_block = True  # Skip the rest of the code in this iteration
        # continue
    if fingers[1] == 0 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0 and handState == "open" and found == True and fist_at_the_same_time == True and skip_block == False:
        handState = "fist"
        # print(time.time() - fistTime)
        # print(handState)
    if fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 1 and handState == "fist" and skip_block == False:
        if time.time() - fistTime < 1:
            handState = "open"
            pyautogui.hotkey('win', 'd')  # Minimize all windows
            # print("Fist - open hand detected")
            # break
    #Fist hand (window tabs)
    if time.time() - fistTime > 1 and found == True and handState == "fist" and win_tab_btn == False and skip_block == False:
        pyautogui.hotkey('win', 'tab')  # Switch between windows
        win_tab_btn = True
    elif time.time() - fistTime < 1 and skip_block == False:
        win_tab_btn = False
    # Frame 
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    cv2.imshow("Image", img)
    cv2.waitKey(1)
    skip_block = False  # Reset skip block for the next iteration
