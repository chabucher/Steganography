# Stenography
A program that allows you to discreetly hide messages within photos 

Author: Charles Bucher

# Architecture
I followed the project description

# Instructions
Install python3 and ensure system support for the PIL and Numpy libraries.

From your terminal, run: <br>
$python3 stenography.py <METHOD> \<INPUT_FILE> \<MESSAGE>

METHOD:<br>
&nbsp;&nbsp;&nbsp;*Required argument.
- HIDE: Will consume an image, embed the message, and output a .png file
- REVEAL: Will analyze the given image for a secret mesage<br>

INPUT_FILE:<br>
&nbsp;&nbsp;&nbsp;*Required argument.
- For REVEAL method, ensure the image is of file type .png<br>

MESSAGE: <br>
&nbsp;&nbsp;&nbsp;*Optional argument.
- Do NOT enter if REVEAL method was chosen
- If not entered with HIDE method, source code will be embedded
- Any input string. .txt files not supported yet.<br>

**Valid Examples:**

$python3 stenography HIDE InputFile.jpg "This is my secret message."<br>
$python3 stenography HIDE InputFile.jpg<br>
$python3 stenography REVEAL InputFile.png<br>
