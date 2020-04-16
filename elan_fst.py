from nltk.tokenize import word_tokenize
import xml.etree.ElementTree as ET
from operator import itemgetter
import re
from uralicNLP.cg3 import Cg3

def get_elan_info(root, orig_tier_part = 'orth'):

    transcription_tiers = []

    max_id = int(root.find(".//HEADER/PROPERTY[@NAME='lastUsedAnnotationId']").text) + 1

    for tier in root.findall(".//TIER"):

        if orig_tier_part in tier.get('TIER_ID'):

            tier_info = {}

            annotations = []

            for annotation in tier.findall('.//ANNOTATION//ANNOTATION_VALUE/..'):

                annotations.append((annotation.get("ANNOTATION_ID"), annotation.find(".//ANNOTATION_VALUE").text))

            tier_info['tier_id'] = tier.get('TIER_ID')
            tier_info['participant'] = tier.get("PARTICIPANT")
            tier_info['annotations'] = annotations

            transcription_tiers.append(tier_info)
            
    return(transcription_tiers, max_id)

def check_tiers_with_type(root, tier_type):

    for tier in root.findall(".//TIER[@LINGUISTIC_TYPE_REF='{tier_types}']"):

        root.remove(tier)
            
    return(root)

def get_last_tier_position(root):

    tier_positions = []

    for number, item in enumerate(list(root)):

        if item.tag == 'TIER':

            tier_positions.append(number)

    return(max(tier_positions))

def tokenize_elan(root, target_type = 'word token', orig_tier_part = 'orth', new_tier_part = 'word', process = word_tokenize):
    
    transcription_tiers, max_id = get_elan_info(root, orig_tier_part)
    
    for tier in transcription_tiers:

        word_tier_id = tier['tier_id'].replace(orig_tier_part, new_tier_part)

        #new_word_tier = ET.Element('TIER', DEFAULT_LOCALE='en', LINGUISTIC_TYPE_REF=target_type, PARENT_REF=tier['tier_id'], TIER_ID = word_tier_id)
        word_tier = root.find(f".//TIER[@TIER_ID='{word_tier_id}']")
        
        root.remove(word_tier)

        for annotations in tier['annotations']:

            transcription = annotations[1]
            annotation_ref = annotations[0]

            for position, word in enumerate(process(transcription)):

                annotation = ET.Element("ANNOTATION")

                if position == 0:

                    ref_annotation = ET.Element("REF_ANNOTATION", ANNOTATION_ID = f'a{str(max_id)}', ANNOTATION_REF = f'{annotation_ref}')

                else:

                    ref_annotation = ET.Element("REF_ANNOTATION", ANNOTATION_ID = f'a{str(max_id)}', ANNOTATION_REF = f'{annotation_ref}', PREVIOUS_ANNOTATION = f'a{str(max_id - 1)}')

                annotation_value = ET.Element("ANNOTATION_VALUE")
                annotation_value.text = word

                ref_annotation.insert(len(ref_annotation), annotation_value)

                annotation.insert(len(annotation), ref_annotation)

                word_tier.insert(len(word_tier), annotation)

                max_id += 1
                
        position = get_last_tier_position(root)

        root.insert(position + 1, word_tier)
    
    root.find(".//HEADER/PROPERTY[@NAME='lastUsedAnnotationId']").text = str(max_id)
    return(root)

