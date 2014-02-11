import os
import urllib2
from dota2py import api

if not os.path.exists("images"):
    os.makedirs("images")
os.chdir("images")

for hero in api.get_heroes()["result"]["heroes"]:
    if hero["name"].find("abyssal_underlord") != -1:
        continue
    if not os.path.exists("{}.png".format(hero["localized_name"])):
        f = open("{}.png".format(hero["localized_name"]), "wb")
        print api.get_hero_image_url(hero["name"][len("npc_dota_hero_"):])
        f.write(urllib2.urlopen(api.get_hero_image_url(hero["name"][len("npc_dota_hero_"):])).read())
        f.close()
