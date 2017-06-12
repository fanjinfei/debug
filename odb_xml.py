#!/usr/bin/env python

import argparse
import os
import time
import datetime
import sys
import logging
import tempfile
import gzip
import json
from collections import defaultdict
from lxml import etree

from functools import partial
import traceback
import unicodecsv
import codecs

def read_xml(filename):
    root = etree.parse(filename).getroot()
    i = 0
    refs = []
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
    

    start = root.find('application').find('parent').find('item').find(
                    'variants').find('variant')

    t = start.find('properties').find('propertyGroup')
    r = root.xpath(u'''
    //propertyRow[
        property[@name="attribute"][value[starts-with(text(),"Audience")]]]
    /property[@name="metadata"]/value/text()
''')
    print(r)

    for l in start.find('properties').findall('property'):
        if l.find('value').text:
            print(l.attrib['name'], l.find('value').text)

    print('\n\n************* custome metadata section ******************\n\n')
    for c in start.find('properties').findall('propertyGroup'):
        assert(c.attrib['name'] == 'customMetadata')
        for row in c.findall('propertyRow'):
            r = {}
            for l in row.findall('property'):
                r[l.attrib['name']] = l.find('value').text
            if r['metadata']:
                print (r)

    for l in start.find('blob'):
        print(l.attrib['name'], l.attrib['path'], l.attrib['mimeType'])
    
    return refs

def main():
    read_xml(sys.argv[1])
    
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
