import json
import os, sys
from lxml import etree

text = '''
{"help": "http://registry.open.canada.ca/api/3/action/help_show?name=datastore_search", "success": true, "result": {"sort": "contract_date desc", "resource_id": "7023455a-cc1c-44b3-9cd6-8273ca646743", "fields": [{"type": "int4", "id": "_id"}, {"type": "text", "id": "reference_number"}, {"type": "text", "id": "procurement_id"}, {"type": "text", "id": "vendor_name"}, {"type": "text", "id": "contract_date"}, {"type": "text", "id": "economic_object_code"}, {"type": "text", "id": "description_en"}, {"type": "text", "id": "description_fr"}, {"type": "text", "id": "contract_period_start"}, {"type": "text", "id": "delivery_date"}, {"type": "text", "id": "contract_value"}, {"type": "text", "id": "original_value"}, {"type": "text", "id": "amendment_value"}, {"type": "text", "id": "comments_en"}, {"type": "text", "id": "comments_fr"}, {"type": "text", "id": "additional_comments_en"}, {"type": "text", "id": "additional_comments_fr"}, {"type": "text", "id": "agreement_type_code"}, {"type": "text", "id": "commodity_type_code"}, {"type": "text", "id": "commodity_code"}, {"type": "text", "id": "country_of_origin"}, {"type": "text", "id": "solicitation_procedure_code"}, {"type": "text", "id": "limited_tendering_reason_code"}, {"type": "text", "id": "derogation_code"}, {"type": "text", "id": "aboriginal_business"}, {"type": "text", "id": "intellectual_property_code"}, {"type": "text", "id": "potential_commercial_exploitation"}, {"type": "text", "id": "former_public_servant"}, {"type": "text", "id": "standing_offer"}, {"type": "text", "id": "standing_offer_number"}, {"type": "text", "id": "document_type_code"}, {"type": "text", "id": "reporting_period"}], "records": [{"comments_en": "This call-up contains one or more amendments, which could include the exercise of an option(s) that was part of the original contract.", "intellectual_property_code": "", "description_fr": "Location de machinerie, de mobilier et d'installation de bureau, et d'autres \u00e9quipement", "limited_tendering_reason_code": "", "commodity_code": "", "agreement_type_code": "", "country_of_origin": "", "standing_offer_number": "", "original_value": "22815.14", "aboriginal_business": "", "contract_date": "2002-02-28", "additional_comments_fr": "", "potential_commercial_exploitation": "", "derogation_code": "", "contract_period_start": "2002-03-08", "contract_value": "23088.87", "document_type_code": "", "standing_offer": "", "procurement_id": "2009005969", "former_public_servant": "", "reporting_period": "", "amendment_value": "207.9", "description_en": "Rental of machinery, office furniture and fixtures and other equipment", "commodity_type_code": "", "comments_fr": "Le pr\u00e9sent commande subs\u00e9quente \u00e0 une offre \u00e0 commandes comprend une modification ou plus.", "reference_number": "C-2001-2002-Q4-00004", "_id": 69098, "solicitation_procedure_code": "", "additional_comments_en": "", "economic_object_code": "0533", "vendor_name": "SHARP ELECTRONICS OF CANADA LTD", "delivery_date": "2011-03-30"}, {"comments_en": "This contract contains one or more amendments.", "intellectual_property_code": "", "description_fr": "Ensembles de logiciels d'ordinateurs", "limited_tendering_reason_code": "", "commodity_code": "", "agreement_type_code": "", "country_of_origin": "", "standing_offer_number": "", "original_value": "475609.65", "aboriginal_business": "", "contract_date": "2002-02-28", "additional_comments_fr": "", "potential_commercial_exploitation": "", "derogation_code": "", "contract_period_start": "", "contract_value": "1020765.46", "document_type_code": "", "standing_offer": "", "procurement_id": "4657725202", "former_public_servant": "", "reporting_period": "", "amendment_value": "105108.15", "description_en": "Computer software", "commodity_type_code": "", "comments_fr": "Le pr\u00e9sent march\u00e9 comprend une modification ou plus.", "reference_number": "C-2001-2002-Q4-00005", "_id": 69099, "solicitation_procedure_code": "", "additional_comments_en": "", "economic_object_code": "1228", "vendor_name": "SOFTCHOICE CORPORATION", "delivery_date": "2009-03-31"}, {"comments_en": "This Call-Up against a standing offer contains one or more amendments, which could include the exercise of an option(s) that was part of the original contract.", "intellectual_property_code": "", "description_fr": "Location de machinerie, de mobilier et d'installation de bureau, et d'autres \u00e9quipement", "limited_tendering_reason_code": "", "commodity_code": "", "agreement_type_code": "", "country_of_origin": "", "standing_offer_number": "", "original_value": "28704", "aboriginal_business": "", "contract_date": "2002-01-24", "additional_comments_fr": "", "potential_commercial_exploitation": "", "derogation_code": "", "contract_period_start": "2002-01-24", "contract_value": "35647.32", "document_type_code": "", "standing_offer": "", "procurement_id": "2002031987", "former_public_servant": "", "reporting_period": "", "amendment_value": "", "description_en": "Rental of machinery, office furniture and fixtures and other equipment", "commodity_type_code": "", "comments_fr": "La pr\u00e9sente commande subs\u00e9quente \u00e0 une offre \u00e0 commandes comprend des modifications, lesquelles pourraient comprendre une option ou plus faisant partie du contrat original.", "reference_number": "C-2001-2002-Q4-00001", "_id": 69095, "solicitation_procedure_code": "", "additional_comments_en": "", "economic_object_code": "0533", "vendor_name": "XEROX CANADA LTD", "delivery_date": "2012-12-31"}, {"comments_en": "Competitively Sourced Contract", "intellectual_property_code": "", "description_fr": "Services de messager", "limited_tendering_reason_code": "", "commodity_code": "", "agreement_type_code": "", "country_of_origin": "", "standing_offer_number": "", "original_value": "", "aboriginal_business": "", "contract_date": "2002-01-24", "additional_comments_fr": "", "potential_commercial_exploitation": "", "derogation_code": "", "contract_period_start": "2002-01-24", "contract_value": "19978.47", "document_type_code": "", "standing_offer": "", "procurement_id": "PCO167666", "former_public_servant": "", "reporting_period": "", "amendment_value": "", "description_en": "Courier services", "commodity_type_code": "", "comments_fr": "Competitively Sourced Contract", "reference_number": "C-2001-2002-Q4-00006", "_id": 69100, "solicitation_procedure_code": "", "additional_comments_en": "", "economic_object_code": "0213", "vendor_name": "TELUS COMMUNICATIONS COMPANY", "delivery_date": "2012-12-31"}], "limit": 10, "filters": {}, "offset": 28300, "_links": {"start": "/api/action/datastore_search", "prev": "/api/action/datastore_search?offset=28290", "next": "/api/action/datastore_search?offset=28310"}, "total": 28304}}
'''
EXTRAS = ['reference_number'] #['procurement_id']
line = {}
for l in sys.stdin:
#for l in text:
#if True:
    o = json.loads(l)
    o = o["result"].get('records', '')
    print ("records: ", len(o))
    for record in o:
      for key,v in record.items():
        if key in EXTRAS:
           line[v] = key

    #print json.dumps(line)
    print ('total: ', len(line))

