from agriculture_simulator.server import server
import asyncio

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
server.launch()
