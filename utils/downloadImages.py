import os, urllib2, cStringIO
from dota2py import api
import Image

if ___name__ == "__main__":
	if not os.path.exists("../data/images"):
	    os.makedirs("../data/images")
	os.chdir("../data/images")

	scale = 50/1080.0

	for hero in api.get_heroes()["result"]["heroes"]:
	    if "abyssal_underlord" in hero["name"]:
	        continue
	    #if not os.path.exists("{}.png".format(hero["localized_name"])):
	    print api.get_hero_image_url(hero["name"][len("npc_dota_hero_"):], "lg")

	    img = Image.open(cStringIO.StringIO(urllib2.urlopen(api.get_hero_image_url(hero["name"][len("npc_dota_hero_"):])).read()))
	    img = img.resize((89, 50), Image.ANTIALIAS)
	    img.save("{}.png".format(hero["localized_name"]))
