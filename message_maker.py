import bitstring

from message_encoder import MessageEncoder, MessageType


class MessageMaker:
    @staticmethod
    def reversed_bytes(bs) -> bytes:
        # for little endian
        return bytes(reversed(bs.bytes))

    class GetService(MessageEncoder):  # 2
        def __init__(self):
            super().__init__(msg_type=MessageType.GET_SERVICE, res_required=True)

    class GetPower(MessageEncoder):  # 20
        def __init__(self):
            super().__init__(msg_type=MessageType.GET_POWER, res_required=True)

    class SetPower(MessageEncoder):  # 21
        def __init__(self, power_level: int = 65535):
            self.power_level = power_level
            super().__init__(msg_type=MessageType.SET_POWER, res_required=True)

        def get_payload(self):
            self.payload_fields.append(("Power", self.power_level))
            payload = MessageMaker.reversed_bytes(bitstring.pack("uint:16", self.power_level))
            return payload

    class GetLabel(MessageEncoder):  # 23
        def __init__(self):
            super().__init__(msg_type=MessageType.GET_LABEL, res_required=True)

    class GetColor(MessageEncoder):  # 101
        def __init__(self):
            super().__init__(msg_type=MessageType.GET_COLOR, res_required=True)

    class SetColor(MessageEncoder):  # 102
        def __init__(
                self,
                hue: float = 0,
                saturation: float = 1,
                brightness: float = 1,
                kelvin: int = 4000,
                duration: int = 100
        ):
            self.hue = hue % 360
            self.saturation: float = max(0.0, min(1.0, saturation))
            self.brightness: float = max(0.0, min(1.0, brightness))
            self.kelvin: int = max(1500, min(9000, kelvin))
            self.duration: int = duration
            super().__init__(msg_type=MessageType.SET_COLOR, ack_required=True)

        def get_payload(self):
            hue = int(self.hue / 360 * MessageEncoder.MAX_UINT16)
            saturation = int(self.saturation * MessageEncoder.MAX_UINT16)
            brightness = int(self.brightness * MessageEncoder.MAX_UINT16)

            reserved_8 = MessageMaker.reversed_bytes(bitstring.pack("uint:8", 0))
            color_fields = [hue, saturation, brightness, self.kelvin]
            color = b"".join(MessageMaker.reversed_bytes(bitstring.pack("uint:16", field)) for field in color_fields)
            duration = MessageMaker.reversed_bytes(bitstring.pack("uint:32", self.duration))
            return reserved_8 + color + duration
