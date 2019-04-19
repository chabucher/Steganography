# Steganography
A program that allows you to discreetly hide messages within photos 

Author: Charles Bucher<br>
Last Modified: 3/21/2018

# Architecture
Every pixel has three 8-bit RBG values. By mainpulating the least significant bit of those values in a uniform way, we can hide any desired message (dependent on the size of the photo), without making any visible change to the photo.

Format: Every pixel will be read from, and written to, from the bottom right of the image by R-value, then G-value, then B-value. <br>
The first 11 pixels (3x11 = 33 bits, ignore the 11th pixel's B-value for an even 32-bits) stores the length of the secret message in bits. Example: If my message has 15 characters, 15 * 8 (bits per character) = 120 bits. 120 in binary is: 0111 1000.<br>
See it visualized below (with Pxl 1 being the bottommost-right pixel of the image):

Pxl 11 | Pxl 10 | Pxl 9 | Pxl 8 | Pxl 7 | Pxl 6 | Pxl 5 | Pxl 4 | Pxl 3 | Pxl 2 | Pxl 1 |
--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | 
RGB | RGB | RGB | RGB | RGB | RGB | RGB | RGB | RGB | RGB | RGB | 
X00 | 001 | 111 | 000 | 000 | 000 | 000 | 000 | 000 | 000 | 000 |

Now, starting at the 12th pixel, we will store the rest of the text, using the 8-bit representation of each character using ASCII convention (https://www.asciitable.com).

# Instructions
Install python3 and ensure system support for the PIL and Numpy libraries.

From your terminal, run: <br>
$python3 steganography.py \<METHOD> \<INPUT_FILE> \<MESSAGE>

METHOD: *(Required)*
- HIDE: Will consume an image, embed the message, and output a .png file
- REVEAL: Will analyze the given image for a secret mesage<br>

INPUT_FILE: *(Required)*
- For REVEAL method, ensure the image is of file type .png<br>

MESSAGE: *(Optional)*
- Do NOT enter if REVEAL method was chosen
- If not entered with HIDE method, source code will be embedded
- Any input string. .txt files not supported yet.<br>

**Valid Examples:**

$python3 steganography HIDE InputFile.jpg "This is my secret message."<br>
$python3 steganography HIDE InputFile.jpg<br>
$python3 steganography REVEAL InputFile.png<br>
