from PIL import Image;

def checkImage(imgPath):
    img = Image.open(imgPath).convert("RGBA")
    if img.size[0] != 384:
        return False # raise ValueError("Width must be 384 pixels")
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            r, g, b, a = img.getpixel((x, y))
            if a != 255 or (r != 0 and r != 255) or (g != 0 and g != 255) or (b != 0 and b != 255):
                return False # raise TypeError("Image must be fully opaque and black and white")
    return True

def calcCrc8(data):
    crcTable = [0x00, 0x07, 0x0e, 0x09, 0x1c, 0x1b, 0x12, 0x15, 0x38, 0x3f, 0x36, 0x31, 0x24, 0x23, 0x2a, 0x2d, 0x70, 0x77, 0x7e, 0x79, 0x6c, 0x6b, 0x62, 0x65, 0x48, 0x4f, 0x46, 0x41, 0x54, 0x53, 0x5a, 0x5d, 0xe0, 0xe7, 0xee, 0xe9, 0xfc, 0xfb, 0xf2, 0xf5, 0xd8, 0xdf, 0xd6, 0xd1, 0xc4, 0xc3, 0xca, 0xcd, 0x90, 0x97, 0x9e, 0x99, 0x8c, 0x8b, 0x82, 0x85, 0xa8, 0xaf, 0xa6, 0xa1, 0xb4, 0xb3, 0xba, 0xbd, 0xc7, 0xc0, 0xc9, 0xce, 0xdb, 0xdc, 0xd5, 0xd2, 0xff, 0xf8, 0xf1, 0xf6, 0xe3, 0xe4, 0xed, 0xea, 0xb7, 0xb0, 0xb9, 0xbe, 0xab, 0xac, 0xa5, 0xa2, 0x8f, 0x88, 0x81, 0x86, 0x93, 0x94, 0x9d, 0x9a, 0x27, 0x20, 0x29, 0x2e, 0x3b, 0x3c, 0x35, 0x32, 0x1f, 0x18, 0x11, 0x16, 0x03, 0x04, 0x0d, 0x0a, 0x57, 0x50, 0x59, 0x5e, 0x4b, 0x4c, 0x45, 0x42, 0x6f, 0x68, 0x61, 0x66, 0x73, 0x74, 0x7d, 0x7a, 0x89, 0x8e, 0x87, 0x80, 0x95, 0x92, 0x9b, 0x9c, 0xb1, 0xb6, 0xbf, 0xb8, 0xad, 0xaa, 0xa3, 0xa4, 0xf9, 0xfe, 0xf7, 0xf0, 0xe5, 0xe2, 0xeb, 0xec, 0xc1, 0xc6, 0xcf, 0xc8, 0xdd, 0xda, 0xd3, 0xd4, 0x69, 0x6e, 0x67, 0x60, 0x75, 0x72, 0x7b, 0x7c, 0x51, 0x56, 0x5f, 0x58, 0x4d, 0x4a, 0x43, 0x44, 0x19, 0x1e, 0x17, 0x10, 0x05, 0x02, 0x0b, 0x0c, 0x21, 0x26, 0x2f, 0x28, 0x3d, 0x3a, 0x33, 0x34, 0x4e, 0x49, 0x40, 0x47, 0x52, 0x55, 0x5c, 0x5b, 0x76, 0x71, 0x78, 0x7f, 0x6a, 0x6d, 0x64, 0x63, 0x3e, 0x39, 0x30, 0x37, 0x22, 0x25, 0x2c, 0x2b, 0x06, 0x01, 0x08, 0x0f, 0x1a, 0x1d, 0x14, 0x13, 0xae, 0xa9, 0xa0, 0xa7, 0xb2, 0xb5, 0xbc, 0xbb, 0x96, 0x91, 0x98, 0x9f, 0x8a, 0x8d, 0x84, 0x83, 0xde, 0xd9, 0xd0, 0xd7, 0xc2, 0xc5, 0xcc, 0xcb, 0xe6, 0xe1, 0xe8, 0xef, 0xfa, 0xfd, 0xf4, 0xf3]
    byte = 0
    for b in data:
        byte = (byte ^ b) & 0xff
        byte = crcTable[byte]
    return byte

def commandBytes(cmd, data):
    dataLen = len(data)
    dataLenLow = dataLen & 0xff
    dataLenHigh = dataLen & 0xff00
    return bytes([0x51, 0x78, cmd, 0x00, dataLenLow, dataLenHigh] + data + [calcCrc8(data), 0xFF])

