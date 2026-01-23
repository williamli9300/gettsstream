# getTSstream v0.8.0 - https://github.com/williamli9300/gettsstream

import wget, ssl, time, os, shutil, subprocess, sys

def merge(sfn):
    print("merging ts files...")
    ts_path = "./" + sfn + ".ts"
    ts_dir = "./" + sfn
    with open(ts_path, 'wb') as merged:
        for ts_file in os.listdir(ts_dir):
            print("> " + ts_file)
            filepath = ts_dir + "/" + ts_file
            with open(filepath, 'rb') as mergefile:
                shutil.copyfileobj(mergefile, merged)
    print("\n----- merging OK. generating mp4. -----")
    cmd = "ffmpeg -i \"" + ts_path + "\" -c:v libx265 -crf 28 -preset fast -bsf:a aac_adtstoasc \"" + sfn + ".mp4\""
    # if hevc_nvenc available: "ffmpeg -i \"" + ts_path + "\" -c:v hevc_nvenc -cq:v 28 -preset fast -bsf:a aac_adtstoasc \"" + sfn + ".mp4\""
    subprocess.run(cmd)
    print("\n----- mp4 created successfully. deleting temp files. -----")
    shutil.rmtree(ts_dir)
    os.remove(ts_path)
    print("\n----- done. -----")

def generate_list(u, en, fn):
    print("generating url list...")
    l = []
    for i in range(0, en +1):
        s = u + str(i) + ".ts\n"
        l.append(s)
    sfn = fn.replace(".txt", "")
    sfn = sfn.replace(".ts", "")
    print("\n----- url list OK. continuing to downloads... -----")
    return l, sfn

def download_files(l, u, sfn):
    print("downloading files...")
    time.sleep(0.1)
    path = "./" + sfn
    os.makedirs(path, exist_ok=True)
    ssl._create_default_https_context = ssl._create_unverified_context
    fn_prefix_list = u.split("/")
    fn_prefix = fn_prefix_list[-1]
    first_error = True
    for i in range(len(l)):
        try:
            filename = "./" + sfn + "/" + (str(i+1)).rjust(5, "0") + ".ts"
            wget.download(l[i], out=filename)
        except Exception as e:
            if first_error == True: 
                print("\n")
                first_error = False
            print("#### Error thrown with URL " + (str(i+1)).rjust(5, "0") + ". moving on...")
            i+=1
    print("----- downloads OK. continuing to merging... -----")
    merge(sfn)
    return True

if len(sys.argv) != 4:
    print("! ERROR: Please enter THREE arguments.\nUsage: python getfiles \"[url]\" [filenum] \"[name]\"")
else:
    uraw = str(sys.argv[1])
    ulist = uraw.split("_")
    ulist[-1]=""
    u = "_".join(ulist)
    en = int(sys.argv[2])
    fn = str(sys.argv[3])
    print("\n----- inputs OK. continuing to url list generation... -----")
    time.sleep(0.1)
    l, sfn = generate_list(u, en, fn)
    dl = download_files(l, u, sfn)
    
    if dl == True:
        input('Press <ENTER> to continue')
