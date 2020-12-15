# -*- coding: utf-8 -*-
"""
Created on Sun Dec 13 13:20:25 2020

@author: noahn
"""
 with open('cache/card_words.txt') as f:
        all_card_words = [w.replace('\n', '') for w in f.readlines()]
            
    random.seed(5)
        
    selected_card_words = random.sample(all_card_words, 25)
    
    with open('cache/clue_words.txt') as f:
        clue_words = [w.replace('\n', '') for w in f.readlines()]
    
     
  
    pairs = list(itertools.combinations(b.get_valid_targets(), 2))
    pair_df = pd.DataFrame(pairs, columns = ['target1', 'target2']) #.set_index(['target1', 'target2'])
    
    best_clues = pair_df.apply(lambda x: b.get_best_clue_for_pair(list(x)), axis=1)
    
    pair_df['clue'], pair_df['score'] = list(zip(*best_clues.values))
    
    
    best_targets_and_clue = pair_df.sort_values('score', ascending=False).iloc[0].to_dict()
    
    board_word_lemmas = [t.lemma_ for t in nlp(' '.join(b.board.words))]

      
    active_unfriendly_cards = [card for card in b.board.cards if not card.revealed and card.team != Team.blue]
    
    bad_words_dict = {}
    
    df = b.board_clue_sims.copy()
    
    
    similarity_thresholds = {Team.blue: 0.3,
                             Team.red: 0.3,
                             Team.neutral: 0.3,
                             Team.assassin: 0.3}
    
    
    danger_df = pd.DataFrame(index = df.columns)
    for unfriendly_team in [t for t in Team if t != Team.blue]:
         bad_words = [c.word for c in active_unfriendly_cards if c.team == unfriendly_team]
         sim_thresh = similarity_thresholds[unfriendly_team]
         
         too_close_to_unfriendly = (df[df.index.isin(bad_words)] > sim_thresh).any()  
         
         danger_df[unfriendly_team.name] = (df[df.index.isin(bad_words)] > sim_thresh).any()  
         
         #df.loc[:, ~too_close_to_unfriendly]
      
    danger_vec = danger_df.any(axis=1)    
    
    x = df.loc[:, danger_vec.values]
    
    w = ['fence', 'queen']
    too_close_to_unfriendly = (df[df.index.isin(w)] > sim_thresh).any()  
    
    df.loc[:, ~too_close_to_unfriendly]
    
    
    (df.loc[w,:] > sim_thresh).any(axis=1)
    
    
    similarity_thresholds = {Team.blue: 0.3,
                             Team.red: 0.3,
                             Team.neutral: 0.3,
                             Team.assassin: 0.3}
    
    
    
    danger_df[unfriendly_team.name] = (df[df.index.isin(unfriendly_words)] > sim_thresh).any()
    
    
    #######################################################
    
    #BAD CLUE LOG
    #CLUE ; INNAPROPRIATE TARGET
    
    # revolutionary ; revoluation
    
    
        
    def touch(self, word, team=None):
        if team == None:
            team = self.player_team
        revealed_cards = self.board.touch(word)
        print(revealed_cards) #make this prettier 
        
        revealed_team_counts = Counter([c.team for c in revealed_cards])
        
        for team in [Team.red, Team.blue]:
            self.scores[team] += revealed_team_counts[team]
        
        self.check_game_end()
    
    