from copy import deepcopy
from GameState import GameState
from Player import Player

import pprint
from GameState import GameState

import random

class JoneAndMike(Player):
    def __init__(self, position):
        self.position = position

    def pass_card(self, gamestate):
        """ returns the index of the card to pass """
        gs_copy = deepcopy(gamestate)
        lowest_score = float('inf')
        best_index = -1
        for i in range(6):
            gs_copy.cards[self.position][i]['rank'] = 'Unclear'
        for i in range(6):
            gs_copy.cards[self.position][i] = gamestate.cards[self.position][i]
            igs = self.get_deductions(gs_copy.cards)
            score = self.num_possible_configs(igs)
            if score < lowest_score:
                lowest_score = score
                best_index = i
            gs_copy.cards[self.position][i]['rank'] = 'Unclear'
        return best_index
    # TODO implement entropy calculation

    def guess_card(self, gamestate):
        deduction = self.get_deductions(gamestate.cards)

        guesses = []
        for i in [(self.position+1)%4, (self.position+3)%4]:
            for j in range(6):
                num_pos = len(deduction[i][j][0])
                if num_pos != 1:
                    guesses.append((num_pos, i, j, list(deduction[i][j][0])[random.randint(0,3)]))

        guesses.sort()

        # print(guesses)

        return (guesses[0][1], guesses[0][2], guesses[0][3])


        """ returns a tuple (pid, ind, guess), which is equivalent to guessing the indth card of pid as guess """
        raise Exception('Unimplemented guess')

    def flip_card(self, gamestate):
        """ returns the index of the card to flip """
        gs_copy = deepcopy(gamestate)
        highest_score = 0
        best_index = -1
        for i in range(6):
            gs_copy.cards[self.position][i]['rank'] = 'Unclear'
        for i in range(6):
            gs_copy.cards[self.position][i] = gamestate.cards[self.position][i]
            igs = self.get_deductions(gs_copy.cards)
            score = self.num_possible_configs(igs)
            if score > highest_score:
                highest_score = score
                best_index = i
            gs_copy.cards[self.position][i]['rank'] = 'Unclear'
        return best_index

    def claim(self, gamestate):
        deduction = self.get_deductions(gamestate.cards)

        if all(all(len(card[0]) == 1 for card in hand) for hand in deduction): 
            claim = []
            for i in range(4):
                hand = []
                for j in range(6):
                    hand.append(list(deduction[i][j][0])[0])
                claim.append(hand)

            return (True, claim)

        return (False, [])

    def get_deductions(self, cards):
        """given a list of cards, updates internal gamestate"""
        deduction = [[[set(range(12)),0] for j in range(6)] for i in range(4)]

        for i in range(4):
            for j in range(6):
                deduction[i][j][1] = cards[i][j]['color']

                if cards[i][j]['rank'] != 'Unclear':
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
