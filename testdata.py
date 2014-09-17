import json
#import pyplot


with open("data/matchups.json", "r") as f:
    data = json.load(f)

data = data["data"]

for hero in data:
    data[hero]["perc"] = 0.
    for perc in data[hero].values():
        data[hero]["perc"] += float(perc)
    print r"{} has a {}% advantage".format(hero, data[hero]["perc"])
