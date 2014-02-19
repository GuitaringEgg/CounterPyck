"""
The first file that showed that it could work the way I wish it too.
Is only kept for reference, and is not part of the project 19/02/14
"""

import cv2
import cv2.cv as cv
import numpy
import os
import time
import operator

hessian_threshold = 85
detector = cv2.SURF(hessian_threshold)

class sample_struct():
    pass

from PIL import ImageGrab
import win32gui
def grab_screenshot():
    toplist, winlist = [], []
    def enum_cb(hwnd, results):
        winlist.append((hwnd, win32gui.GetWindowText(hwnd)))
    win32gui.EnumWindows(enum_cb, toplist)

    dota = [(hwnd, title) for hwnd, title in winlist if 'dota 2' in title.lower()]
    if len(dota) == 0:
        return False
    # just grab the hwnd for first window matching dota
    dota = dota[0]
    hwnd = dota[0]

    win32gui.SetForegroundWindow(hwnd)
    bbox = win32gui.GetWindowRect(hwnd)
    img = ImageGrab.grab(bbox)
    img.save("data/ss.png")

    return True

def get_key_points(file_name, store_keypoints=False):
    points = sample_struct()
    points.name = file_name
    points.matched = 0
    points.total = 0

    template = cv2.imread(file_name)
    (keypoints, descriptors) = detector.detectAndCompute(template, None,
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

def train_knn(points):
    # kNN training - learn mapping from hrow to hkeypoints index
    samples = points.rows
    responses = numpy.arange(len(points.keypoints), dtype = numpy.float32)
    #print len(samples), len(responses)
    knn = cv2.KNearest()
    knn.train(samples,responses)
    return knn

def find_slot_for_hero(point):
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

heroes = []

from DotaBuff import DotaBuff
db = DotaBuff()
db.get_hero_data()

# generate the points for every hero
for image in os.listdir("data/images/"):
    heroes.append(get_key_points(os.path.join("data/images/", image)))
#log.info("Found {} heros".format(len(heroes)))

start_time = time.time()
pos = [{},{}]

while time.time() - start_time < 60:
    last_time = time.time()
    #result = grab_screenshot()
    result = True
    if result == False:
        print("Error: Couldn't find dota screen")
        break

    screen_points = get_key_points("data/ss.png", store_keypoints=True)

    knn = train_knn(screen_points)

    img = cv2.imread("data/ss.png")

    for hero in heroes:
        hero.total = 0
        hero.matches = 0
        matchingpoints = []
        debugprint = []
        if hero.name in debugprint:
            for i, descriptor in enumerate(hero.rows):

                descriptor = numpy.array(descriptor, dtype = numpy.float32).reshape((1, hero.rowsize))
                retval, results, neigh_resp, dists = knn.find_nearest(descriptor, 1)
                res, dist =  int(results[0][0]), dists[0][0]

                if dist < 0.1:
                    hero.matches += 1
                    matchingpoints.append(screen_points.keypoints[res].pt)
                    colour = (0, 0, 255)
                    x,y = screen_points.keypoints[res].pt
                    center = (int(x),int(y))
                    cv2.circle(img,center,2,colour,-1)
                else:
                    colour = (225, 0, 0)


                hero.total += 1

        else:
            for i, descriptor in enumerate(hero.rows):

                descriptor = numpy.array(descriptor, dtype = numpy.float32).reshape((1, hero.rowsize))
                retval, results, neigh_resp, dists = knn.find_nearest(descriptor, 1)
                res, dist =  int(results[0][0]), dists[0][0]

                if dist < 0.1:
                    hero.matches += 1
                    matchingpoints.append(screen_points.keypoints[res].pt)

                hero.total += 1

        hero.match = True if hero.matches >= 3 else False

        if hero.match:
            x = sum(v[0] for v in matchingpoints) / float(len(matchingpoints))
            y = sum(v[1] for v in matchingpoints) / float(len(matchingpoints))
            center = (int(x), int(y))

            slot = find_slot_for_hero(center)
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
                    slot = find_slot_for_hero(center)
                    if not slot == False:
                        break

            cv2.circle(img,center,5,(0, 0, 225),-1)
            #print "{} is on screen at ({}, {}) in slot {}".format(hero.name, x, y, slot)
            if int(slot) < 5:
                pos[0][slot] = hero.name[len("data/images/"):-4]
            else:
                pos[1][slot] = hero.name[len("data/images/"):-4]

    data = db.get_hero_matchup(pos[1])
    print pos
    #keys = sorted(data, key=operator.itemgetter(1), reverse=True)
    highest = -999
    high_key = ""
    for key in data:
        if data[key] > highest:
            highest = data[key]
            high_key = key
    print "{} has a {} advantage".format(high_key, highest)

    print "Time elapsed {}s".format(time.time() - last_time)
