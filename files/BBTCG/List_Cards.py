import pickle

with open("files//BBTCG//card_data.pickle", "rb") as file:
    cards = pickle.load(file)

leg_count = 0
epic_count = 0
rare_count = 0
common_count = 0

for c in cards:
    print(c)
    if c["rarity"] == "Legendary":
        leg_count = leg_count + 1
    elif c["rarity"] == "Epic":
        epic_count = epic_count + 1
    elif c["rarity"] == "Rare":
        rare_count = rare_count + 1
    elif c["rarity"] == "Common":
        common_count = common_count + 1

print(leg_count)
print(epic_count)
print(rare_count)
print(common_count)
