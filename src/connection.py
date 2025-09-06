from bleak import BleakClient;
import asyncio
import sys

class Connection:
    _RX_CHAR = "0000AE02-0000-1000-8000-00805F9B34FB"
    _TX_CHAR = "0000AE01-0000-1000-8000-00805F9B34FB"
    _GET_DEV_STATE = b"\x51\x78\xA3\x00\x01\x00\x00\x00\xFF"

    def _charNotify(self, char, notify):
        if char.uuid == Connection._RX_CHAR.lower() and notify[0] == 0x51 and notify[1] == 0x78 and notify[2] == 0xA3:
            statusByte = bin(notify[6])
            status = None
        if notify[6] == 0x00:
            status = "OKAY"
        elif statusByte.endswith("1"):
            status = "OUT_OF_PAPER"
        elif statusByte.endswith("10"):
            status = "COMPARTMENT_OPEN"
        elif statusByte.endswith("100"):
            status = "OVERHEATED"
        elif statusByte.endswith("1000"):
            status = "LOW_BATTERY"
        elif statusByte.endswith("10000"):
            status = "CHARGING"
        elif statusByte.endswith("10000000"):
            status = "PRINTING"

        print(f"Device status: {status}")

        assert status in ["OKAY", "LOW_BATTERY", "CHAR"]
        self.notifyStatusEvent.set()  # Signal that notification was received

    async def _waitForReady(self):
        if not self.client or not self.client.is_connected:
            raise RuntimeError("Client not connected")
        print("Waiting for device status")
        await self.client.write_gatt_char(Connection._TX_CHAR, Connection._GET_DEV_STATE)
        await self.notifyStatusEvent.wait()
        self.notifyStatusEvent.clear()

    async def connect(self):
        if self.client and self.client.is_connected:
            raise RuntimeError("Client already connected")
        self.client = BleakClient(self.macAddress)
        await self.client.connect()
        self.client.connection = self
        await self.client.start_notify(Connection._RX_CHAR, self._charNotify)
        await self._waitForReady()

    async def disconnect(self):
        if not self.client or not self.client.is_connected:
            raise RuntimeError("Client not connected")
        await self.client.disconnect()

    def __init__(self, macAddress):
        self.macAddress = macAddress
        self.notifyStatusEvent = asyncio.Event()
        self.client = None

    async def __aenter__(self):
        if not self.client or not self.client.is_connected:
            await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_value, exc_tb):
        await self.disconnect()

    async def send(self, commands, delay=0):
        if not self.client or not self.client.is_connected:
            raise RuntimeError("Client not connected")
        print("Sending commands...")
        for cmd in commands:
            await self.client.write_gatt_char(Connection._TX_CHAR, cmd)
            print("Sending " + hex(cmd[2]))
            if delay > 0:
                await asyncio.sleep(delay)
        print("Finished sending commands")
        await self._waitForReady()

class FakeConnection:
    async def connect(self):
        if self.file and not self.file.is_open.closed:
            raise RuntimeError("File already opened")
        self.file = open(self.logFilePath, "ab")
        if self.humanLogFilePath:
            self.humanFile = open(self.humanLogFilePath, "a")

    async def disconnect(self):
        if not self.file or self.file.closed:
            raise RuntimeError("File already closed")
        self.file.close()
        if self.humanFile:
            self.humanFile.close()

    def __init__(self, logFilePath, humanLogFilePath=None):
        self.logFilePath = logFilePath
        self.humanLogFilePath = humanLogFilePath
        self.file = None
        self.humanFile = None

    async def __aenter__(self):
        if not self.file or self.client.closed:
            await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_value, exc_tb):
        await self.disconnect()

    async def send(self, commands, delay=0):
        if not self.file or self.file.closed:
            raise RuntimeError("File not opened")
        print("Sending commands...")
        for cmd in commands:
            self.file.write(cmd)
            if self.humanFile:
                self.humanFile.write(" ".join([hex(c)[2:].zfill(2).upper() for c in cmd]) + "\n")
        print("Finished sending commands")
