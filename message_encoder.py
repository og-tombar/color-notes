import struct
from enum import Enum


class MessageType(Enum):
    GET_SERVICE = 2
    STATE_SERVICE = 3
    GET_POWER = 20
    SET_POWER = 21
    STATE_POWER = 22
    GET_LABEL = 23
    STATE_LABEL = 25
    ACKNOWLEDGEMENT = 45
    GET_COLOR = 101
    SET_COLOR = 102
    LIGHT_STATE = 107


class MessageEncoder:
    HEADER_SIZE_BYTES: int = 36
    SOURCE_INDEX: int = 2
    __sequence: int = -1
    MAX_UINT16: int = 65535

    @staticmethod
    def get_sequence() -> int:
        MessageEncoder.__sequence = (1 + MessageEncoder.__sequence) % 256
        return MessageEncoder.__sequence

    def __init__(
            self,
            msg_type: MessageType = MessageType.GET_SERVICE,
            ack_required: bool = False,
            res_required: bool = False,
            payload: dict = None
    ):
        # Frame
        self.frame_format: list[str] = ["<H", "<H", "<L"]
        self.size = None  # 16 bits/uint16
        self.origin: int = 0  # 2 bits/uint8, must be zero
        self.tagged: int = 1  # 1 bit/bool, also must be one if getservice
        self.addressable: int = 1  # 1 bit/bool, must be one
        self.protocol: int = 1024  # 12 bits/uint16

        # 32 bits/uint32, unique ID set by client.
        # If zero, broadcast reply requested. If non-zero, unicast reply requested.
        self.source_id: int = MessageEncoder.SOURCE_INDEX

        # Frame Address
        self.frame_addr_format: list[str] = ["<Q", "<BBBBBB", "<B", "<B"]
        self.target_addr = "00:00:00:00:00:00"  # 64 bits/uint64, either single MAC address or all zeroes for broadcast.
        self.ack_required: int = 1 if ack_required else 0  # 1 bit/bool, 1 = yes
        self.res_required: int = 1 if res_required else 0  # 1 bit/bool, 1 = yes
        self.sequence: int = MessageEncoder.get_sequence()  # 8 bits/uint8, wraparound

        # Protocol Header
        self.protocol_header_format: list[str] = ["<Q", "<H", "<H"]
        self.message_type: MessageType = msg_type  # 16 bits/uint16

        self.header = None
        self.payload = {} if payload is None else payload
        self.payload_fields = []  # tuples of ("label", value)
        self._packed_message = None
        self.reserved: int = 0  # 16 bits/uint16, all zero

    @property
    def packed_message(self):
        if self._packed_message is None:
            self._packed_message = self.generate_packed_message()
        return self._packed_message

    @packed_message.setter
    def packed_message(self, value):
        self._packed_message = value

    def generate_packed_message(self):
        self.payload = self.get_payload()
        self.header = self.get_header()
        packed_message = self.header + self.payload
        return packed_message

    # frame (and thus header) needs to be generated after payload (for size field)
    def get_header(self):
        if self.size is None:
            self.size = self.get_msg_size()
        frame_addr = self.get_frame_addr()
        frame = self.get_frame()
        protocol_header = self.get_protocol_header()
        header = frame + frame_addr + protocol_header
        return header

    # Default: No payload unless method overridden
    def get_payload(self):
        return struct.pack("")

    def get_frame(self):
        size_format = self.frame_format[0]
        flags_format = self.frame_format[1]
        source_id_format = self.frame_format[2]
        size = struct.pack(size_format, self.size)
        flags = struct.pack(
            flags_format,
            ((self.origin & 0b11) << 14)
            | ((self.tagged & 0b1) << 13)
            | ((self.addressable & 0b1) << 12)
            | (self.protocol & 0b111111111111),
        )
        source_id = struct.pack(source_id_format, self.source_id)
        frame = size + flags + source_id
        return frame

    def get_frame_addr(self):
        mac_addr_format = self.frame_addr_format[0]
        reserved_48_format = self.frame_addr_format[1]
        response_flags_format = self.frame_addr_format[2]
        seq_num_format = self.frame_addr_format[3]
        mac_addr = struct.pack(mac_addr_format, convert_mac_to_int(self.target_addr))
        reserved_48 = struct.pack(reserved_48_format, *([self.reserved] * 6))
        response_flags = struct.pack(
            response_flags_format,
            ((self.reserved & 0b111111) << 2)
            | ((self.ack_required & 0b1) << 1)
            | (self.res_required & 0b1),
        )
        seq_num = struct.pack(seq_num_format, self.sequence)
        frame_addr = mac_addr + reserved_48 + response_flags + seq_num
        return frame_addr

    def get_protocol_header(self):
        reserved_64_format = self.protocol_header_format[0]
        message_type_format = self.protocol_header_format[1]
        reserved_16_format = self.protocol_header_format[2]
        reserved_64 = struct.pack(reserved_64_format, self.reserved)
        message_type = struct.pack(message_type_format, self.message_type.value)
        reserved_16 = struct.pack(reserved_16_format, self.reserved)
        protocol_header = reserved_64 + message_type + reserved_16
        return protocol_header

    def get_msg_size(self):
        payload_size_bytes = len(self.payload)
        return self.HEADER_SIZE_BYTES + payload_size_bytes

    def __str__(self):
        indent = "  "
        s = self.__class__.__name__ + "\n"
        s += indent + "Size: {}\n".format(self.size)
        s += indent + "Origin: {}\n".format(self.origin)
        s += indent + "Tagged: {}\n".format(self.tagged)
        s += indent + "Protocol: {}\n".format(self.protocol)
        s += indent + "Source ID: {}\n".format(self.source_id)
        s += indent + "Target MAC Address: {}\n".format(self.target_addr)
        s += indent + "Ack Requested: {}\n".format(self.ack_required)
        s += indent + "Response Requested: {}\n".format(self.res_required)
        s += indent + "Seq Num: {}\n".format(self.sequence)
        s += indent + "Message Type: {}\n".format(self.message_type.name)
        s += indent + "Payload:"
        for field in self.payload_fields:
            s += "\n" + indent * 2 + "{}: {}".format(field[0], field[1])
        if len(self.payload_fields) == 0:
            s += "\n" + indent * 2 + "<empty>"
        s += "\n"
        s += indent + "Bytes:\n"
        s += indent * 2 + str(
            [
                hex(b)
                for b in struct.unpack(
                    "B" * (len(self.packed_message)), self.packed_message
                )
            ]
        )
        s += "\n"
        return s


# reverses bytes for little endian, then converts to int
def convert_mac_to_int(addr) -> int:
    reverse_bytes_str = addr.split(":")
    reverse_bytes_str.reverse()
    addr_str = "".join(reverse_bytes_str)
    return int(addr_str, 16)
