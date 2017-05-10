# -*- coding: utf-8 -*-
"""
Created on Sun Apr 09 23:39:36 2017

@author: Tong LI
"""

# Data wrangling street map

# Use the following code to take a systematic sample of elements from your original OSM region. Try changing the value of k so that your resulting SAMPLE_FILE ends up at different sizes. When starting out, try using a larger k, then move on to an intermediate k before processing your whole dataset.
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET  # Use cElementTree or lxml if too slow

OSM_FILE = "HartfordCountry.osm"  # Replace this with your osm file
SAMPLE_FILE = "sample.osm"

k = 100 # Parameter: take every k-th top level element

def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag

    Reference:
    http://stackoverflow.com/questions/3095434/inserting-newlines-in-xml-file-generated-via-xml-etree-elementtree-in-python
    """
    context = iter(ET.iterparse(osm_file, events=('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


with open(SAMPLE_FILE, 'wb') as output:
    output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    output.write('<osm>\n  ')

    # Write every kth top level element
    for i, element in enumerate(get_element(OSM_FILE)):
        if i % k == 0:
            output.write(ET.tostring(element, encoding='utf-8'))

    output.write('</osm>')





## to use the iterative parsing to process the map file and find out not only what tags are there, but also how many, to get the feeling on how much of which data you can expect to have in the map. Fill out the count_tags function. It should return a dictionary with the tag name as the key and number of times this tag can be encountered in the map as value.


import xml.etree.cElementTree as ET
import pprint

def count_tags(filename):
    
    tags = {}
    for event, elem in ET.iterparse(filename):
        if elem.tag not in tags:
            tags[elem.tag] = 1
        else:
            tags[elem.tag] += 1
    return tags        

tags = count_tags('sample.osm')
pprint.pprint(tags)



## Auditing street names
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = "sample.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
street_types = defaultdict(set)


expected = [] 

def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)


def print_sorted_dict(d):
    keys = d.keys()
    keys = sorted(keys, key=lambda s: s.lower())
    for k in keys:
        v=d[k]
        print "%s: %d" % (k,v)
        
def is_street_name(elem):
    return (elem.attrib['k'] == "tiger:name_type")


def audit():
    osm_file = open(OSMFILE, "r")
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    pprint.pprint(dict(street_types))


audit()



## problem for the street names: Expy & Expressway, Highway $ Hwy, Ln, Passway, Rd, St, Tpke $ Turnpike, Pl



# improving street names
mapping = { "St": "Street",
            "Ave": "Avenue",
            "Rd": "Road",
            "Expy": "Expressway",
            "Hwy": "Highway",
            "Ln": "Lane",
            "Pl": "Place",
            "Tpke": "Turnpike",
            "Ter": "Terrace",
            "Dr": "Drive",
            "Ct": "Court",
            "Cemetary": "Cemetery",
            "Cir": "Circle",
            "Blvd": "Boulevard",
            "Trl": "Trail"
            }

def audit2(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types

def update_strname(name, mapping):

    sorted_keys = sorted(mapping.keys(), key=len, reverse=True) 
   
    for abbrv in sorted_keys:
        if(abbrv in name):
            #print(abbrv)
            return name.replace(abbrv, mapping[abbrv])

    return name

audit2(OSMFILE)


st_types = audit2(OSMFILE)
for st_type, ways in st_types.iteritems():
    for name in ways:
        better_name = update_strname(name, mapping)
        print name, "=>", better_name




# investigate city

city_types = set()
expectedcity = []

def auditcity():
    osm_file = open(OSMFILE, "r")
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if (tag.attrib['k'] == "tiger:county"):
                    city_types.add(tag.attrib['v'])
                
    pprint.pprint(city_types)


auditcity() # "New Haven, CT", "Hartford, CT:New Haven, CT", "Litchfield, CT:New Haven, CT"

## improve city names
mappingcity = { "Hartford, CT:New Haven, CT": "New Haven, CT",
               "Litchfield, CT:New Haven, CT": "New Haven, CT",
               "Hartford, CT:Litchfield, CT": "Litchfield, CT",
               "Hartford, CT; Tolland, CT:Tolland, CT": "Tolland, CT",
               "Hartford, CT; Tolland, CT": "Tolland, CT",
               "New London, CT:Tolland, CT": "Tolland, CT",
               "Hartford, CT:Middlesex, CT": "Middlesex, CT",
               "Middlesex, CT:New Haven, CT": "New Haven, CT",
               "Middlesex, CT:New London, CT": "New London, CT",
               "; Hartford, CT": "Hartford, CT",
               "Hartford, CT:New London, CT": "New London, CT"
               }

def auditcity2(osmfile):
    osm_file = open(osmfile, "r")
    city_types = set()
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if (tag.attrib['k'] == "tiger:county"):
                    city_types.add(tag.attrib['v'])
    osm_file.close()
    return city_types

'''
def updatecity(name, mapping): 
    words = name.split()
    for w in range(len(words)):
        if words[w] in mapping:
            words[w] = mapping[words[w]] 
            name = " ".join(words)
    return name

'''
def update_cityname(name, mappingcity):

    sorted_keys = sorted(mappingcity.keys(), key=len, reverse=True) 
   
    for abbrv in sorted_keys:
        if(abbrv in name):
            #print(abbrv)
            return name.replace(abbrv, mappingcity[abbrv])

    return name

ct_types = auditcity2(OSMFILE)

for name in ct_types:
    better_name = update_cityname(name, mappingcity)
    print name, "=>", better_name




# investigate phone

phone_types = set()
expectedphone = []

def auditphone():
    osm_file = open(OSMFILE, "r")
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if (tag.attrib['k'] == "phone"):
                    phone_types.add(tag.attrib['v'])
                                
    pprint.pprint(phone_types)


auditphone() #format needs to be unified


# improving phone numbers
mappingphone = {'+1 203 5740096': '203-574-0096',
                '+1 860 223 2885': '860-223-2885',
                '8602161255': '860-216-1255'                
                }

def auditphone2(osmfile):
    osm_file = open(osmfile, "r")
    phone_types = set()
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if (tag.attrib['k'] == "phone"):
                    phone_types.add(tag.attrib['v'])
    osm_file.close()
    return phone_types

def update_phone(name, mappingphone):

    sorted_keys = sorted(mappingphone.keys(), key=len, reverse=True) 
   
    for abbrv in sorted_keys:
        if(abbrv in name):
            #print(abbrv)
            return name.replace(abbrv, mappingphone[abbrv])

    return name

ph_types = auditphone2(OSMFILE)

for name in ph_types:
    better_name = update_phone(name, mappingphone)
    print name, "=>", better_name


#=======================================================================
import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET

import cerberus

import schema

OSM_PATH = "sample.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema




# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']



def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS, problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements

    if element.tag == 'node':
        for attrib, value in element.attrib.iteritems():
            if attrib in node_attr_fields:
                node_attribs[attrib] = value
        
        # For elements within the top element
        for secondary in element.iter():
            if secondary.tag == 'tag':
                if problem_chars.match(secondary.attrib['k']) is not None:
                    continue
                else:
                    new={}
                    new['id']=node_attribs['id']
                    if ":" not in secondary.attrib['k']:
                        new['key'] = secondary.attrib['k']
                        new['type'] = default_tag_type                        
                    else:
                        post_colon = secondary.attrib['k'].index(":") + 1
                        new['key'] = secondary.attrib['k'][post_colon:]
                        new['type'] = secondary.attrib['k'][:post_colon - 1]
                    new['value'] = secondary.attrib['v']
                    if new is not None:
                        tags.append(new)
        return {'node': node_attribs, 'node_tags': tags}
    
    elif element.tag == 'way':
        for attrib, value in element.attrib.iteritems():
            if attrib in way_attr_fields:
                way_attribs[attrib] = value

        counter = 0
        for secondary in element.iter():
            if secondary.tag == 'tag':
                if problem_chars.match(secondary.attrib['k']) is not None:
                    continue
                else:
                    new1={}
                    new1['id']=way_attribs['id']
                    if ":" not in secondary.attrib['k']:
                        new1['key'] = secondary.attrib['k']
                        new1['type'] = default_tag_type                        
                    else:
                        post_colon = secondary.attrib['k'].index(":") + 1
                        new1['key'] = secondary.attrib['k'][post_colon:]
                        new1['type'] = secondary.attrib['k'][:post_colon - 1]
                        
                    if is_street_name(secondary):
                        street_name = update_strname(secondary.attrib['v'], mapping)
                        new1['value'] = street_name
                    elif new1['key'] == 'phone':
                        phone_num = update_phone(secondary.attrib['v'], mappingphone)
                        if phone_num is not None:
                            new1['value'] = phone_num
                        else:
                            return None    
                    elif new1['key'] == 'tiger:county':
                        city = update_cityname(secondary.attrib['v'], mappingcity)
                        if city is not None:
                            new1['value'] = city
                        else:
                            return None
                    else: 
                        new1['value'] = secondary.attrib['v']
                    if new1 is not None:
                        tags.append(new1)
            elif secondary.tag == 'nd':
                newnd = {}
                newnd['id'] = way_attribs['id']
                newnd['node_id'] = secondary.attrib['ref']
                newnd['position'] = counter
                counter += 1
                way_nodes.append(newnd)
        
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}




# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_PATH, validate=False)


#====================================================================================






