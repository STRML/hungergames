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

# Genome instance, 1D List of 6 elements
genome = G1DList.G1DList(6)

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
ga.setMultiProcessing(False)

# ga.terminationCriteria.set(GSimpleGA.RawScoreCriteria)

# Sets the DB Adapter, the resetDB flag will make the Adapter recreate
# the database and erase all data every run, you should use this flag
# just in the first time, after the pyevolve.db was created, you can
# omit it.
sqlite_adapter = DBAdapters.DBSQLite(identify="ex1", resetDB=False)
ga.setDBAdapter(sqlite_adapter)

# Do the evolution, with stats dump
# frequency of 20 generations
ga.evolve(freq_stats=2)

# Best individual
print ga.bestIndividual()
