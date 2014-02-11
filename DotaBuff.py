import requests
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool
from bs4 import BeautifulSoup
import json
import os
import urllib2
from dota2py import api

class DotaBuff():

    matchup_links = {}
    matchups = {}

    def __init__(self):
        pass

    # get all the hero matchup data
    # taken from a snippet by mplewis
    # https://gist.github.com/mplewis/8213062
    # TODO: modigy to fit my style
    def get_hero_data_dotabuff(self):
        heroes_html = BeautifulSoup(requests.get('http://dotabuff.com/heroes').text)
        for a in heroes_html.find('div', class_='hero-grid').find_all('a'):
            self.matchup_links[a.text] = 'http://dotabuff.com%s/matchups' % a['href']

        pool = ThreadPool(8)
        responses = pool.map(requests.get, self.matchup_links.values())

        all_html = [response.text for response in responses]

        pool = ThreadPool(8)
        matchups_list = pool.map(self.process_matchup_html, all_html)

        self.matchups = {matchup[0]: matchup[1] for matchup in matchups_list}
        print 'Processing %s matchups...' % len(self.matchup_links)
        with open("matchups.json", "w") as outfile:
            json.dump(self.matchups, outfile, sort_keys=True, indent=4, separators=(',', ': '))

    def get_hero_data(self):
        if os.path.exists("matchups.json"):
            self.matchups = json.load(open("matchups.json", "r"))
        else:
            get_hero_data_dotabuff()

    def get_matchup_percentage(self, hero, heroes):
        perc = 0.0
        for slot in heroes:
            perc += float(self.matchups[hero][heroes[slot]])

        return perc

    def get_hero_matchup(self, heroes):
        data = {}
        for hero in self.matchups:
            if not hero in heroes.values():
                data[hero] = self.get_matchup_percentage(hero, heroes)
        return data

    def process_matchup_html(self, html):
        soup = BeautifulSoup(html)
        hero_name = soup.find('title').text.split(' - ')[2]
        rows = soup.find('tbody').find_all('tr')
        matchups = {}
        for row in rows:
            cells = row.find_all('td')
            name = cells[1].text
            advantage = cells[2].text.strip('%')
            matchups[name] = advantage
        return (hero_name, matchups)

    def get_hero_images(self):
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
