# -*- coding: utf-8 -*-
"""
Created on Sat Dec 12 09:30:41 2020

@author: noahn
"""

import random
from enum import Enum
import pandas as pd
import itertools
import time
from difflib import SequenceMatcher
from collections import OrderedDict
import numpy as np 


pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

pd.set_option('display.max_columns', 6)


class Team(Enum):
    blue = 1
    red = -1
    neutral = 0
    assassin = 9
    
    def __str__(self):
        return self.name.upper()
    

class Codenames:
    
    def __init__(self, first_team = Team.blue, player_team = Team.blue, seed=None):
        
        self.seed = seed
        if seed is not None:
            print('SEED: {0}'.format(seed))
        self.current_turn_team = first_team
        
        self.player_team = player_team
        self.other_team = Team.red if player_team == Team.blue else Team.blue
        self.player_turn_num = 0
        
        self.board = Board(first_team = first_team, seed=self.seed)
        
        self.scores = {Team.blue: 0, Team.red: 0}
        self.max_scores = {Team.blue: 8, Team.red: 8}
        self.max_scores[first_team] += 1
        self.winner = None
        self.team_hit_assasin = None
        
        self.bot = Bot(board=self.board, owner=self) 
        
    def play(self):
        while self.winner is None:
            print("{0} Team's turn!".format(self.current_turn_team.name.capitalize()))
                  
            if self.player_team == self.current_turn_team:
                
                self.player_turn_num += 1
                
                self.show()     
                clue = self.bot.play(return_clue=True)
                max_guesses = len(clue.targets) + 1
                
                for guess_num in range(1, max_guesses+1):
                    guess = self.prompt_and_validate_response(clue, guess_num, max_guesses)
                    
                    if guess == '_':
                        print('{0} team passes'.format(self.current_turn_team))
                        break

                    revealed_card = self.touch(guess, return_card = True)
                              
                    if revealed_card.team != self.player_team:
                        break
                                   
            else:
                self.simulate_turn()
                    
            self.change_team()
                   
         
    def simulate_turn(self, team=Team.red, max_num_to_touch=2):
        valid_words = self.board.get_words(team=team, revealed=False)
        num_to_touch = min(max_num_to_touch, len(valid_words))
        
        for word_to_touch in random.sample(valid_words, num_to_touch):      
            self.touch(word_to_touch, team=self.other_team)
            
     
    def prompt_and_validate_response(self, clue, guess_num, max_guesses):
       
        valid_response = None
        while valid_response is None:
            print('Guess {0}/{1}'.format(guess_num, max_guesses))
            print('Enter a card for the below clue.\nEnter _ to pass or $ to display the board again.')
            response = input(str(clue) + '\n> ')
            
            if response == '$':
                self.show()            
            elif response in self.board.get_words(revealed=False) + ['_']:
                valid_response = response
            else:
                print(f'''ERROR: {response} is not a valid guess, please enter a word on the board''')     
        return valid_response
      
      
    def touch(self, word, team=None, return_card=False):
          if team == None: team = self.player_team
          revealed_card = self.board.touch(word) 
          
          self.print_guess_result(revealed_card, current_team=team)
          
          if revealed_card.team in (Team.red, Team.blue):
              self.scores[revealed_card.team] += 1 
              self.check_game_end()
          
          if return_card:
              return revealed_card 
        
        
    def print_guess_result(self, revealed_card, current_team = None, sleep_dur = 1):
        if current_team is None: current_team = self.player_team 
        
        result_string = 'RESULT: "{0}" was a {1} card!'.format(revealed_card.word, revealed_card.team.name.upper())
        
        if revealed_card.team in (Team.red, Team.blue):
            result_string += ' +1 point {0} team.'.format(revealed_card.team.name)
           
        if revealed_card.team != current_team:
            result_string += ' Turn over.'    
            print(result_string)
        else:
            print(result_string)       
            
        time.sleep(sleep_dur)
 

    def change_team(self, sleep_dur=2):
        self.current_turn_team = Team(self.current_turn_team.value * -1)
        time.sleep(sleep_dur)
        
  
        
    def show(self, reveal_teams=False):
        self.board.show(reveal_teams=reveal_teams)
        self.print_score()
    
      
        
    def check_game_end(self):
        if self.team_hit_assasin is not None:
            print('Game Over! The {0} Team hit the assassin and loses!'.format(self.team_hit_assassin.name.capitalize()))
            self.winner = Team.red if self.team_hit_assassin == Team.blue else Team.blue
        elif self.scores[Team.blue] >= self.max_scores[Team.blue]:
            print('Game Over! Blue Team wins!')
            self.winner = Team.blue
        elif self.scores[Team.red] >= self.max_scores[Team.red]:
            print('Game Over! Red Team wins!')
            self.winner = Team.red
        
        
    def score(self, team):
        self.score[team] += 1
        
    def print_score(self):
        print('Blue team: {0}/{1}'.format(self.scores[Team.blue], self.max_scores[Team.blue]))
        print('Red team: {0}/{1}'.format(self.scores[Team.red], self.max_scores[Team.red]))
        
  
