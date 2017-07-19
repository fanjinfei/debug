#!/usr/bin/env python

import argparse
import os
import time
from datetime import datetime
import sys
import logging
import tempfile
import gzip
import json
from collections import defaultdict, OrderedDict
from lxml import etree
import yaml

from functools import partial
import traceback
import unicodecsv
import codecs

presets = None
audience = None
canada_resource_type = None
canada_subject = None
canada_resource_language = None
def read_presets(filename):
    with open(filename, 'r') as f:
        _presets = yaml.load(f)
    return _presets

def read_xml(filename):
    root = etree.parse(filename).getroot()
    i = 0
    refs, extras = {}, {}
    '''
    for element in root.iter("item"):
        #print (etree.tostring(element))
        for l in element.iter("property"):
            #print(l.attrib['name'], l.text, l.find('value').text)
            print(l.attrib['name'], l.find('value').text)
            refs.append([l.attrib['name'], l])
    '''
    #print('root', root.attrib, root.tag)
    assert(root.tag=="enterpriseLibrary")
    

    variant = root.find('application').find('parent').find('item').find(
                    'variants').find('variant')
    start = variant.find('properties')

#    t = start.find('propertyGroup')
#    r = root.xpath(u''' 
#    //propertyRow[
#        property[@name="attribute"][value[starts-with(text(),"Audience")]]]
#    /property[@name="metadata"]/value/text()
# ''')
#    print(r)

    for l in start.findall('property'):
        if l.find('value').text:
            refs[l.attrib['name']] =  l.find('value').text

#    print('\n\n************* custome metadata section ******************\n\n')

    for c in start.findall('propertyGroup'):
        assert(c.attrib['name'] == 'customMetadata')
        for row in c.findall('propertyRow'):
            r = {}
            for l in row.findall('property'):
                r[l.attrib['name']] = l.find('value').text
            if r['metadata']:
                extras.update(r)
            else:
                print('discard', r)

    for l in variant.find('blob'):
        pass
        #print(l.attrib['name'], l.attrib['path'], l.attrib['mimeType'])
    
    return refs, extras

def desc(k,v):
    if 'English' in k:
        sub_key='en'
    elif 'French' in k:
        sub_key='fr'
    else:
        raise Exception('no such desc')
    return 'notes_translated', {sub_key:v}

def title(k,v):
    if 'English' in k:
        sub_key='en'
    elif 'French' in k:
        sub_key='fr'
    else:
        raise Exception('no such desc')
    return 'title_translated', {sub_key:v}

organizations = {}
def read_organizations_from_json(filename):
    with open(filename) as f:
        for line in f:
            rec = json.loads(line)
            title = rec['title'].split('|')[0].strip()
            organizations[title] = rec['id']
    print('total organizations', len(organizations))

def owner_org(k,v):
    v = v.split('|')[0].strip()
    id = organizations.get(v, None)
    if not id:
        #raise Exception('No such organiztion')
        print('No such organiztion', v)
    return 'owner_org', id
def _get_choices_value(preset, val):
    name = preset['field_name']
    res = []
    for item in preset['choices']:
        for label in item['label'].values():
            if label in val:
                res.append(item['value'])
                break
    return name, res
    
xml2obd=OrderedDict([
    ('Description English', desc),
    ('Description French', desc),
    ('Title English', title),
    ('Title French', title),
    ('Audience', lambda k,v: _get_choices_value(audience, v),),
    ('Subject', lambda k,v: _get_choices_value(canada_subject, v),),
    ('Publisher Organization', owner_org),
    #('org_title_at_publication', owner_org),

    ('Date Created', lambda k, v: ('metadata_created',v) ),
    ('Date Modified', lambda k, v: ('metadata_modified',v)),
    ('Classification Code', lambda k, v: ('doc_classification_code',v)),
    ('Creator', lambda k, v: ('author',v)), 
    ('retentionTrigger', None),
    ('retentionPeriod', None),
    ('Status Date', None),
])

xml2resource={
    'Resource Type': lambda k,v: _get_choices_value(canada_resource_type, v),
    'Record Date': lambda k,v: ( 'created', v), 
    'Unique ID': lambda k,v: ( 'unique_identifier', v), 
    'Language': lambda k,v: _get_choices_value(canada_resource_language, v),
}

def xml_obd_mapping(dict_data, map_dict):
    res = {}
    for k,f in map_dict.iteritems():
        if k in dict_data:
            v = dict_data[k]
            dict_data.pop(k)
            if not f:
                continue
            new_key, new_val = f(k,v)
            val = res.get(new_key, None)
            if isinstance(val,dict):
                val.update(new_val)
            elif isinstance(val, list):
                for _val in new_val:
                    val.append(_val)
            elif not new_val:
                pass
            else:
                res[new_key] = new_val
    return res

