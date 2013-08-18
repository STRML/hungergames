Pyevolve-based Genetic Survivor Bot
===================================

Overview
--------

This bot's behavior is based on 500 generations of competition, with fitness defined as the player's
place in the final ranking squared (e.g. 100 points for 1st out of 10). Crossover and mutation was done
in development via [Pyevolve](http://pyevolve.sourceforge.net/0_6rc1/index.html), and the project 
structure was based on [Chad Miller's project](https://github.com/ChadAMiller/hungergames).


Motivation
----------

As relative newcomers to Game Theory, we thought that the most interesting way to approach the problem
was goal-based. We would define a set of constraints and possible strategies for the bot, and give it
the freedom to decide which strategies produced the desired result and which did not. All strategies are 
attached to weights, from 0 to 100 and summed. If the sum is greater than or equal to 100, the bot
would hunt; otherwise, it would slack. This allowed for a single strategy to define every round if
necessary, or for all strategies to be weighted by effectiveness.


Results
-------

It became clear, once we empowered the bot with enough possible behaviors to sufficiently affect
its own destiny, that it would tend toward slacking, no matter which behaviors we tried.

A few minutes thinking about this approach led us to a startling realization that we were missing the
entire point of the game. Clearly, the optimum strategy for a single player, if seeking to survive longest,
is to slack whenever possible. The payoff table is quite clearly slanted in this direction. Even with
full advance knowledge of every opponent's move, the winning strategy is to slack each and every time.
The public good affects all players equally and thus does not affect the standings in a direct competition.

We felt it was quite interesting to see the computer find this out on its own. For about 170 generations,
with 80 chromosomes per generation (13600) games, the computer had mostly chosen a strategy oscillating
between hunts and slacks. We found that it especially seemed to favor strategy #1, choosing `h` or `s`
based on the opponent's reputation; if higher, hunt, if lower, slack. Here's an excerpt from the logs:

* `Gen. 162 (32.40%): Max/Min/Avg Fitness(Raw) [39.98(100.00)/29.98(0.00)/33.31(33.31)]`

However, shortly thereafter, we noticed the logs moving in a meaningful direction:

* `Gen. 178 (35.60%): Max/Min/Avg Fitness(Raw) [69.90(100.00)/42.00(0.00)/58.25(58.25)]`
* `Gen. 204 (40.80%): Max/Min/Avg Fitness(Raw) [101.95(100.00)/0.00(9.00)/83.81(83.81)]`

It eventually stabilized at an average of about 84, which indicates that it was in average at 2nd
place or better on every game. Why it couldn't get to first place became immediately clear after
looking at the winning chromosome:

* `[1, 1, 1, 1, 1, 1, 1]`

We had a few similar chromosomes turn up, all of which summed together equal less than 100, essentially
making it impossible for the bot to ever hunt. It simply becomes a freeloader bot.


Conclusion
----------

Allowing the computer to probe the depths of the game proved beneficial to our understanding of 
the complex dynamics within, and raises the question: what are we actually trying to accomplish?
The interactions between players in this simulation are much like the problems that plague
every society: cooperation is the best way to ensure the continued success of the group, yet in
every case, the optimal strategy for an individual to feed upon the work of others.

Much like in the story of the hunger games, the only way to truly win the game is to fight back
against the creators. Arbitrary game length restrictions aside, it is easy for a cooperating
tribe to play the game forever given the generous size of the public good.

From a more interesting movie:

"A strange game. The only winning move is not to play. How about a nice game of chess?"


Addendum
--------

To keep the submission clean, the evolver is not included inside Player.py. The file is below.


evolver.py
----------

```python

from pyevolve import G1DList
from pyevolve import GSimpleGA
from pyevolve import Selectors
from pyevolve import DBAdapters
import pyevolve
from bots import Pushover, Freeloader, Alternator, MaxRepHunter, Random, FairHunter, BoundedHunter, AverageHunter
from Player import Player
from Game import Game

# Enemy players.
player_list = [
    Pushover(),
    Freeloader(),
    Alternator(),
    MaxRepHunter(),
    Random(.2),
    Random(.8),
    FairHunter(),
    BoundedHunter(0.4, 0.6),
    BoundedHunter(0.6, 1),
    AverageHunter()
]


# Fitness evaluation function.
def eval_func(chromosome):
    player = Player(chromosome)
    game = Game([player] + player_list, verbose=False, quiet=True)  # Start the game in quiet mode.
    ranking = game.play_game()
    score = ranking.index('GA Player')

    return score * score

# Enable the pyevolve logging system
pyevolve.logEnable()

# Genome instance, 1D List of 7 elements
genome = G1DList.G1DList(7)

# Sets the range max and min of the 1D List
bestScore = len(player_list) * len(player_list) + 1  # run forever
genome.setParams(rangemin=0, rangemax=100)

# The evaluator function (evaluation function)
genome.evaluator.set(eval_func)

# Genetic Algorithm Instance
ga = GSimpleGA.GSimpleGA(genome)

# Set the Roulette Wheel selector method, the number of generations and
# the termination criteria
ga.selector.set(Selectors.GRouletteWheel)

# GA vars.
ga.setCrossoverRate(1.0)
ga.setMutationRate(0.08)
ga.setPopulationSize(80)
ga.setGenerations(500)
ga.setMultiProcessing(False)  # buggy when True

# ga.terminationCriteria.set(GSimpleGA.RawScoreCriteria)

# Sets the DB Adapter, the resetDB flag will make the Adapter recreate
# the database and erase all data every run. Doesn't seem to actually
# use the DB even when False.
sqlite_adapter = DBAdapters.DBSQLite(identify="ex1", resetDB=True)
ga.setDBAdapter(sqlite_adapter)

# Do the evolution, with stats dump
# frequency of 20 generations
ga.evolve(freq_stats=2)

# Best individual
print ga.bestIndividual()

```