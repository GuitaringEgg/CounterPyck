from ImageMatcher import ImageMatcher
from DotaBuff import DotaBuff
import logging as log
import time
import os
import wx

DEBUG = True

class CounterPyck():

    def __init__(self):
        if DEBUG:
            log.basicConfig(level=log.INFO)
        else:
            log.basicConfig(level=log.WARNING)

        self.image_matcher = ImageMatcher()
        self.dota_buff = DotaBuff()

        self.dota_buff.get_hero_data()

        heroes = []
        for image in os.listdir("data/images/"):
            heroes.append(os.path.join("data/images/", image))

        self.image_matcher.set_templates(heroes)

    def run(self):
        start_time = time.time()

        while time.time() - start_time < 60:
            last_time = time.time()

            result = True if DEBUG else self.grab_screenshot()
            if result == False:
                print "Error: Couldn't find dota screen"
                break

            self.results = self.image_matcher.analyse_for_templates()

            data = self.dota_buff.get_hero_matchup(self.results[0])
            #keys = sorted(data, key=operator.itemgetter(1), reverse=True)
            highest = -999
            high_key = ""
            for key in data:
                if data[key] > highest:
                    highest = data[key]
                    high_key = key
            print "{} has a {} advantage".format(high_key, highest)

            print "Time elapsed {}s".format(time.time() - last_time)


    def grab_screenshot(self):
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

        screen = wx.ScreenDC()
        size = screen.GetSize()
        rect = [[164, 84], [1733, 136]]
        bmp = wx.EmptyBitmap(rect[1][0] - rect[0][0], rect[1][1] - rect[0][1])
        mem = wx.MemoryDC(bmp)
        mem.Blit(0, 0, rect[1][0] - rect[0][0], rect[1][1] - rect[0][1], screen, rect[0][0], rect[0][1])
        del mem  # Release bitmap
        bmp.SaveFile('screenshot.png', wx.BITMAP_TYPE_PNG)


app = wx.App()  # Need to create an App instance before doing anything
cp = CounterPyck()
cp.grab_screenshot_wx()
cp.grab_screenshot_wx()
cp.grab_screenshot_wx()
