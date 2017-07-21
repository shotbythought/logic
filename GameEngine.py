from Game import Game
from ManualAI import ManualAI

num_games = 1000

for game_count in range(0, num_games):
	AIs = []
	for i in range(4):
	    AIs.append(ManualAI(i))

	g = Game(AIs)
	score = g.run_game()
	print("score is %r" % score)