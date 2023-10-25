import binascii
import struct

from message_encoder import MessageType


class IncompleteHeader(Exception):
    def __init__(self):
        super().__init__("Insufficient data to unpack a Header")


class MessageDecoder:
    def __init__(self):
        self._bts = None

    def decode(self, data) -> dict:
        if len(data) < 36:
            raise IncompleteHeader()
        self._bts = data
        return {
            'size': self.size,
            'protocol': self.protocol,
            'addressable': self.addressable,
            'tagged': self.tagged,
            'source': self.source,
            'target': self.target,
            'res_required': self.res_required,
            'ack_required': self.ack_required,
            'sequence': self.sequence,
            'pkt_type': self.pkt_type,
            'payload': self.payload
        }

    def __getitem__(self, rng):
        return self._bts[rng]

    @property
    def size(self):
        """returns the size of the total message."""
        return struct.unpack("<H", self[0:2])[0]

    @property
    def protocol(self):
        """returns the protocol version of the header."""
        v = struct.unpack("<H", self[2:4])[0]
        return v & 0b111111111111

    @property
    def addressable(self):
        """returns whether the addressable bit is set."""
        v = self[3]
        v = v >> 4
        return (v & 0b1) != 0

    @property
    def tagged(self):
        """returns whether the tagged bit is set."""
        v = self[3]
        v = v >> 5
        return (v & 0b1) != 0

    @property
    def source(self):
        """returns then number used by clients to differentiate themselves from other clients"""
        return struct.unpack("<I", self[4:8])[0]

    @property
    def target(self):
        """returns the target Serial from the header."""
        return binascii.hexlify(self[8:16][:6]).decode()

    @property
    def res_required(self):
        """returns whether the response required bit is set in the header."""
        v = self[22]
        return (v & 0b1) != 0

    @property
    def ack_required(self):
        """returns whether the ack required bit is set in the header."""
        v = self[22]
        v = v >> 1
        return (v & 0b1) != 0

    @property
    def sequence(self):
        """returns the sequence ID from the header."""
        return self[23]

    @property
    def pkt_type(self):
        """returns the Payload ID for the accompanying payload in the message."""
        return struct.unpack("<H", self[32:34])[0]

    @property
    def payload(self):
        payload_data = self[36:]
        match self.pkt_type:
            case MessageType.GetService.value:  # 2
                return payload_data.decode("utf-8").rstrip('\x00')

            case MessageType.StateService.value:  # 3
                service = Services[int(payload_data[0])]
                port = int.from_bytes(payload_data[1:5], byteorder='little', signed=False)
                return service, port

            case MessageType.GetPower.value:  # 20
                return payload_data.decode("utf-8").rstrip('\x00')

            case MessageType.StatePower.value:  # 22
                return struct.unpack('<H', payload_data)[0]

            case MessageType.GetLabel.value:  # 23
                return payload_data.decode("utf-8").rstrip('\x00')

            case MessageType.StateLabel.value:  # 25
                return payload_data.decode("utf-8").rstrip('\x00')

            case MessageType.Acknowledgement.value:  # 45
                return None

            case _:
                raise ValueError(f"Unsupported packet type: {self.pkt_type}")

    def __str__(self):
        s = "size: " + str(self.size)
        s += "; protocol: " + str(self.protocol)
        s += "; addressable: " + str(self.addressable)
        s += "; tagged: " + str(self.tagged)
        s += "; source: " + str(self.source)
        s += "; target: " + str(self.target)
        s += "; res_required: " + str(self.res_required)
        s += "; ack_required: " + str(self.ack_required)
        s += "; sequence: " + str(self.sequence)
        s += "; pkt_type: " + str(self.pkt_type)
        s += "; payload: " + str(self.payload)
        return s


Services: dict = {
    1: "UDP",
    2: "RESERVED1",
    3: "RESERVED2",
    4: "RESERVED3",
    5: "RESERVED4"
}
