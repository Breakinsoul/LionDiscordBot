import json
import asyncio
import aiohttp
import aiofiles

def get_price_from_json_file(file_path, name):
    with open(file_path) as file:
        data = json.load(file)
        items = data['lines']
        for item in items:
            if item['name'] == name:
                divine_value = round(float(item.get('divineValue', 'None')), 1)
                formated_divine_value = "{:.1f}".format(divine_value).rstrip('0').rstrip('.')
                chaos_value =  int(item.get('chaosValue', 'None'))


                total_change = item.get('sparkline').get('totalChange')
                if not str(total_change).startswith('-'):
                    formated_total_change = f'+{total_change}%'
                else:
                    formated_total_change = f'{total_change}%'

                if float(formated_divine_value) < 1:
                    if total_change and total_change > 5:
                        return f' - Price: [Chaos:{chaos_value}, Change:{formated_total_change}]\n'
                    else:
                        return f' - Price: [Chaos:{chaos_value}]\n'
                else:
                    if total_change and total_change > 5:
                        return f' - Price: [Chaos:{chaos_value}, Divine:{formated_divine_value}, Change:{formated_total_change}]\n'
                    else:
                        return f' - Price: [Chaos:{chaos_value}, Divine:{formated_divine_value}]\n'

def get_currency_price_from_json_file(file_path, name):
    with open(file_path) as file:
        data = json.load(file)
        items = data['lines']
        for item in items:
            if item['currencyTypeName'] == name:
                receive_data = item.get('receive')
                pay_data = item.get('pay')

                if item.get('receiveSparkLine'):
                    receive_change = int(item['receiveSparkLine'].get('totalChange'))
                if item.get('paySparkLine'):
                    pay_change = int(item['paySparkLine'].get('totalChange'))
                receive_chaos_equivalent = f'{int(receive_data.get("value"))}'
                pay_chaos_equivalent = f'{int(1/pay_data.get("value"))}'
                if not str(receive_change).startswith('-'):
                    formated_receive_change = f'+{receive_change}%'
                else: 
                    formated_receive_change = f'{receive_change}%'
                if not str(pay_change).startswith('-'):
                    formated_pay_change = f'+{pay_change}%'
                else:
                    formated_pay_change = f'{pay_change}%'

                components = []
                if receive_data:
                    if receive_change and receive_change > 5:
                        components.append (f'[Receive: {receive_chaos_equivalent}chaos  Change: {formated_receive_change}]')
                    else:
                        components.append (f'[Receive: {receive_chaos_equivalent}chaos]')

                if pay_data:
                    if pay_change and pay_change > 5:
                        components.append (f'[Pay: {pay_chaos_equivalent}chaos Change: {formated_pay_change}]')
                    else:
                        components.append (f'[Pay: {pay_chaos_equivalent}chaos]')
                if receive_chaos_equivalent or pay_chaos_equivalent:
                    return f' - Price: {" ".join(components)}\n'
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
            total_change = item.get('sparkline').get('totalChange')
            if not str(total_change).startswith('-'):
                formated_total_change = f'+{total_change}%'
            else:
                formated_total_change = f'{total_change}%'
                
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
            if total_change and total_change > 5:
                components.append(f' Change: {formated_total_change}')

            if divine_value < 0.5:
                uniques_records.append(f'[Chaos:{chaos_value}{"".join(components)}]')
            elif chaos_value > 1000:
                uniques_records.append(f'[Divine:{formated_divine_value}{"".join(components)}]')
            else:
                uniques_records.append(f'[Chaos:{chaos_value}, Divine:{formated_divine_value}{"".join(components)}]')
        if len(uniques_records) > 1:
            return '- - Prices:\n - ' + '\n - '.join(uniques_records) + '\n'
        if len(uniques_records) > 1 and len(uniques_records) < 5:
            return ' - Prices:' + ''.join(uniques_records) + '\n'
        elif len(uniques_records) == 1:
            return ' - Price: ' + ''.join(uniques_records) + '\n'
