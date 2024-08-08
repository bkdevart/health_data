# TODO: implement memory efficient method of extracting data below
import datetime as dt
import pandas as pd
import xml.etree.ElementTree as ET

XML_DATA = "../../apple_health_export/export.xml"

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

# Iteratively parse the XML file
for event, elem in ET.iterparse(XML_DATA, events=('end',)):
    if elem.tag == "Record" and elem.attrib['type'] == 'HKQuantityTypeIdentifierActiveEnergyBurned':
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


print(df.head())