# Fetch an array which may be subsections
def fetchXMLArray(objectToXpath, xpath):
    return objectToXpath.xpath(xpath, namespaces={
        'gmd': 'http://www.isotc211.org/2005/gmd',
        'gco': 'http://www.isotc211.org/2005/gco',
        'gml': 'http://www.opengis.net/gml/3.2',
        'csw': 'http://www.opengis.net/cat/csw/2.0.2'})

root = etree.parse("./cra.solr.out").getroot()
print (root.tag)
i = 0
solr_refs = {}
for element in root.iter("doc"):
	i += 1
	if i > 2 and False:
		break
	#print (etree.tostring(element))
	for l in element.iter("str"):
		if l.text=="Canada Revenue Agency" and l.attrib['name']=="org_name_en":
			pass #print( etree.tostring(l))
		if l.attrib['name']=="reference_number":
			#print( etree.tostring(l))
			solr_refs[l.text] = True
#records = fetchXMLArray(root, records_root)

msd = {}
for k,v in line.items():
	if k not in solr_refs:
		msd[k] = True
i =0
for k,v in msd.items():
	i+= 1
	if i > 5: break
	print k

'''
<?xml version="1.0" encoding="UTF-8"?>
<response>

<result name="response" numFound="27992" start="0">
  <doc>
    <str name="aboriginal_business"/>
    <str name="additional_comments_en"/>
    <str name="additional_comments_fr"/>
    <str name="agreement_type_code"/>
    <str name="agreement_type_en"/>
    <str name="agreement_type_fr"/>
    <str name="amendment_value"/>
    <str name="comments_en">This contract contains one or more amendments, which could include the exercise of an option(s) that was part of the original contract.</str>
    <str name="comments_fr">Le présent marché comprend des modifications, lesquelles pourraient comprendre une option ou plus faisant partie du contrat original.</str>
    <str name="commodity_code"/>
    <str name="commodity_en"/>
    <str name="commodity_fr"/>
    <str name="commodity_type_code"/>
    <str name="commodity_type_en"/>
    <str name="commodity_type_fr"/>
    <str name="contract_date">2014-03-24T04:00:00Z</str>
    <str name="contract_period_start">2014-04-01T04:00:00Z</str>
    <str name="contract_value">146448</str>
    <str name="contract_value_en">$100,000.00 - $999,999.99</str>
    <str name="contract_value_fr">100 000,00 $ - 999 999,99 $</str>
    <str name="contract_value_range">2</str>
    <str name="country_of_origin"/>
    <str name="country_of_origin_en"/>
    <str name="country_of_origin_fr"/>
    <str name="date_month">03</str>
    <str name="date_year">2014</str>
    <str name="delivery_date">2017-03-31T04:00:00Z</str>
    <str name="derogation_code"/>
    <str name="derogation_en"/>
    <str name="derogation_fr"/>
    <str name="description_en">Transportation of things not elsewhere specified</str>
    <str name="description_fr">Transport articles (non précisé ailleurs)</str>
    <str name="document_type_code"/>
    <str name="document_type_en"/>
    <str name="document_type_fr"/>
    <str name="economic_object_code">0210</str>
    <str name="economic_object_en">Transportation of things not elsewhere specified</str>
    <str name="economic_object_fr">Transports d'objets non spécifiés ailleurs</str>
    <str name="former_public_servant"/>
    <str name="id">98b9c407a6db0fb5b5b8c4de430417a6</str>
    <str name="intellectual_property_code"/>
    <str name="intellectual_property_en"/>
    <str name="intellectual_property_fr"/>
    <str name="limited_tendering_reason_code"/>
    <str name="limited_tendering_reason_en"/>
    <str name="limited_tendering_reason_fr"/>
    <str name="org_name_code">cra-arc</str>
    <str name="org_name_en">Canada Revenue Agency</str>
    <str name="org_name_fr">Agence du revenu du Canada</str>
    <str name="original_value">46782</str>
    <str name="potential_commercial_exploitation"/>
    <str name="procurement_id">2014003379</str>
    <str name="reference_number">C-2015-2016-00001</str>
    <str name="reporting_period"/>
    <str name="solicitation_procedure_code"/>
    <str name="solicitation_procedure_en"/>
    <str name="solicitation_procedure_fr"/>
    <str name="standing_offer"/>
    <str name="standing_offer_en"/>
    <str name="standing_offer_fr"/>
    <str name="standing_offer_number"/>
    <str name="unique_id">cra-arc|C-2015-2016-00001</str>
    <str name="vendor_name">Buckham Transport Ltd</str>
  </doc>
  <doc>
    <str name="aboriginal_business"/>
    <str name="additional_comments_en"/>
    <str name="additional_comments_fr"/>
    <str name="agreement_type_code"/>
    <str name="agreement_type_en"/>
    <str name="agreement_type_fr"/>
    <str name="amendment_value"/>
    <str name="comments_en">This contract contains one or more amendments, which could include the exercise of an option(s) that was part of the original contract.</str>
    <str name="comments_fr">Le présent marché comprend des modifications, lesquelles pourraient comprendre une option ou plus faisant partie du contrat original.</str>
    <str name="commodity_code"/>
    <str name="commodity_en"/>
    <str name="commodity_fr"/>
    <str name="commodity_type_code"/>
    <str name="commodity_type_en"/>
    <str name="commodity_type_fr"/>
    <str name="contract_date">2014-05-27T04:00:00Z</str>
    <str name="contract_period_start">2014-06-15T04:00:00Z</str>
    <str name="contract_value">260849.49</str>
    <str name="contract_value_en">$100,000.00 - $999,999.99</str>
    <str name="contract_value_fr">100 000,00 $ - 999 999,99 $</str>
    <str name="contract_value_range">2</str>
    <str name="country_of_origin"/>
    <str name="country_of_origin_en"/>
    <str name="country_of_origin_fr"/>
    <str name="date_month">05</str>
    <str name="date_year">2014</str>
    <str name="delivery_date">2017-06-14T04:00:00Z</str>
    <str name="derogation_code"/>
    <str name="derogation_en"/>
    <str name="derogation_fr"/>
    <str name="description_en">Transportation of things not elsewhere specified</str>
    <str name="description_fr">Transport articles (non précisé ailleurs)</str>
    <str name="document_type_code"/>
    <str name="document_type_en"/>
    <str name="document_type_fr"/>
    <str name="economic_object_code">0210</str>
    <str name="economic_object_en">Transportation of things not elsewhere specified</str>
    <str name="economic_object_fr">Transports d'objets non spécifiés ailleurs</str>
    <str name="former_public_servant"/>
    <str name="id">ad5c888ba1ad4ccef503377f266f2b07</str>
    <str name="intellectual_property_code"/>
    <str name="intellectual_property_en"/>
    <str name="intellectual_property_fr"/>
    <str name="limited_tendering_reason_code"/>
    <str name="limited_tendering_reason_en"/>
    <str name="limited_tendering_reason_fr"/>
    <str name="org_name_code">cra-arc</str>
    <str name="org_name_en">Canada Revenue Agency</str>
    <str name="org_name_fr">Agence du revenu du Canada</str>
    <str name="original_value">86949.83</str>
    <str name="potential_commercial_exploitation"/>
    <str name="procurement_id">2015000267</str>
    <str name="reference_number">C-2015-2016-00002</str>
    <str name="reporting_period"/>
    <str name="solicitation_procedure_code"/>
    <str name="solicitation_procedure_en"/>
    <str name="solicitation_procedure_fr"/>
    <str name="standing_offer"/>
    <str name="standing_offer_en"/>
    <str name="standing_offer_fr"/>
    <str name="standing_offer_number"/>
    <str name="unique_id">cra-arc|C-2015-2016-00002</str>
    <str name="vendor_name">Planète Courrier Inc.</str>
  </doc>
</result>
<lst name="spellcheck">
  <lst name="suggestions"/>
</lst>
<lst name="spellcheck">
  <lst name="suggestions"/>
</lst>
<lst name="spellcheck">
  <lst name="suggestions"/>
</lst>
</response>
'''