class Board:
    
    def __init__(self, first_team=Team.blue, seed=None): 
        
        
        with open('cache/card_words.txt') as f: #TODO: move to Codenames
            all_card_words = [w.replace('\n', '') for w in f.readlines()]
            
        if seed is not None:
            random.seed(seed)
        
        selected_card_words = random.sample(all_card_words, 25)                        
        teams = (8 * [Team.blue] +  8 * [Team.red] + 7 * [Team.neutral] +
                 1 * [Team.assassin] + 1 * [first_team])
        
        random.shuffle(selected_card_words)
        random.shuffle(teams)
        
        self.cards = [Card(word, team) for word, team in zip(selected_card_words, teams)]
        self.max_word_length = max([len(w) for w in selected_card_words])
        
     
                
    def show(self, reveal_teams=False):
        
        word_display_length = max(12, self.max_word_length + 1)
        padding_fmt = '{:<xx}'.replace('xx', str(word_display_length)) #format was giving errors

            
        row_indices = list(range(0, 25, 5)) #grid is always 5x5
            
        grid_word_rows = [[padding_fmt.format(c.word) for c in self.cards[i: i+5]] for i in row_indices]
        
        
        if reveal_teams:     
            team_strings = [c.team.name.upper() if c.revealed else c.team.name.upper() + '[?]' for c in self.cards]
        else:
            team_strings = [c.team.name.upper() if c.revealed else '???' for c in self.cards]
            
        grid_team_rows = [[padding_fmt.format(s) for s in team_strings[row_num * 5: (row_num+1)* 5]] for row_num in range(5)]
       
        
        all_grid_rows = [item for pair in zip(grid_word_rows, grid_team_rows) for item in pair + ('\n',)]    
        all_grid_rows = [''.join(row) for row in all_grid_rows] #turn each row into a string     
        
        print('\n' + '\n'.join(all_grid_rows))
    
        
    def touch(self, word):
                    
        if word not in self.get_words(revealed=False):
            raise ValueError('The following target is invalid, please try again: {0}'.format(word))
       
        card  = self.get_card_by_name(word)
        card.revealed = True           
        return card
    
    def get_cards(self, team=None, revealed=None):
        relevant_cards = [card for card in self.cards]
        
        if team is not None:
            if not isinstance(team, list): team = [team]
            relevant_cards = [card for card in relevant_cards if card.team in team]
            
        if revealed is not None:
            relevant_cards = [card for card in relevant_cards if card.revealed == revealed]
                    
        return relevant_cards
     
    def get_words(self, team=None, revealed=None):
        relevant_cards = self.get_cards(team=team, revealed=revealed)
        return [card.word for card in relevant_cards]
    
    def get_card_by_name(self, word):
        for card in self.cards:
            if card.word == word:
                return card
        else:
            raise ValueError('{0} is not a card on the board'.format(word))
  
            
        
class Card:
    
    def __repr__(self):
        return('Card: ' + str(vars(self)))
    
    def __init__(self, word, team):
        self.word = word
        self.team = team
        self.revealed = False
    
    def __str__(self):
        return('CARD: {0} {1}'.format(self.word, self.team.name.upper()))
        
        
  
