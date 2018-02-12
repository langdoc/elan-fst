# -*- coding:utf-8 -*-
import re, os, errno, cgi, json, xml
import numpy
print('numpy version: '+numpy.version.version)
import sys, codecs, locale, getopt
import xml.etree.ElementTree as ET
from subprocess import Popen, PIPE
from operator import itemgetter
from xml.dom.minidom import parse, parseString
from imp import reload
from collections import defaultdict

def main():
    #reload(sys)
    #sys.setdefaultencoding('utf8')
    # to be adjusted as needed
    if len(sys.argv) != 2:
        print('wrong number of arguments')
        sys.exit('Error')
    
    in_dir = sys.argv[1]
    out_dir = 'temp_python'
    cwd = os.getcwd()
    out_dir_path = os.path.join(cwd,out_dir)
    if not os.path.exists(out_dir_path):
        os.mkdir(out_dir_path)

    debug_fst = False

    # parameters to be adjusted as needed
    lang = 'sje'
    plup = Popen('which lookup', shell=True, stdout=PIPE, stderr=PIPE)
    olup, elup = plup.communicate()
    print("___ lookup is ",olup.decode())
    if not olup.decode():
        print('No lookup found, please install it!')
        sys.exit('Error')

    lookup = olup.decode().strip()
    langs_dir = '$GTHOME/langs/'
    rel_xfst_file = '/src/analyser-gt-desc.xfst'
    abs_xfst_file = langs_dir+lang+rel_xfst_file
    abs_prep_file = '$GIELLA_CORE/scripts/preprocess' #!!!!!!!
    
    prep = '| iconv -f UTF-8 -t UTF-8 |'+abs_prep_file
        
    # command to analyse the input string comming from the left of the pipeline
    cmd = "| iconv -f UTF-8 -t UTF-8 | " + lookup + " " + abs_xfst_file

    for root, dirs, files in os.walk(in_dir): # Walk directory tree
        print("Input dir {0} with {1} files ...".format(root, len(files)))

        for f in files:
            if f.endswith('eaf'):
                print('... processing ', str(f))
                tree = ET.parse(os.path.join(in_dir,f))
                f_root = tree.getroot()
                
                a_refs = f_root.findall('.//REF_ANNOTATION')
                ar_ids = []
                for arid in a_refs:
                    ar_ids.append(arid.attrib['ANNOTATION_ID'].replace('a',''))
                ar_ids = sorted(ar_ids, key=int, reverse=True)
                t_counter = int(ar_ids[0])
                #print(t_counter)

                # find the insertion positions for the generated tiers
                child_list = f_root.getchildren()
                child_positions = []
                for child in child_list:
                    c_child = child.tag
                    if child.tag == 'TIER':
                        c_child += '_' + child.attrib['TIER_ID']
                    child_positions.append(c_child)
                
                #print(child_positions)
                p_counter = -1

                participants = []
                for refTIER in f_root.findall('.//TIER[@LINGUISTIC_TYPE_REF="refT"]'):
                    current_participant = refTIER.attrib['TIER_ID'].split('@',1)[1]
                    participants.append(current_participant)
                    
                insertion_positions = {}
                for p in participants:
                     insertion_positions[p] = child_positions.index('TIER_word@'+p)
                    
                #print(insertion_positions)
                                
                # loop over all participants
                for refTIER in f_root.findall('.//TIER[@LINGUISTIC_TYPE_REF="refT"]'):
                    current_participant = refTIER.attrib['TIER_ID'].split('@',1)[1]
                    p_counter += 1
                    #print('___ ', current_participant, ' ___')

                    # create empty list for [wordID, wordform, analysis_output]
                    wlp = []
                    orth = []

                    lang = f_root.find('.//TIER[@TIER_ID="word@'+current_participant+'"]').attrib['LANG_REF']
                    print('___ current lang is ', lang, ' ___')
                    abs_xfst_file = langs_dir+lang+rel_xfst_file 
                    print('___ current xfst file is ', abs_xfst_file, ' ___')
        
                    # command to analyse the input string comming from the left of the pipeline
                    cmd = "| iconv -f UTF-8 -t UTF-8 | " + lookup + " " + abs_xfst_file
                    
                    
                    
                    #######################
                    #Tokenise if not already done
                    if not f_root.find('.//TIER[@TIER_ID="word@'+current_participant+'"]/ANNOTATION/REF_ANNOTATION'):
                        
                        print('==> Tokenising for participant ', current_participant)                        
                        word_tier = f_root.find('.//TIER[@TIER_ID="word@' + current_participant + '"]')
                        for t in f_root.findall('.//TIER[@TIER_ID="orth@'+current_participant+'"]/ANNOTATION/REF_ANNOTATION'):
        
                            ref_ID = t.attrib['ANNOTATION_ID']
                            current_orth = t[0].text
                            if not current_orth:
                                current_orth = "_DWF_"
                            p2 = Popen('echo \''+current_orth+'\''+prep, shell=True, stdout=PIPE, stderr=PIPE)
                            out, err = p2.communicate()
                            
                            current_tokens = numpy.asarray(out.decode().split('\n'))
                            current_tokens = current_tokens[:-1]
                            orth.append([ref_ID ,current_tokens])
                            print('current token: '+str(current_tokens))
                            
                        for i in range(len(orth)):
                            print("inserting token at position ", str(i+1), "/", str(len(orth)))
                            tokens = list(itemgetter(1)(orth[i]))
                            
                            for t in enumerate(tokens):
                                t_counter += 1
                                tok_a_id = 'a'+str(t_counter)
                                tok_a = ET.SubElement(word_tier, 'ANNOTATION')
                                tok_r = ET.SubElement(tok_a, 'REF_ANNOTATION')
                                tok_v = ET.SubElement(tok_r, 'ANNOTATION_VALUE')
                                tok_r.set('ANNOTATION_ID', tok_a_id)
                                tok_r.set('ANNOTATION_REF', itemgetter(0)(orth[i]))
                                if  t[0] > 0:
                                    previous_token = f_root.find('.//TIER[@TIER_ID="word@'+current_participant+'"]/ANNOTATION[last()-1]/REF_ANNOTATION').attrib['ANNOTATION_ID']
                                    tok_r.set('PREVIOUS_ANNOTATION', previous_token)
                                tok_v.text = t[1]
                                
                    #######################                    
                    
                    for t in f_root.findall('.//TIER[@TIER_ID="word@'+current_participant+'"]/ANNOTATION/REF_ANNOTATION'):
                        #//////
    
                        ref_ID = t.attrib['ANNOTATION_ID']
                        #print('_',ref_ID,'_')
                        current_wordform = t[0].text
                        # if the current word form is empty add a dummy one "_DWF_" for "Default Word Form"
                        if not current_wordform:
                            current_wordform = "_DWF_"
                        #print('... xxx ', ref_ID, ' ___ ', current_wordform)
                        p = Popen('echo '+current_wordform+cmd, shell=True, stdout=PIPE, stderr=PIPE)
                        out, err = p.communicate()
                    
