import json
from os import stat
import xlsxwriter
from category import Category
from collection import Collection
from item import Item

collection = Collection()

# Loop over the json file and add items to collection and count them
input_file = "NonFungibleSoup.io_Master_Metadata_Proof.json"
with open(input_file, 'r') as jsonfile:
    data = json.load(jsonfile)
    for c in data['collection']:
        collection.items.append(Item(c))
        collection.item_count += 1

# Loop over items in collection to get list of all category/trait tuples
for i in collection.items:
    for c, t in i.traits.items():
        if (c, t) not in collection.traits:
            collection.traits.append((c, t))
        else:
            pass

# Loop over items in collection to add None type to items and sort and create category objects
for i in collection.items:
    for t in collection.traits:
        # If item has empty attributes/traits in categories make them explicity None
        if t[0] not in i.traits.keys():
            i.traits[t[0]] = None
        # Set up category objects in collection
        if t[1] not in collection.categories.keys():
            collection.categories[t[0]] = Category(t[0])
    #i.traits = dict( sorted(i.traits.items(), key=lambda x: x[0].lower()) )
    #collection.categories = dict( sorted(collection.categories.items(), key=lambda x: x[0].lower()) )

# Loop over items in collection and count trait occurrences into category objects
for i in collection.items:
    for c, t in i.traits.items():
        #print(i.ID, t, v)
        if t in collection.categories[c].traits:
            collection.categories[c].trait_count[t] += 1
        else:
            collection.categories[c].traits.append(t)
            collection.categories[c].trait_count[t] = 1

# Loop over categories and calculate frequency and rarity score
for c in collection.categories.values():
    for t in c.traits:
        c.trait_freq[t] = c.trait_count[t]/collection.item_count
        c.trait_rarity[t] = 1/c.trait_freq[t]
        c.trait_rarity_normed[t] = c.trait_rarity[t]*(collection.get_avg_gm_hm()/len(c.traits))

# Loop over items and calculate statistical rarity and rarity score
for i in collection.items:
    for c, t in i.traits.items():
        i.stat_rarity = i.stat_rarity * collection.categories[c].trait_freq[t]
        i.rarity_score = i.rarity_score + collection.categories[c].trait_rarity[t]
        i.rarity_score_normed = i.rarity_score_normed + collection.categories[c].trait_rarity_normed[t]

for i in collection.items:
    # print(i.traits)
    # print(i.stat_rarity)
    # print(i.rarity_score)
    # print(i.rarity_score_normed)
    pass


# Open workbook for output to excel file, set up number formats
workbook = xlsxwriter.Workbook('baycrarity.xlsx')
ws1 = workbook.add_worksheet("Items")
ws2 = workbook.add_worksheet("Categories")
bold = workbook.add_format({'bold': True})
percent = workbook.add_format({'num_format': 10})
# Write headers for sheet 1 - items
ws1.write(0, 0, "ID", bold)
for idx2, t in enumerate(i.traits):
    ws1.write(0, 2*idx2+1, t, bold)
    ws1.write(0, 2*idx2+2, "Freq. (%)", bold)
ws1.write(0, len(i.traits)*2+1, "Stat. rarity", bold)
ws1.write(0, len(i.traits)*2+2, "Rarity score", bold)
ws1.write(0, len(i.traits)*2+3, "Rarity score normed", bold)
# Write data to sheet 1
for idx, i in enumerate(collection.items):
    ws1.write(idx+1, 0, i.ID)
    for idx2, t in enumerate(i.traits.keys()):
        if i.traits[t]:
            ws1.write(idx+1, 2*idx2+1, i.traits[t])
        else:
            ws1.write(idx+1, 2*idx2+1, "None")
        ws1.write(idx+1, 2*idx2+2, collection.categories[t].trait_freq[i.traits[t]], percent)
    ws1.write(idx+1, len(i.traits)*2+1, i.stat_rarity)
    ws1.write(idx+1, len(i.traits)*2+2, i.rarity_score)
    ws1.write(idx+1, len(i.traits)*2+3, i.rarity_score_normed)
# Write headers for sheet 2
idx = 0                                 # Counter used for writing to ws2
cat_offset = 0                          # Keep track of counts from last category
ws2.write(0, 3, "# of cats", bold)
ws2.write(0, 4, len(collection.categories))
ws2.write(0, 6, "Avg # in cat", bold)
ws2.write(0, 7, collection.get_avg_trait_per_cat())
ws2.write(0, 9, "Med # in cat", bold)
ws2.write(0, 10, collection.get_med_trait_per_cat())
ws2.write(0, 12, "GM # in cat", bold)
ws2.write(0, 13, collection.get_gm_trait_per_cat())
ws2.write(0, 15, "HM # in cat", bold)
ws2.write(0, 16, collection.get_hm_trait_per_cat())
for k, c in collection.categories.items():
    ws2.write(idx+cat_offset, 0, k, bold)
    ws2.write(idx+1+cat_offset, 0, "Rank")
    ws2.write(idx+1+cat_offset, 1, "Name")
    ws2.write(idx+1+cat_offset, 2, "Rarity Score")
    ws2.write(idx+1+cat_offset, 3, "Count")
    ws2.write(idx+1+cat_offset, 4, "Percent")
    ws2.write(idx+1+cat_offset, 5, "Rarity Score Normed")
    ws2.write(idx+1+cat_offset, 6, len(c.traits))
    for t in c.traits:
        ws2.write(idx+2+cat_offset, 0, "rank")
        ws2.write(idx+2+cat_offset, 1, t)
        ws2.write(idx+2+cat_offset, 2, c.trait_rarity[t])
        ws2.write(idx+2+cat_offset, 3, c.trait_count[t])
        ws2.write(idx+2+cat_offset, 4, c.trait_freq[t])
        ws2.write(idx+2+cat_offset, 5, c.trait_rarity_normed[t])
        idx += 1
    cat_offset += 2
workbook.close()
