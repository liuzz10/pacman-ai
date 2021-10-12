# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from util import manhattanDistance
from game import Directions
import random, util

from game import Agent

class ReflexAgent(Agent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
    """


    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {NORTH, SOUTH, WEST, EAST, STOP}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]
        # print("newPos", newPos)
        # print("newFood", newFood)
        # print("str-newGhostStates", list(map(str, newGhostStates)))
        # print("newScaredTimes", newScaredTimes)

        "*** YOUR CODE HERE ***"
        score = 0

        current_food = currentGameState.getFood().asList()
        if newPos in current_food:
            score += 100
        food_distance = [manhattanDistance(newPos, food) for food in current_food]
        nearest_food = min(food_distance)
        score += -nearest_food

        current_capsules = currentGameState.getCapsules()
        if newPos in current_capsules:
            score += 500
        capsule_distance = [manhattanDistance(newPos, cap) for cap in current_capsules]
        if capsule_distance:
            nearest_capsule = min(capsule_distance)
            score += -nearest_capsule * 5

        ghost_position = [new_ghost.getPosition() for new_ghost in newGhostStates]
        ghost_distance = [manhattanDistance(newPos, ghost_p) for ghost_p in ghost_position]
        nearest_ghost = min(ghost_distance)

        if newPos in ghost_position:
            score -= 1000

        if nearest_ghost < 5:
            score += nearest_ghost * 5
        else:
            score += 25

        if action == Directions.STOP:
            score -= 10

        return score


def scoreEvaluationFunction(currentGameState):
    """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
    Your minimax agent (question 2)
    """

    def getAction(self, gameState):
        """
        Returns the minimax action from the current gameState using self.depth
        and self.evaluationFunction.

        Here are some method calls that might be useful when implementing minimax.

        gameState.getLegalActions(agentIndex):
        Returns a list of legal actions for an agent
        agentIndex=0 means Pacman, ghosts are >= 1

        gameState.generateSuccessor(agentIndex, action):
        Returns the successor game state after an agent takes an action

        gameState.getNumAgents():
        Returns the total number of agents in the game

        gameState.isWin():
        Returns whether or not the game state is a winning state

        gameState.isLose():
        Returns whether or not the game state is a losing state
        """
        "*** YOUR CODE HERE ***"
        """
        Depth is how many times a pacman and all ghosts moves. For example,
        depth = 2 will involve Pacman and each ghost moving two times.
        For each move, there are gameState.getNumAgents() layers, each layer
        is an agent.
        Considering depth and all agent, the number of layers in search tree
        = # of agents * # of depth.
        Max layer is the pacman, Min layer is all ghosts.
        Each depth involves following layers:
        Max -> Min1 -> Min2 -> ... -> MinN
        A max layer is followed by a min layer, A min layer can be followed by
        either a max layer or a min layer. The base case is the last Min layer
        which calls a max layer.
        """
        
        def min_value(state, curr_agent, total_agent, depth, evaluation_function):
            """
            Return the mininum value
            """
            if state.isLose() or state.isWin():
                return evaluation_function(state)
            v = float("inf")
            for action in state.getLegalActions(curr_agent):
                next_state = state.generateSuccessor(curr_agent, action)
                if curr_agent == total_agent - 1:
                    value, _ = max_value(next_state, 0, total_agent, depth - 1, evaluation_function)
                    v = min(v, value)
                else:
                    v = min(v, min_value(next_state, curr_agent+1, total_agent, depth, evaluation_function))
            return v
        
        def max_value(state, curr_agent, total_agent, depth, evaluation_function):
            """
            Return the maximum value and the action
            """
            if depth == 0 or state.isLose() or state.isWin():
                return evaluation_function(state), ""
            best_action = ""
            v = float("-inf")
            for action in state.getLegalActions(curr_agent):
                next_state = state.generateSuccessor(curr_agent, action)
                value = min_value(next_state, curr_agent + 1, total_agent, depth, evaluation_function)
                if value > v:
                    v = value
                    best_action = action
            return v, best_action

        total_agent = gameState.getNumAgents()
        _, best_action = max_value(gameState, 0, total_agent, self.depth, self.evaluationFunction)
        return best_action

        # util.raiseNotDefined()

class AlphaBetaAgent(MultiAgentSearchAgent):
    """
    Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
        Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()

class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
        Returns the expectimax action using self.depth and self.evaluationFunction

        All ghosts should be modeled as choosing uniformly at random from their
        legal moves.
        """
        "*** YOUR CODE HERE ***"
        """
        This is the same with Minimax except that min_value() is replaced
        by exp_value() which calculate the expectation of all values instead
        of the min.
        """
        def exp_value(state, curr_agent, total_agent, depth, evaluation_function):
            """
            Return the mininum value
            """
            if state.isLose() or state.isWin():
                return evaluation_function(state)
            v = 0
            count = 0
            for action in state.getLegalActions(curr_agent):
                next_state = state.generateSuccessor(curr_agent, action)
                if curr_agent == total_agent - 1:
                    value, _ = max_value(next_state, 0, total_agent, depth - 1, evaluation_function)
                    v += value
                else:
                    value = exp_value(next_state, curr_agent+1, total_agent, depth, evaluation_function)
                    v += value
                count += 1
            return v / count
        
        def max_value(state, curr_agent, total_agent, depth, evaluation_function):
            """
            Return the maximum value and the action
            """
            if depth == 0 or state.isLose() or state.isWin():
                return evaluation_function(state), ""
            best_action = ""
            v = float("-inf")
            for action in state.getLegalActions(curr_agent):
                next_state = state.generateSuccessor(curr_agent, action)
                value = exp_value(next_state, curr_agent + 1, total_agent, depth, evaluation_function)
                if value > v:
                    v = value
                    best_action = action
            return v, best_action

        total_agent = gameState.getNumAgents()
        _, best_action = max_value(gameState, 0, total_agent, self.depth, self.evaluationFunction)
        return best_action



def betterEvaluationFunction(currentGameState):
    """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"
    util.raiseNotDefined()

# Abbreviation
better = betterEvaluationFunction
