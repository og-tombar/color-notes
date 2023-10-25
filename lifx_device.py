import asyncio

from globals import Globals
from message_encoder import MessageEncoder
from message_maker import MessageMaker


class LifxDevice:
    MAX_POWER: int = 65535

    def __init__(
            self,
            address: tuple[str] = None,
    ):
        self.lock = asyncio.Lock()
        self.address: tuple[str] = address

    def __str__(self):
        return f'Address: {self.address[0]}'

    def __hash__(self):
        return hash(self.address)

    def __eq__(self, other):
        return self.address == other.address if isinstance(other, self.__class__) else False

    async def do(self, method: str = 'set_power', args: tuple = ()):
        return await getattr(self, method)(*args)

    async def get(self, prop: str = 'power'):
        return await getattr(self, prop)

    async def send_and_await_response(self, encoder: MessageEncoder):
        async with self.lock:
            response = await Globals.router.send_and_await_response(encoder, self)
            return response['payload']

    @property
    async def info(self) -> str:
        info = 'LIFX Device:\n'
        info += f'Label: {await self.label}\n'
        info += f'Power: {await self.power}\n'
        return info

    @property
    async def service(self):
        return await self.send_and_await_response(MessageMaker.GetService())

    @property
    async def label(self) -> str:
        return await self.send_and_await_response(MessageMaker.GetLabel())

    @property
    async def power(self) -> int:
        await asyncio.sleep(0.2)
        return await self.send_and_await_response(MessageMaker.GetPower())

    async def set_power(self, power_level: int = MAX_POWER):
        await self.send_and_await_response(MessageMaker.SetPower(power_level))
        return await self.power

    async def turn_on(self):
        return await self.set_power(LifxDevice.MAX_POWER)

    async def turn_off(self):
        return await self.set_power(0)

    async def toggle_power(self) -> int:
        if await self.power == 0:
            return await self.turn_on()
        else:
            return await self.turn_off()
