# import the necessary packages
import numpy as np
import cv2
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('192.168.0.3', 10000)
sock.connect(server_address)

camera = cv2.VideoCapture(0)

# keep looping over the frames in the video
prev_x = 0
prev_y = 0
while True:
    area_array = []
    count = 1

    # grab the current frame
    (grabbed, frame) = camera.read()

    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    roi = gray_frame[0:500, 0:500]

    # gaussian blur and tresholding
    blur = cv2.GaussianBlur(roi, (5, 5), 0)
    ret3, th3 = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    roi = th3
    roi_cpy = roi.copy()

    _, contours, hierarchy = cv2.findContours(roi_cpy, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for i, c in enumerate(contours):
        area = cv2.contourArea(c)
        area_array.append(area)

    # first sort the array by area
    sorted_data = sorted(zip(area_array, contours), key=lambda x: x[0], reverse=True)

    if len(sorted_data) > 0:
        largestContour = sorted_data[0][1]
        M = cv2.moments(largestContour)

        # if denominator is zero, continue
        if M["m00"] == 0:
            continue

        # grab the center of the contour
        center_x = int(M["m10"] / M["m00"])
        center_y = int(M["m01"] / M["m00"])

        diff_x = center_x - prev_x
        diff_y = center_y - prev_y

        # if difference is too small, do not do anything
        if diff_x < 3 and diff_y < 3:
            continue

        message = "move %d %d" % (diff_x, diff_y)
        sock.sendall(message)

        prev_x = center_x
        prev_y = center_y

        # stuff to render
        x, y, w, h = cv2.boundingRect(largestContour)

        color_img = cv2.cvtColor(roi, cv2.COLOR_GRAY2BGR)
        cv2.rectangle(color_img, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # convex hull + defects
        hull = cv2.convexHull(largestContour, returnPoints=False)
        defects = cv2.convexityDefects(largestContour, hull)

        # defects.sort()
        # print defects[0:5]

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
sock.close()

