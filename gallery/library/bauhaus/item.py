class Item:
    '''Representation of item in a collection'''
    def __init__(self, data):
        '''Take data in from json file to create items'''
        self.traits = {}
        self.traits["trait_count"] = 0
        self.stat_rarity = 1
        self.rarity_score = 0
        self.rarity_score_normed = 0
        self.ID = data["name"].split('#')[1]
        for a in data['attributes']:
            if a["trait_type"] == "Block Title":
                self.traits[a["value"]] = True
                self.traits["trait_count"] += 1
            else:
                self.traits[a["trait_type"]] = a["value"]
                self.traits["trait_count"] += 1
