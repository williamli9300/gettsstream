# getTSstream v1.1.0 - https://github.com/williamli9300/gettsstream

import os, pathlib, shutil, ssl, subprocess, sys, time, wget

def check_dir(path, _type="directory"):
    if os.path.exists(path):
        if str(input(f"## WARNING: {path} already exists. Permanently delete this {_type} before moving on? [y/N] ")).lower() == "y":
            if _type == "directory": shutil.rmtree(path)
            elif _type == "file": os.remove(path)
        else:
            if _type == "file":
                path = path.split(".")
                ext = f".{path[-1]}"
                path.pop(-1)
                path = ".".join(path)
            path = path + "_1"
            if _type == "file":
                path = path + ext
            path = check_dir(path, _type)
    return path

def construct_ffmpeg(_input, output, crf, nvenc, subtitle, sublang, subname, preset, vbrf, vbr):
    options = "-hide_banner -benchmark"
    out_flags = "-f mp4 -movflags \"+faststart\""

    if crf != False:
        if crf < 16:
                print(f"## WARNING: CRF value of {crf} too small. Increasing to 16.")
                crf = "16"
        elif crf > 51:
            print(f"## WARNING: CRF value of {crf} too large. Decreasing to 51.")
            crf = "51"
        else:
            crf = str(crf)
    elif vbr != False:
        quality = f"-b:v {vbr}"
    else:
        p = subprocess.run(f"ffprobe -loglevel error -select_streams v:0 -show_entries format=bit_rate -of default=noprint_wrappers=1:nokey=1 {_input}", text=True, capture_output=True)
        if p.stdout.replace("\n", "").isnumeric():
            bitrate = int(int(p.stdout.replace("\n", "")) * vbrf)
            quality = f"-b:v {bitrate}"
        else:
            print(f"## WARNING: unable to estimate input bitrate. Continuing with -crf 28.")
            crf = "28"

    if crf != False:
        if nvenc == True: crf_command = "-cq:v"
        elif nvenc == False: crf_command = "-crf"
        quality = f"{crf_command} {crf}"

    if nvenc == True:
        if preset.lower() not in ["p1", "p2", "p3", "p4", "p5", "p6", "p7", "default", "slow", "medium", "fast", "hp", "hq", "bd", "ll", "llhq", "llhp", "lossless", "losslesshp"]:
            print(f"## WARNING: Preset value {preset} not valid. Defaulting to \"p3\".")
            preset = "p3"
        encode = f"-c:v hevc_nvenc {quality} -preset {preset.lower()}"
    else:
        if preset.lower() not in ["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow", "placebo"]:
            print(f"## WARNING: Preset value {preset} not valid. Defaulting to \"faster\".")
            preset = "faster"
        encode = f"-c:v libx265 {quality} -preset {preset.lower()}"

    if subtitle != False:
        _input = f"{_input} -i {subtitle}"
        output = f"-codec:s mov_text -metadata:s:s:0 title=\"{subname}\" -metadata:s:s:0 language=\"{sublang}\" {out_flags} {output}"
    else:
        output = f"{out_flags} {output}"
    cmd = f"ffmpeg {options} -i {_input} {encode} -bsf:a aac_adtstoasc {output}"
    return cmd

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

