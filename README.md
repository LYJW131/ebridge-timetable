# e-Bridge Timetable to .ics file

### Installation

1. Install Python 3
2. Install dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

### Basic Usage

1. Prepare the .html file of e-bridge timetable and rename it to `e-Bridge.html`
2. Run the script:
   ```bash
   python3 main.py -s [START_DATE]
   ```
   *Replace `[START_DATE]` with the first Monday of the semester. Example: `2026-03-02`*
3. Check `timetable.ics` in the folder

### Advanced Usage

You can safely specify both input file path and output file name:

```bash
python3 main.py -i "My Timetable.html" -s 2026-03-02 -o my_calendar.ics
```
