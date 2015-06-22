#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Problem 1
import xml.etree.ElementTree as ET
import pprint

def count_tags(filename):
    tags = {}
    for _, element in ET.iterparse(filename, events=("start",)):
        if element.tag in tags:
            tags[element.tag] += 1
        else:
            tags[element.tag] = 1
    return tags

def test():

    tags = count_tags('example.osm')
    pprint.pprint(tags)
    assert tags == {'bounds': 1,
                     'member': 3,
                     'nd': 4,
                     'node': 20,
                     'osm': 1,
                     'relation': 1,
                     'tag': 7,
                     'way': 1}

# Problem 2

import re

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

def key_type(element, keys):
    if element.tag == "tag":
        # YOUR CODE HERE
        k = element.attrib['k']
        if lower.search(k):
            keys['lower'] += 1
        elif lower_colon.search(k):
            keys['lower_colon'] += 1
        elif problemchars.search(k):
            keys['problemchars'] += 1
        else:
            keys['other'] += 1

    return keys

def process_map(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)

    return keys

# Problem 3

def get_user(element):
    return

def process_map(filename):
    users = set()
    for _, element in ET.iterparse(filename):
        if element.tag == "node" or element.tag == "relation" or element.tag == "way":
            uid = element.attrib['uid']
            users.add(uid)

    return users

# Problem 4

from collections import defaultdict

OSMFILE = "example.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road",
            "Trail", "Parkway", "Commons"]

mapping = { "St": "Street",
            "St.": "Street",
            "Blvd.": "Boulevard",
            "Rd.": "Road",
            "Ave": "Avenue"
            }

def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)

def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])

    return street_types

def update_name(name, mapping):
    for key in mapping:
        m = street_type_re.search(name)
        if m:
            street_type = m.group()
            if street_type == key:
                #print "street_type: " + street_type
                #print "key: " + key
                name = name.replace(street_type, mapping[key])
                print name
    return name

# Problem 5

import codecs
import json

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]

def shape_element(element):
    node = {}
    if element.tag == "node" or element.tag == "way" :

        node['id'] = element.attrib['id']
        node['type'] = element.tag
        if 'visible' in element.attrib.keys():
            node['visible'] = element.attrib['visible']
        if 'lat' in element.attrib.keys():
            node['pos'] = [float(element.attrib['lat']), float(element.attrib['lon'])]
        node['created'] = {}
        for i in CREATED:
            node['created'][i] = element.attrib[i]
        address = {}
        for tag in element.iter('tag'):
            if problemchars.search(tag.attrib['k']):
                continue
            elif tag.attrib['k'][:5] == "addr:":
                # contain the second :
                if ':' in tag.attrib['k'][5:]:
                    continue
                else:
                    address[tag.attrib['k'][5:]] = tag.attrib['v']
            else:
                node[tag.attrib['k']] = tag.attrib['v']
        if address != {}:
            node['address'] = address
        node_refs = []
        for nd in element.iter('nd'):
            node_refs.append(nd.attrib['ref'])
        if node_refs != []:
            node['node_refs'] = node_refs
        return node
    else:
        return None

def process_map(file_in, pretty = False):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data