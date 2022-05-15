import json


class Vitalik:
    # Class list of all unique trait types
    trait_types = []

    def __init__(self, idx, line):
        # Keep track of line number
        self.idx = idx
        # Initialize all trait types to None
        self.background = None
        self.skintone = None
        self.chest = None
        self.neck = None
        self.eyes = None
        self.mouth = None
        self.forehead = None
        self.ears = None
        self.back = None
        self.nose = None
        self.statue = None
        self.dupes = []
        
        # Load up line as json
        j = json.loads(line)
        # Assign any traits and track list of unique trait types
        for i in j:
            if i['trait_type'] not in Vitalik.trait_types:
                Vitalik.trait_types.append(i['trait_type'])
            if i['trait_type'] == 'Background':
                self.background = i['value']
            elif i['trait_type'] == 'Skintone':
                self.skintone = i['value']
            elif i['trait_type'] == 'Chest':
                self.chest = i['value']
            elif i['trait_type'] == 'Neck':
                self.neck = i['value']
            elif i['trait_type'] == 'Eyes':
                self.eyes = i['value']
            elif i['trait_type'] == 'Mouth':
                self.mouth = i['value']
            elif i['trait_type'] == 'Forehead':
                self.forehead = i['value']
            elif i['trait_type'] == 'Ears':
                self.ears = i['value']
            elif i['trait_type'] == 'Back':
                self.back = i['value']
            elif i['trait_type'] == 'Nose':
                self.nose = i['value']
            elif i['trait_type'] == 'Statue':
                self.statue = i['value']


# Create a list of all Vitalik objects
vitaliks = []
with open ('Trait_03.txt', 'r') as f:
    for idx, line in enumerate(f):
        line = '['+line+']'
        vitaliks.append(Vitalik(idx, line))
print(Vitalik.trait_types)

# Loop over list and check for duplicates over all attributes
for v in vitaliks:
    for v2 in vitaliks:
        # Check if all traits are the same AND that the indices are different
        if (v.background == v2.background and
            v.skintone == v2.skintone and
            v.chest == v2.chest and
            v.neck == v2.neck and
            v.eyes == v2.eyes and
            v.mouth == v2.mouth and
            v.forehead == v2.forehead and
            v.ears == v2.ears and
            v.back == v2.back and
            v.nose == v2.nose and
            v.statue == v2.statue and
            v.idx != v2.idx):
            print(v.idx, v2.idx)

dupes = []
# Loop over list and check for duplicates over all attributes except background and skintone
for v in vitaliks:
    for v2 in vitaliks:
        # Check if all traits are the same AND that the indices are different
        if (v.chest == v2.chest and
            v.neck == v2.neck and
            v.eyes == v2.eyes and
            v.mouth == v2.mouth and
            v.forehead == v2.forehead and
            v.ears == v2.ears and
            v.back == v2.back and
            v.nose == v2.nose and
            v.statue == v2.statue and
            v.idx != v2.idx):
                v.dupes.append(v2.idx)

# Write dupes to file            
for v in vitaliks:
    if v.dupes:
        with open('duplicates_exclude_bg_and_skintone_v3.txt', 'a') as outf:
            outf.write("Vitalik at line number {} has duplicates at line number(s): ".format(v.idx+1))
            for d in v.dupes:
                outf.write("{:.0f} |".format(d+1))
            outf.write("\n")