def getCommandCode(cmdName):
    if cmdName == "BLACKENING" or cmdName == "QUALITY":
        return 0xA4
    elif cmdName == "ENERGY" or cmdName == "ENERAGY":
        return 0xAF
    elif cmdName == "PRINT_TYPE":
        return 0xBE
    elif cmdName == "FEED_PAPER":
        return 0xBD
    elif cmdName == "DRAW_COMPRESSED":
        return 0xBF
    elif cmdName == "DRAW_PACKED":
        return 0xA2
    elif cmdName == "PAPER":
        return 0xA1
    else:
        raise ValueError("Unsupported operation")

def runLength(line):
    encoded = []
    def encodeRun(curr, run):
        while run > 127:
            encoded.append((curr << 7) | 127)
            run -= 127
        if run > 0:
            encoded.append((curr << 7) | run)
    run = 0
    curr = None
    for p in line:
        if p == curr:
            run += 1
        else:
            encodeRun(curr, run)
            curr = p
            run = 1
    encodeRun(curr, run)

    return encoded

def bitPack(line):
    encoded = []
    for p in range(0, len(line), 8):
        byte = 0
        for i in range(8):
            byte <<= 1
            byte |= line[p+7-i]
        encoded.append(byte)
    return encoded

def toArrayLE(num): # to low-endian array
    return [num & 0xff, (num >> 8) & 0xff]

def getEnergy(printDepth):
    if printDepth <= 0 or printDepth > 7:
        raise ValueError("Invalid print depth")
    return int(7500 + (printDepth - 4)*0.15*7500)

def getTypeByte(typeStr):
    if typeStr == "IMAGE":
        return 0x00
    elif typeStr == "TEXT":
        return 0x01
    elif typeStr == "LABEL":
        return 0x03
    else:
        raise ValueError("No such print type")

def getSpeed(typeStr):
    if typeStr == "IMAGE":
        return 30
    elif typeStr == "TEXT":
        return 10
    else:
        raise ValueError("No such print speed type")

def readImage(imgPath):
    if not checkImage(imgPath):
        raise ValueError("Image is not of width 384 and 1bpp")
    img = Image.open(imgPath).convert("1")
    return img

def compressImageToCmds(img):
    commands = []
    for y in range(img.size[1]):
        line = [img.getpixel((i, y))==False for i in range(img.size[0])]
        runs = runLength(line)
        bits = bitPack(line)
        cmd = []
        if len(runs) < len(bits):
            cmd = commandBytes(getCommandCode("DRAW_COMPRESSED"), runs)
        else:
            cmd = commandBytes(getCommandCode("DRAW_PACKED"), bits)
        commands.append(cmd)
    return commands

def saveCommandsToFile(commands, saveToFile=None, saveToFileHuman=None):
    if saveToFile:
        allCmds = b"".join(commands)
        with open(saveToFile, "wb") as f:
            f.write(allCmds)
    if saveToFileHuman:
        humanCmds = [" ".join(hex(b)[2:4].zfill(2).upper() for b in c) for c in commands]
        with open(saveToFileHuman, "w") as f:
            f.write("\n".join(humanCmds))

def genMoveUp(lines=0x60):
    cmds = []
    cmds.append(commandBytes(getCommandCode("FEED_PAPER"), [lines]))
    # The app for some reason splits it up as two commands with 0x30, thus so do I
    while lines > 0x30:
        lines -= 0x30
        cmds.append(commandBytes(getCommandCode("PAPER"), [0x30, 0x00]))
    if lines > 0:
        cmds.append(commandBytes(getCommandCode("PAPER"), [lines, 0x00]))
    cmds.append(commandBytes(getCommandCode("FEED_PAPER"), [lines]))
    return cmds

def genCommands(img, type="IMAGE", energy=None, speed=None, moveUpAfter=True, saveToFile=None, saveToFileHuman=None):
    if energy == None:
        energy = getEnergy(4) if type != "TEXT" else 0 
    if speed == None:
        speed = getSpeed(type if type != "LABEL" else "IMAGE")

    typeByte = getTypeByte(type)

    commands = []
    commands.append(commandBytes(getCommandCode("BLACKENING"), [0x33]))
    if energy > 0: 
        commands.append(commandBytes(getCommandCode("ENERGY"), toArrayLE(energy)))
    commands.append(commandBytes(getCommandCode("PRINT_TYPE"), [typeByte]))
    commands.append(commandBytes(getCommandCode("FEED_PAPER"), [speed]))

    commands.extend(compressImageToCmds(img))

    if moveUpAfter:
        commands.extend(genMoveUp())

    saveCommandsToFile(commands, saveToFile, saveToFileHuman)

    return commands