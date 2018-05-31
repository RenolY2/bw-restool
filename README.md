# bw-restool
Resource archive (.res and .res.gz) packer and unpacker for Battalion Wars and Battalion Wars 2. 
Tool was tested and is known to work with Python 3.6.5 

# Usage
Drag & drop a .res file from BW or .res.gz file from BW2 onto restool.bat to extract their contents into a folder.
Drag & drop an extracted folder onto the bat to pack it into a .res or .res.gz file. Folders extracted from BW will be 
packed into .res, folders extracted from BW2 will be packed and compressed into .res.gz.

If you want to write your own command line scripts, the following describes the command line usage:
```python restool.py [-h] input [output]

positional arguments:
  input       Path to folder, .res or .res.gz file.
  output      If input is a folder, write packed data into output file. If
              output ends with .gz, output file will be compressed with
              gzip. If input is a .res or .res.gz file, write extracted data
              into output folder.

optional arguments:
  -h, --help  show this help message and exit```

if output ends with .gz, the output file will be gzip compressed. Otherwise, compression is not used. Putting .gz at the end is 
recommended for Battalion Wars 2.
  
  
# Extracted folder 
Extracted data is broken up into several categories. Animations, Models, Scripts, Sounds, SpecialEffects and Textures.
Models also have the textures they use in their folder.

* Animations end with .anim 
* Models end with .modl
* Scripts end with .luap
* Sounds end with .adp 
* SpecialEffects end with .txt
* Textures end with .texture 

These are not official file endings but endings that I decided to give them based on the contents of the files. 

For packing the extracted folder the folder structure is not important. The entire folder is searched and files are added 
to the final archive when their extension matches one of the above.

BW2 models and textures have a slightly different structure compared to BW so it is possible the game will crash if you put a 
model from BW2 into BW or vice versa.