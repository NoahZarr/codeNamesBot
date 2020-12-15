# -*- coding: utf-8 -*-
"""
Created on Sat Dec 12 09:43:56 2020

@author: noahn
"""

raise ValueError('Dont run this whole thing, are you a madman?')

import pandas as np
import numpy as np
import itertools
import spacy 


nlp = spacy.load('en_core_web_lg')




with open('cache/card_words.txt') as f:
       all_card_words = [w.replace('\n', '') for w in f.readlines()]
           
random.seed(7)
random.sample(all_card_words, 25)
 
board_words = random.sample(all_card_words, 25)


with open('cache/clue_words.txt') as f:
    all_clue_words = [w.replace('\n', '') for w in f.readlines()]
    
    
lemmas = [t.lemma_ for t in nlp(' '.join(all_clue_words))]    
tdf = pd.DataFrame({'raw': all_clue_words, 'lemma': lemmas})    

    
clue_words = random.sample([w for w in all_clue_words if w not in board_words], 1000)
    
    
pairs = list(itertools.combinations(board_words, 2))
bwpw = pd.DataFrame({'w1': [p[0] for p in pairs], 'w2': [p[1] for p in pairs], 'sim': np.nan})
    
for i, p in bwpw.iterrows():  
    bwpw.loc[i, 'sim'] = nlp(p['w1']).similarity(nlp(p['w2']))
 
bwpw.to_csv('cache/board_words_pairwise_seed5.csv', index=False)
    
df_upper = bwpw.pivot_table(index = 'w1', columns = 'w2', values = 'sim')
df_lower = bwpw.pivot_table(index = 'w2', columns = 'w1', values = 'sim')
bwpw2 = df_upper.combine_first(df_lower)

bwpw2.to_csv('cache/board_words_pairwise_matrix_seed5.csv', index=False)



big_pairs = list(itertools.product(board_words, clue_words))
big_df = pd.DataFrame({'board_word': [p[0] for p in big_pairs], 'clue_word': [p[1] for p in big_pairs], 'sim': np.nan})
    
 
bu = big_df.copy()
 
for i, p in big_df.iterrows():  
    big_df.loc[i, 'sim'] = nlp(p['board_word']).similarity(nlp(p['clue_word']))
    
    
    
big_df2 = big_df.pivot_table(index = 'board_word', columns = 'clue_word', values = 'sim')


start = time.time()
nlp('soldier').similarity(nlp('skeletons'))
end = time.time()
print(end - start)
    

t=0.013004302978515625

(t * len(all_clue_words) * 25)/60


####################################### USE THIS METHOD FOR BOARD x CLUE MATRIX


clue_lemmas = [t.lemma_ for t in nlp(' '.join(all_clue_words))]    
board_lemmas = [w.lemma_ for w in nlp(' '.join(board_words))]

clue_words = list(set([w for w in clue_lemmas if w not in board_lemmas])) #board words aren't valid clues 

list1 = [nlp(x) for x in board_words]
list2 = [nlp(x) for x in clue_words] #hm i already called nlp above, probably can improve this 


similarityMatrix = [[x.similarity(y) for x in list1] for y in list2] #why is this giving me an empty vector warning?

fdf = pd.DataFrame(index=clue_words, columns=board_words, data=similarityMatrix).transpose()

#something giving us weird words like flowcharte; drop them 
fdf2 = fdf.loc[:, fdf.sum() > 0]


fdf2.to_csv('cache/board_to_clue_sims_seed5_lemmatized.csv')


######################################################################

    
    
def myfunc1(row):
    X = str(row['A']) + 'A'
    Y = row['A'] + 50
    return [X, Y]

df = pd.DataFrame(np.random.randint(0,10,size=(2, 2)), columns=list('AB'))

tr = df.apply(myfunc1 ,axis=1)

df[['C', 'D']] = tr
    

pd.DataFrame.from_records(r.to_numpy(

