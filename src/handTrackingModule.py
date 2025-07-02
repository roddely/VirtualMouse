import cv2
import mediapipe as mp
import time
import math

class HandDetector:
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.maxHands,
            min_detection_confidence=self.detectionCon,
            min_tracking_confidence=self.trackCon
        )
        self.mpDraw = mp.solutions.drawing_utils

    def findHands(self, img, draw=True):
        img = cv2.flip(img, 1)  # Flip the image horizontally
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        found = False
        # print(results.multi_hand_landmarks)
        if self.results.multi_hand_landmarks:
            found = True
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
        return img, found

    def findAngel(self, p1, p2, p3):
        """
        Calculate the angle (degrees) between 3 points, with p2 as the vertex.
        """
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = p3

        # Tạo vector
        v1 = (x1 - x2, y1 - y2)
        v2 = (x3 - x2, y3 - y2)

        # Tích vô hướng và độ dài
        dot = v1[0]*v2[0] + v1[1]*v2[1]
        len1 = math.hypot(*v1)
        len2 = math.hypot(*v2)

        # Tính góc bằng arccos
        if len1 * len2 == 0:
            return 0
        cos_angle = max(-1, min(1, dot / (len1 * len2)))
        angle = math.acos(cos_angle)
        return math.degrees(angle)

    def findPosition(self, img, handNo=0, draw=True):
        lmList = []
        xList = []
        yList = []
        bbox = None
        handType = None
            

        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            #Determine if the hand is left or right
            if self.results.multi_handedness:
                handType = self.results.multi_handedness[handNo].classification[0].label

            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                # print(id, cx, cy)  # Print the landmark ID and coordinates 
                xList.append(cx)
                yList.append(cy)  
                lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (205, 179, 139), cv2.FILLED)
            if xList and yList:
                x_min, x_max = min(xList), max(xList)
                y_min, y_max = min(yList), max(yList)
                offset = 20
                x_min = max(0, x_min - offset)
                y_min = max(0, y_min - offset)
                x_max = min(img.shape[1], x_max + offset)
                y_max = min(img.shape[0], y_max + offset)
                bbox = (x_min, y_min, x_max, y_max)
                if draw:
                    cv2.rectangle(img, (x_min, y_min), (x_max, y_max), (205, 179, 139), 2)
        
        return lmList, bbox, handType

    def get_bbox_scale(self, bbox):
        """
        Calculate the area ratio of the current bbox compared to the reference bbox.
        bbox, ref_bbox: tuple (x_min, y_min, x_max, y_max)
        """
        if bbox is None:
            return None
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        area = w * h

        ref_w = 457 - 257
        ref_h = 367 - 147
        ref_area = ref_w * ref_h

        if ref_area == 0:
            return None
        return ref_area / area if area > 0 else None


    def fingerUp(self, lmList, handType):
        if not lmList or len(lmList) != 21 or handType not in ["Left", "Right"]:
            return [0] * 5

        fingers = []

        # Thumb - use xangel
        angel_thumb = self.findAngel(
            (lmList[4][1], lmList[4][2]),  # Tip of thumb
            (lmList[3][1], lmList[3][2]),  # PIP of thumb
            (lmList[2][1], lmList[2][2])   # MCP of thumb
        )

        fingers.append(int(angel_thumb > 160))  # Thumb is up if angle < 50 degrees

        # Other fingers - use y-axis
        tip_ids = [8, 12, 16, 20]
        for tip in tip_ids:
            fingers.append(int(lmList[tip][2] < lmList[tip - 2][2]))  # y_tip < y_PIP

        return fingers


    def findDistance(self, p1, p2, img=None, draw=True, r=10, t=3):
        """
        Calculate the distance between two landmark points.
        
        Parameters:
            p1, p2: IDs of the two landmark points to measure (e.g., 4 and 8)
            lmList: landmark list from findPosition()
            img: image to draw on (if desired)
            draw: whether to draw the connecting line and 2 points
            r: radius of the drawn points
            t: thickness of the drawn line

        Returns:
            distance: float, Euclidean distance
            info: tuple, (x1, y1, x2, y2, cx, cy)
            img: image with drawings (if any)
        """
        lmList, _, _ = self.findPosition(img, draw=False)
        x1, y1 = lmList[p1][1], lmList[p1][2]
        x2, y2 = lmList[p2][1], lmList[p2][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        distance = math.hypot(x2 - x1, y2 - y1)

        if img is not None and draw:
            cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), t)
            cv2.circle(img, (x1, y1), r, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), r, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (cx, cy), r, (0, 0, 255), cv2.FILLED)

        return distance, img, (x1, y1, x2, y2, cx, cy)


def main():
    cap = cv2.VideoCapture(0)
    cTime = 0
    pTime = 0
    detector = HandDetector()

    while True:
        success, img = cap.read()
        img = detector.findHands(img)
        lmList = detector.findPosition(img)
        if len(lmList) != 0:
            print(lmList[4])

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, f'FPS: {int(fps)}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        cv2.imshow("Image", img)
        cv2.waitKey(1)

if __name__ == "__main__":
    main()