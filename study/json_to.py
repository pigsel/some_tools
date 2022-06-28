# work with big json

import json

with open("autoru.json", "r") as read_file:
    offers = json.load(read_file)

colors = []
transmissions = []
vendors = []
body_types = []
fuels = []
engine_volumes = []
powers = []
tags = []


def addtolist(old_list, new_value_path):
    if new_value_path not in old_list:
        old_list.append(new_value_path)


for offer in offers:
    addtolist(colors, offer['color_hex'])
    addtolist(body_types, offer['vehicle_info']['configuration']['body_type'])
    addtolist(vendors, offer['vehicle_info']['vendor'])
    addtolist(transmissions, offer['vehicle_info']['tech_param']['transmission'])
    addtolist(fuels, offer['vehicle_info']['tech_param']['engine_type'])
    addtolist(powers, offer['vehicle_info']['tech_param']['power'])

    new_volume = offer['vehicle_info']['tech_param']['displacement']
    new_volume = round(new_volume/1000, 1)
    if new_volume not in engine_volumes:
        engine_volumes.append(new_volume)

    for tag in offer['tags']:
        if tag not in tags:
            tags.append(tag)

print(1)

