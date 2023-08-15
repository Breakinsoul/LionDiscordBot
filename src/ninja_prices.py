import json
def get_price_from_json_file(file_path, name):
    with open(file_path) as file:
        data = json.load(file)
        items = data['lines']
        print(name)
        for item in items:
            if item['name'] == name:
                divine_value = round(float(item.get('divineValue', 'None')), 1)
                formated_divine_value = "{:.1f}".format(divine_value).rstrip('0').rstrip('.')
                chaos_value =  round(float(item.get('chaosValue', 'None')), 1)
                formated_chaos_value = "{:.1f}".format(chaos_value).rstrip('0').rstrip('.')
                if float(formated_divine_value) < 1:
                    return f' - Price: [Chaos:{formated_chaos_value}]\n'
                else:
                    return f' - Price: [Chaos:{formated_chaos_value}, Divine:{formated_divine_value}]\n'

def get_currency_price_from_json_file(file_path, name):
    with open(file_path) as file:
        data = json.load(file)
        items = data['lines']
        for item in items:
            if item['currencyTypeName'] == name:
                receive_data = item.get('receive')
                pay_data = item.get('pay')
                receive_chaos_equivalent = None
                pay_chaos_equivalent = None

                if receive_data:
                    receive_chaos_equivalent = f'{receive_data.get("value"):.2f}'

                if pay_data:
                    pay_chaos_equivalent = f'{1/pay_data.get("value"):.2f}'

                if receive_chaos_equivalent or pay_chaos_equivalent:
                    return f' - get: {receive_chaos_equivalent}c, pay: {pay_chaos_equivalent}c\n'
def get_uniques_price_from_json_file(file_path, name, tags):
    with open(file_path) as file:
        data = json.load(file)
        items = data['lines']
        uniques_records = []
        
        for item in items:
            if item['name'] != name:
                continue
            chaos_value = int(item.get('chaosValue', 'None'))
                
            divine_value = round(float(item.get('divineValue', 'None')), 1)
            formated_divine_value = "{:.1f}".format(divine_value).rstrip('0').rstrip('.')
            
            links = item.get('links', 'None')
            item_class = str(item.get('itemClass', 'None'))
            variant = item.get('variant', 'None')
            map_tier = item.get('mapTier', 'None')
            if "gem,default" in tags:
                variant = f'Level {variant}'
                if variant.endswith('c'):
                    variant = variant.replace("c", " corrupted")
            is_relic = item_class == "9"

            components = []
            if links != 'None':
                components.append(f' - {links}L')
            if is_relic:
                components.append(f' - Relic')
            if variant != 'None':
                components.append(f' - {variant}')
            if map_tier != 'None':
                components.append(f' - T{map_tier}')
            if divine_value < 0.5:
                uniques_records.append(f'[Chaos:{chaos_value}{"".join(components)}] ')
            elif chaos_value > 1000:
                uniques_records.append(f'[Divine:{formated_divine_value}{"".join(components)}] ')
            else:
                uniques_records.append(f'[Chaos:{chaos_value}, Divine:{formated_divine_value}{"".join(components)}] ')
        
        if len(uniques_records) > 1:
            return ' - Prices:' + ''.join(uniques_records) + '\n'
        else:
            return ' - Price: ' + ''.join(uniques_records) + '\n'
