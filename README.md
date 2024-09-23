# getTSstream

#### Current version: `v0.7`. Tools contained within `Main` branch are always most recent.

A simple script for getting and assembling `*.ts` streamed videos. 

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

## To find the address of your `*.ts` streamed videos:
- `Inspect` the page
- Navigate to the `Network` tab
- Find the numbered `*.ts` files
- Right click > Copy Link Address
- Typically the first Video Number is 0 or 1.
- You can find the last number by clicking into the last 45 seconds of the video, while actively viewing the `Network` tab. You can add +10 to the Last Video Number to catch any missed stream segments, as the script ignores any nonexistent Video Numbers.
