# import the necessary packages
import numpy as np
import cv2
import pyautogui

# define the upper and lower boundaries of the HSV pixel
# intensities to be considered 'skin'
lower = np.array([0, 48, 80], dtype="uint8")
upper = np.array([20, 255, 255], dtype="uint8")

camera = cv2.VideoCapture(0)

# keep looping over the frames in the video
pX = 0
pY = 0
while True:
    areaArray = []
    count = 1

    # grab the current frame
    (grabbed, frame) = camera.read()

    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Otsu's thresholding after Gaussian filtering
    blur = cv2.GaussianBlur(gray_frame, (5, 5), 0)
    ret3, th3 = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    roi = th3[0:400, 0:300]
    roi_cpy = roi.copy()
    _, contours, hierarchy = cv2.findContours(roi_cpy, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for i, c in enumerate(contours):
        area = cv2.contourArea(c)
        areaArray.append(area)

    # first sort the array by area
    sorteddata = sorted(zip(areaArray, contours), key=lambda x: x[0], reverse=True)

    # find the nth largest contour [n-1][1], in this case 2
    if len(sorteddata) > 0:

        largestContour = sorteddata[0][1]

        M = cv2.moments(largestContour)
        if M["m00"] == 0:
            continue

        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])

        diffX = cX - pX
        diffY = cY- pY

        if diffX < 3 and diffY < 3:
            continue

        (mouseX, mouseY) = pyautogui.position()
        pyautogui.moveTo(mouseX + diffX, mouseY + diffY)

        pX = cX
        pY = cY

        # stuff to render
        x, y, w, h = cv2.boundingRect(largestContour)

        color_img = cv2.cvtColor(roi, cv2.COLOR_GRAY2BGR)
        cv2.rectangle(color_img, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # convex hull + defects
        hull = cv2.convexHull(largestContour, returnPoints=False)
        defects = cv2.convexityDefects(largestContour, hull)

        count = 0
        for i in range(defects.shape[0]):
            s, e, f, d = defects[i, 0]
            start = tuple(largestContour[s][0])
            end = tuple(largestContour[e][0])
            far = tuple(largestContour[f][0])
            cv2.line(color_img, start, end, [0, 255, 0], 2)
            cv2.circle(color_img, far, 5, [0, 0, 255], -1)

        cv2.imshow("Otsu plus blur", color_img)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()
