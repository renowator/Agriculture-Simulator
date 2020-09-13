from mesa import Agent
from agriculture_simulator.random_walk import RandomWalker, TargetWalker


class Sheep(TargetWalker):
    """
    A sheep that walks around, reproduces (asexually) and gets eaten.

    The init is the same as the RandomWalker.
    """

    energy = None

    def __init__(self, unique_id, pos, model, moore, energy=None):
        super().__init__(unique_id, pos, model, moore=moore)
        self.fully_grown = False
        self.energy = energy
        self.harvest = 0
        self._limit_harvest = 500
        self.state = 'DROP'
        self.agent_type= 'HARVEST'

    def step(self):
        """
        A model step. Move, then eat grass and reproduce.
        """
        self.target_move()
        living = True

        if self.model.grass:
            # Reduce energy
            #self.energy -= 1

            # If there is grass available, gather it
            this_cell = self.model.grid.get_cell_list_contents([self.pos])
            grass_patch = [obj for obj in this_cell if isinstance(obj, GrassPatch)]
            if len(grass_patch) > 0 and self.harvest < self._limit_harvest:
              if grass_patch[0].fully_grown:
                self.harvest += 10
                grass_patch[0].fully_grown = False
                if self.harvest == self._limit_harvest:
                  self.state = 'PICK'
            shed = [obj for obj in this_cell if isinstance(obj, Shed)]
            if len(shed) > 0:
                shed[0].harvest_level += self.harvest
                self.harvest = 0
                self.state = 'DROP'
            # Death
            if self.energy < 0:
                self.model.grid._remove_agent(self.pos, self)
                self.model.schedule.remove(self)
                living = False




class Wolf(TargetWalker):
    """
    A wolf that walks around, reproduces (asexually) and eats sheep.
    """

    energy = None

    def __init__(self, unique_id, pos, model, moore, energy=None):
        super().__init__(unique_id, pos, model, moore=moore)
        self.fully_grown = False
        self.energy = energy
        self.water_storage = 0
        self._water_cap = 500
        self.state = 'PICK'
        self.agent_type = 'WATER'

    def step(self):
        self.target_move()
        #self.energy -= 1
        if self.water_storage < abs(self.target.pos[0] - self.pos[0]) + abs(self.target.pos[1] - self.pos[1]):
            self.state = 'PICK'
        else:
            self.state = 'DROP'
        # If there are plants that need water present, water
        x, y = self.pos
        this_cell = self.model.grid.get_cell_list_contents([self.pos])
        ws = [obj for obj in this_cell if isinstance(obj, WaterSource)]
        if len(ws) > 0:
            self.water_storage = self._water_cap
        patch = [obj for obj in this_cell if isinstance(obj, GrassPatch)]
        if len(patch) > 0 and self.water_storage > 0:
            patch[0].water_level = patch[0].water_level + self.model.grass_regrowth_time
            self.water_storage = self.water_storage - 1



class GrassPatch(Agent):
    """
    A patch of grass that grows at a fixed rate and it is eaten by sheep
    """

    def __init__(self, unique_id, pos, model, fully_grown, countdown):
        """
        Creates a new patch of grass

        Args:
            grown: (boolean) Whether the patch of grass is fully grown or not
            countdown: Time for the patch of grass to be fully grown again
        """
        super().__init__(unique_id, model)
        self.fully_grown = fully_grown
        self.countdown = countdown
        self.pos = pos
        self.water_level = self.random.random()*self.model.grass_regrowth_time
        self.agent_type = 'GRASS'

    def step(self):
        if self.fully_grown:
            self.water_level = self.water_level - 1
        else:
            self.water_level = self.water_level - 2
        if self.water_level == - self.model.grass_regrowth_time and self.fully_grown:
            self.fully_grown = False
        elif self.water_level < -10* self.model.grass_regrowth_time:
            self.model.grid._remove_agent(self.pos, self)
            self.model.schedule.remove(self)
        elif not self.fully_grown:
            if self.countdown <= 0:
                # Set as fully grown
                self.fully_grown = True
                self.countdown = self.model.grass_regrowth_time
            else:
                self.countdown -= 1


class WaterSource(Agent):
    """
    A Water source to be used by watering agent (wolf)
    """

    def __init__(self, unique_id, pos, model):
        """
        Creates a new water source
        """
        super().__init__(unique_id, model)
        self.fully_grown = False
        self.pos = pos
        self.water_level = 999999999
        self.agent_type = 'WS'

class Shed(Agent):
    """
    A Shed to be used by farming agent (sheep)
    """

    def __init__(self, unique_id, pos, model):
        """
        Creates a new shed
        """
        super().__init__(unique_id, model)
        self.fully_grown = False
        self.pos = pos
        self.harvest_level = 0
        self.agent_type = 'SHED'
