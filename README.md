# getTSstreams

A simple toolset for getting and assembling `*.ts` streamed videos. 

For reference / educational purposes only.

Please make sure your use of these tools do not violate any copyright laws. 

The author offers no warranty and assumes no responsibility for any use of these tools.

To use:
- Use `ts_urllist_getter.py` to create a text document list of all `*.ts` file urls
- Visit each URL using external tool (e.g. browser extension, cURL script)
- Rename files in numerical order (`1.ts`, `2.ts`, ... `469.ts`, `470.ts`, etc.)
- Run `combine.bat` to combine `*.ts` videos into one master file `output.ts`  

To find the addess of your `*.ts` streamed videos:
- `Inspect` the page
- Navigate to the `Network` tab
- Find the numbered `*.ts` files
- Right click > Copy Link Address