class Bot: 
    
    def __init__(self, board, owner=None, team=Team.blue):
        
        self.team = team 
        self.board = board #looking only, no touching.
        self.owner = owner #Codenames instance
      
        sim_path = 'cache/card_to_clue_sims_all.csv'
        
        self.board_clue_sims = pd.read_csv(sim_path, index_col=0).loc[self.board.get_words(), :]
        self.board_clue_sims.index.name = 'board_word'
        #self.remove_clues_similar_to_board_words() #uncomment this 
        
        self.clue_safety = self.set_clue_safety(); #boolean series with same index as board_clue_sims
           
        self.removed_clues = []
        self.clue_log = []
        
        
    def remove_clues_similar_to_board_words(self, substring_len_threshold=5):
        #current method of removing words that share a substring of len >=5 
        #mostly catches clues that are fine. Could potentially be improved. 
        
        board_words = list(self.board_clue_sims.index)
        all_clue_words = list(self.board_clue_sims.columns)
        
        clue_words_not_on_board = [c for c in all_clue_words if c not in board_words]
         
        def length_longest_match(string1, string2):
            match = SequenceMatcher(None, string1, string2).find_longest_match(0, len(string1), 0, len(string2))
            return match.size

        clues_too_similar_to_board_words = []
        for clue in clue_words_not_on_board:
            for board_word in board_words:
                if length_longest_match(clue, board_word) >= substring_len_threshold: 
                    clues_too_similar_to_board_words.append((clue, board_word))
                    continue
        
        too_similar_clue_words = [c[0] for c in clues_too_similar_to_board_words]
        good_clue_words = [c for c in clue_words_not_on_board if c not in too_similar_clue_words]
                  
        self.board_clue_sims = self.board_clue_sims.loc[:, good_clue_words]
        self.removed_clues = clues_too_similar_to_board_words
           
        
    #def get_valid_targets(self):
    #    return [card.word for card in self.board.cards if card.team==self.team and not card.revealed]
    
    def set_clue_safety(self):
             
        similarity_thresholds = {Team.blue: 0.3,
                             Team.red: 0.3,
                             Team.neutral: 0.3,
                             Team.assassin: 0.23}
        
             
        danger_df = pd.DataFrame(index = self.board_clue_sims.columns)
        active_unfriendly_cards = [card for card in self.board.cards if not card.revealed and card.team != Team.blue]
    
        for unfriendly_team in [t for t in Team if t != self.team]:
             unfriendly_words = [c.word for c in active_unfriendly_cards if c.team == unfriendly_team]
             sim_thresh = similarity_thresholds[unfriendly_team]
             
             danger_df[unfriendly_team.name] = (self.board_clue_sims.loc[unfriendly_words, :] > sim_thresh).any()
             
             
        self.clue_safety = ~(danger_df.any(axis=1))
        
          
    def pick_best_clue_for_targets(self, unordered_targets, method='sum', is_anti_clue=False):
        #intended to run in apply, hence the weird return 
  
        relevant_similarities = self.board_clue_sims.loc[unordered_targets, :]
        
        if is_anti_clue:
            relevant_similarities = relevant_similarities * -1
        else:
            relevant_similarities = relevant_similarities.loc[:, self.clue_safety]
        
        if method == 'sum':
            scores = relevant_similarities.sum()       
        elif method == 'prod':
            scores = relevant_similarities.clip(lower=0).prod()
        elif method == 'maxmin':
            scores = relevant_similarities.min()
        
        best_clue_word = scores.idxmax()
        best_clue_df = relevant_similarities[best_clue_word].sort_values(ascending=False)
        
        targets = tuple(best_clue_df.index) #now ordered
        target_sims = tuple(best_clue_df.values)
        
        return pd.Series([best_clue_word, scores.max(), targets, target_sims, method])
        
    def pick_best_anti_clue(self):
        pass
        
    
    def pick_best_clue_for_ntargets(self, ntargets=2, method='sum'):
        
        self.set_clue_safety()
        valid_target_words = self.board.get_words(team=Team.blue, revealed=False)
        target_combos = list(itertools.combinations(valid_target_words, ntargets))
        
        target_df = pd.DataFrame({'target_combo': target_combos})
        
        top_clues_info = target_df['target_combo'].apply(lambda x: self.pick_best_clue_for_targets(x, method=method))
        target_df[['clue_word', 'score', 'targets', 'target_sims', 'method']] = top_clues_info
    
        best_clue_info = (target_df.drop('target_combo', axis=1)
                          .sort_values('score', ascending=False).iloc[0].to_dict())
           
        best_clue_info['sim_df'] = self.make_sim_df(clue_word = best_clue_info['clue_word'])
        best_clue_info['turn_num'] = self.owner.player_turn_num
        best_clue_info['clue_chosen'] = False
        best_clue = Clue(**best_clue_info)

                     
        return best_clue
    
    def make_sim_df(self, clue_word):
        board_words_and_teams = [(c.word, c.team) for c in self.board.get_cards(revealed=False)]
        sim_df = (pd.DataFrame(board_words_and_teams, columns=['board_word', 'team'])
                  .set_index('board_word'))
        sim_df = sim_df.join(self.board_clue_sims.loc[:, clue_word]).rename({clue_word: 'sim'}, axis=1)
        return sim_df 
        
    

    def pick_clue(self, ntargets=2, method='maxmin', reveal=False):      
        clue = self.pick_best_clue_for_ntargets(ntargets=ntargets, method=method) 
        self.clue_log.append(clue)     
        return clue
    
            
    def play(self, return_clue=False, reveal_clue_info=False):
        current_scores = self.owner.scores
        other_team = Team(self.owner.current_turn_team.value * -1)
        
        relative_points = current_scores[self.team] - current_scores[other_team]
        num_points_to_win = self.owner.max_scores[self.team] - current_scores[self.team]
        num_enemy_points_to_win = self.owner.max_scores[other_team] - current_scores[other_team]       
        
        if num_points_to_win <= 2:
            clue = self.pick_clue(ntargets = num_points_to_win)
        elif num_enemy_points_to_win <= 2:
            clue = self.pick_clue(ntargets = min(num_points_to_win, 4))
        elif relative_points <= -3:
            clue = self.pick_clue(ntargets = min(abs(relative_points), 4))
        else:
            #clue = self.pick_clue(ntargets = 2)
            t2clue = self.pick_clue(ntargets=2)
            t3clue = self.pick_clue(ntargets=3)
            clue = self.pick_two_or_three_target_clue(t2clue=t2clue, t3clue=t3clue)
            
        clue.clue_chosen = True 
     
        if return_clue:
            return clue
        else:
            if reveal_clue_info:
                print(clue.__dict__)
            else:
                print(clue)
                
                
    def pick_two_or_three_target_clue(self, t2clue, t3clue):
        t3points = 0 
        
        if t3clue.closest_unfriendly_word_and_sim[1] < t2clue.closest_unfriendly_word_and_sim[1]:
            t3points += 1
        elif t3clue.similarity_ratio > t2clue.similarity_ratio:
            t3points += 1
        elif t3clue.target_sims[1] >= t2clue.target_sims[1]: #too permissive?
            t3points += 1
            
        if t3points >= 2:
            return t3clue
        else:
            return t2clue 
                
                
    def guess(self, clue_word, num_targets):
        #currently this has to be called directly
        
        if clue_word not in self.board_clue_sims.columns:
            return ValueError('Bot is not familiar with the word "{0}"'.format(clue_word))
        
        guesses = list(self.board_clue_sims.loc[:, clue_word]
                   .sort_values(ascending=False)
                   .head(num_targets)
                   .index)
        return guesses
        
            
        
