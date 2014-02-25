import os
import time
import operator

import cv2
import cv2.cv as cv
import numpy


class key_points():
    """
    A fake struct for the keypoint information
    """
    pass


class ImageMatcher():
    """
    The image processing class that processes images against a number of
    templates and returns which are found.
    Extended to support detecing what slot each hero is in for easy team parsing
    """

    def __init__(self):
        """
        Setup the detector
        """
        hessian_threshold = 85
        self.detector = cv2.SURF(hessian_threshold)
        self.templates = []

    def get_key_points(self, file_name, subrect=None, store_keypoints=False):
        """
        Get all key points of an image from a file.
        Subrect will only examine a rect of the image
        Store keypoints will store the keypoint information, which is sometimes needed
        """

        points = key_points()
        points.name = file_name
        points.matched = 0
        points.total = 0

        template = cv2.imread(file_name)
        if subrect is not None:
            template = template[subrect[1]:subrect[3], subrect[0]:subrect[2]]
        cv2.imwrite("test.png", template)
        (keypoints, descriptors) = self.detector.detectAndCompute(template, None, useProvidedKeypoints = False)

        if store_keypoints:
            points.keypoints = keypoints

        points.rowsize = len(descriptors) / len(keypoints)
        if points.rowsize > 1:
            points.rows = numpy.array(descriptors, dtype = numpy.float32).reshape((-1, points.rowsize))
        else:
            points.rows = numpy.array(descriptors, dtype = numpy.float32)
            points.rowsize = len(points.rows[0])
        return points

    def train_knn(self, points):
        """
        Train the knN with data from some points.
        """

        # kNN training - learn mapping from hrow to hkeypoints index
        samples = points.rows
        responses = numpy.arange(len(points.keypoints), dtype = numpy.float32)
        knn = cv2.KNearest()
        knn.train(samples,responses)
        return knn

    def set_templates(self, file_list):
        """
        Set the templates to look from a list of files
        """

        for name in file_list:
            self.templates.append(self.get_key_points(name))

    def find_slot_for_hero(self, point):
        """
        Find which slot the hero is in. Return -1 if no slot was found
        """

        slots = {"0":[[0, 0], [91, 52]],
                 "1":[[107, 0], [198, 52]],
                 "2":[[211, 0], [303, 52]],
                 "3":[[318, 0], [411, 52]],
                 "4":[[425, 0], [517, 52]],

                 "5":[[1051, 0], [1143, 52]],
                 "6":[[1158, 0], [1250, 52]],
                 "7":[[1263, 0], [1356, 52]],
                 "8":[[1370, 0], [1463, 52]],
                 "9":[[1477, 0], [1569, 52]]}

        for key, rect in slots.iteritems():
            if point[0] > rect[0][0] and point[0] < rect[1][0] and\
                point[1] > rect[0][1] and point[1] < rect[1][1]:
                return key
        return False

    def analyse_for_templates(self):
        """
        Analyse the screen of templates and return some nice data
        """

        screen_points = self.get_key_points("data/ss.png", subrect=[164, 84, 1733, 136], store_keypoints=True)

        knn = self.train_knn(screen_points)

        img = cv2.imread("data/ss.png")

        output_data = {"radiant":{}, "dire":{}}

        for template in self.templates:
            template.total = 0
            template.matches = 0
            matchingpoints = []
            debugprint = []
            if template.name in debugprint:
                for i, descriptor in enumerate(template.rows):

                    descriptor = numpy.array(descriptor, dtype = numpy.float32).reshape((1, template.rowsize))
                    retval, results, neigh_resp, dists = knn.find_nearest(descriptor, 1)
                    res, dist =  int(results[0][0]), dists[0][0]

                    if dist < 0.1:
                        template.matches += 1
                        matchingpoints.append(screen_points.keypoints[res].pt)
                        colour = (0, 0, 255)
                        x,y = screen_points.keypoints[res].pt
                        center = (int(x),int(y))
                        cv2.circle(img,center,2,colour,-1)
                    else:
                        colour = (225, 0, 0)


                    template.total += 1

            else:
                for i, descriptor in enumerate(template.rows):

                    descriptor = numpy.array(descriptor, dtype = numpy.float32).reshape((1, template.rowsize))
                    retval, results, neigh_resp, dists = knn.find_nearest(descriptor, 1)
                    res, dist =  int(results[0][0]), dists[0][0]

                    if dist < 0.1:
                        template.matches += 1
                        matchingpoints.append(screen_points.keypoints[res].pt)

                    template.total += 1

            template.match = True if template.matches >= 3 else False

            if template.match:
                x = sum(v[0] for v in matchingpoints) / float(len(matchingpoints))
                y = sum(v[1] for v in matchingpoints) / float(len(matchingpoints))
                center = (int(x), int(y))
                slot = self.find_slot_for_hero(center)
                if slot == False:
                    temp, classified_points, means = cv2.kmeans(data=numpy.asarray(matchingpoints, dtype="float32"), K=2, bestLabels=None,
                    criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_MAX_ITER, 1, 10), attempts=1,
                    flags=cv2.KMEANS_RANDOM_CENTERS)
                    temp_points = [[],[]]
                    for point, allocation in zip(matchingpoints, classified_points):
                        temp_points[allocation].append(point)
                    for points in temp_points:
                        x = sum(v[0] for v in points) / float(len(points))
                        y = sum(v[1] for v in points) / float(len(points))
                        center = (int(x), int(y))
                        slot = self.find_slot_for_hero(center)
                        if not slot == False:
                            break

                cv2.circle(img,center,5,(0, 0, 225),-1)
                #print "{} is on screen at ({}, {}) in slot {}".format(template.name, x, y, slot)
                if int(slot) < 5:
                    output_data["radiant"][slot] = template.name[len("data/images/"):-4]
                else:
                    output_data["dire"][slot] = template.name[len("data/images/"):-4]

        return output_data
