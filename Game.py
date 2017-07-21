from Action import Action
from ManualAI import ManualAI

import pprint
import random

pp = pprint.PrettyPrinter(indent=4)

def generateCards():
    """ returns a list of hands """
    deck = []
    for i in range(2):
        for j in range(12):
            deck.append({'rank' : j, 'color' : i})

    random.shuffle(deck)

    cards = []
    hand_size = 6
    for i in range(4):
        hand = deck[hand_size * i : hand_size * (i + 1)]
        hand.sort(key = (lambda x : x['rank']))
        cards.append(hand)

    return cards

class Game:
    def __init__(self, AIs):
        self.gs = GameState()
        self.turn = random.randint(0, 3)

        self.pgs = []
        for i in range(4):
            self.pgs.append(GameState(self.gs.cards, i))

        self.AIs = AIs
        self.is_game_over = False

    def run_game(self):
        while not self.is_game_over:
            self.play_turn()
        return self.score

    def check_claims(self):
        claimed = False

        for player in list(range(4)):
            is_claiming, cards = self.AIs[player].claim(self.pgs[player])

            if is_claiming:
                assert all(all(card >= 0 or card < 12 for card in hand) for hand in cards)
                self.do_claim(player, cards)
                claimed = True

        return claimed

    def play_turn(self):
        which_card = self.AIs[self.turn].pass_card(self.pgs[self.turn])
        assert which_card >= 0 and which_card < 6, ("Cannot pass the %dth card" % which_card)
        self.do_pass(which_card)      

        if self.check_claims():
            return

        friend = (self.turn+2)%4
        which_player, which_card, guess = self.AIs[friend].guess_card(self.pgs[friend])
        correct = self.do_guess(which_player, which_card, guess)
        assert which_player >= 0 and which_player < 4, ("Does not exist an %dth player" % which_player)
        assert which_card >= 0 and which_card < 6, ("Cannot guess the %dth card" % which_card)
        assert guess >= 0 and guess < 12, ("Cannot guess that a card is %d" % guess)

        if self.check_claims():
            return

        if not correct:
            which_card = self.AIs[friend].flip_card(self.pgs[friend])
            assert which_card >= 0 and which_card < 6, ("Cannot pass the %dth card" % which_card)
            self.do_flip(which_card)

            if self.check_claims():
                return

        self.turn = (self.turn + 1) % 4

    def update_history(self, action):
        self.gs.history.append(action)

        for i in range(4):
            self.pgs[i].history.append(action)

    def do_pass(self, which_card):
        action = Action("pass", player=self.turn, which_card=which_card)
        self.update_history(action)

        from_player = self.turn
        receive_player = (self.turn+2)%4
        self.pgs[receive_player].cards[from_player][which_card] = self.gs.cards[from_player][which_card]

    def do_guess(self, which_player, which_card, guess):
        guessing_player = (self.turn+2)%4

        if (guessing_player - which_player) % 2 == 0:
            print("YOU FAILED YOU SUCK SO MUCH BALLZDEEP WRONG PLAYER TC")
            import sys;sys.exit(1)

        is_correct = self.gs.cards[which_player][which_card]['rank'] == guess

        if is_correct:
            for i in range(4):
                self.pgs[i].cards[which_player][which_card] = self.gs.cards[which_player][which_card]

        action = Action("guess", player=guessing_player, which_card=which_card, which_player=which_player, guess=guess, is_correct=is_correct)
        self.update_history(action)

        return is_correct

    def do_flip(self, which_card):
        flip_player = self.turn

        action = Action("flip", player=flip_player, which_card=which_card)
        self.update_history(action)

        for i in range(4):
            self.pgs[i].cards[flip_player][which_card] = self.gs.cards[flip_player][which_card]

    def do_claim(self, player, cards):
        self.is_game_over = True
        self.score = [0] * 4

        for i in range(4):
            for j in range(6):
                if cards[i][j] != self.gs.cards[i][j]['rank']:
                    print("Wrong claim, Player %d and Player %d Win!" % ((player+1)%4, (player+3)%4))
                    self.score[(player+1)%4] = 1
                    self.score[(player+3)%4] = 1
                    return

        print("Correct claim, Player %d and Player %d Win!" % (player, (player+2)%4))
        self.score[player] = 1
        self.score[(player+2)%4] = 1

class GameState:
    def __init__(self, cards=None, player=-1):
        self.history = []
        self.player = player

        if cards:
            self.cards = []
            for i in range(4):
                hand = []
                for j in range(6):
                    hand.append({'rank': "Unclear", 'color': cards[i][j]['color']})
                self.cards.append(hand)

            self.cards[player] = cards[player]
        else:
            self.cards = generateCards()
            print(self)

    def __str__(self):
        return "Player %d:\nHistory: %r\nCards: \n%s" % (self.player, self.history, pp.pformat(self.cards))