from PIL import Image, ImageDraw, ImageFont
import re

def textToImage(text, fontSize=12, fontFile="DejaVuSans.ttf", align="left", lineSpacing=2, bold=False, whiteOnBlack=False, saveToFile=None):
    font = ImageFont.truetype(fontFile, fontSize)

    WIDTH = 384
    FILL = 0 if not whiteOnBlack else 1
    BACKGROUND = 1 if not whiteOnBlack else 0

    linesRaw = text.split('\n')
    # wrap lines
    lines = []
    for line in linesRaw:
        while font.getlength(line, mode="1") > WIDTH: # binary search
            spaces = [0] + [m.start() for m in re.finditer(' ', line)]
            left = 0
            right = len(spaces)-1
            while left < right-1:
                mid = (left + right) // 2
                if font.getlength(line[:spaces[mid]], mode="1") > WIDTH:
                    right = mid-1
                else:
                    left = mid
            splitLine = line[:spaces[left]]
            bbox = font.getbbox(splitLine)
            lines.append((splitLine, bbox))
            line = line[spaces[left]+1:]
        if len(line) > 0:
            lines.append((line, font.getbbox(line)))

    # draw image
    x = None
    anchor = None
    match align:
        case "left":
            x = 0
            anchor = "la"
        case "center":
            x = WIDTH//2
            anchor = "ma"
        case "right":
            x = WIDTH
            anchor = "ra"
        case _:
            raise ValueError("Invalid align value")

    img_height = sum(bbox[3]-bbox[1] for (_line, bbox) in lines) + (len(lines)-1)*lineSpacing
    img = Image.new('1', (WIDTH, img_height), BACKGROUND)
    draw = ImageDraw.Draw(img)
    y = 0
    for (line, bbox) in lines:
        draw.text((x, y-bbox[1]), line, font=font, fill=FILL, align=align, anchor=anchor, stroke_width=bold)
        y += bbox[3]-bbox[1] + lineSpacing

    if saveToFile:
        img.save(saveToFile)

    return img