def convert_video(ts_path, sfn, crf, nvenc, subtitle, sublang, subname, preset, vbrf, vbr):
    print("\n===== constructing ffmpeg command... =============")
    mp4_path = f"{sfn}.mp4"
    mp4_path = check_dir(mp4_path, _type="file")
    cmd = construct_ffmpeg(ts_path, mp4_path, crf, nvenc, subtitle, sublang, subname, preset, vbrf, vbr)
    print("\n===== converting to hevc mp4 with ffmpeg... ======")
    print(f"## INFO: ffmpeg command: {cmd}")
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        return e.returncode
    print("\n===== mp4 created successfully. ==================")
    return 0

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
          "  -mt, -multithreading [<int threads>] ..... multithread downloading operation. defaults to T(rue) even if flag not passed.\n" +
          "                                              + [<threads>] set to [blank] or \'1\' to use default value of 4 threads (or system maximum, if <4).\n" +
          "                                              + [<threads>] set to \'f\', \'false\', or \'0\' disables multithreading.\n" +
          "                                              + [<threads>] set to int n > 1 will use n threads (up to system maximum).\n" +
          "                                              + [<threads>] set to \'max\' will use maximum number of threads on system.\n" +
        "\n  -f, -ffmpeg [<bool>] ..................... ffmpeg conversion of *.ts output to *.mp4 (HEVC). defaults to T(rue) even if flag not passed.\n" +
          "                                              + <bool> set to \'f\', \'false\', or \'0\' disables ffmpeg conversion to mp4.\n" +
        "\n  -nv, -nvenc [<bool>] ..................... enable nvenc_hevc encoder in ffmpeg. defaults to T(rue). always falls back to libx265 if nvenc device unavailable.\n" +
          "                                              + <bool> set to \'f\', \'false\', or \'0\' disables nvenc acceleration for ffmpeg, even if device available.\n" +
          "                                              + ignored if -ffmpeg set to false.\n" +
        "\n  -k, -keep ................................ keep all temp files (*.ts fragments; merged *.ts if ffmpeg conversion enabled). False if flag not declared.\n" +
        "\n  -s, -subtitle <str url> .................. pass a url to a subtitle file (typically *.vtt) to include in conversion. see README.md for more information.\n" +
          "                                              + ignored if -ffmpeg set to false.\n" +
        "\n  -sl, -sublang <str> ...................... define a language for the subtitle track (3-letter iso 639-2 code). default: \"eng\".\n" +
          "                                              + ignored if -ffmpeg set to false.\n" +
          "                                              + ignored if no subtitle track provided.\n" +
        "\n  -sn, -subname <str> ...................... define a title for the subtitle track. default: \"subtitles\".\n" +
          "                                              + ignored if -ffmpeg set to false.\n" +
          "                                              + ignored if no subtitle track provided.\n" +
        "\n  -c, -crf [<int>] ......................... define a constant rate factor for ffmpeg conversion. defaults to 28 if flag is passed.\n" +
          "                                              + if flag not passed, variable bit rate targeting 0.75 of *.ts bit rate will be used.\n" +
          "                                              + if flag passed, -crf flag holds priority over -vbrf and -vbr.\n" +
          "                                              + ignored if -ffmpeg set to false.\n" +
        "\n  -vf, -vbrf [<float>] ..................... define a scale factor of *.ts bitrate to target (using variable bitrate) during ffmpeg conversion.\n" +
          "                                              + defaults 0.75, even if flag not passed.\n" +
          "                                              + falls back to -crf 28 if target bitrate cannot be identified.\n" +
          "                                              + -crf and -vbr flags hold priority over -vbrf.\n" +
          "                                              + ignored if -ffmpeg set to false.\n" +
        "\n  -v, -vbr <int> ........................... explicitly define a bitrate to target (using variable bitrate) during ffmpeg conversion.\n" +
          "                                              + if flag not passed, variable bit rate targeting 0.75 of *.ts bit rate will be used.\n" +
          "                                              + if flag passed with no argument, variable bit rate targeting 0.75 of *.ts bit rate will be used.\n" +
          "                                              + supports K, M, and G notation (e.g. 1100K, 1.25M, 0.01G).\n" +
          "                                              + ignored if -ffmpeg set to false.\n" +
        "\n  -p, -preset .............................. pass hevc presets to ffmpeg. defaults to p3 (nvenc_hevc) or faster (libx265).\n" +
          "                                              + supported options for nvenc_hevc: \n" +
          "                                                [p1, p2, p3, p4, p5, p6, p7, default, slow, medium, fast, hp, hq, bd, ll, llhq, llhp, lossless, losslesshp]\n"
          "                                              + supported options for libx265: \n" +
          "                                                [ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow, placebo]")
    sys.exit(e)

