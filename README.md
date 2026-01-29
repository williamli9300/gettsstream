# getTSstream

#### Current version: `v1.1.0`. Tools contained within `Main` branch are always most recent.

A simple script for getting and assembling `*.ts` streamed videos. 

## Warnings and Disclaimers

This tool is provided for reference and/or educational purposes only. 

**Please make sure your use of these tools does not violate any copyright laws.** 

**SSL verification for `wget` is disabled.** This reduces security and increases your susceptibility to attacks. **Use at your own risk.**

```
The author of this tool offers no warranty and assumes no responsibility or liability 
whatsoever for any use of these tools, including but not limited to: the actions and 
intents of third parties using these tools, or effects upon users' devices as a result 
of the use of these tools. As previously stated, this tool is provided solely for 
reference and/or educational purposes. Use responsibly, and at your own risk.
```

## Dependencies:
- Requires `python 3.x`.
- Recommend `ffmpeg` installed to path.

## Usage:
- Put `getfiles.py` in the folder you would like to save your TS video.
- Open a command prompt window and navigate to the folder (e.g. using `cd <folder_path>`)

**For help, run `python getfiles.py -h` or `python getfiles.py --help`.**

- Usage: `python getfiles "<url>" <frags> "<name>" [flags]`, where:
  - `"<url>"` is the entire URL of any of the numbered `*.ts` files, flanked by quotation marks `"`.
  - `<frags>` is the number of fragments your video is split into (i.e. largest video number of your links).
  - `"<name>"` is the filename you'd like to save your video as, flanked by quotation marks `"`.
- Flags:
  - `-mt, -multithreading [<int>]`: enables multithreading for downloads.
  - `-f, -ffmpeg [<bool>]`: `ffmpeg` conversion to HEVC `*.mp4` (enabled by default).
    - **If you don't have `ffmpeg` installed, pass `-f false`.**
  - `-nv, -nvenc [<bool>]`: NVENC acceleration of `ffmpeg` (enabled by default). Ignored if no `ffmpeg` conversion or if no NVENC device or encoder is available or installed.
  - `-k, -keep`: keeps temporary files otherwise deleted by the program:
    - `*.ts` fragments if no `ffmpeg` conversion;
    - `*.ts` fragments and merged `*.ts` file if converted using `ffmpeg`).
  - `-s, -subtitle <str>`: enables retrieval and muxing of subtitle from link. See below.
  - `-sl, -sublang <str>`: define a three-letter language code for your subtitle track.
  - `-sn, -subname <str>`: define a title for your subtitle track.
  - `-c, -crf [<int>]`: define a constant rate factor for `ffmpeg` conversion. defaults to 28 if passed. gets priority over `-vbrf` and `-vbr`.
  - `-vf, -vbrf [<float>]`: define a scale factor of the `*.ts` bitrate to target (using vbr) during `ffmpeg` conversion. defaults to 0.75, even if flag not passed. falls back to `-crf 28` if target bitrate cannot be identified.
  - `-v, -vbr <int>`: explicitly define a bitrate to target (using vbr) during `ffmpeg` conversion. gets priority of `-vbrf`.
  - `-p, -preset <str>`: pass hevc presets to `ffmpeg` for conversion.
    - `hevc_nvenc` supported presets: `p1`, `p2`, `p3`, `p4`, `p5`, `p6`, `p7`, `default`, `slow`, `medium`, `fast`, `hp`, `hq`, `bd`, `ll`, `llhq`, `llhp`, `lossless`, `losslesshp`
    - `libx264` supported presets: `ultrafast`, `superfast`, `veryfast`, `faster`, `fast`, `medium`, `slow`, `slower`, `veryslow`, `placebo`
  

## To find the address of your `*.ts` streamed videos:
- `Inspect` the page.
- Navigate to the `Network` tab.
- Find the numbered `*.ts` files.
- Right click > Copy Link Address.
- Typically the first Video Number is 0 or 1.
- You can find the last number by clicking into the last 45 seconds of the video, while actively viewing the `Network` tab. You can add +10 to the Last Video Number to catch any missed stream segments, as the script ignores any nonexistent Video Numbers.

## To find the address of subtitles for your `*.ts` streamed videos, if available:
- `Inspect` the page
- Navigate to the `Network` tab
- Hit `F5` to refresh.
- Find the `*.vtt` subtitle file.
- Right click > Copy Link Address.
