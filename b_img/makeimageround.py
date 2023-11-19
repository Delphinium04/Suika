# Import libraries
import numpy as np
from PIL import Image, ImageDraw
# create the rounded image


def imgRoundFunc(imgName):
    img = Image.open(f'img\{imgName}.png').convert("RGB")  # convert to RGB
    arrImg = np.array(img)  # convert to numpy array
    alph = Image.new('L', img.size, 0)  # create a new image with alpha channel
    draw = ImageDraw.Draw(alph)  # create a draw object
    draw.pieslice([0, 0, img.size[0], img.size[1]],
                  0, 360, fill=255)  # create a circle
    arAlpha = np.array(alph)  # conver to numpy array
    arrImg = np.dstack((arrImg, arAlpha))  # add alpha channel to the image
    # save the resultant image
    Image.fromarray(arrImg).save(f'{imgName}.png')


# driver
if __name__ == "__main__":
    imgName = "O"
    imgRoundFunc(imgName)
