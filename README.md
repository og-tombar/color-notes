
![Color Notes](https://github.com/og-tombar/color-notes/assets/134632821/127a5705-7094-428a-9b80-617c91071cfd)

# Welcome to Color Notes!

The project is a MIDI-controlled smart lighting system designed to synchronize the color and intensity of smart LED lights with MIDI input from a musical instrument or controller. This system allows musicians, performers, or enthusiasts to create dynamic and immersive lighting effects that respond in real-time to their musical performance. The project incorporates concepts from the fields of MIDI communication, smart home automation, and asynchronous programming to achieve its goals.

## Primary Components:
### MIDI Handler:
* Responsible for handling MIDI input from external devices such as musical instruments or MIDI controllers.
* Utilizes the rtmidi library to interact with MIDI devices.
* Monitors for different MIDI messages, such as note on/off events, control change messages, and mode changes.
* Input MIDI messages are sent to the Notes to Hue Converter.

### Notes to Hue Converter:
* Maintains a collection of notes, representing the current notes being played by a musical instrument.
* Converts MIDI note information (pitch, velocity) into corresponding color and intensity values for the smart lights.
* Implements a weighted average algorithm to determine the overall color based on the notes' pitches and velocities.
* When a note is added or removed from the list of currently played notes, the current color is updated.


### LIFX Device Set:
* Responsible for discovery of LIFX devices over LAN and controlling them.
* Monitors Notes to Hue converter for changes in hue. Uses Message Maker to create control messages such as turn on / off or color change, which are passed down to all LIFX Devices in the set.

### LIFX Device:
* Responsible for communications with a single LIFX device, represented by a unique IP address.
* Uses the globally accessible Message Router to send encode UDP messages and send them to the corresponding physical device.

### Message Maker:
* Establishes a high-level API for generating control messages, such as turn on / off and color change messages.

### Message Encoder & Message Decoder:
* Handles the encoding and decoding of messages utilizing aiolifx to facilitate communication with smart LED lights.
* Defines message structures and encodings for various actions supported by the smart lighting system.
* Translates high-level control messages into the low-level binary messages required for communication with the lights.
* Translates UDP responses sent by physical devices back to high-level messages.

### MessageRouter:
* Manages the communication between the system and smart lights, sending messages and awaiting responses.
* Implements device discovery functionality to identify and collect information about available smart lights on the network.
* Uses Message Encoder and Message Decoder to transform high-level messages to binary packets and vice versa.

## Procedure:
### Initialization:
* Globally accessible Message Router and Notes to Hue Converter are initialized.
* MIDI Handler and LIFX Device Set are initialized. 
* LIFX Device Set uses the router to invoke a device discovery message. Devices discovered this way are appended to the set.
* Message Router starts listening to UDP messages from physical devices.
* MIDI Handler starts receiving MIDI from connected musical instruments.
* LIFX Device Set starts listening to the converter for changes in color parameters.

### Communications Loop:
* Input MIDI messages received by the MIDI Handler are sent to the converter for processing.
* Notes to Hue Converter dynamically adjusts the color and intensity of the smart lights based on the notes that are currently being played.
* When the converter returns new color parameters, LIFX Device Set invokes a color change message. The message is encoded to a UDP packet with Message Encoder, and sent to the physical device with Message Router.
* After a physical device receives a message, it sends back a response UDP packet.
* Message Router listens to the incoming packets, transforms them to high-level messages, and sends them back to LIFX Device Set.
* When all devices on the network returned a response, the loop continues to the next iteration.

