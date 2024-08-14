# TODO: implement memory efficient method of extracting data below
# import datetime as dt
import pandas as pd
import xml.etree.ElementTree as ET

# /Users/brandon/Documents/Programming/python/data_analysis/health_data/apple_health_export/export.xml
XML_DATA = "../../tmp/export.xml"

records = []
# cycling data
type = [] 
sourceName = [] 
sourceVersion = [] 
device = [] 
unit = [] 
creationDate = []
startDate = [] 
endDate = [] 
value = []
birthday = ''
sex = ''
blood_type = ''

# Iteratively parse the XML file
for event, elem in ET.iterparse(XML_DATA):
# for event, elem in ET.iterparse(XML_DATA, events=('end',)):
    if elem.tag == 'Me':
        birthday = elem.attrib['HKCharacteristicTypeIdentifierDateOfBirth']
        sex = elem.attrib['HKCharacteristicTypeIdentifierBiologicalSex']
        blood_type = elem.attrib['HKCharacteristicTypeIdentifierBloodType']
    if elem.tag == "Record":
        #    if elem.attrib['type'] == 'HKCharacteristicTypeIdentifierDateOfBirth':
        # pull out columns of interest
        # records.append(elem.attrib)
        type.append(elem.attrib['type'])
        sourceName.append(elem.attrib['sourceName'])
        # sourceVersion.append(elem.attrib['sourceVersion'])
        # device.append(elem.attrib['device'])
        unit.append(elem.attrib['unit'])
        creationDate.append(elem.attrib['creationDate'])
        startDate.append(elem.attrib['startDate'])
        endDate.append(elem.attrib['endDate'])
        value.append(elem.attrib['value'])
    elem.clear()  # Clear the element to save memory

li = list(zip(type, sourceName, 
              #sourceVersion,
               # device, 
               unit,
                creationDate, startDate, endDate, value))
df = pd.DataFrame(li, columns=['type',
                            'sourceName',
                            # 'sourceVersion',
                            # 'device',
                            'unit',
                            'creationDate',
                            'startDate',
                            'endDate',
                            'value'])
df['birthday'] = birthday
df['sex'] = sex
df['blood_type'] = blood_type


print(df.head())