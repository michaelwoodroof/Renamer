# Imports
import base64
import os
import re
import sys

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# Methods
def rename():
    # Check if Prefixes.txt exists
    if not os.path.isfile("prefixes.txt"):
        f = open("prefixes.txt", "x")
        f.close()

    if len(sys.argv) == 4 or len(sys.argv) == 5 or len(sys.argv) == 6:
        # Verify arguments
        if os.path.isdir(sys.argv[1]):
            pattern = re.compile('[a-zA-Z]+')
            if pattern.match(sys.argv[2]):
                pattern = re.compile('[\d+|aa|AA]')
                if not(pattern.match(sys.argv[3])):
                    print("Use number for offset or AA for automatic assignment (based on previous prefixes)")
                    sys.exit(0)
            else:
                print("Not valid prefix use only English Characters [a-z]")
                sys.exit(0)
        else:
            print("Directory does not exist")
            sys.exit(0)

        isNewPrefix(sys.argv[2])

        # Arguments verified begin renaming process
        if sys.argv[3] == "aa" or sys.argv[3] == "AA":
            counter = getPrefix(sys.argv[2])
        else:
            counter = sys.argv[3]

        # Ensure Counter is an integer
        counter = int(counter)
        if counter < 0:
            counter = 0

        for filename in os.listdir(sys.argv[1]):

            counter += 1
            fcounter = str(counter)

            if (counter >= 10000):
                formatCounter = fcounter;
            elif (counter >= 1000):
                formatCounter = "0" + fcounter;
            elif (counter > 100):
                formatCounter = "00" + fcounter;
            elif (counter > 10):
                formatCounter = "000" + fcounter;
            else:
                formatCounter = "0000" + fcounter;

            suffix = filename[filename.find("."):]

            nfn = sys.argv[1] + "\\" + sys.argv[2] + formatCounter + suffix
            src = sys.argv[1] + "\\" + filename
            os.rename(src, nfn)

        updatePrefixes(sys.argv[2], str(counter))

        print("All files renamed")

        # Upload to Google Drive
        if len(sys.argv) == 5:
            if sys.argv[4] == "t" or sys.argv[4] == "T":
                uploadToDrive(sys.argv[1])

        # Remove files
        if len(sys.argv) == 6:
            if sys.argv[5] == "t" or sys.argv[5] == "T":
                deleteFiles(sys.argv[1], sys.argv[2])

    else:
        print("Invalid number of arguments : \nUse > Renamer.py <filepath> <prefix> <offset> <upload to drive {T or F}> <delete files after {T or F}> ")

def isNewPrefix(prefix):
    if getPrefix(prefix) == 0:
        f = open("prefixes.txt", "a")
        f.write("\n" + prefix + "," + "0")
        f.close()

def getPrefix(prefix):
    prefixCount = 0
    # Open File and find Prefix Number
    f = open("prefixes.txt", "r")
    fl = f.readlines()
    for l in fl:
        d = l.split(",")
        if d[0] == prefix:
            f.close()
            if int(d[1]) == 0:
                return -1
            else:
                return int(d[1])
    f.close()
    return prefixCount

def updatePrefixes(prefix, counter):
    # Update all Prefixes
    f = open("prefixes.txt", "r")
    list = []
    fl = f.readlines()
    for l in fl:
        d = l.split(",")
        if d[0] == prefix:
            list.append(prefix + "," + counter + "\n")
        elif d[0] != "\n" and d != "\n":
            list.append(l)

    f.close()
    
    # Delete File
    os.remove("prefixes.txt")

    # Create File
    fn = open("prefixes.txt", "w", newline="")
    for i in range(len(list)):
        item = list[i]
        fn.write(item)

    fn.close()

def uploadToDrive(filepath):
    print("Upload started:")
    # Initialise Google Login variables
    gl = GoogleAuth()
    gl.LocalWebserverAuth()
    drive = GoogleDrive(gl)
    # Upload all files
    for file in os.listdir(filepath):
        filedes = filepath + "\\" + file
        fd = drive.CreateFile({'title': file})
        fd.SetContentFile(filedes)
        fd.Upload()
    print("All files uploaded")

def deleteFiles(filepath, prefix):
    for file in os.listdir(filepath):
        if prefix in file:
            # Delete Files
            os.remove(filepath + "\\" + file)
    print("All files deleted")

# Execution of Methods
rename()
