import random

NONE = 0
BLACK = 1
RED = 2
ZERO = 3
DOUBLE_ZERO = 4

class Table:
    def __init__(self):
        self.results = []

    def spin(self):
        generatedValue = random.randrange(0, 38)
        if generatedValue == 0:
            result = ZERO
        elif generatedValue == 1:
            result = DOUBLE_ZERO
        elif generatedValue in range(2, 20):
            result = BLACK
        elif generatedValue in range(20, 38):
            result = RED
        try:
            self.results.append(result)
        except Exception, e:
            print "Got an exception on value %s" % generatedValue

    def get_streak(self):
        """
        Get the length of the latest streak, and its color, in the format (COLOR, length of streak)
        If nothing has been spun yet, the color is NONE.
        """
        lastColor = NONE
        streak = 0
        index = len(self.results) - 1
        while index >= 0:
            currentColor = self.results[index]

            if lastColor is NONE:
                # The streak starts
                lastColor = currentColor
                streak = 1
            elif lastColor == currentColor:
                # The streak continues
                streak += 1
            else:
                # The streak has been broken, so we're out of here
                break

            # decrement the index, since we're going backwards from the end
            index -= 1

        # Return the streak information
        return (lastColor, streak)


class PerchGame:
    def __init__(self, startingCash=0, numTables=0, desiredEndingCash=None, numTurns=None):
        self.startingCash = startingCash
        self.currentCash = startingCash
        self.numTables = numTables
        self.desiredEndingCash = desiredEndingCash
        self.numTurns = numTurns

    def play(self):
        wins = 0
        losses = 0
        tables = []
        for i in range(0, self.numTables):
            tables.append(Table())
        currentTable = None
        currentStreak = 0
        currentColor = NONE
        turn = 1
        while True:
            bet = calculate_kelly_bet(1, 0.51) * self.currentCash

            for table in tables:
                table.spin()

            if currentTable is None:
                for table in tables:
                    (color, streak) = table.get_streak()
                    if streak >= 4:
                        currentTable = table
                        currentStreak = streak
                        currentColor = color
            else:
                if currentStreak == 4:
                    (color, streak) = table.get_streak()
                    if color != currentColor:
                        self.currentCash += bet
                        currentTable = None
                        wins += 1
                    else:
                        self.currentCash -= bet
                        currentStreak = 5
                        losses += 1
                elif currentStreak == 5:
                    (color, streak) = table.get_streak()
                    if color != currentColor:
                        self.currentCash += (bet * 1.5)
                        currentTable = None
                        currentStreak = 0
                        wins += 1
                    else:
                        self.currentCash -= (bet * 1.5)
                        currentTable = None
                        currentStreak = 0
                        losses += 1
                else:
                    currentTable = None
                    currentStreak = 0
                    currentColor = NONE

            if self.currentCash <= 0:
                break
            elif self.desiredEndingCash is not None and self.currentCash >= self.desiredEndingCash:
                break
            elif self.numTurns is not None and turn >= self.numTurns:
                break

            turn += 1

        return (self.currentCash, turn, wins, losses)

def calculate_kelly_bet(odds, probabilityOfWinning):
    """
    Calculates the percentage of your current bankroll that you should wager based on the odds off winning.
    The odds should be given in x-to-1 terms, ie "2-to-1 odds"
    The probabilityOfWinning should be given as a number between 0.0 and 1.0
    """
    f = (odds * probabilityOfWinning - (1.0 - probabilityOfWinning)) / odds
    return f

def calculate_average_cash_and_turns(runs):
    sumCash = 0.0
    sumTurns = 0.0
    for (cash, turns) in runs:
        sumCash += cash
        sumTurns += turns
    averageCash = sumCash / len(runs)
    averageTurns = sumTurns / len(runs)
    return (averageCash, averageTurns)

def determine_percentage_of_time_you_reached_goal(runs, goal):
    timesReachedGoal = 0.0
    for (cash, turns) in runs:
        if cash >= goal:
            timesReachedGoal += 1
    return timesReachedGoal / len(runs)

def determine_average_turns_to_win_or_bust(runs, goal):
    """
    Look over all your runs and determine the average number of turns it took to reach your goal, as well as the average of how many turns it took to bust.
    Returns (average-turns-to-win, average-turns-to-bust)
    """
    sumWinTurns = 0.0
    numWins = 0
    sumBustTurns = 0.0
    numBusts = 0
    for (cash, turns) in runs:
        if cash <= 0:
            sumBustTurns += turns
            numBusts += 1
        elif cash >= goal:
            sumWinTurns += turns
            numWins += 1
    return ( sumWinTurns/numWins , sumBustTurns/numBusts )

def determine_odds_of_busting(runs):
    numBusts = 0.0
    for (cash, turns) in runs:
        if cash <= 0:
            numBusts += 1
    return numBusts / len(runs)

if __name__ == '__main__':
    wins = 0.0
    losses = 0.0
    startingBankroll = 1000
    currentBankroll = startingBankroll
    numberOfRuns = 5*52
    desiredGoal = None
    numTurns = 100
    runs = []
    for run in range(0, numberOfRuns):
        playingWith = currentBankroll
        game = PerchGame(startingCash=playingWith, numTables=4, desiredEndingCash=desiredGoal, numTurns=numTurns)
        (finalCash, numTurns, gameWins, gameLosses) = game.play()
        #print "Played a game with $%s in %s turns" % (finalCash, numTurns)
        runs.append((finalCash, numTurns))
        currentBankroll += (finalCash - playingWith)
        wins += gameWins
        losses += gameLosses

    (averageCash, averageTurns) = calculate_average_cash_and_turns(runs)
    print "Averaged $%s in %s turns" % (averageCash, averageTurns)

    if desiredGoal is not None:
        percentageReachedGoal = determine_percentage_of_time_you_reached_goal(runs, desiredGoal) * 100
        (averageTurnsToWin, averageTurnsToBust) = determine_average_turns_to_win_or_bust(runs, desiredGoal)
        print "Reached goal %s%% of the time, in %s runs" % (percentageReachedGoal, numberOfRuns)
        print "Average turns to win: %s. Average turns to bust: %s" % (averageTurnsToWin, averageTurnsToBust)

    if numTurns is not None:
        percentageBusted = determine_odds_of_busting(runs) * 100
        print "Busted %s%% of the time" % percentageBusted

    print "Turned $%s into $%s in %s games" % (startingBankroll, currentBankroll, numberOfRuns)

    winningPercentage = (wins / (wins + losses))
    print "Won %s%% of the time" % (winningPercentage * 100)

    kellyBet = calculate_kelly_bet(1, winningPercentage)
    print "Should have been betting %s%% of bankroll each time" % (kellyBet * 100)
