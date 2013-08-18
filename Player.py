import numpy


class BasePlayer(object):
    def __str__(self):
        try:
            return self.name
        except AttributeError:
            # Fall back on Python default
            return super(BasePlayer, self).__repr__()

    def hunt_choices(*args, **kwargs):
        raise NotImplementedError("You must define a strategy!")

    def hunt_outcomes(*args, **kwargs):
        pass

    def round_end(*args, **kwargs):
        pass


class Player(BasePlayer):

    # For reference
    payoff_table = [
        [0, -3],  # h,h  h,s
        [1, -2]   # s,h  s,s
    ]

    '''
    A chromosome contains a number of ints deciding behavior.
    These are weights between 0 and 100.
    Given these weights, we execute a number of strategy functions. Each function returns
    1 (for 'hunt') or 0. The results are multplied by the specified weight in the chromosome
    and summed. A sum >= 100 indicates a hunt.

    Best chromosomes in our longest tests: [15,15,13,15,15,14,15], [1,1,1,1,1,1,1]
    This suggests that slacking is the optimal strategy.
    '''

    def __init__(self, chromosome=[1, 1, 1, 1, 1, 1, 1]):
        self.name = "GA Player"
        assert chromosome and len(chromosome) > 0, "A chromosome must be provided"
        self.chromosome = chromosome
        self.functions = [
            self.reputation_based_hunting,
            self.mean_reputation_hunting,
            self.median_reputation_hunting,
            self.maintain_average_reputation,
            self.evaluate_the_past,
            self.hunt_in_medium_rep,
            self.achieve_public_good
        ]
        self.past_performance = {'h': 0, 's': 0}

    def hunt_choices(self, round_number, current_food, current_reputation,
                     m, player_reputations):
        '''Use our chromosome to make a choice.'''

        args = locals()

        decisions = []

        # For each reputation, make a choice.
        for idx, reputation in enumerate(player_reputations):
            score = 0

            # Add the current opponent's reputation to the args.
            args['opponent_reputation'] = reputation

            # For each decider function, weight its result by the corresponding index in the chromosome.
            for idx, function in enumerate(self.functions):
                score += self.weight_choice(function, args, self.chromosome[idx])

            # If our score is gte than max_score / 2, hunt.
            if score >= 100:
                decisions.append('h')
            # Otherwise, slack
            else:
                decisions.append('s')

        self.last_decisions = decisions[:]
        return decisions

    def hunt_outcomes(self, food_earnings):
        '''For each outcome, keep up a list of how that decision has been going for us.'''
        for idx, decision in enumerate(self.last_decisions):
            self.past_performance[decision] += food_earnings[idx]
        pass

    def round_end(self, award, m, number_hunters):
        pass

    #
    # Utility functions
    #

    # Run a given strategy. Weight its decision by the passed in weight (defined in chromosome).
    # A 'hunt' is 1, a 'slack' is 0.
    def weight_choice(self, strategyFunction, args, weight):
        decision = 1 if strategyFunction(args) == 'h' else 0
        return weight * decision

    # Defining this because numpypy.median is not implemented
    def median(self, numbers):
        "Return the median of the list of numbers."
        # Sort the list and take the middle element.
        n = len(numbers)
        copy = numbers[:]  # So that "numbers" keeps its original order
        copy.sort()
        if n & 1:         # There is an odd number of elements
            return copy[n // 2]
        else:
            return (copy[n // 2 - 1] + copy[n // 2]) / 2

    #
    # Define Strategies below here.
    #

    def reputation_based_hunting(self, args):
        ''' Reputation-based hunting. This will hunt if the opponent's reputation is above ours. '''
        return 'h' if args['opponent_reputation'] > args['current_reputation'] else 's'

    def mean_reputation_hunting(self, args):
        ''' Hunt if an opponent's reputation is above average, slack otherwise '''
        return 'h' if args['opponent_reputation'] > numpy.mean(args['player_reputations']) else 's'

    def median_reputation_hunting(self, args):
        ''' Hunt if an opponent's reputation is above median '''
        # numpypy doesn't have median
        return 'h' if args['opponent_reputation'] > self.median(args['player_reputations']) else 's'

    def maintain_average_reputation(self, args):
        ''' Attempt to keep our reputation above a certain the mean. '''
        return 'h' if args['current_reputation'] < numpy.mean(args['player_reputations']) else 's'

    def evaluate_the_past(self, args):
        ''' Evaluate how it's been going when hunting and slacking in the past. If hunting has been
            better for us, do that. '''
        return 'h' if self.past_performance['h'] > self.past_performance['s'] else 's'

    def hunt_in_medium_rep(self, args):
        ''' Slack if our opponent is a slacker, slack if he's a known hunter (and collect the food),
            hunt in the middle. '''
        op_rep = args['opponent_reputation']
        return 'h' if op_rep > .4 and op_rep < .7 else 's'

    def achieve_public_good(self, args):
        ''' Hunt when necessary to achieve the public good. This is a group survival strategy. '''
        rep = args['player_reputations']
        probable_hunts = numpy.mean(rep) * (len(rep) - 1) ** 2
        hunt_difference = args['m'] - probable_hunts

        return 'h' if hunt_difference > 0 else 's'
