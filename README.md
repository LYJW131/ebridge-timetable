# e-Bridge Timetable to .ics File

An elegant and minimalist tool to convert XJTLU e-Bridge timetables into standard `.ics` calendar files.

## 1. Get Timetable Hash ID (Required)

Whether you use the online tool or the local script, you first need to get your Timetable Hash ID:

1.  Log in to [XJTLU e-Bridge Timetable](https://ebridge.xjtlu.edu.cn/).
2.  Open **Developer Tools** (F12 or Right-click -> Inspect).
3.  Go to the **Network** tab and refresh the page (F5).
4.  Find a Fetch/XHR request that contains `activity?start=1&end=13`.
5.  Copy the `[HASH_ID]` from the request URL (e.g., `https://timetableplus.xjtlu.edu.cn/ptapi/api/enrollment/hash/[HASH_ID]/activity...`).

## 2. Choose Usage Mode

### Online Usage (Recommended)
Just paste your Hash ID into the web interface:
**[https://timetable2ics.lyjw131.com/](https://timetable2ics.lyjw131.com/)**

### Local CLI Usage (Python)
If you prefer running it locally:
1.  Ensure you have **Python 3** installed (no extra dependencies required).
2.  Run: `python3 main.py --id [HASH_ID] -s 2026-03-02`
    *(Note: `-s` is the date of the first Monday of the semester)*

---

## Project Structure
- `index.html`: Web version implemented in pure JavaScript.
- `main.py`: Core logic implemented in Python.