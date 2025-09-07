import os
from PIL import Image
import sys
import glob

os.makedirs("decodedImg", exist_ok=True)

for in_file in glob.glob("data/data*.txt"):
    cmds = []
    with open(in_file, "r") as file:
        data = file.read().split('\n')
        data = [d.strip() for d in data if len(d)>0]
        binary = []
        for d in data:
            binary.extend(bytes.fromhex(d)) 

        idx = -1
        data = []
        cmdCode = 0x00
        dataLen = 0
        crc = 0x00
        for i, b in enumerate(binary):
            idx += 1
            #print(i, idx, hex(b))
            if b == 0x51 and idx == 0:
                pass
            elif b == 0x78 and idx == 1:
                pass
            elif idx == 2:
                cmdCode = b
            elif b == 0x00 and idx == 3:
                pass
            elif idx == 4:
                dataLen = b
            elif idx == 5:
                if b != 0:
                    dataLen = dataLen*0x100 + b
            elif idx >= 6 and idx < 6+dataLen:
                data.append(b)
            elif idx == 6+dataLen:
                crc = b
            elif idx == 6+dataLen+1 and b == 0xFF:
                o = {
                    "cmd": cmdCode,
                    "data": data,
                    "crc": crc
                }
                cmds.append(o)
                idx = -1
                crc = 0
                data = []
                cmdCode = 0
            else:
                idx = -1
                crc = 0
                data = []
                cmdCode = 0
        #print(cmds)
        #for c in cmds:
        #    print(hex(c["cmd"]), hex(len(c["data"])), hex(c["crc"]))

    rows = []
    for c in cmds:
        if c["cmd"] == 0xa2:
            s = "".join([bin(b)[2:10].zfill(8)[::-1] for b in c["data"]]) 
            row = [int(x)==1 for x in s]
            rows.append(row)
        elif c["cmd"] == 0xbf:
            row = []
            for b in c["data"]:
                bit = (b & (1<<7)) == 128
                times = b & ~(1<<7)
                row.extend([bit] * times)
            rows.append(row)

    HEIGHT = len(rows)
    WIDTH = max(len(r) for r in rows)

    img = Image.new("1", (WIDTH, HEIGHT))
    for y in range(HEIGHT):
        for x in range(WIDTH):
            img.putpixel((x,y), not rows[y][x])

    base = in_file.split('\\')[-1].split('.')[0]  # Get base name without extension
    output_file = f"decodedImg/{base}.png"
    img.save(output_file)
