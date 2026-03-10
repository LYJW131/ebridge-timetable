# e-Bridge Timetable to .ics File

An elegant and minimalist tool to convert XJTLU e-Bridge timetables into standard `.ics` calendar files.

## Online Usage (Recommended)

The easiest way to use this tool without installing any dependencies:

**[https://timetable2ics.lyjw131.com/](https://timetable2ics.lyjw131.com/)**

---

## Local CLI Usage (Python)

If you prefer running the script locally, follow these steps:

### 1. Installation
Ensure you have Python 3 installed, then install the dependencies:
```bash
pip3 install -r requirements.txt
```

### 2. Get Timetable Hash ID
1. Open your [XJTLU e-Bridge Timetable](https://ebridge.xjtlu.edu.cn/) page.
2. Open the browser **Developer Tools** (F12 or Right-click -> Inspect).
3. Switch to the **Network** tab and refresh the page (F5).
4. Look for a Fetch/XHR request ending with `activity?start=1&end=13`.
5. Extract the `[HASH_ID]` part from the request URL (a long string of characters).

### 3. Run Conversion
```bash
python3 main.py --id [HASH_ID] -s 2026-03-02
```
*Note: `-s` is the date of the first Monday of the semester.*

---

## Project Structure
- `index.html`: Web version implemented in pure JavaScript.
- `main.py`: Core logic implemented in Python.