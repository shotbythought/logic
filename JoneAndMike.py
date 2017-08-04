from Action import Action
from copy import deepcopy
from GameState import GameState
from Player import Player

import pprint
from GameState import GameState

import random

class JoneAndMike(Player):
    def __init__(self, position):
        self.position = position
        self.friend_position = (self.position + 2)%4
        self.viewpoints = None

        self.actions_processed = 0

        # cards of mine that everyone knows
        self.not_revealed = set(range(6))

        #cards of mine that partner knows
        self.not_passed = set(range(6))

    def pass_card(self, gamestate):
        """ returns the index of the card to pass """
        self.update_internal(gamestate)

        friend_view = self.viewpoints[self.friend_position]
        score_index = []
        for i in self.not_passed:
            friend_with_card = self.update_viewpoint_given_action(self.friend_position, friend_view, Action("pass", self.position, i), gamestate)
            score = self.num_possible_configs(friend_with_card)
            score_index.append((score, i))
        score_index.sort()
        if len(score_index) == 0:
            print(self.position, gamestate.history)
            pprint.pprint(self.viewpoints[self.position])
        self.not_passed.discard(score_index[0][1]) # we want the one with the lowest score
        return score_index[0][1]
    # TODO implement entropy calculation
    # TODO make player reset not_lists after every round

    def guess_card(self, gamestate):
        """ returns a tuple (pid, ind, guess), which is equivalent to guessing the indth card of pid as guess """
        self.update_internal(gamestate)

        possibilities_guess = []
        for which_player in [(self.position+1)%4, (self.position+3)%4]:
            for which_card in range(6):
                num_pos = len(self.viewpoints[self.position][which_player][which_card][0])
                if num_pos != 1:
                    possibilities_guess.append((num_pos, which_player, which_card, list(self.viewpoints[self.position][which_player][which_card][0])[random.randint(0,num_pos-1)]))

        random.shuffle(possibilities_guess)
        possibilities_guess.sort(key=lambda x: x[0])

        return (possibilities_guess[0][1], possibilities_guess[0][2], possibilities_guess[0][3])

    def flip_card(self, gamestate):
        """ returns the index of the card to flip """
        self.update_internal(gamestate)

        score_index = []
        for i in self.not_revealed:
            flip_action = Action("flip", self.position, i)
            opponent1_with_card = self.update_viewpoint_given_action((self.position + 1)%4, self.viewpoints[(self.position + 1)%4], flip_action, gamestate)
            opponent2_with_card = self.update_viewpoint_given_action((self.position + 3)%4, self.viewpoints[(self.position + 3)%4], flip_action, gamestate)
            score = self.num_possible_configs(opponent1_with_card) + self.num_possible_configs(opponent2_with_card)
            score_index.append((score, i))
        score_index.sort(reverse = True)
        self.not_revealed.discard(score_index[0][1]) # we want the one with the higest score
        self.not_passed.discard(score_index[0][1]) # we want the one with the higest score
        return score_index[0][1]

    def claim(self, gamestate):
        self.update_internal(gamestate)

        if all(all(len(card[0]) == 1 for card in hand) for hand in self.viewpoints[self.position]): 
            claim = []
            for i in range(4):
                hand = []
                for j in range(6):
                    hand.append(list(self.viewpoints[self.position][i][j][0])[0])
                claim.append(hand)

            return (True, claim)

        return (False, [])

    def update_internal(self, gamestate):
        """Given external gamestate, update internal gamestate"""

        if not self.viewpoints:
            self.viewpoints = [self.initialize_viewpoint(gamestate.cards,i) for i in range(4)]

        for i in range(4):
            for action in gamestate.history[self.actions_processed:]:
                self.viewpoints[i] = self.update_viewpoint_given_action(i, self.viewpoints[i], action, gamestate, True)

        self.actions_processed = len(gamestate.history)

    def update_viewpoint_given_action(self, player, viewpoint, action, gamestate, is_master = False):
        """Given a view point and an action, """
        """returns modified version of fully reduced view point"""
        """WIP, we probably need to add more things"""
        viewpoint = deepcopy(viewpoint)
        if action.action_type == "pass":
            from_player = action.player
            receive_player = (action.player + 2) % 4

            if receive_player == player and (action.player - self.position) % 2 == 0:
                viewpoint[from_player][action.which_card][0] = set([gamestate.cards[from_player][action.which_card]['rank']])

        elif action.action_type == "guess":
            if action.is_correct:
                viewpoint[action.which_player][action.which_card][0] = set([action.guess])
                if is_master and action.which_player == self.position:
                    self.not_revealed.discard(action.which_card)
                    self.not_passed.discard(action.which_card)
            else:
                viewpoint[action.which_player][action.which_card][0].discard(action.guess)
                # guesser probably doesn't have the card
                # for card_position in range(6):
                    # viewpoint[action.player][card_position][0].discard(action.guess)
            
        elif action.action_type == "flip":
            viewpoint[action.player][action.which_card][0] = set([gamestate.cards[action.player][action.which_card]['rank']])
        return self.do_complete_deduction(viewpoint)

    def initialize_viewpoint(self, cards, position):
        """given a list of cards and a position, returns one viewpoint of the position"""
        deduction = [[[set(range(12)),0] for j in range(6)] for i in range(4)]

        for i in range(4):
            for j in range(6):
                deduction[i][j][1] = cards[i][j]['color']

                if cards[i][j]['rank'] != 'Unclear' and position == i:
                    deduction[i][j][0] = set([cards[i][j]['rank']])

        deduction = self.do_complete_deduction(deduction)

        return deduction

    def do_complete_deduction(self, deduction):
        old_deduction = deepcopy(deduction)
        deduction = self.do_deduction(deduction)
        while old_deduction != deduction:
            old_deduction = deepcopy(deduction)
            deduction = self.do_deduction(deduction)
        return deduction

    def do_deduction(self, deduction):
        # Increasing
        for i in range(4):
            mins = [-1, -1]
            for j in range(6):
                for num in deepcopy(deduction[i][j][0]):
                    if num <= mins[deduction[i][j][1]] or num < mins[(deduction[i][j][1]+1)%2]:
                        deduction[i][j][0].remove(num)
                        # print("Hand %d Card %d can't be %d because it must be greater" % (i, j, num))
                mins[deduction[i][j][1]] = min(deduction[i][j][0]) 

        # Decreasing
        for i in range(4):
            maxs = [12, 12]
            for j in reversed(range(6)):
                for num in deepcopy(deduction[i][j][0]):
                    if num >= maxs[deduction[i][j][1]] or num > maxs[(deduction[i][j][1]+1)%2]:
                        deduction[i][j][0].remove(num)
                        # print("Hand %d Card %d can't be %d because it must be smaller" % (i, j, num))

                maxs[deduction[i][j][1]] = max(deduction[i][j][0]) 

        # Uniqueness
        for i in range(4):
            for j in range(6):
                if len(deduction[i][j][0]) == 1:
                    only_number = list(deduction[i][j][0])[0]
                    for k in range(4):
                        for l in range(6):
                            if not (i == k and j == l):
                                if deduction[i][j][1] == deduction[k][l][1] and only_number in deduction[k][l][0]:
                                    deduction[k][l][0].remove(only_number)
                                    # print("Hand %d Card %d can't be %d because it already exists somewhere" % (i, j, num))

        # Uniqueness of 2s
        for color in range(2):
            for rank1 in range(12):
                for rank2 in range(12):
                    if rank1 == rank2:
                        continue
                    instances = []
                    for i in range(4):
                        for j in range(6):
                            if set([rank1, rank2]) == deduction[i][j][0] and color == deduction[i][j][1]:
                                instances.append((i,j))
                    if len(instances) == 2:
                        for i in range(4):
                            for j in range(6):
                                if (i,j) not in instances and color == deduction[i][j][1]:
                                    deduction[i][j][0].discard(rank1)
                                    deduction[i][j][0].discard(rank2)

        # Existence
        for rank in range(12):
            for color in range(2):
                instances = 0
                person = -1
                card = -1

                for i in range(4):
                    for j in range(6):
                        if rank in deduction[i][j][0] and color == deduction[i][j][1]:
                            instances += 1
                            person = i
                            card = j
                if instances == 0:
                    pprint.pprint(self.viewpoints)
                    raise Exception("bad") 
                if instances == 1:
                    # if len(deduction[person][card][0]) > 1:
                    #     print("Hand %d Card %d must be %d because it's the only card that can be" % (person, card, rank))
                    deduction[person][card][0] = set([rank])

        return deduction

    def num_possible_configs(self, igs):
        """given an Internal Gamestate structure, calculates approximate number of possible configs"""

        #Sharon's number
        product = 1
        for i in range(len(igs)):
            for j in range(len(igs[0])):
                product *= len(igs[i][j][0])
        return product

    def DFS(self, igs):
        """Potential thing we can use for DFS"""
        if all(all(len(card[0]) == 1 for card in hand) for hand in igs): 
            self.config_count += 1
            return

        for i in range(len(igs)):
            for j in range(len(igs[0])):
                card = igs[i][j]
                color = card[1]
                pos = card[0]
                if len(pos) != 1:
                    for pos_num in pos:
                        newigs = deepcopy(igs)
                        newigs[i][j][0] = set([pos_num])
                        try:
                            newigs = self.do_complete_deduction(newigs)
                        except Exception:
                            pass
                        self.search(newigs)