def parse_args(user_args):
    if "-h" in user_args or "-help" in user_args or len(user_args) == 0:
        usage(0)
    elif len(user_args) < 3:
        print("## ERROR: Please enter at least THREE arguments.")
        usage(1)
    
    mt = 4
    ffmpeg = True
    nvenc = True
    keep = False
    subtitle = False
    crf=False
    sublang = "eng"
    subname = "subtitles"
    preset="p3"
    vbrf = 0.75
    vbr = False
    
    flags = ["-mt", "-multithreading", "-f", "-ffmpeg", "-nv", "-nvenc", "-k", "-keep", "-s", "-subtitle", "-sl", "-sublang", "-sn", "-subname", "-c", "-crf", "-vf", "-vbrf", "-v", "-vbr", "-p", "-preset"]
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
            if str(user_args[i]).lower() in flags[0:2]: # "-mt", "-multithreading"
                print(f"i={i}, len(user_args)={len(user_args)}, user_args[i]={user_args[i]}, user_args[i+1]={user_args[i]}")
                if len(user_args) > i+1:
                    if str(user_args[i+1]) in boolf:
                        mt = False
                        parsed = True
                    elif str(user_args[i+1]).isnumeric():
                        mt = int(user_args[i+1])
                        parsed = True
                    elif str(user_args[i+1]).lower() == "max":
                        mt = os.cpu_count()
                        parsed = True
                mt = threads(mt)
                print(f"\n## INFO: Multithreading enabled. {str(os.cpu_count())} logical processors detected. {mt} processors to be used.")
            elif str(user_args[i]).lower() in flags[2:4]: # "-f", "-ffmpeg"
                if len(user_args) > i+1:
                    if str(user_args[i+1]).lower() in boolf:
                        ffmpeg = False
                        parsed = True
            elif str(user_args[i]).lower() in flags[4:6]: # "-nv", "-nvenc"
                if len(user_args) > i+1:
                    if str(user_args[i+1]).lower() in boolf:
                        nvenc = False
                        parsed = True
            elif str(user_args[i]).lower() in flags[6:8]: # "-k", "-keep"
                keep = True
            elif str(user_args[i]).lower() in flags[8:10]: # "-s", "-subtitle"
                if len(user_args) <= i+1:
                    print(f"## WARNING: Expected argument after flag {user_args[i]}. Ignoring...")
                else:
                    if "http" not in user_args[i+1]:
                        print(f"## WARNING: Expected http/https url after flag {user_args[i]}. Ignoring...")
                    else:
                        try:
                            print(f"\n## INFO: Downloading subtitles from {user_args[i+1]} to {subtitle}...")
                            subtitle = "./subtitle.vtt"
                            wget.download(user_args[i+1], out=subtitle)
                            print(f"\n## INFO: Subtitle file downloaded from {user_args[i+1]} to {subtitle}.\n")
                        except Exception as e:
                            print(f"##WARNING: Exception {e} thrown while downloading subtitle file. Proceeding without subtitles.")
                            subtitle = False
                        parsed = True
            elif str(user_args[i]) in flags[10:12]: # "-sl", "-sublang"
                if len(user_args) <= i+1:
                    print(f"## WARNING: Expected argument after flag {user_args[i]}. Ignoring...")
                else:
                    sublang = str(user_args[i+1])
                    parsed = True
            elif str(user_args[i]) in flags[12:14]: # "-sn", "-subname"
                if len(user_args) <= i+1:
                    print(f"## WARNING: Expected argument after flag {user_args[i]}. Ignoring...")
                else:
                    sublang = str(user_args[i+1])
                    parsed = True
            elif str(user_args[i]) in flags[14:16]: # "-c", "-crf"
                if len(user_args) > i+1:
                    if not (user_args).isnumeric():
                        print(f"## WARNING: {user_args[i]} value {user_args[i+1]} not valid. Using default -crf 28...")
                        crf = 28
                    else:
                        crf = int(user_args[i+1])
                        parsed = True
                else:
                    print(f"## WARNING: Expected argument after flag {user_args[i]}. Using default -crf 28...")
                    crf = 28
            elif str(user_args[i]) in flags[16:18]: # "-vf", "-vbrf"
                if len(user_args) > i+1:
                    try: vbrf = float(user_args[i+1])
                    except ValueError: print(f"## WARNING: {user_args[i]} value {user_args[i+1]} not valid. Using default -vbrf 0.75...")
                    if not float(user_args[i+1]) > 0:
                        print(f"## WARNING: {user_args[i]} value {user_args[i+1]} not valid. Using default -vbrf 0.75...")
                        vbrf = 0.75
                    else:
                        vbrf = float(user_args[i+1])
                        parsed = True
                else:
                    print(f"## WARNING: {user_args[i]} value {user_args[i+1]} not valid. Using default -vbrf 0.75...")
            elif str(user_args[i]) in flags[18:20]: # "-v", "-vbr"
                if len(user_args) > i+1:
                    try:
                        if str(user_args[i+1]).lower().endswith("g"):
                            vbr = int(float(str(user_args[i+1])[:-1]) * 1000000000)
                        elif str(user_args[i+1]).lower().endswith("m"):
                            vbr = int(float(str(user_args[i+1])[:-1]) * 1000000)
                        elif str(user_args[i+1]).lower().endswith("k"):
                            vbr = int(float(str(user_args[i+1])[:-1]) * 1000)
                        else:
                            vbr = int(user_args[i+1])
                        parsed = True
                    except Exception as e:
                        print(f"## WARNING: {user_args[i]} value {user_args[i+1]} returned exception {e}. Using default -vbrf 0.75...")
                        vbr = False
                else:
                    print(f"## WARNING: Expected argument after flag {user_args[i]}. Using default -vbrf 0.75...")
            elif str(user_args[i]) in flags[22:24]: # "-p", "-preset"
                if len(user_args) <= i+1:
                    print(f"## WARNING: Expected argument after flag {user_args[i]}. Ignoring...")
                else:
                    preset = str(user_args[i+1])
                    parsed = True
            elif parsed == True:
                parsed = False
            else:
                print(f"## WARNING: Argument {user_args[i]} not understood. Ignoring and continuing...")
    if subtitle == False:
        sublang = "n/a"
        subname = "n/a"
    if crf != False:
        vbrf = False
        vbr = False
    if vbr != False:
        vbrf = False
        crf = False
    if vbr == False and vbrf == False and crf == False:
        vbrf = 0.75
    return mt, ffmpeg, nvenc, keep, subtitle, sublang, subname, crf, preset, vbrf, vbr

