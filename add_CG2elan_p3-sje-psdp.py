#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import re, os#, errno, cgi, json, xml
import numpy
print('numpy version: '+numpy.version.version)
import sys#, codecs, locale, getopt
import xml.etree.ElementTree as ET
from subprocess import Popen, PIPE
#from operator import itemgetter
from imp import reload
from collections import defaultdict
from itertools import chain
import logging

def l_p_m_tree(): return defaultdict(l_p_m_tree)

def main():

#    if len(sys.argv) != 2:
#        print('wrong number of arguments')
#        sys.exit('Error')

    in_dir = sys.argv[1]
#    print('number 1: ', sys.argv[0])

    print('number 2: ', sys.argv[1])
    out_dir = 'output_input-sje'
    
    cwd = os.getcwd()
    out_dir_path = os.path.join(cwd,out_dir)
    if not os.path.exists(out_dir_path):
        os.mkdir(out_dir_path)

    #debug_fst = False

    # This sets up a logger, following these instructions:
    # https://fangpenlin.com/posts/2012/08/26/good-logging-practice-in-python/
    
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler('elan-fst.log')
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.info('+++New session+++')#why doesn't this work reliably?
    logger.info('sjeYYYYMMDDx.eaf - annotNo (partic) - lemma/pos')#

    # parameters to be adjusted as needed
	# Comment from Niko: we could also pick the language from the language attribute
    lang = 'sje'
    plup = Popen('which lookup', shell=True, stdout=PIPE, stderr=PIPE)
    olup, elup = plup.communicate()
    print("___ lookup is ",olup.decode())   #/usr/local/bin/lookup
    if not olup.decode():
        print('No lookup found, please install it!')
        sys.exit('Error')

    #lookup = olup.decode().strip()
    langs_dir = '$GTHOME/langs/'
    rel_xfst_file = '/src/analyser-gt-desc.xfst'
    abs_xfst_file = langs_dir+lang+rel_xfst_file
    abs_prep_file = '$GIELLA_CORE/scripts/preprocess'
    
    abs_gloss_file = 'sjeGlosses.xml'
    gloss_tree = ET.parse(abs_gloss_file)
    gloss_root = gloss_tree.getroot()
    
    lookup = olup.decode().strip()
    usje = "lookup -q -flags mbTT $GTHOME/langs/" + lang + "/src/analyser-gt-desc.xfst"
    cmd = "| iconv -f UTF-8 -t UTF-8 | " + lookup + " " + abs_xfst_file
    cmd2 = "| iconv -f UTF-8 -t UTF-8 | " + abs_prep_file + " | " + usje + "| $GIELLA_CORE/scripts/lookup2cg |vislcg3 -g " + langs_dir + lang + "/src/syntax/disambiguator.cg3"

    for root, dirs, files in os.walk(in_dir): # Walk directory tree
        print("Input dir {0} with {1} files ...".format(root, len(files)))

        for f in files:
            if f.endswith('eaf'):
                print('... processing ', str(f))
                tree = ET.parse(os.path.join(in_dir,f))
                f_root = tree.getroot()
                
                # set last annotation id
                a_refs = f_root.findall('.//REF_ANNOTATION')
                ar_ids = []
                for arid in a_refs:
                    ar_ids.append(arid.attrib['ANNOTATION_ID'].replace('a','').replace('nn', ''))
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
                     insertion_positions[p] = child_positions.index('TIER_ref@'+p)

                # check for cgT-type, if not extant, then add
                #set_lingTypePos = root.find('position(.//LINGUISTIC_TYPE[last()])')
                #get_some_lingType = root.find('position(.//LINGUISTIC_TYPE[@LINGUISTIC_TYPE_ID="noteT"])')

                ref_position = list(f_root).index(f_root.find('.//LINGUISTIC_TYPE[@LINGUISTIC_TYPE_ID="refT"]'))
                #print(ref_position)

                if f_root.find('.//LINGUISTIC_TYPE[@LINGUISTIC_TYPE_ID="cgT"]') == None:
                    #print(set_lingTypePos)
                    cg_type = ET.Element('LINGUISTIC_TYPE')
                    cg_type.set('CONSTRAINTS', 'Symbolic_Association')
                    cg_type.set('GRAPHIC_REFERENCES', 'false')
                    cg_type.set('TIME_ALIGNABLE', 'false')
                    cg_type.set('LINGUISTIC_TYPE_ID', 'cgT')
                    f_root.insert(ref_position+1, cg_type)
                    

                                
                # loop over all participants
                for refTIER in f_root.findall('.//TIER[@LINGUISTIC_TYPE_REF="refT"]'):
                    current_participant = refTIER.attrib['TIER_ID'].split('@',1)[1]
                    p_counter += 1
                    print('\n\n___ Current participant: ', current_participant, ' ___')
                    
                    i_position = insertion_positions[current_participant]+3*p_counter+1
                    print('_ip_' + str(i_position) + '_ip_')
                    
                    # set insertion tiers and remove child nodes OR insert generated tiers at the specified position
                    #cg-tier
                    if f_root.find('.//TIER[@TIER_ID="cg@' + current_participant + '"]') == None:
                        cg_tier = ET.Element('TIER')
                        cg_tier.set('LINGUISTIC_TYPE_REF', 'cgT')
                        cg_tier.set('PARENT_REF', 'orth@'+current_participant)
                        cg_tier.set('TIER_ID', 'cg@' + current_participant)
                        f_root.insert(i_position, cg_tier)
                    else:
                        cg_tier = f_root.find('.//TIER[@TIER_ID="cg@' + current_participant + '"]')
                        for i in range(len(cg_tier.findall('ANNOTATION'))):
                            cg_tier.remove(cg_tier[0])                   

                    #word-tier
                    if f_root.find('.//TIER[@TIER_ID="word@' + current_participant + '"]') == None:
                        word_tier = ET.Element('TIER')
                        word_tier.set('LINGUISTIC_TYPE_REF', 'wordT')
                        word_tier.set('PARENT_REF', 'orth@'+current_participant)
                        word_tier.set('TIER_ID', 'word@' + current_participant)
                        f_root.insert(i_position, word_tier)
                    else:
                        word_tier = f_root.find('.//TIER[@TIER_ID="word@' + current_participant + '"]')
                        for i in range(len(word_tier.findall('ANNOTATION'))):
                            word_tier.remove(word_tier[0])                   
                    
                    #lemma-tier
                    if f_root.find('.//TIER[@TIER_ID="lemma@' + current_participant + '"]') == None:
                        lemma_tier = ET.Element('TIER')
                        lemma_tier.set('LINGUISTIC_TYPE_REF', 'lemmaT')
                        lemma_tier.set('PARENT_REF', 'word@'+current_participant)
                        lemma_tier.set('TIER_ID', 'lemma@' + current_participant)
                        f_root.insert(i_position, lemma_tier)
                    else:
                        lemma_tier = f_root.find('.//TIER[@TIER_ID="lemma@' + current_participant + '"]')
                        for i in range(len(lemma_tier.findall('ANNOTATION'))):
                            lemma_tier.remove(lemma_tier[0])
                    
                    #pos-tier
                    if f_root.find('.//TIER[@TIER_ID="pos@' + current_participant + '"]') == None:
                        pos_tier = ET.Element('TIER')
                        pos_tier.set('LINGUISTIC_TYPE_REF', 'posT')
                        pos_tier.set('PARENT_REF', 'lemma@' + current_participant)
                        pos_tier.set('TIER_ID', 'pos@' + current_participant)
                        f_root.insert(i_position, pos_tier)
                    else:
                        pos_tier = f_root.find('.//TIER[@TIER_ID="pos@' + current_participant + '"]')
                        for i in range(len(pos_tier.findall('ANNOTATION'))):
                            pos_tier.remove(pos_tier[0])
                    
                    #morph-tier
                    if f_root.find('.//TIER[@TIER_ID="morph@' + current_participant + '"]') == None:
                        morph_tier = ET.Element('TIER')
                        morph_tier.set('LINGUISTIC_TYPE_REF', 'morphT')
                        morph_tier.set('PARENT_REF', 'pos@' + current_participant)
                        morph_tier.set('TIER_ID', 'morph@' + current_participant)
                        f_root.insert(i_position, morph_tier)
                    else:
                        morph_tier = f_root.find('.//TIER[@TIER_ID="morph@' + current_participant + '"]')
                        for i in range(len(morph_tier.findall('ANNOTATION'))):
                            morph_tier.remove(morph_tier[0])                   
                    
                    #gloss-tier
                    if f_root.find('.//TIER[@TIER_ID="gloss@' + current_participant + '"]') == None:
                        gloss_tier = ET.Element('TIER')
                        gloss_tier.set('LINGUISTIC_TYPE_REF', 'glossT')
                        gloss_tier.set('PARENT_REF', 'pos@'+current_participant)
                        gloss_tier.set('TIER_ID', 'gloss@' + current_participant)
                        f_root.insert(i_position, gloss_tier)
                    else:
                        gloss_tier = f_root.find('.//TIER[@TIER_ID="gloss@' + current_participant + '"]')
                        for i in range(len(gloss_tier.findall('ANNOTATION'))):
                            gloss_tier.remove(gloss_tier[0])
                    

                    # create empty list for [wordID, wordform, analysis_output]
                    tlpm = []	#tlpm=token,lemma,pos,morph

                    lang = f_root.find('.//TIER[@TIER_ID="word@'+current_participant+'"]').attrib['LANG_REF']
                    print('___ current lang is ', lang, ' ___')
                    
                    print('==> Tokenising for participant ', current_participant, "\n\n")
                    
                    # count iterations to show progress
                    n_annos = len(f_root.findall('.//TIER[@TIER_ID="orth@'+current_participant+'"]/ANNOTATION/REF_ANNOTATION'))
                    counter = 1
                    
                    #loop through orth-tier annotations
                    for t in f_root.findall('.//TIER[@TIER_ID="orth@'+current_participant+'"]/ANNOTATION/REF_ANNOTATION'):

                        #get current ANNOTATION_ID for orth annotation
                        ref_ID = t.attrib['ANNOTATION_ID']
                        print('**********************\n**START of utterance', str(counter)+"/"+str(n_annos), '\n**ref_ID: ',ref_ID)
                        counter +=1
                        #get current utterance (from orth annotation)
                        current_utterance = t[0].text
                        print('\n+++ Current_utterance: ',current_utterance)
                        if not current_utterance:
                            current_utterance = "_NO-UTTERANCE_"
                        #feed orthography to CG/FST
                        p3 = Popen('echo \"'+current_utterance+'\"'+cmd2, shell=True, stdout=PIPE, stderr=PIPE)
                        
                        out, err = p3.communicate()

                        #CG/FST results:
                        cgOut = out.decode()#.replace('@+','PIG ').replace('FMAINV','HOG ')
                        cgOut2 = re.sub(r'@[\+\>\<]?\w+\>?', '', cgOut) # remove syntactic flags from CG output for ELAN
                        print("CG-ANALYSIS:\n"+cgOut2)
                        cgOutTokenList = cgOut2.split('\n"')
                        #print("cgOutTokenList: ",cgOutTokenList)
                        

                        ##### 
                        ## Output complete CG analysis minus token into ELAN on a unique tier (CG@-tier)
                        ##### 
                        cgOutStr = str(cgOut2)
                        cgOutNoToken = re.sub(r'<.*"', '', cgOutStr).strip('"\n').replace('"\n\t',' | ').strip('\t').replace('\t',' ~ ').replace('\n','')
                        print("\n+++++Output for cg@"+current_participant+":\n   "+cgOutNoToken+"\n")


                        # analyse parts of "-" compounds
                        # if analysis equals "?" and word is compound
                        if cgOutNoToken.find('?')!=-1 and cgOutNoToken.find('-') != -1:
                            # find all compounds
                            pattern_comp_analyses = r'(?=(?:\||^)( ?\"?\w*-.+? ?)(?:\||$))'
                            compound_analyses = re.findall(pattern_comp_analyses, cgOutNoToken)
                            
                            for c_a in compound_analyses:
                                pattern_token = r'\"(.+?)\"'
                                compound = re.findall(pattern_token, c_a)[0]
                                compound_cg = []
                                components = compound.split("-")
                                
                                # analyse components
                                for comp in components:
                                    p = Popen('echo '+comp+cmd, shell=True, stdout=PIPE, stderr=PIPE)
                                    out, err = p.communicate()
                                    compound_analysis = str(out.decode())
                                    print(compound_analysis)
        
                                    compound_analysis = re.sub(r'(^|\n).+?\t', r'\1', compound_analysis).replace('+', ' ').strip().replace('\t', '')
                                    print(compound_analysis)
                                    compound_analysis = re.sub(r'(^|\n)(.+?) ', r' \1"\2" ', compound_analysis).replace('\n','~ ').strip()
                                    
                                    print("COMPOUND:", compound_analysis)
                                    
                                    compound_cg.append(compound_analysis)
                                
                                # replace cg analysis
                                return_string = ' # '.join(compound_cg)
                                return_string = " " + return_string + " "
                                cgOutNoToken = cgOutNoToken.replace(c_a, return_string)
                                print(cgOutNoToken)


                        t_counter += 1
                        cg_a_id = 'a'+str(t_counter)
                        #create new cg annotation (cg_a)
                        cg_a = ET.SubElement(cg_tier, 'ANNOTATION')
                        #create new cg reference annotation (cg_r)
                        cg_r = ET.SubElement(cg_a, 'REF_ANNOTATION')
                        #create new cg annotation value (cg_v)
                        cg_v = ET.SubElement(cg_r, 'ANNOTATION_VALUE')
                        #set REF_ANNOTATION ID to new cg_a_id
                        cg_r.set('ANNOTATION_ID', cg_a_id)
                        cg_r.set('ANNOTATION_REF', ref_ID)
                        cg_v.text = cgOutNoToken
                        
                        ##### 
                        ## Experimenting here to output complete CG analysis minus token into ELAN on a unique tier (CG@-tier)
                        ##### 







                        tokens_list = []

                        #for each token in current orth-tier annotation...
                        for i, cgTokenAnalysis in enumerate(cgOutTokenList):
                            #print("cgTokenAnalysis ", cgTokenAnalysis, " itemnr ", i)
                            
                            #extract token
                            token = (cgTokenAnalysis.split('<'))[1].split('>')[0]
                            # extract all lemmas
                            lemma = re.findall(r'\n\t"(.+?)"', cgTokenAnalysis)
                            # extract all analyses
                            analyses = re.findall(r'" (.+?)(?:\n|$)', cgTokenAnalysis)

                            # extract pos from analyses # is pos always 1 word?
                            pos = [x.split(' ', 1)[0] for x in analyses]
                            # insert __ if no morph annotation
                            try:
                                morph = [x.split(' ', 1)[1] for x in analyses]
                            except IndexError:
                                morph = ['__' for x in analyses]
                            
                            # analyse components if word is compound
                            for lemma_index, string in enumerate(lemma):
                                print(string)
                                print(pos)
                                if string.find('#') != -1:
                                    new_pos = []
                                    new_morph = []
                                    # get first xfst-analysis
                                    p = Popen('echo '+token+cmd, shell=True, stdout=PIPE, stderr=PIPE)
                                    out, err = p.communicate()
                                    compound_analysis = filter(None,out.decode().split('\n'))
                                    compound_analysis = [w.replace('\t+','+') for w in compound_analysis]
                                    compound_analysis = [w.split('\t',1)[1] for w in compound_analysis][0]
                                    print("COMPOUND:", compound_analysis)
                                    
                                    # split components
                                    components = compound_analysis.split('#')
                                    # exclude head
                                    components = components[:len(components)-1]
                                    # get pos and morph of components
                                    for c in components:
                                        analysis = c.split('+', 2)
                                        try:
                                            c_pos = analysis[1]
                                        except IndexError:
                                            c_pos = '__'
                                        try:
                                            c_morph = analysis[2]
                                        except IndexError:
                                            c_morph = '__'
                                        new_pos.append(c_pos)
                                        new_morph.append(c_morph)
                                        print("pos:", new_pos, "morph:", new_morph)
                                    # add component analysis to cg-output
                                    #for index, ps in enumerate(pos):
                                    pos[lemma_index] = '#'.join(new_pos)+"#"+pos[lemma_index]
                                    #for index, m in enumerate(morph):
                                    morph[lemma_index] = '#'.join(new_morph)+"#"+morph[lemma_index]

                            # analyse parts of "-" compounds
                            # if analysis equals "?" and word is compound
                            print(token, lemma, pos)
                            #sys.exit()
                            if pos[0] == "?" and token.find('-') != -1:
                                new_lemma = []
                                new_pos = []
                                new_morph = []
                                    
                                # split compound
                                components = token.split("-")
                                # analyse components
                                for comp in components:
                                    p = Popen('echo '+comp+cmd, shell=True, stdout=PIPE, stderr=PIPE)
                                    out, err = p.communicate()
                                    compound_analysis = filter(None,out.decode().split('\n'))
                                    compound_analysis = [w.replace('\t+','+') for w in compound_analysis]
                                    compound_analysis = [w.split('\t',1)[1] for w in compound_analysis][0]
                                    print("COMPOUND:", compound_analysis)
                                    
                                    # if analysis was successful, split lemma, pos and morph
                                    new_lemma.append(compound_analysis.split("+")[0])
                                    analysis = compound_analysis.split('+', 1)[1]
                                    
                                    if analysis == "?":
                                        new_pos.append("?")
                                        new_morph.append("__")
                                    else:
                                        analysis = analysis.split('+', 1)
                                        try:
                                            new_pos.append(analysis[0])
                                        except IndexError:
                                            new_pos.append("?")
                                        try:
                                            new_morph.append(analysis[1])
                                        except IndexError:
                                            new_morph.append("__")
                                    
                                # join component results
                                lemma[lemma_index] = '#'.join(new_lemma)
                                pos[lemma_index] = '#'.join(new_pos)
                                morph[lemma_index] = '#'.join(new_morph)
                                    
                            print("token:", token, "; lemma:", lemma, "; pos:", pos, "; morph:", morph)
                            
                            # list for one cgTokenAnalysis
                            analyses_list = [token, lemma, pos, morph]                            
                            tokens_list.append(analyses_list)
                            print(analyses_list)
                            ###############
                            # insert tokens for current orth-tier annotation
                            t_counter += 1
                            w_a_id = 'a'+str(t_counter)
                            #create new word annotation (w_a)
                            w_a = ET.SubElement(word_tier, 'ANNOTATION')
                            #create new word reference annotation (w_r)
                            w_r = ET.SubElement(w_a, 'REF_ANNOTATION')
                            #create new word annotation value (w_v)
                            w_v = ET.SubElement(w_r, 'ANNOTATION_VALUE')
                            #set REF_ANNOTATION ID to new w_a_id
                            w_r.set('ANNOTATION_ID', w_a_id)
                            w_r.set('ANNOTATION_REF', ref_ID)
                            #set PREVIOUS_ANNOTATION as needed
                            if i > 0:
                                # since all tokens are new, no need to find previous token. just use token id -1
                                w_r.set('PREVIOUS_ANNOTATION', 'a'+str(t_counter-1))
                            w_v.text = token
                            ###############
                            

                        print('\n**END of utterance\n**********************\n\n')
                        tlpm.append([ref_ID ,tokens_list]) # could remove ref_ID, but may be useful?
                    
                    
                    #flatten list so all words (and not utterances) are on the same level
                    temp = [x[1:] for x in tlpm]
                    all_flat = list(chain(*list(chain(*temp))))
                    print("all annotations for participant:", all_flat)
                    
                    
                    ###############
                    # populate lemma, pos, morph
                    print('==> Populating the generated tiers for participant ', current_participant)
                    #print("number of words in tier: ", len(f_root.findall('.//TIER[@TIER_ID="word@'+current_participant+'"]/ANNOTATION/REF_ANNOTATION')))
                    
                    # iterate over all previously generated word-tier annotations
                    for i, t in enumerate(f_root.findall('.//TIER[@TIER_ID="word@'+current_participant+'"]/ANNOTATION/REF_ANNOTATION')):   
                        
                        # id of orth@-tier annotation
                        orth_id = t.attrib['ANNOTATION_REF']
                        # id of ref@-tier annotation
                        ref_id = f_root.find('.//TIER[@TIER_ID="orth@'+current_participant+'"]/ANNOTATION/REF_ANNOTATION[@ANNOTATION_ID="'+orth_id+'"]').attrib['ANNOTATION_REF']
                        
                        current_analysis = all_flat[i]
                        
                        print(str(i+1)+"/"+str(len(all_flat)), "current analysis: ", current_analysis)
                        
                        ref = t.attrib['ANNOTATION_ID']
                        #print(ref)
                        
                        # set values
                        token = current_analysis[0]
                        lemmas = current_analysis[1]
                        poss = current_analysis[2]
                        morphs = current_analysis[3]

                        if poss[0] in ('?'):
