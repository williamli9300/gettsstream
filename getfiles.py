# getTSstream v0.7 - https://github.com/williamli9300/gettsstream

import wget, ssl, time, os, subprocess, shutil

def merge(sfn):
    print("merging ts files...")
    final_path = "./" + sfn + ".ts"
    ts_dir = "./" + sfn
    with open(final_path, 'wb') as merged:
        for ts_file in os.listdir(ts_dir):
            print("    > " + ts_file)
            filepath = ts_dir + "/" + ts_file
            with open(filepath, 'rb') as mergefile:
                shutil.copyfileobj(mergefile, merged)
    print("----- merging OK. -----")

def generate_list(u, sn, en, fn, wl):
    print("generating url list...")
    time.sleep(0.1)
    l = []
    for i in range(sn, en +1):
        s = u + str(i) + ".ts\n"
        l.append(s)
    sfn = fn.replace(".txt", "")
    sfn = sfn.replace(".ts", "")

    if wl.upper() != "N":
        print("writing url list...")
        time.sleep(0.1)
        folderpath = "./" + sfn
        os.makedirs(folderpath, exist_ok=True)
        path = folderpath + "/" + sfn + ".txt"

        print("list path: " + path)
        time.sleep(0.1)
        with open(path, "w") as f:
            for i in l:
                f.write(i)
    print("----- url list OK. continuing to downloads... -----")
    time.sleep(0.25)
    return l, sfn

def download_files(l, u, sfn):
    dl = input("WARNING: SSL verification disabled. Continue? default=Yes, enter N for no\n")
    if dl.upper == "N":
        return False
    else:
        print("downloading files...")
        time.sleep(0.1)
        path = "./" + sfn
        os.makedirs(path, exist_ok=True)
        ssl._create_default_https_context = ssl._create_unverified_context
        fn_prefix_list = u.split("/")
        fn_prefix = fn_prefix_list[-1]
        for i in range(len(l)):
            try:
                filename = "./" + sfn + "/" + (str(i+1)).rjust(5, "0") + ".ts"
                print("    > writing " + filename + "...")
                wget.download(l[i], out=filename)
            except Exception as e:
                print("##### Error thrown with URL " + (str(i+1)).rjust(5, "0") + ". moving on...")
                i+=1
        print("----- downloads OK. continuing to merging... -----")
        merge(sfn)
        return True

uraw = str(input("please enter any URL (incl. number and '.ts') \n"))
ulist = uraw.split("_")
ulist[-1]=""
u = "_".join(ulist)

sn = int(input("please enter the number of the first *.ts file \n"))
en = int(input("please enter the number of the last *.ts file \n"))
fn = str(input("please enter file name\n"))
wl = str(input("write file list? default=Yes, enter N for no\n"))   

print("----- inputs OK. continuing to url list generation... -----")
time.sleep(0.1)
l, sfn = generate_list(u, sn, en, fn, wl)
dl = download_files(l, u, sfn)

if dl == False:
    input('Operation cancelled. Press <ENTER> to continue\n')
else:
    input('Done. Press <ENTER> to continue')