def annotate_elan(root, cg, orig_tier_part = 'word', lemma_tier_part = 'lemma', pos_tier_part = 'pos', morph_tier_part = 'morph', syntax_tier_part = 'syntax', syntax = False):
    
    transcription_tiers, max_id = get_elan_info(root, orig_tier_part)

    a_refs = root.findall('.//REF_ANNOTATION')
    ar_ids = []
    for arid in a_refs:
        ar_ids.append(arid.attrib['ANNOTATION_ID'].replace('a',''))
    ar_ids = sorted(ar_ids, key=int, reverse=True)
    t_counter = int(ar_ids[0])

    child_list = root.getchildren()
    child_positions = []
    for child in child_list:
        c_child = child.tag
        if child.tag == 'TIER':
            c_child += '_' + child.attrib['TIER_ID']
        child_positions.append(c_child)

    p_counter = -1
    
    for tier in transcription_tiers:
        
        # Both of the operations here should be done with distinct functions
        # Tier types need to be arguments
        
        morph_tier_id = tier['tier_id'].replace(orig_tier_part, morph_tier_part)
        pos_tier_id = tier['tier_id'].replace(orig_tier_part, pos_tier_part)
        lemma_tier_id = tier['tier_id'].replace(orig_tier_part, lemma_tier_part)
        syntax_tier_id = tier['tier_id'].replace(orig_tier_part, syntax_tier_part)

        morph_tier = root.find(f".//TIER[@TIER_ID='{morph_tier_id}']")
        pos_tier = root.find(f".//TIER[@TIER_ID='{pos_tier_id}']")
        lemma_tier = root.find(f".//TIER[@TIER_ID='{lemma_tier_id}']")
        syntax_tier = root.find(f".//TIER[@TIER_ID='{syntax_tier_id}']")
        
        i_position = get_last_tier_position(root)
        
        if root.find(f".//TIER[@TIER_ID='{morph_tier_id}']") == None:
            morph_tier = ET.Element('TIER')
            morph_tier.set('LINGUISTIC_TYPE_REF', 'morphT')
            morph_tier.set('PARENT_REF', pos_tier_id)
            morph_tier.set('TIER_ID', morph_tier_id)
            root.insert(i_position, morph_tier)
        else:
            morph_tier = root.find(f".//TIER[@TIER_ID='{morph_tier_id}']")

        if root.find(f".//TIER[@TIER_ID='{pos_tier_id}']") == None:
            pos_tier = ET.Element('TIER')
            pos_tier.set('LINGUISTIC_TYPE_REF', 'posT')
            pos_tier.set('PARENT_REF', lemma_tier_id)
            pos_tier.set('TIER_ID', pos_tier_id)
            root.insert(i_position, pos_tier)
        else:
            pos_tier = root.find(f".//TIER[@TIER_ID='{pos_tier_id}']")

        if root.find(f".//TIER[@TIER_ID='{lemma_tier_id}']") == None:
            lemma_tier = ET.Element('TIER')
            lemma_tier.set('LINGUISTIC_TYPE_REF', 'lemmaT')
            lemma_tier.set('PARENT_REF', tier['tier_id'])
            lemma_tier.set('TIER_ID', lemma_tier_id)
            root.insert(i_position, lemma_tier)
        else:
            lemma_tier = root.find(f".//TIER[@TIER_ID='{lemma_tier_id}']")
            
        if syntax:

            if root.find(f".//TIER[@TIER_ID='{syntax_tier_id}']") == None:
                syntax_tier = ET.Element('TIER')
                syntax_tier.set('LINGUISTIC_TYPE_REF', 'syntaxT')
                syntax_tier.set('PARENT_REF', pos_tier_id)
                syntax_tier.set('TIER_ID', syntax_tier_id)
                root.insert(i_position, syntax_tier)
            else:
                syntax_tier = root.find(f".//TIER[@TIER_ID='{syntax_tier_id}']")

            
        wlp = []

        tokens = []

        for annotation in tier['annotations']:

            tokens.append(annotation[1])

        for token, disambiguations in zip(tier['annotations'], cg.disambiguate(tokens)):

            current_dict = {}

            for possible_word in disambiguations[1]:
                key = possible_word.lemma
                morphology = [x for x in possible_word.morphology if not x.startswith('<')]
                value = '+'.join(morphology)

                if not key in current_dict:
                    current_dict[key] = []
                current_dict[key].append(value)

            for key in current_dict:
                c_val = current_dict[key]
                pm_dict = {}

                for v in c_val:
                    xval = v.split('+')
                    pos = v.split('+',1)[0]

                    morph = '_'
                    if len(xval) > 1:
                        morph = v.split('+',1)[1]

                    if not pos in pm_dict:
                        pm_dict[pos] = []
                    pm_dict[pos].append(morph)

                current_dict[key] = pm_dict

            wlp.append([token[0], token[1], current_dict])

        for i in range(len(wlp)):

            lemma_dict = itemgetter(2)(wlp[i])
            for l_i, l_key in enumerate(lemma_dict):
                t_counter += 1
                l_a_id = 'a'+str(t_counter)
                l_a = ET.SubElement(lemma_tier, 'ANNOTATION')
                l_r = ET.SubElement(l_a, 'REF_ANNOTATION')
                l_v = ET.SubElement(l_r, 'ANNOTATION_VALUE')
                l_r.set('ANNOTATION_ID', l_a_id)
                l_r.set('ANNOTATION_REF', itemgetter(0)(wlp[i]))
                if l_i > 0:
                    previous_lemma = root.find(f".//TIER[@TIER_ID='{lemma_tier_id}']/ANNOTATION[last()-1]/REF_ANNOTATION").attrib['ANNOTATION_ID']
                    l_r.set('PREVIOUS_ANNOTATION', previous_lemma)
                l_v.text = l_key

                pos_dict = lemma_dict[l_key]
                
                for p_i, p_key in enumerate(pos_dict):
                    t_counter += 1
                    p_a_id = 'a'+str(t_counter)
                    p_a = ET.SubElement(pos_tier, 'ANNOTATION')
                    p_r = ET.SubElement(p_a, 'REF_ANNOTATION')
                    p_v = ET.SubElement(p_r, 'ANNOTATION_VALUE')
                    p_r.set('ANNOTATION_ID', p_a_id)
                    p_r.set('ANNOTATION_REF', l_a_id)
                    if p_i > 0:
                        previous_pos = root.find(f".//TIER[@TIER_ID='{pos_tier_id}']/ANNOTATION[last()-1]/REF_ANNOTATION").attrib['ANNOTATION_ID']
                        p_r.set('PREVIOUS_ANNOTATION', previous_pos)
                    p_v.text = p_key

                    morph_list = pos_dict[p_key]
                    
                    for m_i, m_m in enumerate(morph_list):
                        t_counter += 1
                        m_a_id = 'a'+str(t_counter)
                        m_a = ET.SubElement(morph_tier, 'ANNOTATION')
                        m_r = ET.SubElement(m_a, 'REF_ANNOTATION')
                        m_v = ET.SubElement(m_r, 'ANNOTATION_VALUE')
                        m_r.set('ANNOTATION_ID', m_a_id)
                        m_r.set('ANNOTATION_REF', p_a_id)
                        if m_i > 0:
                            previous_morph = root.find(f".//TIER[@TIER_ID='{morph_tier_id}']/ANNOTATION[last()-1]/REF_ANNOTATION").attrib['ANNOTATION_ID']
                            m_r.set('PREVIOUS_ANNOTATION', previous_morph)
                        m_text = morph_list[m_i]
                        m_text = re.sub('\+?@.+', '', m_text)
                        if m_text == '':
                            m_text = '_'
                        m_v.text = m_text
                        
                        morph_list = pos_dict[p_key]
                        
                    if syntax:
                    
                        for s_i, s_m in enumerate(morph_list):
                            t_counter += 1
                            s_a_id = 'a'+str(t_counter)
                            s_a = ET.SubElement(syntax_tier, 'ANNOTATION')
                            s_r = ET.SubElement(s_a, 'REF_ANNOTATION')
                            s_v = ET.SubElement(s_r, 'ANNOTATION_VALUE')
                            s_r.set('ANNOTATION_ID', s_a_id)
                            s_r.set('ANNOTATION_REF', p_a_id)
                            if s_i > 0:
                                previous_syntax = root.find(f".//TIER[@TIER_ID='{syntax_tier_id}']/ANNOTATION[last()-1]/REF_ANNOTATION").attrib['ANNOTATION_ID']
                                s_r.set('PREVIOUS_ANNOTATION', previous_syntax)
                            s_text = morph_list[s_i]
                            try:
                                s_tag = re.search('(@.+?)$', s_text).group(1)
                            except AttributeError:
                                s_tag = '_' # apply your error handling

                            s_v.text = s_tag

    return(root)

