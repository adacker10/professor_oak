import hashlib
import json
import os
import subprocess
from typing import Dict
import requests

import imagehash
import PIL
import yaml

import database


def discatcher() -> None:
    owd = os.getcwd()
    wd = 'DisCatcher'
    if not os.path.exists(wd):
        subprocess.run(['git', 'clone', 'https://github.com/MikeTheShadow/DisCatcher.git'], check=True)
    os.chdir(wd)
    subprocess.run(['git', 'pull'], check=True)
    os.chdir(owd)
    hashes = {}
    phashes: Dict[str, str] = {}
    with open('imagehashes.json', mode='r') as f:
        hashes.update({value["hash"]: value["name"] for value in json.load(f)})
    with open('phashes.yaml', mode='r') as f:
        phashes.update(yaml.safe_load(f))

    for img in os.scandir(os.path.join(wd, 'pokedex')):
        with open(img.path, mode='rb') as imgfile:
            md5 = hashlib.md5(imgfile.read()).hexdigest()
            name = img.name.split('.')[0]
            name = name[0].upper() + name[1:]
            if name == 'TypeNull':
                name = 'Type: Null'
            hashes[md5] = name
        with PIL.Image.open(img.path) as image:
            phash = str(imagehash.phash(image))
            phashes[phash] = name

    with open('imagehashes.json', mode='w') as f:
        json.dump([{'name': h[1], 'hash': h[0]} for h in hashes.items()], f, indent=2)
    with open('phashes.yaml', mode='w') as f:
        yaml.dump(phashes, f)

def hash2phash() -> None:
    db = database.Database(None)
    phashes: Dict[str, str] = {}
    with open('phashes.yaml', mode='r') as f:
        phashes.update(yaml.safe_load(f))
    for img in os.scandir('images'):
        if not img.name.endswith('.jpg'):
            continue
        md5 = img.name.split('.')[0]
        pkmn = db.get_pokemon_image_by_hash(md5)
        if pkmn.pokemon is None:
            continue
        with PIL.Image.open(img.path) as image:
            phash = str(imagehash.phash(image))
            if pkmn.name:
                phashes[phash] = pkmn.name

    with open('phashes.yaml', mode='w') as f:
        yaml.dump(phashes, f)

def evolutions() -> None:
    req = requests.get('https://docs.google.com/spreadsheets/d/1OGNmAax8ncek4VIb9TaeDTnyGKH808MoTHX9x_CwC_U/export?format=tsv&id=1OGNmAax8ncek4VIb9TaeDTnyGKH808MoTHX9x_CwC_U&gid=0')
    sheet = req.content.decode('utf-8').splitlines(False)
    data = []
    columns = sheet[0].split('\t')
    columns[1] = 'First Stage ' + columns[1]
    columns[3] = 'Second Stage ' + columns[3]

    for line in sheet[1:]:
        row = line.split('\t')
        d = {}
        for i in range(len(row)):
            d[columns[i]] = row[i]
        data.append(d)
    with open('evos.yaml', mode='w') as f:
        yaml.dump(data, f)
