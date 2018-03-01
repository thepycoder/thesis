import numpy as np
import cv2


class MobileNetDetector:
    def __init__(self,
                 prototxt = "MobileNetSSD_deploy.prototxt",
                 caffemodel = "MobileNetSSD_deploy.caffemodel",
                 conf = 0.4):
        self.net = cv2.dnn.readNetFromCaffe(prototxt, caffemodel)
        self.conf = conf

    def detect(self, frame, height, width):
        # Create a blob from the source frame by resizing to the required 300x300 size
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)

        # Feed blob to the net and perform a forward pass
        self.net.setInput(blob)
        detections = self.net.forward()

        # List of bounding boxes
        boxes = []

        # loop over the detections
        for i in np.arange(0, detections.shape[2]):
            # extract the confidence (i.e., probability) associated with the prediction
            confidence = detections[0, 0, i, 2]

            # filter out weak detections by ensuring the `confidence` is greater than the minimum confidence
            if confidence > self.conf:
                # Compute the (x, y)-coordinates of the bounding box for the object
                box = detections[0, 0, i, 3:7] * np.array([width, height, width, height])
                boxes.append(box.astype("int"))

        return boxes
