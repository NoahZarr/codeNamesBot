# -*- coding: utf-8 -*-
"""
Created on Sat Dec 12 09:43:56 2020

@author: noahn

Run in cmd/conda cmd

python -m spacy download en_core_web_lg

"""

import spacy
import pandas as pd
import os
import yaml

def create_directories():
    settings = yaml.safe_load(open('settings.yaml', 'r'))
    home_dir = settings['paths']['home']
    home_dir_contents = os.listdir(home_dir)
    
    if 'codenames.py' in home_dir_contents:
        os.chdir(home_dir)
    else:
        raise ValueError("Home directory configured incorrectly. " +
                         "Can't find codenames.py in {0}""".format(home_dir))
    
    paths_to_create = [p for p in list(settings['paths'].values()) 
                       if p != home_dir and p not in home_dir_contents]
    for path in paths_to_create:
        os.mkdir(path)

    

def rebuild_card_words():
    settings = yaml.safe_load(open('settings.yaml', 'r'))
    raw_resources_path = settings['paths']['raw_resources']
    cache_path = settings['paths']['cache']
    
    with open(raw_resources_path + '/codeNamesWords.txt') as f:
        codenames_words = [w.replace('\n', '') for w in f.readlines()]
        
    with open(raw_resources_path + '/linuxWords.txt') as f:
        linux_words = [w.replace('\n', '') for w in f.readlines()]
        
    words = [w for w in linux_words if w.upper() in codenames_words] #use linux words to get proper capitalization
    
    #create cache folder if it doesnt exist
    with open(cache_path + '/card_words.txt', 'w') as f:
        f.write('\n'.join(words))
        
        
def rebuild_clue_words(nlp=None):
    
    settings = yaml.safe_load(open('settings.yaml', 'r'))
    raw_resources_path = settings['paths']['raw_resources']
    cache_path = settings['paths']['cache']
    
    print('Rebuilding list of possible clues.')
    
    if nlp is None: nlp = spacy.load('en_core_web_lg')
    
    
    with open(raw_resources_path + '/linuxWords.txt') as f:
        linux_words = [w.replace('\n', '') for w in f.readlines()]
    
    doc = nlp(' '.join(linux_words))
    
     # https://spacy.io/api/annotation  
    valid_pos = ['NOUN', 'VERB', 'ADJ', 'PROPN'] #not clear whether to include PROPN
    invalid_tags = ['NNS', 'NNPS']
    
    
    good_words = [token.lemma_ for token in doc if 
                  token.pos_ in valid_pos
                  and token.tag_ not in invalid_tags
                  and token.has_vector]
    
    good_words = list(set(good_words))
    
    with open(cache_path + '/clue_words.txt', 'w') as f:
        f.write('\n'.join(good_words))

    print('Completed list of possible clues.')
    
    
def rebuild_sim_matrix(nlp=None):
    
    print('Rebuilding similarity matrix.')

    #create dataframe with pairwise similarity between each card and possible clue
    
    if nlp is None: nlp = spacy.load('en_core_web_lg')
    
    with open('cache/card_words.txt') as f:
       all_card_words = [w.replace('\n', '') for w in f.readlines()]
       
    with open('cache/clue_words.txt') as f:
        all_clue_words = [w.replace('\n', '') for w in f.readlines()]
    
    
    card_tokens = [nlp(x) for x in all_card_words]
    clue_tokens = [nlp(x) for x in all_clue_words]  
    
    card_clue_sim_matrix = [[w1.similarity(w2) for w1 in card_tokens] for w2 in clue_tokens] 

    card_clue_sim_df = pd.DataFrame(index=all_clue_words, columns=all_card_words,
                                    data=card_clue_sim_matrix).transpose()
    
    card_clue_sim_df = card_clue_sim_df.loc[:, card_clue_sim_df.sum() > 0] # 144/18543 words missing

    card_clue_sim_df.to_csv('cache/card_to_clue_sims_all.csv')
    print('Completed similarity matrix.')


def rebuild_all():
    nlp = spacy.load('en_core_web_lg')
    
    create_directories()
    rebuild_card_words()
    rebuild_clue_words(nlp=nlp)
    rebuild_sim_matrix(nlp=nlp)
    
if __name__ == '__main__':
    rebuild_all()
    
    
    
    
    
    
    
    