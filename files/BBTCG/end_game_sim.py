import pickle

with open("files//BBTCG//cards//available_cards.pickle", "rb+") as file:
    avail_cards = pickle.load(file)

avail_cards = avail_cards[12:15]

with open("files//BBTCG//cards//available_cards.pickle", "rb+") as file:
    pickle.dump(avail_cards, file)

try:
    with open("files//BBTCG//users//224665053570400275.pickle", "rb+") as file:
        user = pickle.load(file)
        user["money"] = 9999999
    
    with open("files//BBTCG//users//224665053570400275.pickle", "rb+") as file:
        pickle.dump(user, file)
except:
    print("Can't load your user file... skipping.")

