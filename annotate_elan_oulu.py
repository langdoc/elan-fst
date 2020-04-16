from elan_fst import *

import sys

#print(len(str(sys.argv))

# if len(str(sys.argv)) != 3:

#print("Too many arguments provided. Please call the script as: python annotate_elan_oulu.py input.eaf target.eaf"   
#exit()

elan_file_path = sys.argv[1]
with open(elan_file_path, 'r') as file:
    elan_xml = file.read()

root = ET.fromstring(elan_xml)

elan_tokenized = tokenize_elan(root, 
                              target_type = 'word token', 
                              orig_tier_part = 'orth', 
                              new_tier_part = 'word', 
                              process = word_tokenize)

cg = Cg3("smn")
elan_annotated = annotate_elan(elan_tokenized, cg = cg)

ET.ElementTree(elan_annotated).write(sys.argv[2], xml_declaration=True, encoding='utf-8', method="xml")

#! xmllint --format - < /Users/niko/github/oulu-elan/test.eaf > /Users/niko/github/oulu-elan/test-pretty.eaf
#! xmllint --noout --schema /Users/niko/github/oulu-elan/EAFv3.0.xsd /Users/niko/github/oulu-elan/test-pretty.eaf