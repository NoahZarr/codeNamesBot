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
        self.current_turn_team = first_team
        
        self.player_team = player_team
        self.other_team = Team.red if player_team == Team.blue else Team.blue
        
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
            response = input(clue)
            #response = prompt_response(clue)
            
            if response == '$':
                self.show()            
            elif response in self.board.get_words(revealed=False) + ['_']:
                valid_response = response
            else:
                print(f'''ERROR: {response} is not a valid guess, please enter a word on the board.
                Enter _ to pass, $ to see the board or ! to quit''')     
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
        
        team_assignment_seed = str(int(time.time()))[-2:]
       
        print('Team assignment seed: {0}'.format(team_assignment_seed))
        random.seed(team_assignment_seed)
        random.shuffle(selected_card_words)
        
        teams = 8 * [Team.blue] +  8 * [Team.red] + 7 * [Team.neutral] + 1 * [Team.assassin] + 1 * [first_team]
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
     
    def get_words(self, team=None, revealed=None):
        relevant_cards = [card for card in self.cards]
        
        if team is not None:
            relevant_cards = [card for card in relevant_cards if card.team == team]
            
        if revealed is not None:
            relevant_cards = [card for card in relevant_cards if card.revealed == revealed]
                    
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
        
        #needs master word list to make matrices - but for now just loading from file 
        #self.potential_clues = [w for w in master_word_list if w not in board.words] #TODO: improve  

        #self.nlp = spacy.load('en_core_web_lg') #is this whats taking so long? 

        self.team = team 
        self.board = board #looking only, no touching.
        self.owner = owner #Codenames instance
        
      
        sim_path = 'cache/card_to_clue_sims_all.csv'
        
        self.board_clue_sims = pd.read_csv(sim_path, index_col=0).loc[self.board.get_words(), :]
        self.board_clue_sims.index.name = 'board_word'
        
        self.clue_safety = self.set_clue_safety(); #boolean series with same index as board_clue_sims
           
        self.clue_log = []
        
        
    def remove_clues_similar_to_board_words(self):
       #board_word_lemmas = [t.lemma_ for t in self.nlp(' '.join(self.board.words))]
      # columns_to_drop = [c for c in self.board_clue_sims.columns if self.nlp(c)[0].lemma_ in board_word_lemmas]
      
      #this now redundant - we lemmatize earlier
      #columns_to_drop = [c for c in self.board_clue_sims.columns if self.nlp(c)[0].lemma_ in board_word_lemmas]  
       
     # self.board_clue_sims = self.board_clue_sims.drop(labels=columns_to_drop, axis=1) 
     
     
     #implement later once we are running with random setups; right now this is handled before saving file 
     #i could still add rules here that need to be implemented?
     #idea: no more than 5-6 shared letters?
     pass
       
        
    def get_valid_targets(self):
        return [card.word for card in self.board.cards if card.team==self.team and not card.revealed]
    
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
        
          
    def pick_best_clue_for_targets(self, targets, method='sum'):
        #intended to run in apply, hence the weird return 
  
        relevant_similarities = self.board_clue_sims.loc[targets, self.clue_safety]
        
        if method == 'sum':
            scores = relevant_similarities.sum()       
        elif method == 'prod':
            scores = relevant_similarities.clip(lower=0).prod()
        elif method == 'maxmin':
            scores = relevant_similarities.min()
        
        best_clue_word = scores.idxmax()
        
        return pd.Series([best_clue_word, scores.max(), tuple(relevant_similarities[best_clue_word].values), method])
        
    def pick_best_clue_for_ntargets(self, ntargets=2, method='sum'):
        
        self.set_clue_safety()
        target_combos = list(itertools.combinations(self.get_valid_targets(), ntargets))
        
        target_df = pd.DataFrame({'targets': target_combos})
        
        top_clues_info = target_df['targets'].apply(lambda x: self.pick_best_clue_for_targets(x, method=method))
        target_df[['clue_word', 'score', 'target_sims', 'method']] = top_clues_info
    
        best_targets_and_clue = target_df.sort_values('score', ascending=False).iloc[0].to_dict()
                                
        return Clue(**best_targets_and_clue)  
    

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
        elif relative_points <= -3 or num_enemy_points_to_win <= 2:
            clue = self.pick_clue(ntargets = min(abs(relative_points), 4))
        else:
            clue = self.pick_clue(ntargets = 2)
            
        if return_clue:
            return clue
        else:
            if reveal_clue_info:
                print(clue.__dict__)
            else:
                print(clue)
     
        
        
class Clue:
    def __init__(self, clue_word, targets, score, target_sims, method):
        self.clue_word = clue_word
        self.targets = targets
        self.score = score
        self.target_sims = target_sims
        self.method = method 
        
        
    def __repr__(self):
        return str(self.__dict__)
    
    def __str__(self):
        return 'CLUE: {0}, {1}\n> '.format(self.clue_word, len(self.targets))
        

        
if __name__ == "__main__":

    cn = Codenames(seed = str(int(time.time()))[-4:])  
    
    b = cn.bot
    
    cn.play()
    
    
    
    #b.clue()
    
    #for ntargets in range(2,5):
    #    for method in ['sum', 'prod', 'maxmin']:
    #        b.pick_clue(ntargets=ntargets, method=method)
    

   # b.get_best_pair_clue(method='prod')
    
   

    
    
    
    
    