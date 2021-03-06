# multiAgents.py
# --------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

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
    some Directions.X for some X in the set {North, South, West, East, Stop}
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
    remaining food (oldFood) and Pacman position after moving (newPos).
    newScaredTimes holds the number of moves that each ghost will remain
    scared because of Pacman having eaten a power pellet.

    Print out these variables to see what you're getting, then combine them
    to create a masterful evaluation function.
    """
    # Useful information you can extract from a GameState (pacman.py)
    successorGameState = currentGameState.generatePacmanSuccessor(action)
    newPos = successorGameState.getPacmanPosition()
    oldFood = currentGameState.getFood()
    newGhostStates = successorGameState.getGhostStates()
    newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

    "*** YOUR CODE HERE ***"

    # get the closest food by creating PriorityQueue
    oldFoodByDistance = util.PriorityQueue()
    for food in oldFood.asList():
      oldFoodByDistance.push(food, util.manhattanDistance(newPos, food))
    closestFoodPos = oldFoodByDistance.pop()

    # weigh food as the distance from the closest food
    foodWeight = util.manhattanDistance(newPos, closestFoodPos)

    # get the closest ghost by creating PriorityQueue
    ghostsByDistance = util.PriorityQueue()
    for ghost in newGhostStates:
      ghostsByDistance.push(ghost.getPosition(), util.manhattanDistance(newPos, ghost.getPosition()))

    # no ghosts here
    if ghostsByDistance.isEmpty():
      ghostWeight = 0

    else:
      # get closest ghost
      closestGhostPos = ghostsByDistance.pop()

      # ghost at new pos !, worst case
      if util.manhattanDistance(newPos, closestGhostPos) == 0:
        return -float("inf")

      #! set ghost score as negative, give better results when pacman is further from a ghost
      ghostWeight = -2 * 1 / util.manhattanDistance(newPos, closestGhostPos)

    if foodWeight == 0:
      # next move is food, give better score
      score = 2 + ghostWeight
    else:
      # set score to give better results fore closer food and weigh in the ghosts proximity
      score = 1 / float(foodWeight) + ghostWeight

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

      Directions.STOP:
        The stop direction, which is always legal

      gameState.generateSuccessor(agentIndex, action):
        Returns the successor game state after an agent takes an action

      gameState.getNumAgents():
        Returns the total number of agents in the game
    """
    pacman = 0
    legal_actions = gameState.getLegalActions(pacman)
    actions = util.PriorityQueue()
    iteration = self.depth * gameState.getNumAgents()

    # check all legal actions and keep scores in a reversed PriorityQueue (max) for the best options to return
    for action in legal_actions:
      # remove stop action
      if action is Directions.STOP:
        continue
      actions.push(action, (self.minMaxVals(gameState.generateSuccessor(pacman, action), pacman, iteration - 1) * -1))

    return actions.pop()

  def minMaxVals(self, state, agent, iteration):

    if state.isWin() or state.isLose() or iteration == 0:
      return self.evaluationFunction(state)

    # round robin agent
    agent = (agent + 1) % state.getNumAgents()

    legal_actions = state.getLegalActions(agent)
    actions = []

    # Only pacman == 0 so all other are min agents
    if agent > 0:
      for action in legal_actions:
        actions.append(self.minMaxVals(state.generateSuccessor(agent, action), agent, iteration - 1))
      return min(actions)

    # Pacman's turn
    for action in legal_actions:
      # remove stop action
      if action is Directions.STOP:
        continue
      actions.append(self.minMaxVals(state.generateSuccessor(agent, action), agent, iteration -1))
    return max(actions)

class AlphaBetaAgent(MultiAgentSearchAgent):
  """
    Your minimax agent with alpha-beta pruning (question 3)
  """

  def getAction(self, gameState):
    """
      Returns the minimax action using self.depth and self.evaluationFunction
    """
    pacman = 0
    legal_actions = gameState.getLegalActions(pacman)
    iteration = self.depth * gameState.getNumAgents()

    v = -float("inf")
    a = -float("inf")
    b = float("inf")

    # check all legal actions of pacman
    for action in legal_actions:
      # remove stop action
      if action is Directions.STOP:
        continue

      v = max(v, self.minValue(gameState.generateSuccessor(pacman, action), pacman + 1, iteration - 1, a, b))

      # redundent at top level, here for the algo structure
      if v > b:
        next_action = action
        break

      if a < v:
        next_action = action
        a = v

    return next_action

  def maxValue(self, state, agent, iteration, a, b):
    if state.isWin() or state.isLose() or iteration == 0:
      return self.evaluationFunction(state)

    v = -float("inf")
    legal_actions = state.getLegalActions(agent)

    for action in legal_actions:
      # remove stop action - Only for max agent (pacman)
      if action is Directions.STOP:
        continue

      successor = state.generateSuccessor(agent, action)
      # get next agent, round robin agent
      next_agent = (agent + 1) % state.getNumAgents()

      v = max(v, self.minValue(successor, next_agent, iteration -1, a, b))
      if v > b:
        return v
      a = max(a, v)

    return v

  def minValue(self, state, agent, iteration, a, b):
    if state.isWin() or state.isLose() or iteration == 0:
      return self.evaluationFunction(state)

    v = float("inf")
    legal_actions = state.getLegalActions(agent)

    for action in legal_actions:
      successor = state.generateSuccessor(agent, action)
      # get next agent, round robin agent
      next_agent = (agent + 1) % state.getNumAgents()

      # if next is pacman(0), we need to check the max value
      if next_agent == 0:
        v = min(v, self.maxValue(successor, next_agent, iteration - 1, a, b))
      else:
        v = min(v, self.minValue(successor, next_agent, iteration - 1, a, b))

      if v < a:
        return v
      b = min(b, v)

    return v


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
    util.raiseNotDefined()

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

class ContestAgent(MultiAgentSearchAgent):
  """
    Your agent for the mini-contest
  """

  def getAction(self, gameState):
    """
      Returns an action.  You can use any method you want and search to any depth you want.
      Just remember that the mini-contest is timed, so you have to trade off speed and computation.

      Ghosts don't behave randomly anymore, but they aren't perfect either -- they'll usually
      just make a beeline straight towards Pacman (or away from him if they're scared!)
    """
    "*** YOUR CODE HERE ***"
    util.raiseNotDefined()