def get_preset(name):
    for it in presets['presets']:
        if it['preset_name']==name:
            return it['values']
    return None
def main():
    global presets, audience, canada_resource_type,canada_subject
    global canada_resource_language
    refs, extras = read_xml(sys.argv[1])
    read_organizations_from_json(sys.argv[2])
    presets = read_presets(sys.argv[3])
    audience = get_preset('canada_audience')
    canada_resource_type = get_preset('canada_resource_type')
    canada_subject = get_preset('canada_subject')
    canada_resource_language = get_preset('canada_resource_language')
    
    ds = xml_obd_mapping(refs, xml2obd)
    ds['collection'] = 'publication'

    res = xml_obd_mapping(refs, xml2resource)
    ds['resources'] = [res]
    print(json.dumps(ds))
    print(refs, extras)
    
if __name__=='__main__':
    main()

'''


<?xml version="1.0"?>
<enterpriseLibrary version="1.0" mode="create">
    <application name="OBD">
        <folder displayName="Open by Default"/>
        <parent>
            <path displayName="Open by Default"/>
            <item displayName="Advanced_Workflow_Techniques.pdf" type="OBD.record">
                <securityClearanceInfo/>
                <!--Variants-->
                <variants>
                    <variant major="-1" rendition="application/pdf" type="OBD.record">
                    <properties>
                        <property name="Title English">
                            <value>Advanced_Workflow_Techniques.pdf</value>
                        </property>
                        <property name="Description English">
                            <value>A sample description</value>
                        </property>
                        <property name="Title French">
                            <value>Techniques des processeuses</value>
                        </property>
                        <property name="Description French">
                            <value>Descrits</value>
                        </property>
                        <property name="Unique ID">
                            <value>447789</value>
                        </property>
                        <property name="Audience">
                            <value>Scientists | scientifiques</value>
                        </property>
                        <property name="Publisher Organization">
                            <value>Public Works and Government Services Canada | Travaux publics et Services gouvernementaux Canada</value>
                        </property>
                        <property name="Publisher Organization- Section">
                            <value/>
                        </property>
                        <property name="Language">
                            <value>eng - English | anglais</value>
                        </property>
                        <property name="Resource Type">
                            <value>Liscensing |Licences</value>
                        </property>
                        <property name="Resource Type">
                            <value>Guide | guide</value>
                        </property>
                        <property name="Date Created">
                            <value>2017-05-24T09:57:28</value>
                        </property>
                        <property name="Date Modified">
                            <value>2017-05-30T12:55:29</value>
                        </property>
                        <property name="Creator">
                            <value/>
                        </property>
                        <property name="Record Date">
                            <value>2017-05-24</value>
                        </property>
                        <property name="Received Date">
                            <value/>
                        </property>
                        <property name="Classification Code">
                            <value>OBD</value>
                        </property>
                        <property name="Subject">
                            <value>Open by Default</value>
                        </property>
                        <property name="Status Date">
                            <value>2017-05-30</value>
                        </property>
                        <property name="retentionTrigger">
                            <value>ACT</value>
                        </property>
                        <property name="retentionTriggerDate">
                            <value/>
                        </property>
                        <property name="retentionPeriod">
                            <value>OPENBYDEFAULTPUBLISH</value>
                        </property>
                        <propertyGroup name="customMetadata">
                            <propertyRow>
                                <property name="category">
                                    <value>Usage Conditions</value>
                                </property>
                                <property name="attribute">
                                    <value>Type &#x2013; Type</value>
                                </property>
                                <property name="metadata">
                                    <value>Liscensing |Licences</value>
                                </property>
                            </propertyRow>
                            <propertyRow>
                                <property name="category">
                                    <value>Usage Conditions</value>
                                </property>
                                <property name="attribute">
                                    <value>Description - Description</value>
                                </property>
                                <property name="metadata">
                                    <value>No restrictions -  open source</value>
                                </property>
                            </propertyRow>
                            <propertyRow>
                                <property name="category">
                                    <value>Agent</value>
                                </property>
                                <property name="attribute">
                                    <value>Agent Corporate Name - Nom de l&#x2019;institution de l&#x2019;agent</value>
                                </property>
                                <property name="metadata">
                                    <value>Public Works and Government Services Canada | Travaux publics et Services gouvernementaux Canada</value>
                                </property>
                            </propertyRow>
                            <propertyRow>
                                <property name="category">
                                    <value>Agent</value>
                                </property>
                                <property name="attribute">
                                    <value>Internal Agent Identifier &#x2013; Identificateur interne de l&#x2019;agent</value>
                                </property>
                                <property name="metadata">
                                    <value>alannah.hilt@tbs-sct.gc.ca</value>
                                </property>
                            </propertyRow>
                            <propertyRow>
                                <property name="category">
                                    <value>Agent</value>
                                </property>
                                <property name="attribute">
                                    <value>Agent Numeric ID &#x2013; Identificateur num&#xE9;rique de l&#x2019;agent</value>
                                </property>
                                <property name="metadata">
                                    <value/>
                                </property>
                            </propertyRow>
                            <propertyRow>
                                <property name="category">
                                    <value>Agent</value>
                                </property>
                                <property name="attribute">
                                    <value>Agent Name - Nom de l&#x2019;agent</value>
                                </property>
                                <property name="metadata">
                                    <value/>
                                </property>
                            </propertyRow>
                            <propertyRow>
                                <property name="category">
                                    <value>Agent</value>
                                </property>
                                <property name="attribute">
                                    <value>Agent Role - R&#xF4;le de l&#x2019;agent</value>
                                </property>
                                <property name="metadata">
                                    <value>Author | Auteur</value>
                                </property>
                            </propertyRow>
                            <propertyRow>
                                <property name="category">
                                    <value>Agent</value>
                                </property>
                                <property name="attribute">
                                    <value>Agent Position Title - Titre du poste de l&#x2019;agent</value>
                                </property>
                                <property name="metadata">
                                    <value/>
                                </property>
                            </propertyRow>
                            <propertyRow>
                                <property name="category">
                                    <value>Agent</value>
                                </property>
                                <property name="attribute">
                                    <value>Agent Section Name - Nom de la section de l&#x2019;agent</value>
                                </property>
                                <property name="metadata">
                                    <value/>
                                </property>
                            </propertyRow>
                            <propertyRow>
                                <property name="category">
                                    <value>Agent</value>
                                </property>
                                <property name="attribute">
                                    <value>Additional Agent Corporate Name &#x2013; Nom de l&#x2019;institution de l&#x2019;agent additional</value>
                                </property>
                                <property name="metadata">
                                    <value>Treasury Board | Conseil du Tr&#xE9;sor</value>
                                </property>
                            </propertyRow>
                            <propertyRow>
                                <property name="category">
                                    <value>Agent</value>
                                </property>
                                <property name="attribute">
                                    <value>External Agent &#x2013; Agent externe</value>
                                </property>
                                <property name="metadata">
                                    <value>TBS-SCT External Agent</value>
                                </property>
                            </propertyRow>
                            <propertyRow>
                                <property name="category">
                                    <value>General</value>
                                </property>
                                <property name="attribute">
                                    <value>Language &#x2013; Langue</value>
                                </property>
                                <property name="metadata">
                                    <value>eng - English | anglais</value>
                                </property>
                            </propertyRow>
                            <propertyRow>
                                <property name="category">
                                    <value>General</value>
                                </property>
                                <property name="attribute">
                                    <value>Type &#x2013; Type</value>
                                </property>
                                <property name="metadata">
                                    <value>Guide | guide</value>
                                </property>
                            </propertyRow>
                            <propertyRow>
                                <property name="category">
                                    <value>General</value>
                                </property>
                                <property name="attribute">
                                    <value>Office of Primary Interest &#x2013; Bureau de premier int&#xE9;r&#xEA;t</value>
                                </property>
                                <property name="metadata">
                                    <value>Information Management Services | Services de gestion de l&#x2019;information</value>
                                </property>
                            </propertyRow>
                            <propertyRow>
                                <property name="category">
                                    <value>General</value>
                                </property>
                                <property name="attribute">
                                    <value>Releasable to &#x2013; Diffusable aupr&#xE8;s de</value>
                                </property>
                                <property name="metadata">
                                    <value>CA - CANADA | CANADA</value>
                                </property>
                            </propertyRow>
                            <propertyRow>
                                <property name="category">
                                    <value>General</value>
                                </property>
                                <property name="attribute">
                                    <value>Jurisdiction &#x2013; Administration</value>
                                </property>
                                <property name="metadata">
                                    <value>CA - CANADA | CANADA</value>
                                </property>
                            </propertyRow>
                            <propertyRow>
                                <property name="category">
                                    <value>General</value>
                                </property>
                                <property name="attribute">
                                    <value>Audience &#x2013; Auditoire</value>
                                </property>
                                <property name="metadata">
                                    <value>Scientists | scientifiques</value>
                                </property>
                            </propertyRow>
                            <propertyRow>
                                <property name="category">
                                    <value>Open by Default</value>
                                </property>
                                <property name="attribute">
                                    <value>Open to Public</value>
                                </property>
                                <property name="metadata">
                                    <value>1</value>
                                </property>
                            </propertyRow>
                        </propertyGroup>
                    </properties>
                    <!--BLOB-->
                    <blob name="Advanced_Workflow_Techniques.pdf" path="C:\Openbydefault\Documents\Docs_ETA_108\Advanced_Workflow_Techniques.pdf" mimeType="application/pdf"/>
                </variant>
            </variants>
        </item>
    </parent>
</application>
</enterpriseLibrary>


'''
