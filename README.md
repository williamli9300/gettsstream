# getTSstream

#### Current version: `v0.8.0`. Tools contained within `Main` branch are always most recent.

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
- Requires `ffmpeg`.
## Usage:
- Put `getfiles.py` in the folder you would like to save your TS video.
- Open a command prompt window and navigate to the folder (e.g. using `cd <folder_path>`)
- Usage: `python getfiles "[url]" [filenum] "[name]"` where:
  - `"[url]" is the entire URL of any of the numbered `*.ts` files, flanked by quotation marks `"`.
  - `[filenum]` is the largest video number in any of the links
  - `"[name]"` is the filename you'd like to save your video as, flanked by quotation marks `"`.

## To find the address of your `*.ts` streamed videos:
- `Inspect` the page
- Navigate to the `Network` tab
- Find the numbered `*.ts` files
- Right click > Copy Link Address
- Typically the first Video Number is 0 or 1.
- You can find the last number by clicking into the last 45 seconds of the video, while actively viewing the `Network` tab. You can add +10 to the Last Video Number to catch any missed stream segments, as the script ignores any nonexistent Video Numbers.
