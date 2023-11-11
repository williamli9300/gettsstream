# getTSstream

#### Current version: `v0.5.1`. Tools contained within `Main` branch are always most recent.

A simple script for getting and assembling `*.ts` streamed videos. "Streaming" means that several videos (numbered in order) are played sequentially (i.e. in a stream) to form one larger amalgamated video.

## Warnings and Disclaimers

This tool is provided for reference and/or educational purposes only. 

**Please make sure your use of these tools does not violate any copyright laws.** 

**SSL verification for `wget` is disabled.** If used improperly, this may increase risk of MitM and other attacks SSL verification is designed to protect against. Heed on-screen warning and use at your own risk.

```
The author of this tool offers no warranty and assumes no responsibility or liability 
whatsoever for any use of these tools, including but not limited to: the actions and 
intents of third parties using these tools, or effects upon users' devices as a result
of the use of these tools. As previously stated, this tool is provided solely for 
reference and/or educational purposes. Use responsibly, and at your own risk.
```
## Usage:
- Put `getfiles.py` in the folder you would like to save your TS video.
- Run script.
- Follow the command line prompts.
- Not designed for streamed `*.ts` files where file number includes leading zeros.

## To find the address of your `*.ts` streamed videos:
- `Inspect` the page
- Navigate to the `Network` tab
- Hit `Play` on your video
- Find the numbered `*.ts` files
- Right click > Copy Link Address
- If this doesn't work, refresh page and try again

## Program Instructions:
- Find URL for first video using instructions above:
  - After navigating to `Network` tab, start playing video from beginning. Find the `*.ts` file with the lowest number at the end.
- Find URL for last video using the instructions above:
  - After navigating to `Network` tab, start playing video from 30s before end. Find the `*.ts` file with the highest number at the end.
- For example, if your first URL is `https://media.myurl.com/myvideo_1.ts` and your last URL is `https://media.myurl.com/myvideo_100.ts`, your input to the program would look like the following:
```
please enter the URL prefix (before number and '.ts') 
> https://media.myurl.com/myvideo_
please enter the first video number 
> 1
please enter the last video number 
> 100
please enter file name
> myvideo
...
```
