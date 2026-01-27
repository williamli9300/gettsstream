# getTSstream v1.0.0 - https://github.com/williamli9300/gettsstream

import os, pathlib, shutil, ssl, subprocess, sys, time, wget

def check_dir(path, _type="directory"):
    if os.path.exists(path):
        if str(input(f"## WARNING: {path} already exists. Permanently delete this {_type} before moving on? [y/N] ")).lower() == "y":
            if _type == "directory": shutil.rmtree(path)
            elif _type == "file": os.remove(path)
        else:
            path = path + "_1"
            path = check_dir(path)
    return path

def check_nvenc(file):
    r = subprocess.run("ffmpeg -hide_banner -encoders", text=True, capture_output=True)
    if not "hevc_nvenc" in r.stdout:
        print("## WARNING: ffmpeg encoder \"hevc_nvenc\" not available in your ffmpeg install. Falling back to libx265.")
        return False
    else:
        r = subprocess.run(f"ffmpeg -hide_banner -i {file} -c:v hevc_nvenc -f null -", text=True, capture_output=True)
        if "CUDA_ERROR" in r.stderr:
            print("## WARNING: Error invoking ffmpeg encoder \"hevc_nvenc\". Falling back to libx265.")
            return False
    print("## INFO: ffmpeg encoder \"hevc_nvenc\" OK.")
    return True

def delete_temp(ts_dir, ts_path=""):
    print("\n===== deleting temp files... =====================")
    shutil.rmtree(ts_dir)
    if ts_path != "": os.remove(ts_path)
    print("\n===== done deleting temp files. ==================")

def convert_video(ts_path, sfn, nvenc):
    print("\n===== converting to hevc mp4 with ffmpeg... ======")
    if nvenc == True: cmd = f"ffmpeg -hide_banner -i \"{ts_path}\" -c:v hevc_nvenc -cq:v 28 -preset fast -bsf:a aac_adtstoasc \"{sfn}.mp4\""
    else: cmd = f"ffmpeg -hide_banner -i \"{ts_path}\" -c:v libx265 -crf 28 -preset fast -bsf:a aac_adtstoasc \"{sfn}.mp4\""
    subprocess.run(cmd)
    print("\n===== mp4 created successfully. ==================")

def generate_list(url, frags, filename):
    print("\n===== generating url list... =====")
    l = []
    for i in range(0, frags+1):
        l.append(f"{url}{str(i)}.ts\n")
    sfn = filename.replace(".txt", "").replace(".ts", "").replace(".mp4", "") # sanitized file name (no extension)
    print("\n===== url list OK. downloading fragments... ======")
    return l, sfn

def download_file(u, sfn, i):
    filename = f"./{sfn}/{(str(i+1)).rjust(5, "0")}.ts"
    wget.download(u, out=filename)
    return i

def download_files(l, sfn):
    print("\n===== downloading files... =======================")
    path = check_dir(f"./{sfn}")
    os.makedirs(path)
    ssl._create_default_https_context = ssl._create_unverified_context
    for i in range(len(l)):
        try: 
            download_file(l[i], sfn, i)
        except Exception as e:
            print(f"## WARNING: {e} thrown with URL {(str(i+1)).rjust(5, "0")}. Moving on...")
    print("\n===== downloads OK. continuing to merging... =====")
    return True

def mt_download(l, sfn, t=4):
    import concurrent.futures
    print("\n===== downloading files (multithreaded)... =======")
    path = check_dir(f"./{sfn}")
    os.makedirs(path)
    ssl._create_default_https_context = ssl._create_unverified_context
    with concurrent.futures.ThreadPoolExecutor(max_workers=t) as executor:
        future_download = {executor.submit(download_file, l[i], sfn, i): i for i in range(len(l))}
        for future in concurrent.futures.as_completed(future_download):
            i = future_download[future]
            try:
                data = future.result()
            except Exception as e:
                print(f"## WARNING: {e} thrown with URL {(str(i+1)).rjust(5, "0")}. Moving on...")
    print("\n===== downloads OK. continuing to merging... =====")
    return True

def merge(sfn):
    print("\n===== merging *.ts files... ======================")
    ts_path = f"./{sfn}.ts"
    ts_dir = f"./{sfn}"
    check_dir(ts_path, _type="file")
    with open(ts_path, 'wb') as merged:
        for ts_file in os.listdir(ts_dir):
            print(f"- merging {ts_file}...")
            with open(f"{ts_dir}/{ts_file}", 'rb') as merge_file:
                shutil.copyfileobj(merge_file, merged)
    print("\n===== merging OK. ================================")
    return ts_path, ts_dir

def threads(t):
    if t == 1: 
        return 4
    elif t > os.cpu_count():
        print(f"\n## WARNING: Number of threads selected exceeds maximum number of threads available. Setting thread count to maximum ({str(os.cpu_count())}).")
        return os.cpu_count()
    else:
        return t

