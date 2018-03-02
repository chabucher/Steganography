# Stenography
A program that allows you to discreetly hide messages within photos 

Author: Charles Bucher

# Architecture
I followed the project description

# Instructions
Install python3 and ensure you have support for PIL and Numpy
From your terminal, run:

$python3 stenography.py <METHOD> <INPUT_FILE> {<MESSAGE>}

METHOD:
- Required argument.
- HIDE: Will consume an image, embed the message, and output a .png file
- REVEAL: Will analyze the given image for a secret mesage

INPUT_FILE:
- Required argument.
- For REVEAL method, ensure the image is of file type .png

MESSAGE:
- Optional argument.
- Do NOT enter if REVEAL method was chosen
- If not entered with HIDE method, source code will be embedded
- Any input string. .txt files not supported yet.

Valid Examples:

$python3 stenography HIDE InputFile.jpg "This is my secret message."
$python3 stenography HIDE InputFile.jpg
$python3 stenography REVEAL InputFile.jpg
