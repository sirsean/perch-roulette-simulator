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
    def __init__(self, startingCash, numTables, desiredEndingCash):
        self.startingCash = startingCash
        self.currentCash = startingCash
        self.numTables = numTables
        self.desiredEndingCash = desiredEndingCash

    def play(self):
        tables = []
        for i in range(0, self.numTables):
            tables.append(Table())
        currentTable = None
        currentStreak = 0
        currentColor = NONE
        bet = 10
        turn = 1
        while True:
            for table in tables:
                table.spin()

            if currentTable is None:
                for table in tables:
                    (color, streak) = table.get_streak()
                    if streak >= 4:
                        currentTable = table
                        currentStreak = streak
                        currentColor = color
                        bet = 10
            else:
                if currentStreak == 4:
                    (color, streak) = table.get_streak()
                    if color != currentColor:
                        self.currentCash += bet
                        bet = 10
                        currentTable = None
                    else:
                        self.currentCash -= bet
                        bet = bet * 1.5
                        currentStreak = 5
                elif currentStreak == 5:
                    (color, streak) = table.get_streak()
                    if color != currentColor:
                        self.currentCash += bet
                        bet = 10
                        currentTable = None
                else:
                    currentTable = None
                    currentStreak = 0
                    currentColor = NONE

            if self.currentCash <= 0:
                break
            elif self.currentCash >= self.desiredEndingCash:
                break

            turn += 1

        return (self.currentCash, turn)

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

if __name__ == '__main__':
    numberOfRuns = 1000
    desiredGoal = 400
    runs = []
    for run in range(0, numberOfRuns):
        game = PerchGame(10, 4, desiredGoal)
        (finalCash, numTurns) = game.play()
        #print "Played a game with $%s in %s turns" % (finalCash, numTurns)
        runs.append((finalCash, numTurns))

    (averageCash, averageTurns) = calculate_average_cash_and_turns(runs)
    percentageReachedGoal = determine_percentage_of_time_you_reached_goal(runs, desiredGoal) * 100
    (averageTurnsToWin, averageTurnsToBust) = determine_average_turns_to_win_or_bust(runs, desiredGoal)
    print "Averaged $%s in %s turns" % (averageCash, averageTurns)
    print "Reached goal %s%% of the time, in %s runs" % (percentageReachedGoal, numberOfRuns)
    print "Average turns to win: %s. Average turns to bust: %s" % (averageTurnsToWin, averageTurnsToBust)

