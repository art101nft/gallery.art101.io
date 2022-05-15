import json
from statistics import median
from statistics import median_grouped
from statistics import geometric_mean
from statistics import harmonic_mean

from gallery.collections import Collection as BaseCollection


class Item:
    '''Representation of a single item/token in a collection'''
    def __init__(self, data):
        self.traits = {}
        self.traits["trait_count"] = 0
        self.stat_rarity = 1
        self.rarity_score = 0
        self.rarity_score_normed = 0
        for a in data['attributes']:
            if a["trait_type"] == "Generation":
                self.ID = a["value"]
            elif a["trait_type"] == "birthday":
                self.birthday = a["value"]
            else:
                self.traits[a["trait_type"]] = a["value"]
                self.traits["trait_count"] += 1

    def __rep__(self):
        return self.ID


class Category:
    '''Contain info on category including counts and stuff'''
    def __init__(self, name):
        self.name = name
        self.traits = []
        self.trait_count = {}
        self.trait_freq = {}
        self.trait_rarity = {}
        self.trait_rarity_normed = {}


class Collection:
    '''Representation of an entire collection of items'''
    def __init__(self):
        self.traits = []                # List of tuples coupling (category, trait)
        self.item_count = 0             # Number of items in collection
        self.items = []                 # List of all item objects in collection
        self.trait_count = {}           # Mapping of number of traits to count
        self.categories = {}            # Dict of all categories in collection with counts and stuff

    def get_avg_trait_per_cat(self):
        '''Return the average number of traits per category'''
        traits_per_cat = []
        for c in self.categories.values():
            traits_per_cat.append(len(c.traits))
        return sum(traits_per_cat)/len(traits_per_cat)

    def get_med_trait_per_cat(self):
        traits_per_cat = []
        for c in self.categories.values():
            traits_per_cat.append(len(c.traits))
        return median(traits_per_cat)

    def get_gm_trait_per_cat(self):
        traits_per_cat = []
        for c in self.categories.values():
            traits_per_cat.append(len(c.traits))
        return geometric_mean(traits_per_cat)

    def get_hm_trait_per_cat(self):
        traits_per_cat = []
        for c in self.categories.values():
            traits_per_cat.append(len(c.traits))
        return harmonic_mean(traits_per_cat)

    def get_avg_med_gm_hm(self):
        return (self.get_avg_trait_per_cat()*self.get_med_trait_per_cat()*self.get_gm_trait_per_cat()*self.get_hm_trait_per_cat())**0.25

    def get_avg_gm_hm(self):
        return (self.get_avg_trait_per_cat()*self.get_gm_trait_per_cat())**(1/2)


_c = BaseCollection('non-fungible-soup')
c = Collection()
for i in range(_c.token_start, _c.token_end):
    with open(f'data/{_c.contract_address}/{i}.json') as f:
        d = f.read()
        print(d)
        data = json.loads(d)
        print(data)
        c.items.append(Item(data))
        c.item_count += 1

print(c.items[0])
