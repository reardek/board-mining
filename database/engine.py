from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine

client = AsyncIOMotorClient()
engine = AIOEngine(motor_client=client, database="board_mining")