def get_ninja_price(name, class_name, tags, rarity):
    splited_tags = tags.split(',')
    print(f'name: {name}, class_name: {class_name}, tags: {tags}, splited_tags: {splited_tags}')
    artifacts = ['Exotic Coinage', 'Burial Medallion', 'Scrap Metal', 'Astragali']
    accessories_types = ['belt', 'ring', 'amulet']
    
    if tags == "affliction_orb,currency,default":
        return get_price_from_json_file('ninja_data/delirium_orb.json', name)
    if tags == "currency,default" and "Fossil" not in name and "Vial" not in name:
        #https://poe.ninja/api/data/currencyoverview?league=Crucible&type=Currency
        return get_currency_price_from_json_file('ninja_data/currency.json', name)
    if "divination_card,default" in tags:
        #https://poe.ninja/api/data/itemoverview?league=Crucible&type=DivinationCard
        return get_price_from_json_file('ninja_data/divination_card.json', name)
    if class_name == "Map Fragment" and tags == "default":
        #https://poe.ninja/api/data/currencyoverview?league=Crucible&type=Fragment
        return get_currency_price_from_json_file('ninja_data/fragment.json', name)
    if name in artifacts:
        #https://poe.ninja/api/data/itemoverview?league=Crucible&type=Artifact
        return get_price_from_json_file('ninja_data/artifact.json', name)
    if tags == "mushrune,currency,default":
        #https://poe.ninja/api/data/itemoverview?league=Crucible&type=Oil
        return get_price_from_json_file('ninja_data/oil.json', name, tags)
    if "weapon,default" in tags and rarity == "Unique":
        #https://poe.ninja/api/data/itemoverview?league=Crucible&type=UniqueWeapon
        return get_uniques_price_from_json_file('ninja_data/UniqueWeapon.json', name, tags)
    if "armour,default" in tags and rarity == "Unique":
        #https://poe.ninja/api/data/itemoverview?league=Crucible&type=UniqueArmour
        return get_uniques_price_from_json_file('ninja_data/UniqueArmour.json', name, tags)
    if any(tag in accessories_types for tag in splited_tags):
        #https://poe.ninja/api/data/itemoverview?league=Crucible&type=UniqueAccessory
        return get_uniques_price_from_json_file('ninja_data/UniqueAccessory.json', name, tags) 
    if "flask,default" in tags and rarity == "Unique":
        #https://poe.ninja/api/data/itemoverview?league=Crucible&type=unique-flasks
        return get_uniques_price_from_json_file('ninja_data/UniqueFlask.json', name, tags)    
    if class_name == "Jewel" and rarity == "Unique":
        #https://poe.ninja/api/data/itemoverview?league=Crucible&type=unique-jewels
        return get_uniques_price_from_json_file('ninja_data/UniqueJewel.json', name, tags)
    if "gem,default" in tags:
        #https://poe.ninja/api/data/itemoverview?league=Crucible&type=SkillGem
        return get_uniques_price_from_json_file('ninja_data/SkillGem.json', name, tags)
    #if class_name == "Map" or class_name == "Miscellaneous Map":
        #https://poe.ninja/api/data/itemoverview?league=Crucible&type=Map
        #return get_price_from_json_file('ninja_data/Map.json', name)    
    if "map,default" in tags and rarity == "Unique":
        #https://poe.ninja/api/data/itemoverview?league=Crucible&type=UniqueMap
        return get_uniques_price_from_json_file('ninja_data/UniqueMap.json', name, tags)
    if "primordial_map,default" in tags or "maven_map" in tags:
        #https://poe.ninja/api/data/itemoverview?league=Crucible&type=Invitation
        return get_price_from_json_file('ninja_data/Invitation.json', name)   
    if "gilded_scarab,default" in tags or "polished_scarab,default" in tags or "jewelled_scarab,default" in tags or "rusted_scarab,default" in tags:
        #https://poe.ninja/api/data/itemoverview?league=Crucible&type=Scarab
        return get_price_from_json_file('ninja_data/Scarab.json', name)
    if tags == "currency,default" and "Fossil" in name:
        #https://poe.ninja/api/data/itemoverview?league=Crucible&type=Fossil
        return get_price_from_json_file('ninja_data/Fossil.json', name)
    if class_name == "Resonator":
        #https://poe.ninja/api/data/itemoverview?league=Crucible&type=Resonators
        return get_price_from_json_file('ninja_data/Resonator.json', name)
    if tags == "essence,currency,default":
        #https://poe.ninja/api/data/itemoverview?league=Crucible&type=Essence
        return get_price_from_json_file('ninja_data/Essence.json', name)
    if "Vial of" in name:
        #https://poe.ninja/api/data/itemoverview?league=Crucible&type=Vial
        return get_price_from_json_file('ninja_data/Vial.json', name)
    return
