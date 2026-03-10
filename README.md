# e-Bridge Timetable to .ics file

### Installation

1. Install Python 3
2. Install dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

### Basic Usage

#### Mode A: Via Timetable Hash ID (Recommended)

1. Open your [XJTLU e-Bridge Timetable](https://ebridge.xjtlu.edu.cn/) page.
2. Open the browser **Developer Tools** (Right-click > **Inspect**, or press `F12` / `Ctrl+Shift+I` on Windows/Linux, `Cmd+Option+I` on Mac).
3. Switch to the **Network** tab and refresh the page (Press `F5` / `Cmd+R`).
4. Look for a Fetch/XHR request with a URL like:
   `https://timetableplus.xjtlu.edu.cn/ptapi/api/enrollment/hash/[TIMETABLE_ID]/activity?start=1&end=13`
5. Copy the `[TIMETABLE_ID]` portion (the long string).
6. Run the script:
   ```bash
   python3 main.py --id [HASH_ID] -s [START_DATE]
   ```
   *Replace `[START_DATE]` with the first Monday of the semester. Example: `2026-03-02`*

#### Mode B: Via Local JSON File

1. Follow steps 1-4 above to find the same Fetch/XHR request.
2. Right-click the request and select **Copy** > **Copy response** (or click the request and copy the JSON from the **Response** tab).
3. Save the response content as `input.json`.
4. Run the script:
   ```bash
   python3 main.py --file input.json -s [START_DATE]
   ```

### Advanced Usage

Check `timetable.ics` in the folder. You can also specify the output file name:

```bash
python3 main.py --id [HASH_ID] -s 2026-03-02 -o my_calendar.ics
```