#                        print("|", out.decode().split('\n', 1 ),"|")
    
                        current_analysis = filter(None,out.decode().split('\n'))
                        # fix inconsistency of TAB usage in the FST output
                        current_analysis = [w.replace('\t+','+') for w in current_analysis]
                        # get rid of the word form from the FST output 
                        current_analysis = [w.split('\t',1)[1] for w in current_analysis]
                        current_dict = {}
                    
                        for item in current_analysis:
                            key = item.split('+',1)[0]
                            value = item.split('+',1)[1]

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
                        # output of the current analysis to be added to the file
                        print(current_dict)
                        # output of the FST to compare to the current_dict
                        if debug_fst:
                            print(current_analysis)
    
                        wlp.append([ref_ID ,current_wordform, current_dict])

                    #///////////
                    i_position = insertion_positions[current_participant]+3*p_counter+1
                    #print('_ip_' + str(i_position) + '_ip_')
                    
                    # set insertion tiers OR insert generated tiers at the specified position
                    if f_root.find('.//TIER[@TIER_ID="gloss@' + current_participant + '"]') == None:
                        gloss_tier = ET.Element('TIER')
                        gloss_tier.set('LINGUISTIC_TYPE_REF', 'glossT')
                        gloss_tier.set('PARENT_REF', 'pos@'+current_participant)
                        gloss_tier.set('TIER_ID', 'gloss@' + current_participant)
                        f_root.insert(i_position, gloss_tier)
                    else:
                        gloss_tier = f_root.find('.//TIER[@TIER_ID="gloss@' + current_participant + '"]')

                    if f_root.find('.//TIER[@TIER_ID="morph@' + current_participant + '"]') == None:
                        morph_tier = ET.Element('TIER')
                        morph_tier.set('LINGUISTIC_TYPE_REF', 'morphT')
                        morph_tier.set('PARENT_REF', 'pos@' + current_participant)
                        morph_tier.set('TIER_ID', 'morph@' + current_participant)
                        f_root.insert(i_position, morph_tier)
                    else:
                        morph_tier = f_root.find('.//TIER[@TIER_ID="morph@' + current_participant + '"]')
                    
                    if f_root.find('.//TIER[@TIER_ID="pos@' + current_participant + '"]') == None:
                        pos_tier = ET.Element('TIER')
                        pos_tier.set('LINGUISTIC_TYPE_REF', 'posT')
                        pos_tier.set('PARENT_REF', 'lemma@' + current_participant)
                        pos_tier.set('TIER_ID', 'pos@' + current_participant)
                        f_root.insert(i_position, pos_tier)
                    else:
                        pos_tier = f_root.find('.//TIER[@TIER_ID="pos@' + current_participant + '"]')
                    
                    if f_root.find('.//TIER[@TIER_ID="lemma@' + current_participant + '"]') == None:
                        lemma_tier = ET.Element('TIER')
                        lemma_tier.set('LINGUISTIC_TYPE_REF', 'lemmaT')
                        lemma_tier.set('PARENT_REF', 'word@'+current_participant)
                        lemma_tier.set('TIER_ID', 'lemma@' + current_participant)
                        f_root.insert(i_position, lemma_tier)
                    else:
                        lemma_tier = f_root.find('.//TIER[@TIER_ID="lemma@' + current_participant + '"]')
                    
                    # populate all tiers
                    print('==> Populating the generated tiers for participant ', current_participant)
                    for i in range(len(wlp)):
                        print("populating lemma at position ", str(i+1), "/", str(len(wlp)))
                        lemma_dict = itemgetter(2)(wlp[i])
                        #print(wlp[i])
                        lemma_exists = False
                        if lemma_tier.find('.//ANNOTATION/REF_ANNOTATION[@ANNOTATION_REF="'+itemgetter(0)(wlp[i]) + '"]') != None:
                            lemma_exists = True
                            node = lemma_tier.find('.//ANNOTATION/REF_ANNOTATION[@ANNOTATION_REF="'+itemgetter(0)(wlp[i]) + '"]')
                            l_a_id = node.attrib['ANNOTATION_ID']
                                            
                        for l_i, l_key in enumerate(lemma_dict):
                            if not lemma_exists:
                                t_counter += 1
                                l_a_id = 'a'+str(t_counter)
                                l_a = ET.SubElement(lemma_tier, 'ANNOTATION')
                                l_r = ET.SubElement(l_a, 'REF_ANNOTATION')
                                l_v = ET.SubElement(l_r, 'ANNOTATION_VALUE')
                                l_r.set('ANNOTATION_ID', l_a_id)
                                l_r.set('ANNOTATION_REF', itemgetter(0)(wlp[i]))
                                if l_i > 0:
                                    previous_lemma = f_root.find('.//TIER[@TIER_ID="lemma@'+current_participant+'"]/ANNOTATION[last()-1]/REF_ANNOTATION').attrib['ANNOTATION_ID']
                                    l_r.set('PREVIOUS_ANNOTATION', previous_lemma)
                                l_v.text = l_key
    
                            pos_exists = False
                            if pos_tier.find('.//ANNOTATION/REF_ANNOTATION[@ANNOTATION_REF="'+l_a_id + '"]') != None:
                                node = pos_tier.find('.//ANNOTATION/REF_ANNOTATION[@ANNOTATION_REF="'+l_a_id + '"]')
                                pos_exists = True
                                p_a_id = node.attrib['ANNOTATION_ID']
                                
                            pos_dict = lemma_dict[l_key]
                            for p_i, p_key in enumerate(pos_dict):                            
                                if not pos_exists:
                                    t_counter += 1
                                    p_a_id = 'a'+str(t_counter)
                                    p_a = ET.SubElement(pos_tier, 'ANNOTATION')
                                    p_r = ET.SubElement(p_a, 'REF_ANNOTATION')
                                    p_v = ET.SubElement(p_r, 'ANNOTATION_VALUE')
                                    p_r.set('ANNOTATION_ID', p_a_id)
                                    p_r.set('ANNOTATION_REF', l_a_id)
                                    if p_i > 0:
                                        previous_pos = f_root.find('.//TIER[@TIER_ID="pos@'+current_participant+'"]/ANNOTATION[last()-1]/REF_ANNOTATION').attrib['ANNOTATION_ID']
                                        p_r.set('PREVIOUS_ANNOTATION', previous_pos)
                                    p_v.text = p_key
    
                                morph_list = pos_dict[p_key]
                                
                                if morph_tier.find('.//ANNOTATION/REF_ANNOTATION[@ANNOTATION_REF="'+p_a_id + '"]') == None:
                                    for m_i, m_m in enumerate(morph_list):
                                        t_counter += 1
                                        m_a_id = 'a'+str(t_counter)
                                    
                                        m_a_id = 'a'+str(t_counter)
                                        m_a = ET.SubElement(morph_tier, 'ANNOTATION')
                                        m_r = ET.SubElement(m_a, 'REF_ANNOTATION')
                                        m_v = ET.SubElement(m_r, 'ANNOTATION_VALUE')
                                        m_r.set('ANNOTATION_ID', m_a_id)
                                        m_r.set('ANNOTATION_REF', p_a_id)
                                        if m_i > 0:
                                            previous_morph = f_root.find('.//TIER[@TIER_ID="morph@'+current_participant+'"]/ANNOTATION[last()-1]/REF_ANNOTATION').attrib['ANNOTATION_ID']
                                            m_r.set('PREVIOUS_ANNOTATION', previous_morph)
                                        m_v.text = morph_list[m_i]
                                    
                #set lastUsedAnnotationId
                print('last used annotation after processing is ' + str(t_counter))
                f_root.find('.//PROPERTY[@NAME="lastUsedAnnotationId"]').text = str(t_counter)
                
                
                tree.write(os.path.join(out_dir_path,str(f)),
                            xml_declaration=True,encoding='utf-8',
                            method="xml")
                print('DONE ', f, '\n\n')
                
                # txt = ET.tostring(f_root)
                # text_file = open(os.path.join(out_dir_path,str(f)), "w")
                # text_file.write(xml.dom.minidom.parseString(txt).toprettyxml())
                # text_file.close()
    
    
if __name__ == "__main__":
    reload(sys)
    main()


 
