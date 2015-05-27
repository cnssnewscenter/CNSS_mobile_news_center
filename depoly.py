import os
import re

print("Clean the env")
os.system("git branch -D depoly")
print("Check out new branch")
os.system("git checkout -b depoly")
# print("Install the necessary dependency for gulp")
# os.system("")
print("Compile the js and css file")
os.system("gulp")

if "DEBUG" in open("config.py").read():
    f = open("config.py", 'r').read()
    f = re.sub(r"^DEBUG.*", "DEBUG = False", f, flags=re.MULTILINE)
    with open("config.py", 'w') as fp:
        fp.write(f)
else:
    with open("config.py", 'w+a') as fp:
        fp.write("\nDEBUG = False")
print("Update the config")
