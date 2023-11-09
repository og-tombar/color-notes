import asyncio

from globals import Globals
from message_encoder import MessageEncoder
from message_maker import MessageMaker


class LifxDevice:
    def __init__(self, address: tuple[str] = None):
        self.lock = asyncio.Lock()
        self.address: tuple[str] = address

    def __str__(self):
        return f'Address: {self.address[0]}'

    def __hash__(self):
        return hash(self.address)

    def __eq__(self, other):
        return self.address == other.address if isinstance(other, self.__class__) else False

    async def do(self, method: str = 'set_power', kwargs: dict = None):
        kwargs = {} if kwargs is None else kwargs
        return await getattr(self, method)(**kwargs)

    async def get(self, prop: str = 'power'):
        return await getattr(self, prop)

    async def send_and_await_response(self, encoder: MessageEncoder):
        async with self.lock:
            response = await Globals.router.send_and_await_response(encoder, self)
            return response['payload']

    @property
    async def info(self) -> str:
        state = await self.color
        info = f'Label: {state["label"]}\n'
        info += f'Power: {state["power"]}\n'
        info += f'Hue: {state["hue"]}\n'
        info += f'Saturation: {state["saturation"]}\n'
        info += f'Brightness: {state["brightness"]}\n'
        info += f'Kelvin: {state["kelvin"]}\n'
        return info

    @property
    async def service(self) -> dict:
        return await self.send_and_await_response(MessageMaker.GetService())

    @property
    async def label(self) -> dict:
        return await self.send_and_await_response(MessageMaker.GetLabel())

    @property
    async def power(self) -> dict:
        return await self.send_and_await_response(MessageMaker.GetPower())

    async def set_power(self, power_level: int = MessageEncoder.MAX_UINT16) -> dict:
        await self.send_and_await_response(MessageMaker.SetPower(power_level))
        return await self.power

    async def turn_on(self) -> dict:
        return await self.set_power(MessageEncoder.MAX_UINT16)

    async def turn_off(self) -> dict:
        return await self.set_power(0)

    async def toggle_power(self) -> dict:
        if await self.power == 0:
            return await self.turn_on()
        else:
            return await self.turn_off()

    @property
    async def color(self):
        return await self.send_and_await_response(MessageMaker.GetColor())

    async def set_color(
            self,
            hue: int = 0,
            saturation: int = 1,
            brightness: int = 1,
            kelvin: int = 4000,
            duration: int = 100
    ):

        return await self.send_and_await_response(MessageMaker.SetColor(
            hue=hue,
            saturation=saturation,
            brightness=brightness,
            kelvin=kelvin,
            duration=duration
        ))
