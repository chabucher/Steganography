# Author: Charles Bucher
# Last Modified: 3/21/18

from PIL import Image
import numpy as np
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


def getMsgLenFromGrid(pixelGrid): # As number of characters

    width = pixelGrid.shape[0]
    height = pixelGrid.shape[1]

    sizeStr = ""
    pixelCtr = 11
    for i in reversed(range(0, width)):
        for j in reversed(range(0, height)):
            if pixelCtr == 0:
                sizeStr = sizeStr[::-1] # Reverse to get correct bit string
                retVal = int(sizeStr, 2)
                # Not divisble by 8 means this picture was not embedded correctly!
                return -1 if retVal % 8 != 0 else int(retVal / 8)

            r, g, b = pixelGrid[i, j]
            # Concatenate in reverse order the LSB of each
            # value (i.e., whether or not it is an odd number)
            sizeStr = "%s%s%s"%(b % 2,g % 2, r % 2) + sizeStr
            if pixelCtr == 1:
                sizeStr = sizeStr[1:] # The "B" value of the last pixel is not used
            pixelCtr -= 1

    return 0


def embedMsgInGrid(msg, pixelGrid, isMsgLen):

    w = pixelGrid.shape[0]
    h = pixelGrid.shape[1]

    # If msg is the message length, start at beginning, otherwise, pixel #11
    startAfter = 0 if isMsgLen else 11
    pixelCtr = 0 # The current pixel

    idx = 0
    for i in reversed(range(0, w)):
        for j in reversed(range(0, h)):

            if pixelCtr < startAfter:
                pixelCtr += 1
                continue
            if idx >= len(msg):
                return
            
            r_lsb = 0
            g_lsb = 0
            b_lsb = 0

            # Get the new LSB for each pixel value. Bounds check each time
            if idx <= len(msg) - 1:
                r_lsb = int(msg[idx])
            if idx <= len(msg) - 2:
                g_lsb = int(msg[idx+1])
            if idx <= len(msg) - 3:
                b_lsb = int(msg[idx+2])
            
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
            idx += 3
            
    return


def retrieveMsgFromGrid(msgSize, pixelGrid):

    width = pixelGrid.shape[0]
    height = pixelGrid.shape[1]

    pixelCtr = 0 # Skips first 11 pixels
    secretMsg = ""
    masterCtr = 0 # Stop when total num of bits for secret msg are reached
    letterCtr = 0 # Counts up to 8 bits
    binStr = ""


    for i in reversed(range(0, width)):
        for j in reversed(range(0, height)):
            if pixelCtr < 11:
                pixelCtr += 1
                continue
            r, g, b = pixelGrid[i, j]

            overflowBinStr = ""
            overflowStart = 0
            if letterCtr <= 5:
                # All three values go to this current letter's binary
                binStr = "%s%s%s"%(b % 2, g % 2, r % 2) + binStr
                letterCtr += 3
            elif letterCtr == 6:
                # G, R goes to current letter
                binStr = "%s%s"%(g % 2, r % 2) + binStr
                letterCtr += 2

                # B goes to next letter
                overflowBinStr = "%s"%(b % 2)
                overflowStart = 1

            elif letterCtr == 7:
                # R goes to current letter
                binStr = "%s"%(r % 2) + binStr
                letterCtr += 1
                
                # B, G goes to next letter
                overflowBinStr = "%s%s"%(b % 2,g % 2)
                overflowStart = 2
            
            masterCtr += 3

            if letterCtr == 8:
                # Reverse the bit string for proper letter
                binStr = binStr[::-1]
                secretMsg = secretMsg + chr(int(binStr, 2))
                
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
        msgLen = format(len(message)*8, "#034b")[2:]
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
        if msgLen == -1:
            print("Message not embedded propely. Cannot read\n")
            return
        secretMessage = retrieveMsgFromGrid(msgLen, pixelGrid)
        print("Secret Message:", secretMessage)

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
