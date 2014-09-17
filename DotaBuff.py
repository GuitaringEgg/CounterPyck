import os
import requests
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool
import json
import urllib2
import time
import logging as log
import cStringIO

from bs4 import BeautifulSoup
from dota2py import api
import Image



class DotaBuff():
    """
    A class encapsulation the hero matchup data methods,
    downloading, storing and searching
    """

    # All the matchup data between every hero
    matchups = {}

    def __init__(self):
        """
        Nothing to initialise
        """
        pass

    def get_hero_data_dotabuff(self):
        """
        Download all the hero matchup data and store it in a file
        taken from a snippet by mplewis
        https://gist.github.com/mplewis/8213062
        """

        log.warning("Downloading matchup data. This normally takes a minute...")
        matchup_links = {}

        # grab all the heroes names and generate all the links we need
        heroes_html = BeautifulSoup(requests.get('http://dotabuff.com/heroes').text)
        for a in heroes_html.find('div', class_='hero-grid').find_all('a'):
            matchup_links[a.text] = 'http://dotabuff.com{}/matchups'.format(a['href'])

        # download all the html data for all the sites using 8 threads at a time
        log.info("Getting {} matchup pages from DotaBuff".format(len(matchup_links)))
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

    def process_matchup_html(self, html):
        """
        Process all raw matchup html and extract the useful info
        Used by get_hero_data_dotabuff()
        """

        # make some soup from the html
        soup = BeautifulSoup(html)
        # find the hero name
        hero_name = soup.find('title').text.split(' - ')[0]
        log.info("Getting matchup data for {}".format(hero_name))

        # find all the rows and get all the heroes and corresponding matchup data
        rows = soup.find('tbody').find_all('tr')
        matchups = {}
        for row in rows:
            cells = row.find_all('td')
            name = cells[1].text
            advantage = cells[2].text.strip('%')
            matchups[name] = advantage
        return (hero_name, matchups)

    def get_hero_data(self, force=False):
        """
        Load the matchup data from file if possible,
        otherwise scrape it from DotaBuff
        """

        if os.path.exists("data/matchups.json") and not force:
            self.matchups = json.load(open("data/matchups.json", "r"))
            time_since_last_update = time.time() - self.matchups["time"]
            if time_since_last_update > 3600*24*7:
                log.warning("It's been over a week since the data was last updated.")
                self.get_hero_data_dotabuff()
        else:
            self.get_hero_data_dotabuff()

    def get_matchup_percentage(self, hero, heroes):
        """
        Get the matchup percentage between a hero and a list of other heroes
        """

        perc = 0.0
        for slot in heroes:
            perc += float(self.matchups["data"][hero][heroes[slot]])

        return perc

    def get_hero_matchup(self, heroes):
        """
        Get the matchup percentage data for every hero
        verses a list of other heroes
        """

        data = {}
        for hero in self.matchups["data"]:
            if not hero in heroes.values():
                data[hero] = self.get_matchup_percentage(hero, heroes)
        return data

    def get_team_matchup(self, heroes, enemies):
        """
        Get the matchup percentage data for every hero + the current line-up
        verses a list of enemy heroes
        """

        # Calculate the team percentage based on the current lineup
        team_percentage = 0.0
        for ally in heroes:
            team_percentage += self.get_matchup_percentage(heroes[ally], enemies)

        data = {}
        for hero in self.matchups["data"]:
            if hero not in heroes.values() and hero not in enemies.values():
                data[hero] = self.get_matchup_percentage(hero, enemies)
                data[hero] += team_percentage
        return data

    def get_heroes_images(self, size="lg", force=False, ratio=1.0):
        """
        Get all the hero images and store them in data/images
        """

        loc = "data/images_{}".format(size)

        if not os.path.exists(loc):
            os.makedirs(loc)
        os.chdir(loc)

        log.basicConfig(level=log.INFO)

        log.warning("Downloading all hero images. This will take a few minutes.")

        for hero in api.get_heroes()["result"]["heroes"]:
            # if the hero is Abyssal Underlord, ignore because he's not in the game yet
            if hero["name"].find("abyssal_underlord") != -1:
                continue
            if not os.path.exists("{}.png".format(hero["localized_name"])) or force:

                if ratio == 1.0:
                    with open("{}.png".format(hero["localized_name"]), "wb") as outfile:
                        log.info("Getting hero image from {}".format(api.get_hero_image_url(hero["name"][len("npc_dota_hero_"):])))
                        outfile.write(urllib2.urlopen(api.get_hero_image_url(hero["name"][len("npc_dota_hero_"):], image_size=size)).read())
                        outfile.close()

                else:
                    log.info("Getting hero image from {}".format(api.get_hero_image_url(hero["name"][len("npc_dota_hero_"):])))
                    img = Image.open(cStringIO.StringIO(urllib2.urlopen(api.get_hero_image_url(hero["name"][len("npc_dota_hero_"):])).read()))
                    img = img.resize((int(89 * ratio), int(50 * ratio)), Image.ANTIALIAS)
                    img.save("{}.png".format(hero["localized_name"]))

    def test(self):

        import string
        words = ["http://media.steampowered.com/apps/dota2/images/heroes/antimage_" + first + second + ".png" for second in string.ascii_lowercase for first in string.ascii_lowercase]

        suc = []
        fail = []

        log.basicConfig(level=log.INFO)

        pool = ThreadPool(8)
        responses = pool.map(requests.get, words)


        for response, word in zip(responses, words):
            if response.status_code == 404:
                fail.append(word)
            else:
                suc.append(word)

        """
        for word in words:
            try:
                req = urllib2.Request("http://media.steampowered.com/apps/dota2/images/heroes/antimage_{}.png".format(word))
                print "http://media.steampowered.com/apps/dota2/images/heroes/antimage_{}.png".format(word)

                hangle = urllib2.urlopen(req)

            except urllib2.HTTPError, e:
                fail.append(word)
                print "fail"
                continue

            suc.append(word)
        """
        print suc
        print fail



