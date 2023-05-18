url = str(input("please enter the URL prefix (before number and '.ts') \n"))
startnum = int(input("please enter the first video number \n"))
endnum = int(input("please enter the last video number \n"))
filename = str(input("please enter file name\n"))

l = []
for i in range(startnum, endnum +1):
    s = url + str(i) + ".ts\n"
    l.append(s)

strippedfn = filename.replace(".txt", "")
path = "./" + strippedfn + ".txt"
print("list path: " + path)
with open(path, "w") as f:
    for i in l:
        f.write(i)

input('Done. Press <ENTER> to continue')
