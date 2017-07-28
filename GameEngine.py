from Game import Game
from ManualAI import ManualAI

AIs = []
for i in range(4):
    AIs.append(ManualAI(i))

g = Game(AIs)
g.start()