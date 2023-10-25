import bitstring

from message_encoder import MessageEncoder, MessageType


class MessageMaker:
    @staticmethod
    def little_endian(bs):
        return bytes(reversed(bs.bytes))

    class GetService(MessageEncoder):  # 2
        def __init__(self):
            super().__init__(msg_type=MessageType.GetService, res_required=True)

    class GetPower(MessageEncoder):  # 20
        def __init__(self):
            super().__init__(msg_type=MessageType.GetPower, res_required=True)

    class SetPower(MessageEncoder):  # 21
        def __init__(self, power_level: int = 65535):
            self.power_level = power_level
            super().__init__(msg_type=MessageType.SetPower, res_required=True)

        def get_payload(self):
            self.payload_fields.append(("Power", self.power_level))
            payload = MessageMaker.little_endian(bitstring.pack("uint:16", self.power_level))
            return payload

    class GetLabel(MessageEncoder):  # 23
        def __init__(self):
            super().__init__(msg_type=MessageType.GetLabel, res_required=True)
