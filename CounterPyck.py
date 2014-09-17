import os
import logging as log
import time
import operator

import wx

from ImageMatcher import ImageMatcher
from DotaBuff import DotaBuff


DEBUG = True


class CounterPyck():
    """
    Class that pulls all the image processing and data mining together
    """

    def __init__(self):
        if DEBUG:
            log.basicConfig(level=log.INFO)
        else:
            log.basicConfig(level=log.WARNING)

        self.app = wx.App()  # Need to create an App instance before doing anything

        self.image_matcher = ImageMatcher()
        self.dota_buff = DotaBuff()

        self.dota_buff.get_hero_data()

        self.screenshot_folder = []
        self.dota2_location = "E:\\Steam\\SteamApps\\common\\dota 2 beta\\dota\\"

        heroes = []
        for image in os.listdir("data/images/"):
            heroes.append(os.path.join("data/images/", image))

        self.image_matcher.set_templates(heroes)

    def run(self):
        """
        Current main running function
        """

        start_time = time.time()

        while time.time() - start_time < 60:
            if not self.check_for_screenshot():
                continue

            last_time = time.time()

            result = True if DEBUG else self.grab_screenshot()
            if result == False:
                print "Error: Couldn't find dota screen"
                return

            self.results = self.image_matcher.analyse_for_templates()

            print self.results

            data = self.dota_buff.get_team_matchup(self.results["dire"], self.results["radiant"])
            sorted_dota = sorted(data.iteritems(), key=operator.itemgetter(1), reverse=True)

            print "{} has a {} advantage".format(sorted_dota[0][0], sorted_dota[0][1])

            with open("dump.log", "w") as o:
                o.write(str(data))

            print "Time elapsed {}s".format(time.time() - last_time)

    def check_for_screenshot(self):
        files = os.listdir(os.path.join(self.dota2_location, "screenshot"))

        return set(files).intersection(self.screenshot_folder)

    def find_dota2_folder(self):
        pass


    def grab_screenshot(self):
        """
        Grab a screenshot using win32gui
        """

        from PIL import ImageGrab
        import win32gui

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

    def grab_screenshot_wx(self):
        """
        Grab a screenshot using wx
        """

        screen = wx.ScreenDC()
        size = screen.GetSize()
        rect = [[164, 84], [1733, 136]]
        bmp = wx.EmptyBitmap(rect[1][0] - rect[0][0], rect[1][1] - rect[0][1])
        mem = wx.MemoryDC(bmp)
        mem.Blit(0, 0, rect[1][0] - rect[0][0], rect[1][1] - rect[0][1], screen, rect[0][0], rect[0][1])
        del mem  # Release bitmap
        bmp.SaveFile('screenshot.png', wx.BITMAP_TYPE_PNG)

