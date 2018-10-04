import pathlib

# define the path
currentDirectory = pathlib.Path('img')

for currentFile in currentDirectory.iterdir():
    print(currentFile)