from math import ceil
import os
from PIL import Image
import glob

WIDTH = 256
OFFSET = 9

os.makedirs("dataImg", exist_ok=True)

for data_file in glob.glob("data/data*.txt"):
    with open(data_file, "r") as f:
        data = f.read().replace('\n', '')

    bytes_array = [int(data[i:i+2], 16) for i in range(0, len(data), 2)]

    HEIGHT = 1 + ceil((len(bytes_array)-OFFSET)/WIDTH)
    IMG_WIDTH = max(WIDTH, OFFSET)

    def getColor(value):
        return (value, value, value)


    img = Image.new("RGB", (IMG_WIDTH, HEIGHT))
    for i in range(0, IMG_WIDTH):
        if i < OFFSET:
            img.putpixel((i, 0), getColor(bytes_array[i]))
        else:
            img.putpixel((i, 0), (255, 0, 255))
    for i in range(1, HEIGHT):
        for j in range(0, IMG_WIDTH):
            if j >= WIDTH:
                img.putpixel((j, i), (255, 0, 255))
                continue

            idx = OFFSET + (i - 1) * WIDTH + j
            if idx < len(bytes_array):
                img.putpixel((j, i), getColor(bytes_array[idx]))
            else:
                img.putpixel((j, i), (255, 0, 255))
    base = data_file.split('\\')[-1].split('.')[0]  # Get base name without extension
    output_file = f"dataImg/{base}.png"
    img.save(output_file)