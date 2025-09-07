from math import ceil
import random
from PIL import Image
import zipfile
import os

def getColor(value):
    return (value, value, value)

WIDTH = 384

def makeTestImage(testGen, name):
    rows = testGen()
    HEIGHT = len(rows)
    print("Test image " + name + " is " + str(WIDTH) + "x" + str(HEIGHT))
    img = Image.new("RGB", (WIDTH, HEIGHT))
    for i in range(HEIGHT):
        for j in range(WIDTH):
            img.putpixel((j, i), getColor(rows[i][j]))
    img.save("testImages/" + name + ".png")

def genTest1():
    rows = []
    i = 0
    while 2**i <= WIDTH:
        row = [255]
        power = 2**i
        for j in range(1, WIDTH):
            color = row[j-1]
            if j % power == 0:
                color = 255-color
            row.append(color)
        rows.append(row)
        i += 1
    return rows

def genTest2():
    rows = []
    i = 0
    while 2**i <= WIDTH:
        row = []
        power = 2**i
        for j in range(0, WIDTH):
            color = (j % power) * (255 // max(power-1, 1))
            row.append(color)
        rows.append(row)
        i += 1
    return rows

def genTest3():
    rows = []
    for _ in range(9):
        row = []
        for j in range(WIDTH):
            color = (j%2) * 255
            row.append(color)
        rows.append(row)
    return rows

def genTest4():
    blackRow = [0 for _ in range(WIDTH)]
    whiteRow = [255 for _ in range(WIDTH)]

    rows = []
    for i in range(9):
        rows.append(blackRow if i % 2 == 0 else whiteRow)
    return rows

def genTest5():
    blackRow = [0 for _ in range(WIDTH)]
    whiteRow = [255 for _ in range(WIDTH)]

    rows = []
    for i in range(9):
        rows.append(whiteRow if i % 2 == 0 else blackRow)
    return rows

def genTest6():
    rows = []
    for _ in range(9):
        row = []
        for _ in range(WIDTH):
            color = random.randint(0, 255)
            row.append(color)
        rows.append(row)
    return rows

tests = [
    (genTest1, "test1"),
    (genTest2, "test2"),
    (genTest3, "test3"),
    (genTest4, "test4"),
    (genTest5, "test5"),
    (genTest6, "test6")
]

os.makedirs("testImages", exist_ok=True)

for testGen, name in tests:
    makeTestImage(testGen, name)

with zipfile.ZipFile("testImages/test_images.zip", "w") as zf:
    for _, name in tests:
        zf.write("testImages/" + name + ".png")