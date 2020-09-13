from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.UserParam import UserSettableParameter

from agriculture_simulator.agents import Wolf, Sheep, GrassPatch, WaterSource, Shed
from agriculture_simulator.model import WolfSheep


def wolf_sheep_portrayal(agent):
    if agent is None:
        return

    portrayal = {}

    if type(agent) is Shed:
        portrayal["Shape"] = "agriculture_simulator/resources/shed.png"
        # https://icons8.com/web-app/36821/German-Shepherd
        portrayal["scale"] = 0.9
        portrayal["Layer"] = 2
        portrayal["text"] = round(agent.harvest_level, 1)
        portrayal["text_color"] = "Black"

    if type(agent) is Sheep:
        portrayal["Shape"] = "agriculture_simulator/resources/roboarm.png"
        # https://icons8.com/web-app/433/sheep
        portrayal["scale"] = 0.9
        portrayal["Layer"] = 2
        portrayal["text"] = round(agent.harvest, 1)
        portrayal["text_color"] = "Black"

    elif type(agent) is Wolf:
        portrayal["Shape"] = "agriculture_simulator/resources/watercart.png"
        # https://icons8.com/web-app/36821/German-Shepherd
        portrayal["scale"] = 0.9
        portrayal["Layer"] = 2
        portrayal["text"] = round(agent.water_storage, 1)
        portrayal["text_color"] = "Black"

    elif type(agent) is GrassPatch:
        if agent.fully_grown:
            portrayal["Color"] = ["#00FF00", "#00CC00", "#009900"]
        else:
            portrayal["Color"] = ["#84e184", "#adebad", "#d6f5d6"]
        portrayal["Shape"] = "rect"
        portrayal["Filled"] = "true"
        portrayal["Layer"] = 0
        portrayal["w"] = 1
        portrayal["h"] = 1

    elif type(agent) is WaterSource:
        portrayal["Shape"] = "agriculture_simulator/resources/water.png"
        # https://icons8.com/web-app/36821/German-Shepherd
        portrayal["scale"] = 0.9
        portrayal["Layer"] = 0

    return portrayal


canvas_element = CanvasGrid(wolf_sheep_portrayal, 20, 20, 500, 500)


model_params = {
    "grass": UserSettableParameter("checkbox", "Grass Enabled", True),
    "grass_regrowth_time": UserSettableParameter(
        "slider", "Grass Regrowth Time", 20, 1, 50
    ),
    "initial_sheep": UserSettableParameter(
        "slider", "Initial Sheep Population", 100, 1, 300
    ),
    "initial_wolves": UserSettableParameter(
        "slider", "Initial Wolf Population", 50, 1, 300
    ),
}

server = ModularServer(
    WolfSheep, [canvas_element], "Wolf Sheep Predation", model_params
)
server.port = 8521
