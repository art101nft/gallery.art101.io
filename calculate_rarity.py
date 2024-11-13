#!/usr/bin/env python3

import json
from os.path import exists
from os import stat

from gallery.collections import all_collections
from gallery.collections import Collection as LocalCollection
from gallery.library.rarity import Token, Category, Collection
from gallery import config


for collection in [LocalCollection(k) for k in all_collections]:
    # Define new collection
    rarity_collection = Collection()
    print(f'[+] Reading metadata for {collection.title} - {collection.contract_address}')
    _p = f'{config.DATA_PATH}/{collection.contract_address}'
    # Loop over each token in the collection to grab the JSON metadata
    for token_id in range(collection.token_start, collection.token_end + 1):
        data = None
        p = f'{_p}/{str(token_id)}.json'

        # If file does not exist locally or is empty, stop processing collection
        if not exists(p) or stat(p).st_size == 0:
            print(f'[!] {p} does not exist or is empty. Rarity rankings will be incomplete. Skipping collection.')
            exit(1)

        # Read the JSON file, stopping if unable to read it
        with open(p, 'r') as f:
            try:
                data = json.loads(f.read())
            except Exception:
                print(f'[!] Unable to load JSON data from {p}. Rarity rankings will be incomplete. Skipping collection.')
                exit(1)

        # Add token metadata to collection
        new_item = Token(token_id, data)
        rarity_collection.tokens.append(new_item)

    print('[+] Looping over tokens to get list of all category and trait tuples')
    for token in rarity_collection.tokens:
        for k, v in token.traits.items():
            if (k, v) not in rarity_collection.traits:
                rarity_collection.traits.append((k, v))

    print('[+] Looping over tokens in collection to add `None` type to tokens and sort and create category objects')
    for token in rarity_collection.tokens:
        for trait in rarity_collection.traits:
            # If item has empty attributes/traits in categories make them explicity None
            if trait[0] not in token.traits.keys():
                token.traits[trait[0]] = None
            # Set up category objects in collection
            if trait[1] not in rarity_collection.categories.keys():
                rarity_collection.categories[trait[0]] = Category(trait[0])

    print('[+] Looping over tokens in collection to count trait occurrences into category objects')
    for token in rarity_collection.tokens:
        for k, v in token.traits.items():
            if v in rarity_collection.categories[k].traits:
                rarity_collection.categories[k].trait_count[v] += 1
            else:
                rarity_collection.categories[k].traits.append(v)
                rarity_collection.categories[k].trait_count[v] = 1

    print('[+] Looping over categories to calculate frequency and rarity score')
    for cat in rarity_collection.categories.values():
        for trait in cat.traits:
            cat.trait_freq[trait] = cat.trait_count[trait] / len(rarity_collection.tokens)
            cat.trait_rarity[trait] = 1 / cat.trait_freq[trait]
            cat.trait_rarity_normed[trait] = cat.trait_rarity[trait] * (rarity_collection.get_avg_gm_hm() / len(cat.traits))

    print('[+] Looping over tokens to calculate statistical rarity and rarity score')
    for token in rarity_collection.tokens:
        for k, v in token.traits.items():
            token.stat_rarity = token.stat_rarity * rarity_collection.categories[k].trait_freq[v]
            token.rarity_score = token.rarity_score + rarity_collection.categories[k].trait_rarity[v]
            token.rarity_score_normed = token.rarity_score_normed + rarity_collection.categories[k].trait_rarity_normed[v]

    res = {}
    ranked_by = 'rarity_score_normed'
    for token in rarity_collection.tokens:
        res[token.id] = {
            'stat_rarity': token.stat_rarity,
            'rarity_score': token.rarity_score,
            'rarity_score_normed': token.rarity_score_normed
        }

    ranked = sorted(res, key=lambda x: res[x][ranked_by], reverse=True)
    res['ranks'] = {}
    for count, value in enumerate(ranked):
        rank = count + 1
        res[value]['rank'] = rank
        res[value]['ranked_by'] = ranked_by
        res['ranks'][rank] = value

    score_path = f'gallery/library/rarityscores/{collection.url_slug}.json'
    print(f'[+] Saving rarity score to {score_path}')
    with open(score_path, 'w') as f:
        f.write(json.dumps(res))
