
![Color Notes](https://github.com/og-tombar/color-notes/assets/134632821/127a5705-7094-428a-9b80-617c91071cfd)

# Welcome to Color Notes!

Color Notes is a MIDI-controlled smart lighting system designed to synchronize the color and intensity of smart LED lights with MIDI input from a musical instrument or controller. This system allows musicians, performers, or enthusiasts to create dynamic and immersive lighting effects that respond in real-time to their musical performance. The project incorporates concepts from the fields of MIDI communication, smart home automation, and asynchronous programming to achieve its goals.

## Primary Components
### MIDI Handler
* Responsible for handling MIDI input from external devices such as musical instruments or MIDI controllers.
* Utilizes the __rtmidi__ library to interact with MIDI devices.
* Monitors for different MIDI messages, such as note on/off events and control change messages.
* Input MIDI messages are sent to the __Notes to Hue Converter.__

### Notes to Hue Converter
* Maintains a collection of notes, representing the current notes being played by a musical instrument.
* Converts MIDI note information (pitch, velocity) into corresponding color and intensity values for the smart lights.
* Implements a weighted average algorithm to determine the overall color based on the notes' pitches and velocities. The mathematical portion of this algorithm can be found in this [this link](https://www.mathcha.io/editor/jm9mrcODsYQuDrWK0Df5d8P29i01NmQqUNBNWZV).
* When a note is added or removed from the list of currently played notes, the current color is updated.


### LIFX Device Set
* Responsible for discovery of __LIFX Devices__ over LAN and controlling them.
* Monitors __Notes to Hue Converter__ for changes in hue. Uses __Message Maker__ to create control messages such as turn on / off or color change, which are passed down to all __LIFX Devices__ in the set.

### LIFX Device
* Responsible for communications with a single LIFX physical device, represented by a unique IP address.
* Uses the globally accessible __Message Router__ to encode UDP packets and send them to the corresponding physical device.

### Message Maker
* Establishes a high-level API for generating control messages, such as turn on / off and color change messages.

### Message Encoder & Message Decoder
* Handle encoding and decoding of UDP packets utilizing __aiolifx__ to facilitate communication with smart LED lights.
* Defines message structures and encodings for various actions supported by the smart lighting system.
* Translates high-level messages into low-level binary packets required for communication with the lights.
* Translates UDP responses sent by physical devices back to high-level messages.

### MessageRouter
* Manages the communication between the system and smart lights, sending messages and awaiting responses.
* Implements device discovery functionality to identify and collect information about available smart lights on the network.

## Procedure
### Initialization
* Globally accessible __Message Router__ and __Notes to Hue Converter__ are initialized.
* __MIDI Handler__ and __LIFX Device Set__ are initialized. 
* __LIFX Device Set__ uses __Message Router__ to invoke a device discovery message. __LIFX Devices__ discovered this way are appended to the set.
* __Message Router__ starts listening to UDP packets from physical devices.
* __MIDI Handler__ starts receiving MIDI from connected musical instruments.
* __LIFX Device Set__ starts listening to the converter for changes in color parameters.

### Communications Loop
* Input MIDI messages received by __MIDI Handler__ are sent to the converter for processing.
* __Notes to Hue Converter__ dynamically adjusts the color and intensity of the smart lights based on the notes that are currently being played.
* When the converter returns new color parameters, __LIFX Device Set__ invokes a color change message.
* This message is encoded to a UDP packet with __Message Encoder,__, passed down to all __LIFX Devices__ in the set, and then sent to each corresponding physical device with __Message Router.__
* After a physical device receives a message, it sends back a response UDP packet.
* __Message Router__ listens to the incoming packets, transforms them to high-level messages, and sends them back to the corresponding __LIFX Devices.__
* After every physical device on the network returned a response, the loop continues to the next iteration.
