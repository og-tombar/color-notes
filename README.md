
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
* Implements a weighted average algorithm to determine the overall color based on the notes' pitches and velocities. The mathematical portion of this algorithm can be found to the bottom of this document.
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

$` \begin{array}{l}
1) \ A\ "hue"\ is\ defined\ to\ be\ a\ number\ 0\leq hue\leq 360\in \mathbb{R}\\
\\
2) \ Define\ a\ "note"\ to\ be\ a\ pair\ of\ values\ n=( p,v) \ where\ p,v\ represent\ pitch\ and\ velocity\\
respectively.\ We\ denote\ the\ set\ of\ all\ musical\ notes\ as\ MN,\ hence\ for\ all\ note\ n,\\
n\in MN\\
\\
3) \ Define\ the\ pitch-hue\ map\ to\ be\\
\\
hue( p) =\begin{cases}
0 & if\ p\%12=0 & ( corresponds\ to\ the\ note\ 'C')\\
30 & if\ p\%12=7 & "-"\ 'G')\\
60 & if\ p\%12=2 & "-"\ 'D')\\
90 & if\ p\%12=9 & "-"\ 'A')\\
120 & if\ p\%12=4 & "-"\ 'E')\\
150 & if\ p\%12=11 & "-"\ 'B')\\
180 & if\ p\%12=6 & "-"\ 'F\#')\\
210 & if\ p\%12=1 & "-"\ 'Db')\\
240 & if\ p\%12=8 & "-"\ 'Ab')\\
270 & if\ p\%12=3 & "-"\ 'Eb')\\
300 & if\ p\%12=10 & "-"\ 'Bb')\\
330 & if\ p\%12=5 & "-"\ 'F')
\end{cases}\\
\\
*\ By\ the\ MIDI\ protocol,\ \forall p,v\ we\ have\ 0\leq p,v\leq 127\ and\ p,v\in \mathbb{N}\\
\\
4) \ Define\ a\ "chord"\ C\ to\ be\ a\ sequence\ of\ notes:\ C=( n_{i})_{1}^{k} =( n_{1} ,n_{2} ,\dotsc ,n_{k})\\
such\ that\ \forall n_{i} =( p_{i} ,v_{i}) \ and\ n_{j} =( p_{j} ,v_{j}) \ for\ which\ i< j\ we\ have\ that\ p_{i} < p_{j} ,\ or\ in\\
other\ words,\ the\ pitches\ of\ the\ notes\ in\ the\ sequence\ are\ increasing.\\
\\
5) \ Define\ the\ "X\ inversion"\ of\ a\ given\ chord\ to\ be\ the\ sequence:\\
\\
C^{X} =\left(\overline{n_{x_{1}}} ,\overline{n_{x_{2}}} ,\dotsc \overline{n_{x_{k}}}\right) \ where:\\
\\
\overline{n_{x_{i}}} =\left(\overline{p_{x_{i}}} ,v_{x_{i}}\right) \ and\ \overline{p_{x_{i}}} =\begin{cases}
p_{i} +360 & if\ 1\leq i\leq x\\
p_{i} & else
\end{cases}\\
\\
6) \ Denote\ the\ "0\ inversion"\ of\ a\ chord\ as\ the\ "root\ position",\ and\ define\ it\ to\ be\ equal\\
to\ the\ original\ chord:\ C^{0} =C\\
\\
7) \ Define\ the\ average\ hue\ of\ a\ given\ chord\ inversion\ as\ the\ weighted\ average\ of\ the\\
note\ pitches,\ converted\ to\ hues,\ with\ respect\ to\ the\ note\ velocities:\\
\\
avghue\left( C^{X}\right) =\frac{{\displaystyle \sum\limits _{i=1}^{k}}\left[ v_{x_{i}} \cdot hue\left(\overline{p_{x_{i}}}\right)\right]}{{\displaystyle \sum\limits _{i=1}^{k}} v_{x_{i}}}\\
\\
8) \ Define\ the\ distance\ of\ a\ given\ chord\ inversion\ from\ a\ given\ hue\ to\ be:\\
\\
dist\left( C^{X} ,h\right) =\sum _{i=1}^{k} v_{x_{i}} \cdotp \left| hue\left(\overline{p_{x_{i}}}\right) -h\right| \\
\\
9) \ Define\ the\ average\ hue\ of\ a\ given\ chord\ C\ to\ be\ avghue\left( C^{\overline{X}}\right) \ where\ \overline{X} \ minimizes\\
dist\left( C^{X} ,avghue\left( C^{X}\right)\right) ,\ \forall 1\leq X\leq k,\ hence\\
\\
avghue( C) =avghue\left( C^{\overline{X}}\right) \ where\ \forall 1\leq X\leq k\ we\ have\\
\\
\sum _{i=1}^{k} v_{\overline{x}_{i}} \cdotp \left| hue\left(\overline{p_{\overline{x}_{i}}}\right) -\frac{{\displaystyle \sum\limits _{i=1}^{k}}\left[ v_{\overline{x}_{i}} \cdot hue\left(\overline{p_{\overline{x}_{i}}}\right)\right]}{{\displaystyle \sum\limits _{i=1}^{k}} v_{\overline{x}_{i}}}\right| \leq \sum _{i=1}^{k} v_{x_{i}} \cdotp \left| hue\left(\overline{p_{x_{i}}}\right) -\frac{{\displaystyle \sum\limits _{i=1}^{k}}\left[ v_{x_{i}} \cdot hue\left(\overline{p_{x_{i}}}\right)\right]}{{\displaystyle \sum\limits _{i=1}^{k}} v_{x_{i}}}\right| 
\end{array}`$
