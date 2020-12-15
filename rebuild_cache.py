# -*- coding: utf-8 -*-
"""
Created on Sat Dec 12 09:43:56 2020

@author: noahn
"""

import spacy, itertools, random
import pandas as pd
import numpy as np

RAW_RESOURCES_DIR = 'raw_resources'
CACHE_DIR = 'cache'

def rebuild_card_words():

    with open(RAW_RESOURCES_DIR + '/codeNamesWords.txt') as f:
        codenames_words = [w.replace('\n', '') for w in f.readlines()]
        
    
    with open(RAW_RESOURCES_DIR + '/linuxWords.txt') as f:
        linux_words = [w.replace('\n', '') for w in f.readlines()]
        
    words = [w for w in linux_words if w.upper() in codenames_words] #use linux words to get proper capitalization
    
    with open(CACHE_DIR + '/card_words.txt', 'w') as f:
        f.write('\n'.join(words))
        
        
def rebuild_clue_words():
    with open(RAW_RESOURCES_DIR + '/linuxWords.txt') as f:
        linux_words = [w.replace('\n', '') for w in f.readlines()]
    
    doc = nlp(' '.join(linux_words))
    
     # https://spacy.io/api/annotation  
    valid_pos = ['NOUN', 'VERB', 'ADJ']
    invalid_tags = ['NNS', 'NNPS']
    
    
    good_words = [token.lemma_ for token in doc if 
                  token.pos_ in valid_pos
                  and token.tag_ not in invalid_tags
                  and token.has_vector]
    
    good_words = list(set(good_words))
    
    with open(CACHE_DIR + '/clue_words.txt', 'w') as f:
        f.write('\n'.join(good_words))


    
    
def save_sim_matrices(seed=5):
    # normally bot should do this during init
    # can be much improved
      
    with open('cache/card_words.txt') as f:
       all_card_words = [w.replace('\n', '') for w in f.readlines()]
       
    with open('cache/clue_words.txt') as f:
        all_clue_words = [w.replace('\n', '') for w in f.readlines()]
    
    random.seed(seed)
    card_words = random.sample(all_card_words, 25)
    
    
    ##########################################################################
    ## Pairwise similarity between each of the cards - possibly not needed? ##
    ##########################################################################
    pairs = list(itertools.combinations(card_words, 2))
    pair_sims = pd.DataFrame({'w1': [p[0] for p in pairs], 'w2': [p[1] for p in pairs], 'sim': np.nan})
    
    for i, p in pair_sims.iterrows():  
       pair_sims.loc[i, 'sim'] = nlp(p['w1']).similarity(nlp(p['w2']))

    df_upper = pair_sims.pivot_table(index = 'w1', columns = 'w2', values = 'sim')
    df_lower = pair_sims.pivot_table(index = 'w2', columns = 'w1', values = 'sim')
    pair_sim_matrix = df_upper.combine_first(df_lower)

    pair_sim_matrix.to_csv('cache/card_words_pairwise_sims_seed{0}.csv'.format(seed), index=False)
    
    
    ##########################################################################
    ## Pairwise similarity between each card and possible clue              ##
    ##########################################################################
    
    
    valid_clue_words = [c for c in all_clue_words if c not in card_words]
    
    card_tokens = [nlp(x) for x in card_words]
    clue_tokens = [nlp(x) for x in valid_clue_words]  
    
    card_clue_sim_matrix = [[w1.similarity(w2) for w1 in card_tokens] for w2 in clue_tokens] #why is this giving me an empty vector warning?

    card_clue_sim_df = pd.DataFrame(index=valid_clue_words, columns=card_words, data=card_clue_sim_matrix).transpose()
    card_clue_sim_df = card_clue_sim_df.loc[:, card_clue_sim_df.sum() > 0]

    
    card_clue_sim_df.to_csv('cache/card_to_clue_sims_seed{0}.csv'.format(seed))


#TODO: rebuild clue list 

nlp = spacy.load('en_core_web_lg')
doc = nlp(' '.join(linux_words))

for token in doc:
    print(token.text, token.pos_)
    

bad_words = [token.text for token in doc if token.pos_ not in usable_pos_tags]


with open(CACHE_DIR + '/clue_words.txt', 'w') as f:
        f.write('\n'.join(good_words))
        
        
if False:

    pairs = list(itertools.combinations(words, 2))
    
    pdf = pd.DataFrame({'w1': [p[0] for p in pairs], 'w2': [p[1] for p in pairs], 'sim': np.nan})
    
    #pdf = pdf.head().copy()
    
    for i, p in pdf.iterrows():
        #getting sims and saving them separately as creating the df directly may have
        #overheated cpu?
        pdf.loc[i, 'sim'] = nlp(p['w1']).similarity(nlp(p['w2']))
        
        if i % 5000 == 0:
            print(f'Done up to row {i}, saving...')
            pdf.to_csv('pairwise_similarities.csv')
    print('Done with pairwise similarities.')
    pdf.to_csv('pairwise_similarities.csv')   

t= nlp('revolution')[0]

def dump(obj):
  for attr in dir(obj):
    if str(attr) in ['vector', 'tensor']:
        continue
    print("obj.%s = %r" % (attr, getattr(obj, attr)))