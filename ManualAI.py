from Player import Player

class ManualAI(Player):
    def pass_card(self, gs):
        print("\n\n\n\nPlayer " + str(self.position) + " Passing")
        print(gs)
        return input("Pass which card: ")

    def guess_card(self, gs):
        print("\n\n\n\nPlayer " + str(self.position) + " Guessing")
        print(gs)
        which_player = input("Who are you guessing: ")
        which_card = input("Which card are you guessing: ")
        rank = input("Enter number: ")
        return which_player, which_card, rank

    def flip_card(self, gs):
        print("\n\n\n\nPlayer " + str(self.position) + " Flipping")
        print(gs)
        return input("Flip which card: ")

    def claim(self, gs):
        print("\n\n\n\nPlayer " + str(self.position) + " Claiming")
        print(gs)
        is_claiming = raw_input("Are you claiming? ")

        if is_claiming == "Yes":
            cards = []
            for i in range(4):
                hand = []
                for j in range(6):
                    print("For the " + str(i) + "th player and the " + str(j) + "th card: ")
                    rank = input("Enter number: ")
                    hand.append(rank)

                cards.append(hand)
            return True, cards

        else:
            return False, None
