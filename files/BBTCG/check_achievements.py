

import inspect

class CheckAchievements():

    def __init__(self):

        # Sets up colors to refer to later.
        self.godlike = {"rarity": "God-like", "color": 0xffef14}
        self.legendary = {"rarity": "Legendary", "color": 0xff7d00}
        self.epic = {"rarity": "Epic", "color": 0xff00ff}
        self.rare = {"rarity": "Rare", "color": 0x0062ff}
        self.common = {"rarity": "Common", "color": 0x00ff00}


    ################################################################################################
    # Card Count Achievements                                                                      #
    ################################################################################################

    def WTBB(self, user):
        uid = str(inspect.currentframe().f_code.co_name)
        if len(user["inventory"]) >= 1:
            payload = {"uid": uid, "name": "Welcome to Bikini Bottom", "description": "Have at least one card in your inventory.", "reward": 25, "color": self.common["color"], "rarity": self.common["rarity"]}
            return payload
        else:
            return False
    
    def NCC(self, user):
        uid = str(inspect.currentframe().f_code.co_name)
        if len(user["inventory"]) >= 5:
            payload = {"uid": uid, "name": "Novice Card Collector", "description": "Have at least five cards in your inventory.", "reward": 50, "color": self.common["color"], "rarity": self.common["rarity"]}
            return payload
        else:
            return False
    
    def ICC(self, user):
        uid = str(inspect.currentframe().f_code.co_name)
        if len(user["inventory"]) >= 10:
            payload = {"uid": uid, "name": "Intermediate Card Collector", "description": "Have at least 10 cards in your inventory.", "reward": 100, "color": self.common["color"], "rarity": self.common["rarity"]}
            return payload
        else:
            return False
    
    def ECC(self, user):
        uid = str(inspect.currentframe().f_code.co_name)
        if len(user["inventory"]) >= 20:
            payload = {"uid": uid, "name": "Expert Card Collector", "description": "Have at least 20 cards in your inventory.", "reward": 200, "color": self.rare["color"], "rarity": self.rare["rarity"]}
            return payload
        else:
            return False
    
    def MCC(self, user):
        uid = str(inspect.currentframe().f_code.co_name)
        if len(user["inventory"]) >= 30:
            payload = {"uid": uid, "name": "Master Card Collector", "description": "Have at least 30 cards in your inventory.", "reward": 300, "color": self.epic["color"], "rarity": self.epic["rarity"]}
            return payload
        else:
            return False
    
    def COC(self, user):
        uid = str(inspect.currentframe().f_code.co_name)
        if len(user["inventory"]) >= 50:
            payload = {"uid": uid, "name": "Curator of Cards", "description": "Have at least 50 cards in your inventory.", "reward": 500, "color": self.legendary["color"], "rarity": self.legendary["rarity"]}
            return payload
        else:
            return False
    
    def IATC(self, user):
        uid = str(inspect.currentframe().f_code.co_name)
        if len(user["inventory"]) >= 100:
            payload = {"uid": uid, "name": "I AM THE CARDS", "description": "Have at least 100 cards in your inventory.", "reward": 1000, "color": self.godlike["color"], "rarity": self.godlike["rarity"]}
            return payload
        else:
            return False
    
    def C(self, user):
        uid = str(inspect.currentframe().f_code.co_name)
        if len(user["inventory"]) >= 143:
            payload = {"uid": uid, "name": "C A R D S", "description": "Have every single card in the game, in your inventory.", "reward": 69420, "color": self.godlike["color"], "rarity": self.godlike["rarity"]}
            return payload
        else:
            return False
    
    def BF(self, user):
        uid = str(inspect.currentframe().f_code.co_name)
        cards = user["inventory"]
        card_rarities = [card["rarity"] for card in cards]
        common_count = card_rarities.count("Common")
        if common_count >= 20:
            payload = {"uid": uid, "name": "Bottom Feeder",
            "description": "Have at least 20 Common cards in your inventory at the same time.", "reward": 250, "color": self.rare["color"], "rarity": self.rare["rarity"]}
            return payload
        else:
            return False

    ################################################################################################
    # Card Set Achievements                                                                        #
    ################################################################################################

    def TBT(self, user):
        uid = str(inspect.currentframe().f_code.co_name)
        cards = user["inventory"]
        card_names = [card["name"] for card in cards]

        if set(["SpongeBob SquarePants", "Patrick Star", "Squidward Tentacles"]).issubset(card_names):
            payload = {"uid": uid, "name": "The Big Three",
            "description": "Have SpongeBob SquarePants, Patrick Star, and Squidward Tentacles in your inventory at the same time.", "reward": 500, "color": self.legendary["color"], "rarity": self.legendary["rarity"]}
            return payload
        else:
            return False
    
    def FH(self, user):
        uid = str(inspect.currentframe().f_code.co_name)
        cards = user["inventory"]
        card_names = [card["name"] for card in cards]

        if set(["SpongeBob SquarePants", "Patrick Star", "Squidward Tentacles", "Eugene H. Krabs", "Sheldon J. Plankton", "Karen Plankton", "Sandy Cheeks", "Mrs. Puff", "Pearl Krabs", "Gary the Snail"]).issubset(card_names):
            payload = {"uid": uid, "name": "Full House",
            "description": "Have all 10 Legendaries in your inventory at the same time.", "reward": 69420, "color": self.godlike["color"], "rarity": self.godlike["rarity"]}
            return payload
        else:
            return False
    
    def DOTD(self, user):
        uid = str(inspect.currentframe().f_code.co_name)
        cards = user["inventory"]
        card_names = [card["name"] for card in cards]

        if set(["Mermaid Man", "Barnacle Boy"]).issubset(card_names):
            payload = {"uid": uid, "name": "Defenders of the Deep",
            "description": "Have Mermaid Man and Barnacle Boy in your inventory at the same time.", "reward": 250, "color": self.epic["color"], "rarity": self.epic["rarity"]}
            return payload
        else:
            return False
    
    def EVIL(self, user):
        uid = str(inspect.currentframe().f_code.co_name)
        cards = user["inventory"]
        card_names = [card["name"] for card in cards]

        if set(["Man Ray", "Dirty Bubble", "Barnacle Boy"]).issubset(card_names):
            payload = {"uid": uid, "name": "Every Villain Is Lemons",
            "description": "Have all the members of E.V.I.L (Man Ray, Dirty Bubble, and Barnacle Boy) in your inventory at the same time.", "reward": 300, "color": self.epic["color"], "rarity": self.epic["rarity"]}
            return payload
        else:
            return False
    
    def WTTKK(self, user):
        uid = str(inspect.currentframe().f_code.co_name)
        cards = user["inventory"]
        card_names = [card["name"] for card in cards]

        if set(["SpongeBob SquarePants", "Squidward Tentacles", "Eugene H. Krabs"]).issubset(card_names):
            payload = {"uid": uid, "name": "Welcome to the Krusty Krab",
            "description": "Have SpongeBob SquarePants, Squidward Tentacles, and Eugene H. Krabs in your inventory at the same time.", "reward": 500, "color": self.legendary["color"], "rarity": self.legendary["rarity"]}
            return payload
        else:
            return False
    
    def WTTCB(self, user):
        uid = str(inspect.currentframe().f_code.co_name)
        cards = user["inventory"]
        card_names = [card["name"] for card in cards]

        if set(["Sheldon J. Plankton", "Karen Plankton"]).issubset(card_names):
            payload = {"uid": uid, "name": "Welcome to the Chum Bucket",
            "description": "Have Sheldon J. Plankton and Karen Plankton in your inventory at the same time.", "reward": 350, "color": self.legendary["color"], "rarity": self.legendary["rarity"]}
            return payload
        else:
            return False

    ################################################################################################
    # Single Card Achievements                                                                     #
    ################################################################################################

    def LLL(self, user):
        uid = str(inspect.currentframe().f_code.co_name)
        cards = user["inventory"]
        card_names = [card["name"] for card in cards]

        if set(["Larry the Lobster"]).issubset(card_names):
            payload = {"uid": uid, "name": "Living Like Larry",
            "description": "Have Larry the Lobster in your inventory.", "reward": 25, "color": self.common["color"], "rarity": self.common["rarity"]}
            return payload
        else:
            return False

    ################################################################################################
    # Statistical Achievements                                                                     #
    ################################################################################################

    def FL(self, user):
        uid = str(inspect.currentframe().f_code.co_name)

        if user["slots_stats"]["slots_played"] >= 100:
            payload = {"uid": uid, "name": "Feelin' Lucky",
            "description": "Play slots 100 times.", "reward": 25, "color": self.common["color"], "rarity": self.common["rarity"]}
            return payload
        else:
            return False
    
    def SSDD(self, user):
        uid = str(inspect.currentframe().f_code.co_name)

        if user["slots_stats"]["slots_played"] >= 250:
            payload = {"uid": uid, "name": "Same Slots Different Day",
            "description": "Play slots 250 times.", "reward": 100, "color": self.rare["color"], "rarity": self.rare["rarity"]}
            return payload
        else:
            return False
    
    def SITWI(self, user):
        uid = str(inspect.currentframe().f_code.co_name)

        if user["slots_stats"]["slots_played"] >= 500:
            payload = {"uid": uid, "name": "Spin It To Win It",
            "description": "Play slots 500 times.", "reward": 200, "color": self.epic["color"], "rarity": self.epic["rarity"]}
            return payload
        else:
            return False
    
    def BB(self, user):
        uid = str(inspect.currentframe().f_code.co_name)

        if user["shop_stats"]["steals_purchased"] >= 1:
            payload = {"uid": uid, "name": "Breaking Bad",
            "description": "Steal someone else's card.", "reward": 25, "color": self.common["color"], "rarity": self.common["rarity"]}
            return payload
        else:
            return False
    
    def DMIID(self, user):
        uid = str(inspect.currentframe().f_code.co_name)

        if user["shop_stats"]["steals_purchased"] >= 5:
            payload = {"uid": uid, "name": "Don't Mind if I Do",
            "description": "Steal 5 cards.", "reward": 100, "color": self.rare["color"], "rarity": self.rare["rarity"]}
            return payload
        else:
            return False
    
    def MW(self, user):
        uid = str(inspect.currentframe().f_code.co_name)

        if user["shop_stats"]["steals_purchased"] >= 10:
            payload = {"uid": uid, "name": "Most Wanted",
            "description": "Steal 10 cards.", "reward": 200, "color": self.epic["color"], "rarity": self.epic["rarity"]}
            return payload
        else:
            return False
    
    def I(self, user):
        uid = str(inspect.currentframe().f_code.co_name)

        if user["shop_stats"]["steals_purchased"] >= 20:
            payload = {"uid": uid, "name": "Infamous",
            "description": "Steal 20 cards.", "reward": 350, "color": self.legendary["color"], "rarity": self.legendary["rarity"]}
            return payload
        else:
            return False
    
    def DS(self, user):
        uid = str(inspect.currentframe().f_code.co_name)

        if user["market_stats"]["cards_purchased"] >= 1:
            payload = {"uid": uid, "name": "Deal Seeker",
            "description": "Purchase 1 cards from the market.", "reward": 25, "color": self.common["color"], "rarity": self.common["rarity"]}
            return payload
        else:
            return False
    
    def PT(self, user):
        uid = str(inspect.currentframe().f_code.co_name)

        if user["market_stats"]["cards_purchased"] >= 5:
            payload = {"uid": uid, "name": "Poppin Tags",
            "description": "Purchase 5 cards from the market.", "reward": 50, "color": self.rare["color"], "rarity": self.rare["rarity"]}
            return payload
        else:
            return False
    
    def DD(self, user):
        uid = str(inspect.currentframe().f_code.co_name)

        if user["market_stats"]["cards_purchased"] >= 10:
            payload = {"uid": uid, "name": "Dumpster Diver",
            "description": "Purchase 10 cards off of the market.", "reward": 100, "color": self.epic["color"], "rarity": self.epic["rarity"]}
            return payload
        else:
            return False
    
    def OMT(self, user):
        uid = str(inspect.currentframe().f_code.co_name)

        if user["market_stats"]["cards_purchased"] >= 20:
            payload = {"uid": uid, "name": "One Man's Trash",
            "description": "Purchase 20 cards off of the market.", "reward": 200, "color": self.legendary["color"], "rarity": self.legendary["rarity"]}
            return payload
        else:
            return False