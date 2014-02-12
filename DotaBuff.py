import requests
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool
from bs4 import BeautifulSoup
import json
import os
import urllib2
import logging as log
from dota2py import api
import time

class DotaBuff():

    matchups = {}

    def __init__(self):
        log.basicConfig(level=log.INFO)
        pass

    # get all the hero matchup data
    # taken from a snippet by mplewis
    # https://gist.github.com/mplewis/8213062
    def get_hero_data_dotabuff(self):
        log.warning("Downloading matchup data. This normally takes a minute..")
        matchup_links = {}

        # grab all the heroes names and generate all the links we need
        heroes_html = BeautifulSoup(requests.get('http://dotabuff.com/heroes').text)
        for a in heroes_html.find('div', class_='hero-grid').find_all('a'):
            matchup_links[a.text] = 'http://dotabuff.com%s/matchups' % a['href']

        # download all the html data for all the sites using 8 threads at a time
        log.info("Getting {} matchup pages from dotabuff".format(len(matchup_links)))
        pool = ThreadPool(8)
        responses = pool.map(requests.get, matchup_links.values())

        # get all the raw html data from the responses
        all_html = [response.text for response in responses]

        # process all the download data and scrape the matchup info
        log.info("Processing all pages and scraping matchup data")
        pool = ThreadPool(8)
        matchups_list = pool.map(self.process_matchup_html, all_html)

        # store the scraped data in an easily accessible dict
        self.matchups["data"] = {matchup[0]: matchup[1] for matchup in matchups_list}
        self.matchups["time"] = time.time()

        # dump the data to a file so we don't have to take so long next time
        with open("data/matchups.json", "w") as outfile:
            json.dump(self.matchups, outfile, sort_keys=True, indent=4, separators=(',', ': '))
            log.info("Saved matchup data to '{}'".format("data/matchups.json"))

    # process the matchup data of one hero
    def process_matchup_html(self, html):
        # make some soup from the html
        soup = BeautifulSoup(html)
        # find the hero name
        hero_name = soup.find('title').text.split(' - ')[2]
        log.info("Getting matchup data for {}".format(hero_name))

        # find all the rows and get all the heros and corrisponding matchup data
        rows = soup.find('tbody').find_all('tr')
        matchups = {}
        for row in rows:
            cells = row.find_all('td')
            name = cells[1].text
            advantage = cells[2].text.strip('%')
            matchups[name] = advantage
        return (hero_name, matchups)

    # load the matchup data from file if possible, otherwise scrape it from dotabuff
    def get_hero_data(self, force=False):
        if os.path.exists("data/matchups.json") and not force:
            self.matchups = json.load(open("data/matchups.json", "r"))
            time_since_last_update = time.time() - self.matchups["time"]
            if time_since_last_update > 3600*24*7:
                log.warning("It's been over a week since the data was last updated.")
        else:
            self.get_hero_data_dotabuff()

    # get the matchup percentage between a hero and a list of other heroes
    def get_matchup_percentage(self, hero, heroes):
        perc = 0.0
        for slot in heroes:
            perc += float(self.matchups[hero][heroes[slot]])

        return perc

    # get the matchup percentage data for every hero verse a list of other heroes
    def get_hero_matchup(self, heroes):
        data = {}
        for hero in self.matchups:
            if not hero in heroes.values():
                data[hero] = self.get_matchup_percentage(hero, heroes)
        return data


    # get all the hero images and store them in data/images
    def get_heroes_images(self, size="lg", force=False):
        if not os.path.exists("data/images"):
            os.makedirs("data/images")
        os.chdir("data/images")

        for hero in api.get_heroes()["result"]["heroes"]:
            # if the hero is abyssal underlord, ignore because he's not in the game yet
            if hero["name"].find("abyssal_underlord") != -1:
                continue
            if not os.path.exists("{}.png".format(hero["localized_name"])) or force:
                with open("{}.png".format(hero["localized_name"]), "wb") as outfile:
                    log.info("Getting hero image from {}".format(api.get_hero_image_url(hero["name"][len("npc_dota_hero_"):]) ) )
                    outfile.write(urllib2.urlopen(api.get_hero_image_url(hero["name"][len("npc_dota_hero_"):], image_size=size)).read())
                    outfile.close()

    # get all the hero images and resize them
    # this is to reduce the load on the image matching
    def get_heroes_images_resize(self, size="lg", ratio=1.0):
        import cStringIO
        import Image

        for hero in api.get_heroes()["result"]["heroes"]:
            # if the hero is abyssal underlord, ignore because he's not in the game yet
            if hero["name"].find("abyssal_underlord") != -1:
                continue
            log.info("Getting hero image from {}".format(api.get_hero_image_url(hero["name"][len("npc_dota_hero_"):], "lg")))

            # Download the image directly and open it as an image.
            # Resize it based on the standard scale size and ratio and save it as normal
            img = Image.open(cStringIO.StringIO(urllib2.urlopen(api.get_hero_image_url(hero["name"][len("npc_dota_hero_"):])).read()))
            img = img.resize((int(89 * ratio), int(50 * ratio)), Image.ANTIALIAS)
            img.save("data/images/{}.png".format(hero["localized_name"]))

# Force downloading for testing
#db = DotaBuff()
#db.get_heroes_images(force=True)