if __name__ == '__main__':
    jam = JoneAndMike(0)

    jam.get_deductions([   [   {'color': 1, 'rank': 0},
            {'color': 1, 'rank': 1},
            {'color': 0, 'rank': 2},
            {'color': 0, 'rank': 4},
            {'color': 1, 'rank': 8},
            {'color': 1, 'rank': 11}],
        [   {'color': 1, 'rank': 'Unclear'},
            {'color': 1, 'rank': 'Unclear'},
            {'color': 1, 'rank': 'Unclear'},
            {'color': 0, 'rank': 'Unclear'},
            {'color': 1, 'rank': 'Unclear'},
            {'color': 1, 'rank': 'Unclear'}],
        [   {'color': 0, 'rank': 'Unclear'},
            {'color': 1, 'rank': 'Unclear'},
            {'color': 1, 'rank': 'Unclear'},
            {'color': 0, 'rank': 'Unclear'},
            {'color': 0, 'rank': 'Unclear'},
            {'color': 0, 'rank': 'Unclear'}],
        [   {'color': 0, 'rank': 'Unclear'},
            {'color': 0, 'rank': 'Unclear'},
            {'color': 0, 'rank': 'Unclear'},
            {'color': 0, 'rank': 'Unclear'},
            {'color': 1, 'rank': 'Unclear'},
            {'color': 0, 'rank': 'Unclear'}]])

    # cards = [   [   {'color': 1, 'rank': 0},
    #         {'color': 1, 'rank': 1},
    #         {'color': 0, 'rank': 2},
    #         {'color': 0, 'rank': 4},
    #         {'color': 1, 'rank': 8},
    #         {'color': 1, 'rank': 11}],
    #     [   {'color': 1, 'rank': 'Unclear'},
    #         {'color': 1, 'rank': 'Unclear'},
    #         {'color': 1, 'rank': 'Unclear'},
    #         {'color': 0, 'rank': 'Unclear'},
    #         {'color': 1, 'rank': 'Unclear'},
    #         {'color': 1, 'rank': 'Unclear'}],
    #     [   {'color': 0, 'rank': 'Unclear'},
    #         {'color': 1, 'rank': 'Unclear'},
    #         {'color': 1, 'rank': 'Unclear'},
    #         {'color': 0, 'rank': 'Unclear'},
    #         {'color': 0, 'rank': 'Unclear'},
    #         {'color': 0, 'rank': 'Unclear'}],
    #     [   {'color': 0, 'rank': 'Unclear'},
    #         {'color': 0, 'rank': 'Unclear'},
    #         {'color': 0, 'rank': 'Unclear'},
    #         {'color': 0, 'rank': 'Unclear'},
    #         {'color': 1, 'rank': 'Unclear'},
    #         {'color': 0, 'rank': 'Unclear'}]]

    cards = [[{'color': 0, 'rank': 1}, {'color': 0, 'rank': 3}, {'color': 1, 'rank': 4}, {'color': 0, 'rank': 4}, {'color': 1, 'rank': 8}, {'color': 0, 'rank': 8}], [{'color': 0, 'rank': 2}, {'color': 0, 'rank': 7}, {'color': 1, 'rank': 7}, {'color': 0, 'rank': 9}, {'color': 1, 'rank': 9}, {'color': 1, 'rank': 10}], [{'color': 1, 'rank': 0}, {'color': 1, 'rank': 2}, {'color': 1, 'rank': 3}, {'color': 1, 'rank': 5}, {'color': 1, 'rank': 6}, {'color': 1, 'rank': 11}], [{'color': 0, 'rank': 0}, {'color': 1, 'rank': 1}, {'color': 0, 'rank': 5}, {'color': 0, 'rank': 6}, {'color': 0, 'rank': 10}, {'color': 0, 'rank': 11}]]

    gs = GameState(cards=cards, player=0)

    gs.cards = cards

    print(jam.claim(gs))


    # jam.get_internal_gamestate([   [   {'color': 1, 'rank': 0},
    #         {'color': 1, 'rank': 1},
    #         {'color': 0, 'rank': 2},
    #         {'color': 0, 'rank': 4},
    #         {'color': 1, 'rank': 8},
    #         {'color': 1, 'rank': 11}],
    #     [   {'color': 1, 'rank': 'Unclear'},
    #         {'color': 1, 'rank': 'Unclear'},
    #         {'color': 1, 'rank': 'Unclear'},
    #         {'color': 0, 'rank': 'Unclear'},
    #         {'color': 1, 'rank': 'Unclear'},
    #         {'color': 1, 'rank': 'Unclear'}],
    #     [   {'color': 0, 'rank': 1},
    #         {'color': 1, 'rank': 'Unclear'},
    #         {'color': 1, 'rank': 'Unclear'},
    #         {'color': 0, 'rank': 'Unclear'},
    #         {'color': 0, 'rank': 'Unclear'},
    #         {'color': 0, 'rank': 'Unclear'}],
    #     [   {'color': 0, 'rank': 'Unclear'},
    #         {'color': 0, 'rank': 'Unclear'},
    #         {'color': 0, 'rank': 'Unclear'},
    #         {'color': 0, 'rank': 'Unclear'},
    #         {'color': 1, 'rank': 'Unclear'},
    #         {'color': 0, 'rank': 'Unclear'}]])
