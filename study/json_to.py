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

for offer in offers:
    new_color = offer['color_hex']
    if new_color not in colors:
        colors.append(new_color)

    new_body_type = offer['vehicle_info']['configuration']['body_type']
    if new_body_type not in body_types:
        body_types.append(new_body_type)

    new_vendor = offer['vehicle_info']['vendor']
    if new_vendor not in vendors:
        vendors.append(new_vendor)

    new_transmission = offer['vehicle_info']['tech_param']['transmission']
    if new_transmission not in transmissions:
        transmissions.append(new_transmission)

    new_fuel = offer['vehicle_info']['tech_param']['engine_type']
    if new_fuel not in fuels:
        fuels.append(new_fuel)

    new_volume = offer['vehicle_info']['tech_param']['displacement']
    new_volume = round(new_volume/1000, 1)
    if new_volume not in engine_volumes:
        engine_volumes.append(new_volume)

    new_power = offer['vehicle_info']['tech_param']['power']
    if new_power not in powers:
        powers.append(new_power)

    new_tags = offer['tags']
    for tag in new_tags:
        if tag not in tags:
            tags.append(tag)

print(1)