def main():
    t0 = time.time()
    user_args = sys.argv[1:]
    ssl._create_default_https_context = ssl._create_unverified_context
    mt, ffmpeg, nvenc, keep, subtitle, sublang, subname, crf, preset, vbrf, vbr = parse_args(user_args)
    if mt != False: multithreading = f"{mt} threads"
    else: multithreading = "False"
    chopped_url = str(user_args[0]).split("_")
    chopped_url[-1] = ""
    url = "_".join(chopped_url)
    frags = int(user_args[1])
    filename = str(user_args[2])
    print(f"\nInputs OK. Processing with options: \n" +
          f"    url            =  {str(user_args[0])}\n" +
          f"    fragments      =  {int(frags)}\n" +
          f"    filename       =  \"{str(filename)}\"\n" +
          f"    multithreaded  =  {str(multithreading)}\n" +
          f"    ffmpeg_convert =  {str(ffmpeg)}\n" +
          f"    nvenc          =  {str(nvenc)}\n" +
          f"    keep_temp      =  {str(keep)}\n" +
          f"    subtitle       =  {str(subtitle)}\n" +
          f"    sub_lang       =  {str(sublang)}\n" +
          f"    sub_name       =  {str(subname)}\n" +
          f"    crf            =  {str(crf)}\n" +
          f"    vbr factor     =  {str(vbrf)}\n" +
          f"    vbr target     =  {str(vbr)}\n" +
          f"    ffmpeg_preset  =  {str(preset)}")
    time.sleep(0.5)
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
        converted = convert_video(ts_path, sfn, crf, nvenc, subtitle, subname, sublang, preset, vbrf, vbr)
        if converted != 0:
            if keep == False:
                print(f"\n==============================================\n## WARNING: ffmpeg returned with error {converted}. Keeping temp files.")
            keep = True
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