def usage(e):
    print("\nUsage:\n" +
          "  python getfiles.py \"<url>\" <fragments> \"<name>\"\n" +
          "      \"<url>\": ....... quotation mark flanked string: http/https URL of one *.ts fragment.\n" +
          "      <fragments> .... integer corresponding to total number of *.ts fragments.\n" +
          "      \"<name>\" ....... quotation mark flanked string: file name to save file as (no extension).\n" +
          "\nFlags: \n" +
          "  -mt, --multithreading [<threads>] ..... multithread downloading operation. defaults to T(rue) even if flag not declared.\n" +
          "                                            [<threads>] set to [blank] or \'1\' to use default value of 4 threads (or system maximum, if <4).\n" +
          "                                            [<threads>] set to \'f\', \'false\', or \'0\' disables multithreading.\n" +
          "                                            [<threads>] set to int n > 1 will use n threads (up to system maximum).\n" +
          "                                            [<threads>] set to \'max\' will use maximum number of threads on system.\n" +
          "\n  -f, --ffmpeg [<bool>] ................. ffmpeg conversion of *.ts output to *.mp4 (HEVC). defaults to T(rue) even if flag not declared.\n" +
          "                                            <bool> set to \'f\', \'false\', or \'0\' disables ffmpeg conversion to mp4.\n" +
          "\n  -nv, --nvenc [<bool>] ................. enable nvenc_hevc encoder in ffmpeg. defaults to T(rue). always falls back to libx265 if nvenc device unavailable.\n" +
          "                                            <bool> set to \'f\', \'false\', or \'0\' disables nvenc acceleration for ffmpeg, even if device available.\n" +
          "                                            ignored if --ffmpeg set to false.\n" +
          "\n  -k, --keep ............................ keep all temp files (*.ts fragments; merged *.ts if ffmpeg conversion enabled). False if flag not declared.\n")
    sys.exit(e)

def parse_args(user_args):
    if "-h" in user_args or "--help" in user_args:
        usage(0)
    elif len(user_args) < 3:
        print("## ERROR: Please enter at least THREE arguments.")
        usage(1)
    
    mt = 4
    ffmpeg = True
    nvenc = True
    keep = False
    flags = ["-mt", "--multithreading", "-f", "-ffmpeg", "-nv", "--nvenc", "-k", "--keep"]
    boolf = ["false", "f", "0"]
    
    if "http" not in user_args[0]:
        print("## ERROR: Please ensure an http/https url was entered as the first argument.")
        usage(1)
    elif ".ts" not in user_args[0]:
        print("## ERROR: Please ensure the URL in your first argument contains a *.ts file.")
        usage(1)
    elif not user_args[1].isnumeric():
        print("## ERROR: Please ensure the second argument is an integer.")
        usage(1)
    
    if len(user_args) > 3:
        parsed = False
        for i in range(3, len(user_args)):
            if str(user_args[i]).lower() in flags[0:2]:
                if str(user_args[i+1]) in boolf:
                    mt = False
                    parsed = True
                elif str(user_args[i+1]).isnumeric():
                    mt = threads(int(user_args[i+1]))
                    parsed = True
                else:
                    mt = threads(4)
                print(f"\n## INFO: Multithreading enabled. {str(os.cpu_count())} logical processors detected. {mt} processors to be used.")
            elif str(user_args[i]).lower() in flags[2:4]:
                if str(user_args[i+1]) in boolf:
                    ffmpeg = False
                    parsed = True
            elif str(user_args[i]).lower() in flags[4:6]:
                if str(user_args[i+1]) in boolf:
                    nvenc = False
                    parsed = True
            elif str(user_args[i]).lower() in flags[6:]:
                keep = True
            elif parsed == True:
                parsed = False
            else:
                print(f"## WARNING: Argument {user_args[i]} not understood. Ignoring and continuing...")
    return mt, ffmpeg, nvenc, keep

def main():
    t0 = time.time()
    user_args = sys.argv[1:]
    mt, ffmpeg, nvenc, keep = parse_args(user_args)
    if mt != False: multithreading = f"{mt} threads"
    else: multithreading = "False"
    chopped_url = str(user_args[0]).split("_")
    chopped_url[-1] = ""
    url = "_".join(chopped_url)
    frags = int(user_args[1])
    filename = str(user_args[2])
    print(f"\nInputs OK. Processing with options: \n" +
          f"    url            = {str(user_args[0])}\n" +
          f"    fragments      = {frags}\n" +
          f"    filename       = \"{filename}\"\n" +
          f"    multithreaded  = {str(multithreading)}\n" +
          f"    ffmpeg_convert = {str(ffmpeg)}\n" +
          f"    nvenc          = {str(nvenc)}\n" +
          f"    keep_temp      = {str(keep)}")
    print("\n===== continuing to url list generation... =======")
    l, sfn = generate_list(url, frags, filename) # file list & sanitized filename (no extension)
    if mt != False:
        mt_download(l, sfn, t=mt)
    else:
        download_files(l, sfn)
    ts_path, ts_dir = merge(sfn)
    if ffmpeg == True:
        if nvenc == True:
            print("\n===== checking nvenc... ======================")
            nvenc = check_nvenc(ts_dir + "/00001.ts")
        convert_video(ts_path, sfn, nvenc)
        if keep == False:
            delete_temp(ts_dir, ts_path)
    elif keep == False:
        delete_temp(ts_dir)
    t1 = time.time()
    runtime = round(t1-t0, 2)
    print("\n===== Processing complete. =======================")
    print(f"{str(runtime)} seconds elapsed.")
    input("Press <ENTER> to continue.")

if __name__ == "__main__":
    main()
