import socket
import asyncio

from message_encoder import MessageEncoder
from message_decoder import MessageDecoder
from message_maker import MessageMaker


class MessageRouter:
    HOST_IP = socket.gethostbyname(socket.gethostname())
    PORT = 56700
    HOST_ADDRESS = (HOST_IP, PORT)

    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(MessageRouter.HOST_ADDRESS)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        self.decoder = MessageDecoder()
        self.lock = asyncio.Lock()
        self.is_receiving: bool = False
        self.responses: dict = {}

    async def discover_devices(self, discovery_timeout: float = 2) -> dict:
        async with self.lock:
            self.socket.settimeout(discovery_timeout)
            self.socket.sendto(MessageMaker.GetLabel().generate_packed_message(), ('<broadcast>', MessageRouter.PORT))

            devices_info = {}
            while True:
                try:
                    response, address = self.socket.recvfrom(1024)
                    label = self.decoder.decode(response)['payload']
                    devices_info[address] = label
                except socket.timeout:
                    break

            self.socket.settimeout(None)
            return devices_info

    async def set_receiving(self, receiving: bool = True):
        async with self.lock:
            self.is_receiving = receiving
        if not receiving:
            self.socket.sendto(b'', MessageRouter.HOST_ADDRESS)

    async def start_receiving(self) -> None:
        while self.is_receiving:
            asyncio.create_task(self.store_response(*await asyncio.to_thread(self.socket.recvfrom, 1024)))

    async def store_response(self, response, address):
        async with self.lock:
            self.responses[address] = response

    async def send_and_await_response(self, encoder: MessageEncoder, device) -> dict:
        async with self.lock:
            self.socket.sendto(encoder.generate_packed_message(), device.address)
        if encoder.res_required + encoder.ack_required > 0:
            while device.address not in self.responses:
                await asyncio.sleep(0)
            async with self.lock:
                response = self.responses.pop(device.address)
                return self.decoder.decode(response)
        else:
            return {}