def get_ninja_price(name, class_name, tags, rarity, league):
    splited_tags = tags.split(',')
    print(f'name: {name}, class_name: {class_name}, tags: {tags}, splited_tags: {splited_tags}')
    json_folder = 'ninja_data'
    artifacts = ['Exotic Coinage', 'Burial Medallion', 'Scrap Metal', 'Astragali']
    accessories_types = ['belt', 'ring', 'amulet']
    
    if tags == "affliction_orb,currency,default":
        return get_price_from_json_file(f'{json_folder}/{league}_DeliriumOrb.json', name)
    if tags == "currency,default" and "Fossil" not in name and "Vial" not in name:
        return get_currency_price_from_json_file(f'{json_folder}/{league}_Currency.json', name)
    if "divination_card,default" in tags:
        return get_price_from_json_file(f'{json_folder}/{league}_DivinationCard.json', name)
    if class_name == "Map Fragment" and tags == "default":
        return get_currency_price_from_json_file(f'{json_folder}/{league}_Fragment.json', name)
    if name in artifacts:
        return get_price_from_json_file(f'{json_folder}/{league}_Artifact.json', name)
    if tags == "mushrune,currency,default":
        return get_price_from_json_file(f'{json_folder}/{league}_Oil.json', name, tags)
    if "weapon,default" in tags and rarity == "Unique":
        return get_uniques_price_from_json_file(f'{json_folder}/{league}_UniqueWeapon.json', name, tags)
    if "armour,default" in tags and rarity == "Unique":
        return get_uniques_price_from_json_file(f'{json_folder}/{league}_UniqueArmour.json', name, tags)
    if any(tag in accessories_types for tag in splited_tags):
        return get_uniques_price_from_json_file(f'{json_folder}/{league}_UniqueAccessory.json', name, tags) 
    if "flask,default" in tags and rarity == "Unique":
        return get_uniques_price_from_json_file(f'{json_folder}/{league}_UniqueFlask.json', name, tags)    
    if class_name == "Jewel" and rarity == "Unique":
        return get_uniques_price_from_json_file(f'{json_folder}/{league}_UniqueJewel.json', name, tags)
    if "gem,default" in tags:
        return get_uniques_price_from_json_file(f'{json_folder}/{league}_SkillGem.json', name, tags)
    #if class_name == "Map" or class_name == "Miscellaneous Map":
        #return get_price_from_json_file(f'{json_folder}/Map.json', name)    
    if "map,default" in tags and rarity == "Unique":
        return get_uniques_price_from_json_file(f'{json_folder}/{league}_UniqueMap.json', name, tags)
    if "primordial_map,default" in tags or "maven_map" in tags:
        return get_price_from_json_file(f'{json_folder}/{league}_Invitation.json', name)   
    if "gilded_scarab,default" in tags or "polished_scarab,default" in tags or "jewelled_scarab,default" in tags or "rusted_scarab,default" in tags:
        return get_price_from_json_file(f'{json_folder}/{league}_Scarab.json', name)
    if tags == "currency,default" and "Fossil" in name:
        return get_price_from_json_file(f'{json_folder}/{league}_Fossil.json', name)
    if class_name == "Resonator":
        return get_price_from_json_file(f'{json_folder}/{league}_Resonator.json', name)
    if tags == "essence,currency,default":
        return get_price_from_json_file(f'{json_folder}/{league}_Essence.json', name)
    if "Vial of" in name:
        return get_price_from_json_file(f'{json_folder}/{league}_Vial.json', name)
    return

async def download_ninja_prices(leagues, currencyoverviews, itemoverviews):
    ninja_json_link_start = 'https://poe.ninja/api/data/'
    async with aiohttp.ClientSession() as session:
        for league in leagues:
            for currency in currencyoverviews:
                url = f'{ninja_json_link_start}currencyoverview?league={league}&type={currency}'
                async with session.get(url) as response:
                    data = await response.read()
                    async with aiofiles.open(f'ninja_data/{league}_{currency}.json', 'wb') as f:
                        await f.write(data)
                await asyncio.sleep(1)
                
            for items in itemoverviews:
                url = f'{ninja_json_link_start}itemoverview?league={league}&type={items}'
                async with session.get(url) as response:
                    data = await response.read()
                    async with aiofiles.open(f'ninja_data/{league}_{items}.json', 'wb') as f:
                        await f.write(data)
                await asyncio.sleep(1)        