import requests
from bs4 import BeautifulSoup
from requests.api import request
import pickle
import re

characters = []
c_num = 1

root_character_category = "https://spongebob.fandom.com/wiki/List_of_characters/"
character_categories = {"Main Character": "Main", "Supporting Character": "Supporting", "Minor Character": "Minor", "Other Character": "Other"}

for category in character_categories:
    r = requests.get(f"{root_character_category}{character_categories[category]}")
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "html.parser")
        soup = soup.find_all("div", {"class": "bounceme"})

        for div in soup:
            links = (div.find_all("a", {"href": lambda x : x.startswith('/wiki/')}))
            for link in links:
                if link.find("img", {"class": "lazyload"}):
                    c_name = link.get("title").replace(" (character)", "")
                    c_img = link.find("img").get("data-src")
                    c_img = re.sub(r'\/revision.+', "", c_img)
                    if category == "Main Character":
                        c_rarity = "Legendary"
                        c_color = "0xff7d00"
                        c_value = 215
                    elif category == "Other Character":
                        c_rarity = "Epic"
                        c_color = "0xff00ff"
                        c_value = 105
                    elif category == "Supporting Character":
                        c_rarity = "Rare"
                        c_color = "0x0062ff"
                        c_value = 65
                    elif category == "Minor Character":
                        c_rarity = "Common"
                        c_color = "0x00ff00"
                        c_value = 25
                    else:
                        c_rarity = "UNKOWN"
                        c_color = "UNKOWN"
                        c_value = "UNKOWN"
                    character = {"num": c_num, "name": c_name, "category": category, "rarity": c_rarity, "color": c_color, "value": c_value, "img": c_img}
                    characters.append(character)
                    c_num = c_num + 1
    else:
        print(r.text)

with open("files//BBTCG//card_data.pickle", "wb") as file:
    pickle.dump(characters, file)