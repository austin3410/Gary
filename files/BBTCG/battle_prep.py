import pickle
from random import randint, uniform
import random


def crit_check(crit_chance):
    return uniform(0, 1) < crit_chance

def calc_damage_move(move, crit_chance, crit_mult):
    damage = 0
    if move["damage_type"] == "range":
        if move["damage_interval"] > 1:
            damage = []
            for i in range(move["damage_interval"]):
                damage.append(randint(move["damage_min"], move["damage_max"]))
        else:
            for i in range(move["damage_interval"]):
                damage += randint(move["damage_min"], move["damage_max"])

    elif move["damage_type"] == "static":
        damage = move["damage"]
    
    is_crit = crit_check(crit_chance)
    if is_crit:
        print("It's a crit!")
        damage *= crit_mult

    return damage

def calc_heal_move(move, crit_chance, crit_mult):
    healing = 0
    if move["heal_type"] == "range":
        if move["heal_interval"] > 1:
            healing = []
            for i in range(move["heal_interval"]):
                healing.append(randint(move["heal_min"], move["heal_max"]))
        
        else:
            for i in range(move["heal_interval"]):
                healing += randint(move["heal_min"], move["heal_max"])
    
    is_crit = crit_check(crit_chance)
    if is_crit:
        print("It's a crit!")
        healing *= crit_mult
    
    return healing



with open("files//BBTCG//card_data.pickle", "rb") as file:
    cards = pickle.load(file)

for c in cards:
    if c["rarity"] == "Legendary":
        if c["name"] == "SpongeBob SquarePants":
            spongebob_moves = [
                {"name": "Bubble Blow", "text": "Deals 10-25 damage", "type": "damage", "damage_type": "range", "damage_min": 10, "damage_max": 25, "damage_interval": 1, "uses": -1},
                {"name": "Karate Chop", "text": "Deals 15 damage", "type": "damage", "damage_type": "static", "damage": 15, "uses": -1},
                {"name": "Le Spatula", "text": "Deals 8-12 damage twice", "type": "damage", "damage_type": "range", "damage_min": 8, "damage_max": 12, "damage_interval": 2, "uses": 3},
                {"name": "I'm Ready!", "text": "Heals 8-15", "type": "heal", "heal_type": "range", "heal_min": 8, "heal_max": 15, "heal_interval": 1, "uses": 2}
            ]
            spongebob_stats = {"health": 100, "crit_chance": .2, "crit_mult": 2}
            c["battle"] = {"stats": spongebob_stats, "moves": spongebob_moves}
        
        elif c["name"] == "Mrs. Puff":
            mp_moves = [
                {"name": "Bad Noodle", "text": "Deals 10-25 damage", "type": "damage", "damage_type": "range", "damage_min": 10, "damage_max": 25, "damage_interval": 1, "uses": -1},
                {"name": "Ruler Slap", "text": "Deals 15 damage", "type": "damage", "damage_type": "static", "damage": 15, "uses": -1},
                {"name": "Puff Up", "text": "Deals 8-12 damage twice", "type": "damage", "damage_type": "range", "damage_min": 8, "damage_max": 12, "damage_interval": 2, "uses": 3},
                {"name": "Crash Helmet", "text": "Heals 8-15", "type": "heal", "heal_type": "range", "heal_min": 8, "heal_max": 15, "heal_interval": 1, "uses": 2}
            ]
            mp_stats = {"health": 100, "crit_chance": .2, "crit_mult": 2}
            c["battle"] = {"stats": mp_stats, "moves": mp_moves}


print("Mocking Battle...\n\n")
mp_card = next(c for c in cards if c["name"] == "Mrs. Puff")
sb_card = next(c for c in cards if c["name"] == "SpongeBob SquarePants")

class battle_card:

    def __init__(self, card, enemy):
        self.name = card["name"]
        self.health = card["battle"]["stats"]["health"]
        self.crit_chance = card["battle"]["stats"]["crit_chance"]
        self.crit_mult = card["battle"]["stats"]["crit_mult"]

        self.moves = card["battle"]["moves"]

        self.enemy = enemy
    
    def do_move(self, move):
        pass
    
    def take_turn(self):
        
        if self.health < 20:
            for move in self.moves:
                if move["type"] == "heal" and move["uses"] > 0:
                    self.do_move(move)
        else:
            self.do_move(self.moves[randint(1,4)])





while True:

    print("SB's Turn!")




"""stats = c["battle"]["stats"]
moves = c["battle"]["moves"]
print(c["name"])
print(f"Health: {stats['health']}")
print(f"Crit Chance: {stats['crit_chance']}")
print(f"Crit Multiplier: {stats['crit_mult']}\n")  
for move in moves:
    if move["type"] == "damage":
    
        damage = calc_damage_move(move, stats["crit_chance"], stats["crit_mult"])
        print(f"Name: {move['name']}")
        print(f"Description: {move['text']}")
        print(f"Actual Damage: {damage}")
        if type(damage) == list:
            print(f"Total Damage: {sum(damage)}")
        print("\n")
    
    else:
        healing = calc_heal_move(move, stats["crit_chance"], stats["crit_mult"])
        print(f"Name: {move['name']}")
        print(f"Description: {move['text']}")
        print(f"Actual Healing: {healing}")
        if type(healing) == list:
            print(f"Total Healing: {sum(healing)}")
        print("\n")"""