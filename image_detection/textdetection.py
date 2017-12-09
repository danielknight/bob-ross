#!/usr/bin/python

import sys
import os
import cv2
import numpy as np
from pathlib import Path


def main(pathname, imgPath):
    print('\ntextdetection.py')
    print('       A demo script of the Extremal Region Filter algorithm described in:')
    print('       Neumann L., Matas J.: Real-Time Scene Text Localization and Recognition, CVPR 2012\n')
    print(pathname + " " + imgPath)
    pathname = os.path.dirname(pathname)

    img = cv2.imread(str(imgPath))
    print(img.shape)
    # for visualization

    vis = img.copy()

    # Extract channels to be processed individually
    channels = cv2.text.computeNMChannels(img)
    # Append negative channels to detect ER- (bright regions over dark background)
    cn = len(channels) - 1
    for c in range(0, cn):
        channels.append((255 - channels[c]))

    # Apply the default cascade classifier to each independent channel (could be done in parallel)
    print("Extracting Class Specific Extremal Regions from " + str(len(channels)) + " channels ...")
    print("    (...) this may take a while (...)")
    curr_ch = 0
    for channel in channels:

        erc1 = cv2.text.loadClassifierNM1(os.path.abspath(r'trained_classifierNM1.xml'))
        er1 = cv2.text.createERFilterNM1(erc1, 16, 0.00015, 0.13, 0.2, True, 0.1)

        erc2 = cv2.text.loadClassifierNM2(os.path.abspath(r'trained_classifierNM2.xml'))
        er2 = cv2.text.createERFilterNM2(erc2, 0.5)

        regions = cv2.text.detectRegions(channel, er1, er2)
        if len(regions) > 0:
            rects = cv2.text.erGrouping(img, channel, [r.tolist() for r in regions])
            # rects = cv2.text.erGrouping(img,channel,[x.tolist() for x in regions], cv2.text.ERGROUPING_ORIENTATION_ANY,'../../GSoC2014/opencv_contrib/modules/text/samples/trained_classifier_erGrouping.xml',0.5)

            # Visualization
            for r in range(0, np.shape(rects)[0]):
                rect = rects[r]
                cv2.rectangle(vis, (rect[0], rect[1]), (rect[0] + rect[2], rect[1] + rect[3]), (0, 0, 0), 2)
                cv2.rectangle(vis, (rect[0], rect[1]), (rect[0] + rect[2], rect[1] + rect[3]), (255, 255, 255), 1)
        curr_ch += 1
    # Visualization
    vis = cv2.resize(vis, (0,0), fx =.5, fy=.5)
    cv2.imshow("Text detection result" + str(curr_ch), vis)
    cv2.waitKey(0)
    return 0   #return the rectangles so we can send to tesseract


if __name__ == '__main__':
    if (len(sys.argv) < 2):
        print(' (ERROR) You must call this script with an argument (path_to_image_to_be_processed)\n')
        quit()
    main(sys.argv[0], sys.argv[1])
