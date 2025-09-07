import asyncio
from datetime import datetime

from commands import *
from connection import Connection, FakeConnection;
from textToImage import textToImage;

def getDate():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

async def beginLog(conn):
    img = textToImage(f"BEGIN LOG @ [{getDate()}]", fontSize=16, align="center", bold=True)
    cmds = genCommands(img, energy=getEnergy(7), moveUpAfter=False)
    await conn.send(cmds)

async def printToLog(conn, text):
    img = textToImage(f"[{getDate()}] {text}")
    cmds = genCommands(img, energy=getEnergy(7), moveUpAfter=False)
    await conn.send(cmds)

async def finishLog(conn):
    img = textToImage(f"END LOG @ [{getDate()}]", fontSize=16, align="center", bold=True)
    cmds = genCommands(img, energy=getEnergy(7), moveUpAfter=True)
    await conn.send(cmds)

async def main():
    async with Connection("AA:BB:CC:DD:EE:FF") as conn:
        await beginLog(conn)
        for i in range(3):
            await printToLog(conn, f"Message in log #{i+1}")
        await finishLog(conn)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())