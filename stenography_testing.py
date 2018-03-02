from PIL import Image
from PIL import ImageOps
import numpy as np
import scipy.misc as smp
from scipy import ndimage
import sys
import os.path

inputImage = None
message = ""
method = ""
paramErrorMsg = \
"""
\   Example A: HIDE InputFile.jpg \"This is my secret message.\"
\   Example B: HIDE InputFile.jpg - (No third parameter means hide the source code)
\   Example C: REVEAL InputFile.jpg\n
"""

def pictureIsLargeEnough(msg, w, h):

    msgSize = len(msg) * 8 # Number of bits needed
    picSize = (w * h - 11) * 3 # Number of pixels available to manipulate
    return msgSize <= picSize


def msgToBinary(msg):

    binMsg = ""
    for letter in msg:
        binMsg += format(ord(letter), '#010b')[2:]

    return binMsg


def binaryToMsg(binary):

    msg = ""
    i = 0
    while i < len(binary):
        letterBin = ""
        for j in range(0, 8):
            letterBin += binary[i+j]
        msg += chr(int(letterBin, 2))
        i += 8
    return msg


def getMsgLenFromGrid(pixelGrid):

    w = pixelGrid.shape[0]
    h = pixelGrid.shape[1]

    sizeStr = ""
    stop = 33
    for i in reversed(range(0, w)):
        for j in reversed(range(0, h)):
            if stop == 0:
                return int(sizeStr, 2)
            r, g, b = pixelGrid[i, j]
            print("Index (",i,j, "). RGB =", r % 2, g % 2, b % 2)
            # Concatenate in reverse order the LSB of each
            # value (i.e., whether or not it is an odd number)
            sizeStr = "%s%s%s"%(r % 2,g % 2,b % 2) + sizeStr
            stop -= 3

    return 0


def embedMsgInGrid(msg, pixelGrid, isMsgLen):

    w = pixelGrid.shape[0]
    h = pixelGrid.shape[1]

    # If msg is the message length, start at beginning, otherwise, pixel #11
    startAfter = 0 if isMsgLen else 11
    pixelCtr = 0 # The current pixel

    idx = len(msg) - 1 # Read from right to left
    for i in reversed(range(0, w)):
        for j in reversed(range(0, h)):

            if pixelCtr < startAfter:
                pixelCtr += 1
                continue
            if idx < 0:
                return

            # Get the new LSB for each pixel value
            b_lsb = int(msg[idx])
            g_lsb = int(msg[idx-1])
            r_lsb = int(msg[idx-2])
            r, g, b = pixelGrid[i, j]
            # Change the LSB of the grid if it doesn't
            # match the new LSB
            if r_lsb != (r % 2):
                r = r - (1 if r % 2 == 1 else -1)
            if g_lsb != (g % 2):
                g = g - (1 if g % 2 == 1 else -1)
            if b_lsb != (b % 2):
                b = b - (1 if b % 2 == 1 else -1)
            
            # Update the grid with the new values
            pixelGrid[i, j] = [r, g, b]
            idx -= 3
            
    return


def retrieveMsgFromGrid(msgSize, pixelGrid):

    w = pixelGrid.shape[0]
    h = pixelGrid.shape[1]

    pixelCtr = 0
    secretMsg = ""
    masterCtr = 0
    letterCtr = 0
    binStr = ""


    for i in reversed(range(0, w)):
        for j in reversed(range(0, h)):
            if pixelCtr < 11:
                pixelCtr += 1
                continue
            r, g, b = pixelGrid[i, j]

            overflowBinStr = ""
            overflowStart = 0
            if letterCtr <= 5:
                # All three values go to this current letter's binary
                binStr = "%s%s%s"%(r % 2,g % 2,b % 2) + binStr
                letterCtr += 3
            elif letterCtr == 6:
                # G, B goes to current letter
                binStr = "%s%s"%(g % 2,b % 2) + binStr
                letterCtr += 2

                # R goes to next letter
                overflowBinStr = "%s"%(r % 2)
                overflowStart = 1

            elif letterCtr == 7:
                # B goes to current letter
                binStr = "%s"%(b % 2) + binStr
                letterCtr += 1
                
                # G, R goes to next letter
                overflowBinStr = "%s%s"%(r % 2,g % 2)
                overflowStart = 2
            
            masterCtr += 3

            if letterCtr == 8:
                # Add the letter to the message!
                secretMsg = chr(int(binStr, 2)) + secretMsg
                # Handle any overflow.
                if masterCtr >= (msgSize * 8):
                    return secretMsg
                else:
                    binStr = overflowBinStr
                    letterCtr = overflowStart
            
    return secretMsg


def main():

    # 1. Open the image and get it's dimensions
    extension = os.path.splitext(inputImage)[1]
    photo = Image.open(inputImage)
    photo = photo.convert("RGB")
    width = photo.size[0]
    height = photo.size[1]

    # 2. Exit gracefully if the photo isn't large enough
    if not pictureIsLargeEnough(message, width, height):
        print("Photo is not large enough to contain the message!")
        return
    
    # 3. Retrieve the pixel grid from the input image
    pixelGrid = np.array(photo)

    # 4. Read or hide the message in the picture
    if method == "HIDE":
        print("Hiding message...")
        # 5. Embed message length
        msgLen = format(len(message), "#035b")[2:]
        embedMsgInGrid(msgLen, pixelGrid, isMsgLen=True)
        
        # 6. Embed secret message
        embedMsgInGrid(msgToBinary(message), pixelGrid, isMsgLen=False)

        # 7. Output the encoded image
        newImage = Image.fromarray(pixelGrid)

        # 8. Consume the original file
        os.remove(inputImage)
        
        # 9. Output the new image as a png file.
        newImage.save(os.path.splitext(inputImage)[0] + ".png")
    else:
        # 5. Retrieve message!
        print("Retrieving message...")

        msgLen = getMsgLenFromGrid(pixelGrid)
        print(msgLen)
        #ecretMessage = retrieveMsgFromGrid(msgLen, pixelGrid)
        #print("Secret Message:", secretMessage)

    print()


if __name__ == "__main__":
    print()

    if len(sys.argv) == 3 or len(sys.argv) == 4:
        method = sys.argv[1]
        inputImage = sys.argv[2]

        if method != "HIDE" and method != "REVEAL":
            print("Please choose HIDE or REVEAL")
            print(paramErrorMsg)
        else:
            if method == "HIDE" and len(sys.argv) == 4:
                message = sys.argv[3]
            else:
                # No secret message means we want to hide the source code itself
                message = open(sys.argv[0], 'r').read()
            main()
    else:         
        print("Incorrect number of parameters.")
        print(paramErrorMsg)
