"""
Generalized behavior for random walking, one grid cell at a time.
"""

from mesa import Agent


class RandomWalker(Agent):
    """
    Class implementing random walker methods in a generalized manner.

    Not indended to be used on its own, but to inherit its methods to multiple
    other agents.

    """

    grid = None
    x = None
    y = None
    moore = True

    def __init__(self, unique_id, pos, model, moore=True):
        """
        grid: The MultiGrid object in which the agent lives.
        x: The agent's current x coordinate
        y: The agent's current y coordinate
        moore: If True, may move in all 8 directions.
                Otherwise, only up, down, left, right.
        """
        super().__init__(unique_id, model)
        self.pos = pos
        self.moore = moore

    def random_move(self):
        """
        Step one cell in any allowable direction.
        """
        # Pick the next cell from the adjacent cells.
        next_moves = self.model.grid.get_neighborhood(self.pos, self.moore, True)
        next_move = self.random.choice(next_moves)
        # Now move:
        self.model.grid.move_agent(self, next_move)


class TargetWalker(Agent):
    """
    Class implementing random walker methods in a generalized manner.

    Not indended to be used on its own, but to inherit its methods to multiple
    other agents.

    """

    grid = None
    x = None
    y = None
    moore = True

    def __init__(self, unique_id, pos, model, moore=True):
        """
        grid: The MultiGrid object in which the agent lives.
        x: The agent's current x coordinate
        y: The agent's current y coordinate
        moore: If True, may move in all 8 directions.
                Otherwise, only up, down, left, right.
        """
        super().__init__(unique_id, model)
        self.pos = pos
        self.moore = moore
        self.target = None
        self.state = 'PICK'
        self.agent_type = None

    def target_move(self):
        """
        Step one cell in any allowable direction.
        """
        # Pick the next cell from the adjacent cells.
        next_moves = self.model.grid.get_neighborhood(self.pos, self.moore, True)
        next_move = None
        if self.agent_type is not None:
            if self.state == 'DROP' and self.agent_type == 'WATER':
                for move in next_moves:
                    patch = self.model.grid.get_cell_list_contents(move)
                    min_level = 5000
                    if len(patch) > 0:
                        for i in range(len(patch)):
                            if patch[i].agent_type == 'GRASS' and min_level >= patch[i].water_level:
                                next_move = move
                                min_level = patch[i].water_level
            elif self.state == 'DROP' and self.agent_type == 'HARVEST':
                for move in next_moves:
                    patch = self.model.grid.get_cell_list_contents(move)
                    if len(patch) > 0:
                        if patch[0].fully_grown:
                            next_move = move
                            break
                if next_move == None:
                    next_move = self.random.choice(next_moves)
            elif self.state == 'PICK':
                for move in next_moves:
                    if abs(self.target.pos[0] - move[0]) + abs(self.target.pos[1] - move[1]) < abs(self.target.pos[0] - self.pos[0]) + abs(self.target.pos[1] - self.pos[1]):
                        next_move = move
                        break
                if next_move is None:
                    next_move = self.random.choice(next_moves)
        if next_move is not None:
            # Now move:
            self.model.grid.move_agent(self, next_move)
