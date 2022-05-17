#!/usr/bin/env python3

import requests, json
from os.path import exists
from os import stat
from time import sleep

from gallery.collections import all_collections
from gallery.collections import Collection as LocalCollection
from gallery.library.rarity import Item, Category, Collection
from gallery import config


for collection in [LocalCollection(k) for k in all_collections]:
    rarity_collection = Collection()
    if collection.url_slug != 'non-fungible-soup':
        continue
    print(f'[+] Reading metadata for {collection.title} - {collection.contract_address}')
    _p = f'{config.DATA_PATH}/{collection.contract_address}'
    for token_id in range(collection.token_start, collection.token_end + 1):
        data = None
        p = f'{_p}/{str(token_id)}.json'

        if not exists(p) or stat(p).st_size == 0:
            print(f'{p} does not exist or is empty. Rarity rankings will be incomplete. Skipping collection.')
            sleep(3)
            continue

        with open(p, 'r') as f:
            try:
                data = json.loads(f.read())
            except:
                print(f'Unable to load JSON data from {p}. Rarity rankings will be incomplete. Skipping collection.')
                sleep(3)
                continue

        # Loop over all token metadata and add tokens to collection and count them
        new_item = Item(token_id, data)
        rarity_collection.tokens.append(new_item)

        # Loop over tokens in collection to get list of all category/trait tuples
        for i in rarity_collection.tokens:
            for k, v in i.traits.items():
                if (k, v) not in rarity_collection.traits:
                    rarity_collection.traits.append((k, v))
                else:
                    pass

        # Loop over tokens in collection to add None type to tokens and sort and create category objects
        for i in rarity_collection.tokens:
            for t in rarity_collection.traits:
                # If item has empty attributes/traits in categories make them explicity None
                if t[0] not in i.traits.keys():
                    i.traits[t[0]] = None
                # Set up category objects in collection
                if t[1] not in rarity_collection.categories.keys():
                    rarity_collection.categories[t[0]] = Category(t[0])

        # Loop over tokens in collection and count trait occurrences into category objects
        for i in rarity_collection.tokens:
            for k, v in i.traits.items():
                #print(i.ID, t, v)
                if t in rarity_collection.categories[k].traits:
                    rarity_collection.categories[k].trait_count[v] += 1
                else:
                    rarity_collection.categories[k].traits.append(v)
                    rarity_collection.categories[k].trait_count[v] = 1

        # Loop over categories and calculate frequency and rarity score
        for v in rarity_collection.categories.values():
            for t in v.traits:
                v.trait_freq[t] = v.trait_count[t]/rarity_collection.item_count()
                v.trait_rarity[t] = 1/v.trait_freq[t]
                v.trait_rarity_normed[t] = v.trait_rarity[t]*(rarity_collection.get_avg_gm_hm()/len(v.traits))

        # Loop over tokens and calculate statistical rarity and rarity score
        for i in rarity_collection.tokens:
            for k, v in i.traits.items():
                i.stat_rarity = i.stat_rarity * rarity_collection.categories[k].trait_freq[v]
                i.rarity_score = i.rarity_score + rarity_collection.categories[k].trait_rarity[v]
                i.rarity_score_normed = i.rarity_score_normed + rarity_collection.categories[k].trait_rarity_normed[v]

    for i in rarity_collection.tokens:
        print(i.traits)
        print(i.stat_rarity)
        print(i.rarity_score)
        print(i.rarity_score_normed)
