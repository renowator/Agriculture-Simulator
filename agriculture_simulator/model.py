"""
Wolf-Sheep Predation Model
================================

Replication of the model found in NetLogo:
    Wilensky, U. (1997). NetLogo Wolf Sheep Predation model.
    http://ccl.northwestern.edu/netlogo/models/WolfSheepPredation.
    Center for Connected Learning and Computer-Based Modeling,
    Northwestern University, Evanston, IL.
"""

from mesa import Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector

from agriculture_simulator.agents import Sheep, Wolf, GrassPatch, WaterSource, Shed
from agriculture_simulator.schedule import RandomActivationByBreed


class WolfSheep(Model):
    """
    Wolf-Sheep Predation Model
    """

    height = 20
    width = 20

    initial_sheep = 2
    initial_wolves = 5
    sheep_reproduce = 0.04
    wolf_reproduce = 0.05

    wolf_gain_from_food = 20

    grass = False
    grass_regrowth_time = 5
    sheep_gain_from_food = 4

    verbose = False  # Print-monitoring

    description = (
        "A model for simulating wolf and sheep (predator-prey) ecosystem modelling."
    )

    def __init__(
        self,
        height=20,
        width=20,
        initial_sheep=100,
        initial_wolves=50,
        sheep_reproduce=0.04,
        wolf_reproduce=0.05,
        wolf_gain_from_food=20,
        grass=False,
        grass_regrowth_time=30,
        sheep_gain_from_food=4
    ):
        """
        Create a new Wolf-Sheep model with the given parameters.

        Args:
            initial_sheep: Number of sheep to start with
            initial_wolves: Number of wolves to start with
            sheep_reproduce: Probability of each sheep reproducing each step
            wolf_reproduce: Probability of each wolf reproducing each step
            wolf_gain_from_food: Energy a wolf gains from eating a sheep
            grass: Whether to have the sheep eat grass for energy
            grass_regrowth_time: How long it takes for a grass patch to regrow
                                 once it is eaten
            sheep_gain_from_food: Energy sheep gain from grass, if enabled.
        """
        super().__init__()
        # Set parameters
        self.height = height
        self.width = width
        self.initial_sheep = initial_sheep
        self.initial_wolves = initial_wolves
        self.sheep_reproduce = sheep_reproduce
        self.wolf_reproduce = wolf_reproduce
        self.wolf_gain_from_food = wolf_gain_from_food
        self.grass = grass
        self.grass_regrowth_time = grass_regrowth_time
        self.sheep_gain_from_food = sheep_gain_from_food
        self.schedule = RandomActivationByBreed(self)
        self.grid = MultiGrid(self.height, self.width, torus=True)
        self.datacollector = DataCollector(
            {
                "Wolves": lambda m: m.schedule.get_breed_count(Wolf),
                "Sheep": lambda m: m.schedule.get_breed_count(Sheep),
            }
        )
        # Create Shed
        x = self.random.randrange(self.width)
        y = self.random.randrange(self.height)
        shed = Shed(self.next_id(), (x, y), self)
        self.grid.place_agent(shed, (x, y))
        self.schedule.add(shed)

        # Create water source
        while True:
          x = self.random.randrange(self.width)
          y = self.random.randrange(self.height)
          this_cell = self.grid.get_cell_list_contents([(x,y)])
          cell = [obj for obj in this_cell if isinstance(obj, Shed)]
          if len(cell) == 0:
              break
        ws1 = WaterSource(self.next_id(), (x, y), self)
        self.grid.place_agent(ws1, (x, y))
        self.schedule.add(ws1)
        while True:
          x = self.random.randrange(self.width)
          y = self.random.randrange(self.height)
          this_cell = self.grid.get_cell_list_contents([(x,y)])
          cell = [obj for obj in this_cell if isinstance(obj, Shed)]
          if len(cell) == 0:
              break
          cell = [obj for obj in this_cell if isinstance(obj, WaterSource)]
          if len(cell) == 0:
              break
        ws2 = WaterSource(self.next_id(), (x, y), self)
        self.grid.place_agent(ws2, (x, y))
        self.schedule.add(ws2)

        # Create grass patches
        if self.grass:
            for agent, x, y in self.grid.coord_iter():
                this_cell = self.grid.get_cell_list_contents([(x,y)])
                is_water = [obj for obj in this_cell if isinstance(obj, WaterSource)]
                is_shed = [obj for obj in this_cell if isinstance(obj, Shed)]
                if len(is_water) > 0 or len(is_shed)> 0:
                    continue
                fully_grown = self.random.choice([True, False])
                if fully_grown:
                    countdown = self.grass_regrowth_time
                else:
                    countdown = self.random.randrange(self.grass_regrowth_time)

                patch = GrassPatch(self.next_id(), (x, y), self, fully_grown, countdown)
                self.grid.place_agent(patch, (x, y))
                self.schedule.add(patch)


        # Create sheep:
        for i in range(self.initial_sheep):
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            energy = self.random.randrange(2 * self.sheep_gain_from_food)
            sheep = Sheep(self.next_id(), (x, y), self, True, energy)
            sheep.target = shed
            self.grid.place_agent(sheep, (x, y))
            self.schedule.add(sheep)

        # Create wolves
        for i in range(self.initial_wolves):
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            energy = self.random.randrange(2 * self.wolf_gain_from_food)
            wolf = Wolf(self.next_id(), (x, y), self, True, energy)
            if abs(ws1.pos[0] - x) + abs(ws1.pos[1] - y) < abs(ws2.pos[0] - x) + abs(ws2.pos[1] - y):
                wolf.target = ws1
            else:
                wolf.target = ws2
            self.grid.place_agent(wolf, (x, y))
            self.schedule.add(wolf)



        self.running = True
        self.datacollector.collect(self)

    def step(self):
        self.schedule.step()
        # collect data
        self.datacollector.collect(self)
        if self.verbose:
            print(
                [
                    self.schedule.time,
                    self.schedule.get_breed_count(Wolf),
                    self.schedule.get_breed_count(Sheep),
                ]
            )

    def run_model(self, step_count=200):

        if self.verbose:
            print("Initial number wolves: ", self.schedule.get_breed_count(Wolf))
            print("Initial number sheep: ", self.schedule.get_breed_count(Sheep))

        for i in range(step_count):
            self.step()

        if self.verbose:
            print("")
            print("Final number wolves: ", self.schedule.get_breed_count(Wolf))
            print("Final number sheep: ", self.schedule.get_breed_count(Sheep))
