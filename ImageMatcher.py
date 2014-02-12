import cv2
import cv2.cv as cv
import numpy
import os
import time
import operator

class key_points():
    pass

class ImageMatcher():

    def __init__(self):
        hessian_threshold = 85
        self.detector = cv2.SURF(hessian_threshold)
        self.templates = []

    def get_key_points(self, file_name, store_keypoints=False):
        points = key_points()
        points.name = file_name
        points.matched = 0
        points.total = 0

        template = cv2.imread(file_name)
        (keypoints, descriptors) = self.detector.detectAndCompute(template, None,
                                                               useProvidedKeypoints = False)

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
        # kNN training - learn mapping from hrow to hkeypoints index
        samples = points.rows
        responses = numpy.arange(len(points.keypoints), dtype = numpy.float32)
        #print len(samples), len(responses)
        knn = cv2.KNearest()
        knn.train(samples,responses)
        return knn

    def find_slot_for_hero(self, point):
        slots = {"0":[[164, 84], [255, 136]],
                 "1":[[271, 84], [362, 136]],
                 "2":[[375, 84], [467, 136]],
                 "3":[[482, 84], [575, 136]],
                 "4":[[589, 84], [681, 136]],

                 "5":[[1215, 84], [1307, 136]],
                 "6":[[1322, 84], [1414, 136]],
                 "7":[[1427, 84], [1520, 136]],
                 "8":[[1534, 84], [1627, 136]],
                 "9":[[1641, 84], [1733, 136]]}

        for key, rect in slots.iteritems():
            if point[0] > rect[0][0] and point[0] < rect[1][0] and\
                point[1] > rect[0][1] and point[1] < rect[1][1]:
                return key
        return False

    def set_templates(self, file_list):
        for name in file_list:
            self.templates.append(self.get_key_points(name))

    def find_slot_for_hero(self, point):
        slots = {"0":[[164, 84], [255, 136]],
                 "1":[[271, 84], [362, 136]],
                 "2":[[375, 84], [467, 136]],
                 "3":[[482, 84], [575, 136]],
                 "4":[[589, 84], [681, 136]],

                 "5":[[1215, 84], [1307, 136]],
                 "6":[[1322, 84], [1414, 136]],
                 "7":[[1427, 84], [1520, 136]],
                 "8":[[1534, 84], [1627, 136]],
                 "9":[[1641, 84], [1733, 136]]}

        for key, rect in slots.iteritems():
            if point[0] > rect[0][0] and point[0] < rect[1][0] and\
                point[1] > rect[0][1] and point[1] < rect[1][1]:
                return key
        return False

    def analyse_for_templates(self):
        screen_points = self.get_key_points("data/ss.png", store_keypoints=True)

        knn = self.train_knn(screen_points)

        img = cv2.imread("data/ss.png")

        output_data = [{}, {}]

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
                    output_data[0][slot] = template.name[len("data/images/"):-4]
                else:
                    output_data[1][slot] = template.name[len("data/images/"):-4]

        return output_data
