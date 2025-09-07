# thermal-printer
A project to reverse engineer the protocol of my thermal printer - Vyzio B15
(X6) and [implement it myself](#Usage), so I can print from my laptop.

This project was inspired by
[WerWolv's Cat printer blogpost](https://werwolv.net/blog/cat_printer), but I
avoided looking at their code and peaking at the blogpost as much as i could.

In the end I made small python library, located in [/src](/src). You can see its
documentation [here](#usage).

## Article
You can read about my process of reverse engineering the protocol
[here](ARTICLE.md).

## Protocol
### Command structure
Consists of commands. Each command has the following structure:  
`0x51` - Magic value  
`0x78` - Magic value  
`0x..` - Command byte  
`0x00` or `0x01` - Direction (0 for Phone->Printer, 1 for reverse)  
`0x..` - Data length, low byte  
`0x00` - Data length, high byte (always zero)  
`data` * N - Data
`crc8` - crc8 of only the data  
`0xFF` - End magic  

### Printing an image
And the app sends the following commands to print an image (refer to the
[commands](#getcommandcodecmdname)):
1. Blackening (quality) - always 51 (3) for my printer. It is from 1 to 5 (49 to
53).
2. Energy - only if the print type isn't TEXT: corresponds to the _Print depth_
set in the app, with the formula `energy = 7500 + (PD - 4)*0.15*7500`. The Print
depth is from 1 to 7.
3. PrintType - Image(`0x00`), Text(`0x01`) of Label(`0x03`). Still can't find
the differences between them, but I think that Image allows for darker images,
but I'm not sure.
4. FeedPaper(speed) - I don't know what it does, but the speed is 10 for text
and 30 for images and labels.
5. Drawing - commands with either run-length encoded or bit-packed lines
6. FeedPaper(25), Paper(0x30), Paper(0x30), FeedPaper(25)
I don't know what the FeedPaper calls do, but the Paper command feeds the paper
so the printed image emerges.

## Usage
In the `./src` directory you can find python files with functions to use the
protocol and example usage in `./src/main.py`.

### commands.py
Here you can find functions to create the bytes to command the printer.

#### checkImage(imgPath)
Checks if the image at this path is usable for the printer (384 px wide and
1bpp)

#### calcCrc8(data)
Calculates the crc8 checksum

#### commandBytes(cmd, data)
Generates the byte array for a command

#### getCommandCode(cmdName)
Returns the byte corresponding to the command. Accepts:
| Name(s) | Description | Byte |
| - | - | - |
| BLACKENING _(QUALITY)_ | Sets the quality level for the printer. I recommend keeping at default value 51. | `0xA4` |
| ENER(A)GY | Sets the energy (print depth) - the strength of heating of the black pixels. Use the `getEnergy()` function. Default value is 7500 for my model. | `0xAF` |
| PRINT_TYPE | Sets the print type. | `0xBE` |
| FEED_PAPER | Idk what, **DOES NOT** feed the paper. | `0xBD` |
| DRAW_COMPRESSED | Draws a row of pixels, encoded with run-length encoding. The highest bit of each byte is the value and the other 7 encode the run length. | `0xBF` |
| DRAW_PACKED | Draws a row of pixels where each pixel corresponds to one bit in the command's data. | `0xA2` |
| PAPER | Actually feeds the paper. Takes number of lines to move, with data size 2 (potentially 16 bite, little endian). | `0xA1` |

#### runLenght(line)
Creates a byte array with the line compresses as explained above (see
DRAW_COMPRESSED).

#### bitPack(line)
Creates a byte array with each pixel corresponding to a bit.

#### toArrayLE(num)
Converts 16-bit number to little-endian

#### getEnergy(printDepth)
Calculates the energy corresponding to a certain value of "Print depth" in the
app

#### getTypeByte(typeStr)
Returns byte code for the print type. Supports
| Type | Byte |
| - | - |
| IMAGE | `0x00` |
| TEXT | `0x01` |
| LABEL | `0x03` |

#### getSpeed(typeStr)
Returns the app's default "printSpeed" for types. Supports "IMAGE" (30) and
"TEXT" (10). This is used with FEED_PAPER, idk how.

#### readImage(imgPath)
Reads image from the path specified.

#### compressImageToCmds(img)
For each line applies both run-length encoding and bit packing and chooses the
shorter. Packages each line's compressed data into the appropriate command.

#### saveCommandsToFile(commands, saveToFile=None, saveToFileHuman=None)
Saves a list of commands to a binary file and/or a human-readable hex file.

#### genMoveUp(lines=0x60)
Generates the paper feeding commands at the end of the app's routine for
printing an image.

#### genCommands( img, ... _(see source code)_ )
Generates the commands for printing an image with the specified parameters.

### connection.py and class Connection
#### async connect()
Connects to the device and awaits OKAY status.

#### async disconnect()
Disconnects from the device.

#### \_\_init\_\_(macAddress)
Sets up the Connection for the .connect method.

#### send(commands, delay=0)
Writes each command individually to the appropriate characteristic, waiting
_delay_ seconds between each one. In the end asks device for status and awaits
OKAY.

#### Context managers
The Connection class supports the context manager protocol. It automatically
connects and disconnects to the device.
```python
async with Connection("AA:BB:CC:DD:EE:FF") as conn:
    ...
```

#### FakeConnection
This class mirrors the methods of Connection, but its constructor takes paths to
log files, where the sent data gets dumped.

### decode.py
#### readHumanFile(fileName)
Reads a human-readable file of hex values into an array of bytes.

#### readFile(fileName)
Reads a binary file into an array of bytes.

#### decodeCommands(cmdBytes, saveFilename=None)
Decodes the bytes given into the image they convey and returns it. If
_saveFilename_ is set, then it saves the image there.

### textToImage.py
#### textToImage(text, ... _(see source code)_ )
Generates a PIL image from the given text.