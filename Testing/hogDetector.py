import csv
import time

import cv2
import numpy as np
from imutils import resize
from imutils.object_detection import non_max_suppression

from Testing import utils


class HogDetector:

    def __init__(self, winstride=(4, 4), padding=(8, 8), scale=1.05):
        self.winstride = winstride
        self.padding = padding
        self.scale = scale
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        self.detections = []

    def evaluateHog(self, videopath, groundtruth, threshold=0.5):
        print("[INFO] Running detector...")
        self.detectVideo(videopath, False)
        print("[INFO] Detection Done!")
        print("[INFO] Running evaluation...")
        utils.evalutate(groundtruth, self.detections, threshold)

    def printSpeed(self, startTime, endTime, framecount):
        print("[RESULT] it took %s seconds." % (endTime - startTime))
        if framecount > 1:
            print("[RESULT] clip has %s frames" % framecount)
        print("[RESULT] that makes %s fps" % (framecount / (endTime - startTime)))

    def detectImage(self, imagePath, showimage=True):
        image = cv2.imread(imagePath)
        image = resize(image, width=min(400, image.shape[1]))

        start = time.time()
        image = self.hogDetector(image)
        end = time.time()

        self.printSpeed(start, end, 1)

        cv2.imshow("frame", image)
        cv2.waitKey(0)


    def detectVideo(self, videoPath, showvideo=True):
        cap = cv2.VideoCapture()
        vid = cap.open(videoPath)
        framecount = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        framenumber = 0

        start = time.time()

        while True:
            # Capture frame-by-frame
            ret, frame = cap.read()

            if not ret:
                break

            image = self.hogDetector(frame, framenumber)

            # Display the resulting frame
            if showvideo:
                cv2.imshow('frame', image)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            # Finally update the frame number, so the csv writer knows at which frame we are
            framenumber += 1

        end = time.time()


        # When everything done, release the capture
        cap.release()
        cv2.destroyAllWindows()

    def writeDetectionsToFile(self, filename):
        f = open(filename, "w")
        reader = csv.writer(f)
        for row in self.detections:
            reader.writerow(row)

    def hogDetector(self, frame, frameNumber):
        (ho, wo) = frame.shape[:2]
        originalFrame = frame

        frame = resize(frame, width=min(400, frame.shape[1]))
        (hr, wr) = frame.shape[:2]

        widthScale = wo / wr
        heightScale = ho / hr

        (rects, weights) = self.hog.detectMultiScale(frame, winStride=self.winstride, padding=self.padding, scale=self.scale)

        # apply non-maxima suppression to the bounding boxes using a
        # fairly large overlap threshold to try to maintain overlapping
        # boxes that are still people
        rects = np.array(
            [[x, y, x + w, y + h] * np.array([widthScale, heightScale, widthScale, heightScale]) for (x, y, w, h) in
             rects])
        pick = non_max_suppression(rects, probs=None, overlapThresh=0.65)

        # draw the final bounding boxes
        for (xA, yA, xB, yB) in pick:
            # add the detection to the csv file
            self.detections.append([frameNumber, xA, yA, xB, yB])
            cv2.rectangle(originalFrame, (xA, yA), (xB, yB), (0, 255, 0), 2)

        return originalFrame

    def setWinStride(self, winstride):
        self.winstride = winstride

    def setPadding(self, padding):
        self.padding = padding

    def setScale(self, scale):
        self.scale = scale