#                            logger.info(f+' - '+ref_id+' (@'+current_participant+') - '+str(current_analysis))
                            logger.info(f+' - '+ref_id+' (@'+current_participant+') - '+str(current_analysis[1])+str(current_analysis[2]))
                        
                        l_p_m_dict = l_p_m_tree()
                        
                        for lemma, pos, morph in zip(lemmas, poss, morphs):
                            l_p_m_dict[lemma][pos][morph]
                        
                        #print(l_p_m_dict)
                                                
                        # insert lemmas                           
                        for j, lemma in enumerate(l_p_m_dict):
                            
                            #print(j, " ", lemma)
                            
                            t_counter += 1
                            l_a_id = 'a'+str(t_counter)
                            l_a = ET.SubElement(lemma_tier, 'ANNOTATION')
                            l_r = ET.SubElement(l_a, 'REF_ANNOTATION')
                            l_v = ET.SubElement(l_r, 'ANNOTATION_VALUE')
                            l_r.set('ANNOTATION_ID', l_a_id)
                            l_r.set('ANNOTATION_REF', ref)
                            #set PREVIOUS_ANNOTATION as needed
                            if j > 0:
                                previous_lemma = f_root.find('.//TIER[@TIER_ID="lemma@'+current_participant+'"]/ANNOTATION[last()-1]/REF_ANNOTATION').attrib['ANNOTATION_ID']
                                l_r.set('PREVIOUS_ANNOTATION', previous_lemma)
                            l_v.text = str(lemma)
                            
                            # set reference id for pos
                            lemma_ref = "a"+str(t_counter)
                            
                            # insert pos
                            for k, pos in enumerate(l_p_m_dict[lemma]):    
                                                                
                                t_counter += 1
                                p_a_id = 'a'+str(t_counter)
                                p_a = ET.SubElement(pos_tier, 'ANNOTATION')
                                p_r = ET.SubElement(p_a, 'REF_ANNOTATION')
                                p_v = ET.SubElement(p_r, 'ANNOTATION_VALUE')
                                p_r.set('ANNOTATION_ID', p_a_id)
                                p_r.set('ANNOTATION_REF', lemma_ref)
                                #set PREVIOUS_ANNOTATION as needed
                                if k > 0:
                                    previous_pos = f_root.find('.//TIER[@TIER_ID="pos@'+current_participant+'"]/ANNOTATION[last()-1]/REF_ANNOTATION').attrib['ANNOTATION_ID']
                                    p_r.set('PREVIOUS_ANNOTATION', previous_pos)
                                p_v.text = str(pos)
                                
                                # set reference id for morph
                                pos_ref = "a"+str(t_counter)
                                
                                # insert morphs
                                for l, morph in enumerate(l_p_m_dict[lemma][pos]):
                                    
                                    t_counter += 1
                                    m_a_id = 'a'+str(t_counter)
                                    m_a = ET.SubElement(morph_tier, 'ANNOTATION')
                                    m_r = ET.SubElement(m_a, 'REF_ANNOTATION')
                                    m_v = ET.SubElement(m_r, 'ANNOTATION_VALUE')
                                    m_r.set('ANNOTATION_ID', m_a_id)
                                    m_r.set('ANNOTATION_REF', pos_ref)
                                    #set PREVIOUS_ANNOTATION as needed
                                    if l > 0:
                                        previous_morph = f_root.find('.//TIER[@TIER_ID="morph@'+current_participant+'"]/ANNOTATION[last()-1]/REF_ANNOTATION').attrib['ANNOTATION_ID']
                                        m_r.set('PREVIOUS_ANNOTATION', previous_morph)
                                    m_v.text = str(morph)
                        
                        
                    ################ ADD GLOSSES ################
                    print('Inserting glosses ...')
                    # one gloss for each pos anno
                    for p_ref in f_root.findall('.//TIER[@TIER_ID="pos@'+current_participant+'"]/ANNOTATION/REF_ANNOTATION'):
                        p_id = p_ref.attrib['ANNOTATION_ID']
                        p_ref_id = p_ref.attrib['ANNOTATION_REF']
                        
                        # find lemma
                        lemma = f_root.find('.//TIER[@TIER_ID="lemma@'+current_participant+'"]/ANNOTATION/REF_ANNOTATION[@ANNOTATION_ID="'+p_ref_id+'"]/ANNOTATION_VALUE')
                        
                        # if compound, find component glosses
                        if lemma.text.find('#') != -1:
                            lemma_split = lemma.text.split('#')
                            print(lemma_split)
                            
                            all_glosses = ""
                            
                            for stem in lemma_split:
                                nodes = [elem for elem in gloss_root.findall('sje') if elem.find('orth').text==stem]
                                gloss_array = [e.find('.//glosses/gloss[@lang="eng"]').text for e in nodes]
                                if gloss_array == [None]:
                                    gloss_array = [e.find('.//glosses/gloss[@lang="swe"]').text for e in nodes]
                                    if gloss_array == [None]:
                                        gloss_array = ['']
                                all_glosses += ' | '.join(gloss_array)
                                all_glosses += ' # '
                            all_glosses = all_glosses[:len(all_glosses)-2]
                            print(all_glosses)
                        
                        else:
                            # find all possible glosses
                            nodes = [elem for elem in gloss_root.findall('sje') if elem.find('orth').text==lemma.text]
                            # concatenate glosses
                            gloss_array = [e.find('.//glosses/gloss[@lang="eng"]').text for e in nodes]
                            if gloss_array == [None]:
                                gloss_array = [e.find('.//glosses/gloss[@lang="swe"]').text for e in nodes]
                                if gloss_array == [None]:
                                    gloss_array = ['']
                            all_glosses = ' | '.join(gloss_array)
                        
                        # insert glosses
                        t_counter +=1
                        g_a_id = 'a'+str(t_counter)
                        
                        g_a = ET.SubElement(gloss_tier, 'ANNOTATION')
                        g_r = ET.SubElement(g_a, 'REF_ANNOTATION')
                        g_v = ET.SubElement(g_r, 'ANNOTATION_VALUE')
                        g_r.set('ANNOTATION_ID', g_a_id)
                        g_r.set('ANNOTATION_REF', p_id)
                        g_v.text = all_glosses
                        
                        print(lemma.text, ' : ', all_glosses)



                #set lastUsedAnnotationId
                print('last used annotation after processing is ' + str(t_counter))
                f_root.find('.//PROPERTY[@NAME="lastUsedAnnotationId"]').text = str(t_counter)
                
                
                
                tree.write(os.path.join(out_dir_path,str(f)),
                            xml_declaration=True,encoding='utf-8',
                            method="xml")
                print('DONE ', f, '\n\n')
                
                
                

                
    
    
if __name__ == "__main__":
    reload(sys)
    main()


 
