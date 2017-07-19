class Player:
    def __init__(self, player):
        self.player = player

    def pass_card(self, gamestate):
        """ returns the index of the card to pass """
        raise Exception('Unimplemented pass_card')

    def guess_card(self, gamestate):
        """ returns a tuple (pid, ind, guess), which is equivalent to guessing the indth card of pid as guess """
        raise Exception('Unimplemented guess')

    def flip_card(self, gamestate):
        """ returns the index of the card to flip """
        raise Exception('Unimplemented flip')

    def claim(self, gamestate):
        """ returns a tuple of a boolean and a list of list """
        """ bool: true or false, whether the player wants to claim """
        """ list of list: structure which contains all the correct answers """
        raise Exception('Unimplemented claim')