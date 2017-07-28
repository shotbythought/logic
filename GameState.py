import pprint
import random

pp = pprint.PrettyPrinter(indent=4)

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
            self.cards = self.generateCards()

    def generateCards(self):
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

    def __str__(self):
        return "Player %d:\nHistory: %r\nCards: \n%s" % (self.player, self.history, pp.pformat(self.cards))