class Clue:
    #currently eassuming only Blue team has instances of Clue
    
    def __init__(self, clue_word, targets, score,
                 target_sims, method, sim_df = None, turn_num = None, clue_chosen=False):
        
        self.team = Team.blue
        self.clue_word = clue_word
        self.targets = targets
        self.score = score
        self.target_sims = target_sims
        self.method = method 
        self.sim_df = sim_df
        self.turn_num = turn_num
        self.clue_chosen = clue_chosen

        
        self.sim_df['friendly'] = self.sim_df['team'] == self.team
        
        
    def __repr__(self):
        d = self.__dict__.copy()
        del d['sim_df']
        return str(d)
    
    def report(self):
        d = OrderedDict()
        d['clue_word'] = self.clue_word
        d['targets'] = self.targets
        d['target_sims'] = tuple(s.round(3) for s in self.target_sims)
        d['score'] = self.score.round(3)
        d['method'] = self.method
        d['similarity_ratio'] = self.similarity_ratio.round(3)
        d['closest_unfriendly'] = self.closest_unfriendly_word_and_sim
        d['sim_gap']  = self.friendly_unfriendly_sim_gap
        d['turn_num'] = self.turn_num
        d['clue_chosen'] = self.clue_chosen
        
        for k in d:
            print('{0}: {1}'.format(k, d[k]))
        
    
    def __str__(self):
        return 'CLUE: {0}, {1}'.format(self.clue_word, len(self.targets))
    
    @property
    def similarity_ratio(self):
        thresh = 0.15
        friendly_score = self.sim_df.query('friendly & (sim > @thresh)')['sim'].sum()
        unfriendly_score = self.sim_df.query('not friendly & (sim > @thresh)')['sim'].sum()
        
        if unfriendly_score == 0:
            return np.Inf
        else:
            return friendly_score / unfriendly_score
       
    @property         
    def closest_unfriendly_word_and_sim(self):
        return list(self.sim_df.query('team != @self.team')['sim']
                .nlargest(1).round(3).items())[0]
             
    @property
    def friendly_unfriendly_sim_gap(self):
        return self.target_sims[-1] - self.closest_unfriendly_word_and_sim[1]
        
        
if __name__ == "__main__":
    
    seed = str(int(time.time()))[-4:]
    #seed = 7577 #good first clue
    
    cn = Codenames(seed = seed)  
    b = cn.bot 
    
    if False:

        #cn.show()
        #b.play()
        cn.play()
        
        print('\n')
        for c in b.clue_log:
            c.report()
            print('\n')
            
            
    df = b.board_clue_sims
    
    #nlp = spacy.load('en_core_web_lg')

    #c2 = b.pick_clue(ntargets=2)
    #c3 = b.pick_clue(ntargets=3)
    
    #c2.report()
    
   # print(clue2.__repr__())
    #print(clue3.__repr__())
    
    #cn.play()

    #b.clue()
    
    #for ntargets in range(2,5):
    #    for method in ['sum', 'prod', 'maxmin']:
    #        b.pick_clue(ntargets=ntargets, method=method)
    

   # b.get_best_pair_clue(method='prod')
    
   

    