from math import ceil
from PIL import Image
import glob
import os

os.makedirs("dataImg", exist_ok=True)

def getColor(value):
    return (value, value, value)

# Find all files matching data*.txt
for data_file in glob.glob("data/data*.txt"):
    with open(data_file, "r") as f:
        data = f.read().replace('\n', '')

    bytes_array = [int(data[i:i+2], 16) for i in range(0, len(data), 2)]

    runs_array = []
    run = []
    runSum = 0
    for b in bytes_array:
        run.append(b)
        runSum += b
        if b == 255:
            runs_array.append(run)
            run = []
    if len(run) > 0 and runSum > 0:
        runs_array.append(run)

    if not runs_array:
        continue

    HEIGHT = len(runs_array)
    WIDTH = max(len(run) for run in runs_array)

    img = Image.new("RGB", (WIDTH, HEIGHT))
    for i in range(HEIGHT):
        for j in range(WIDTH):
            if j < len(runs_array[i]):
                img.putpixel((j, i), getColor(runs_array[i][j]))
            else:
                img.putpixel((j, i), (255, 0, 255))

    # Generate output filename: image#.png
    base = data_file.split('\\')[-1].split('.')[0]  # Get base name without extension
    output_file = f"dataImg/{base}.png"
    img.save(output_file)