from Production import MobileNetDetector
from Production import HogDetector
from Production import IouTracker
import cv2
import time


class CountPeople:
    def __init__(self, detector, tracker=None):
        self.det = detector
        self.tracker = tracker
        self.detections = []

    def countInVideo(self, videoPath, showVideo = True, showSpeed = True):
        cap = cv2.VideoCapture()
        cap.open(videoPath)
        framecount = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        framenumber = 0

        start = time.time()

        while True:
            # Capture frame-by-frame
            ret, frame = cap.read()

            if not ret:
                break

            boxes = self.det.detect(frame, height, width)

            # draw the final bounding boxes
            for (xA, yA, xB, yB) in boxes:
                # add the detection to the csv file
                self.detections.append([framenumber, xA, yA, xB, yB])
                cv2.rectangle(frame, (xA, yA), (xB, yB), (0, 255, 0), 2)

            tracks = self.tracker.track(boxes)

            # Draw active tracks
            for track in tracks:
                # Start at first element so we can draw lines between current and previous element
                previouselement = track[0]
                for (xA, yA, xB, yB) in track[1:]:
                    # cv2.rectangle(frame, (xA, yA), (xB, yB), (0, 0, 255), 2)
                    oldCenter = (int((previouselement[2] + previouselement[0])/2),
                                 int((previouselement[3] + previouselement[1])/2))
                    newCenter = (int((xB + xA)/2), int((yB + yA)/2))
                    previouselement = (xA, yA, xB, yB)
                    cv2.line(frame, newCenter, oldCenter, (0, 0, 255), 5)

            # Display the resulting frame
            if showVideo:
                cv2.imshow('frame', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            # Finally update the frame number, so the csv writer knows at which frame we are
            framenumber += 1

        end = time.time()

        # When everything done, release the capture and print speed

        if showSpeed:
            print("[INFO] it took %s seconds." % (end - start))
            print("[INFO] clip has %s frames" % framecount)
            print("[INFO] that makes %s fps" % (framecount / (end - start)))

        cap.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    vid = "/media/victor/57a90e07-058d-429d-a357-e755d0820324/Footage/TestSeqFPS.mp4"

    hog = HogDetector.HogDetector()
    net = MobileNetDetector.MobileNetDetector(prototxt="../MobileNetSSD_deploy.prototxt",
                                              caffemodel="../MobileNetSSD_deploy.caffemodel")
    iou = IouTracker.IouTracker()
    det = CountPeople(net, iou)
    det.countInVideo(vid, showVideo=True)
