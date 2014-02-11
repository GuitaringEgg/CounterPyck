import requests
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool
from bs4 import BeautifulSoup
import json

class DotaBuff():

    matchup_links = {}

    def __init__(self):
        pass

    # get all the hero matchup data
    # taken from a snippet by mplewis
    # https://gist.github.com/mplewis/8213062
    # TODO: modigy to fit my style
    def get_hero_data(self):
        heroes_html = BeautifulSoup(requests.get('http://dotabuff.com/heroes').text)
        for a in heroes_html.find('div', class_='hero-grid').find_all('a'):
            self.matchup_links[a.text] = 'http://dotabuff.com%s/matchups' % a['href']

        pool = ThreadPool(8)
        responses = pool.map(requests.get, self.matchup_links.values())

        all_html = [response.text for response in responses]

        pool = ThreadPool(8)
        matchups_list = pool.map(self.process_matchup_html, all_html)

        matchups = {matchup[0]: matchup[1] for matchup in matchups_list}
        print 'Processing %s matchups...' % len(self.matchup_links)
        with open("matchups.json", "w") as outfile:
            json.dump(matchups, outfile, sort_keys=True, indent=4, separators=(',', ': '))


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






db = DotaBuff()
db.get_hero_data()
#with open("matchups.json", "w+") as outfile:
    #data = []
    #data = json.load(outfile)
    #json.dump(data, outfile, sort_keys=True, indent=4, separators=(',', ': '))


