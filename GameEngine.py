from Game import Game
from ManualAI import ManualAI
from JoneAndMike import JoneAndMike

num_games = 10
total_score = [0] * 4
debug = True

for game_count in range(0, num_games):
	AIs = []
	for i in range(4):
	    AIs.append(JoneAndMike(i))
	g = Game(AIs, debug = debug)
	score = [0] * 4
	try:
		score = g.run_game()
	except RuntimeError as e:
		score = e.args[0]
		print(">>> Error: %r <<<" % e.args[1])

	total_score = [sum(x) for x in zip(score, total_score)]
	print("score is %r, with %d turns" % (score, g.turns_occurred))
	print("total score is %r" % total_score)