# Logic AI Competition

Welcome to our first Logic AI competition!

## Getting Started
Start with Player.py and GameState.py. Or ask Michael or Joanne.

## Components with Minimal Documentation

#### Player.py
The framework of the AI you are implementing. Make sure the values you return follow 0 indexing (see below).
- `position`: the position of the player in the game, in the range [0,4]
#### GameState.py
Each time you are asked to make a move, we provide you with a GameState object.
- `cards`: a list of list of the cards you can currently see. `cards[2][3]` gives you a dictionary that looks like `{'rank': 5, 'color': 1}`, which means that you can see that the 2nd player's 3rd card is a 5 with color 1. If you can't see that card, the rank will be the string `"unclear"`.
- `history`: a list of Actions.
#### Action.py
Used for recording every action that has been performed. Different information is stored depending on the action type (pass, guess, or flip).
- `action_type`: the type of action, one of `["pass", "guess", "flip"]`.
- `player`: the position of the player that initiated the action, in the range [0,4].
- `which_card`: the card that the action was performed on.
- The rest are only valid if `action_type == "guess"`:
    - `which_player`: the player whose card is guessed.
    - `guess`: the rank of the guess.
    - `is_correct`: whether a guess was correct.
#### ManualAI.py
A dumb AI we created that literally gets input from the command line and plays accordingly.
#### Game.py
A game that contains the logic of the game. You shouldn't need this, but feel free to take a look.
#### GameEngine.py
How we will be running the game (sort of). There are a few parameters you can set and see:
- `AIs`: list of AIs that are playing. 
- `num_games`: number of games played between this set of AIs.
- `total_score`: a size 4 list, keeping track of the total score.
- `debug`: if `True`, this will exit the game everytime an invalid input is given by an AI. Otherwise, the team that gave the invalid input automatically loses the game. When we are running this during the final showdown, we will set `debug` to be false.

## Indexing
Everything is 0 indexed. In other words, the range of cards you can guess is [0,11], the range of position of cards is [0,6], the range of colors is [0,1], and the range of players is [0,3]. Player 0 is friends with player 2, and player 1 is friends with player 3.

## Invalid Inputs
During the final showdown, an invalid input will result in the loss of a game.
- A card that is not in the range [0,11]
- A card position that is not in the range [0,6]
- A player position that is not in the range [0,4]
- Passing a card that has already been passed/revealed
- Guessing the card of a friend
- Guessing a card that has already been revealed
- Flipping a card that has already been revealed

## Scoring
For each game, you and your friend will each get 1 point if you claim correctly. Otherwise, your opponent and their friend will each get 1 point. If you submit an input that is not allowed (see _Invalid Inputs_), your opponent and their friend will each get 1 point. A game ends after any group gets receives a point.
We run each pair of submitted AIs against each other for a large number (to be decided) of games and keep track of the score. The team with the highest total score against all its opponents wins.