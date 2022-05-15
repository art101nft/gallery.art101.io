class Item:
    '''Representation of item in a collection'''
    def __init__(self, data):
        '''Take data in from json file to create items'''
        self.traits = {}
        self.traits["trait_count"] = 0
        self.stat_rarity = 1
        self.rarity_score = 0
        self.rarity_score_normed = 0
        for k, v in data['traits'].items():
            if k == "Generation":
                self.ID = v             
            elif k == "birthday":
                self.birthday = v
            else:
                self.traits[k] = v
                self.traits["trait_count"] += 1
