import argparse
import datetime
import re
import uuid
import sys
from bs4 import BeautifulSoup

DAYS = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]

def parse_timetable(html_content: str) -> dict:
    soup = BeautifulSoup(html_content, "html.parser")
    lesson_dict = {}

    table = soup.find(class_="timetable")
    if not table:
        return lesson_dict
        
    tbody = table.find("tbody")
    if not tbody:
        return lesson_dict

    # Walk through every body row
    rows = tbody.find_all("tr", recursive=False)

    for row in rows:
        time_str = ""
        cells = row.find_all(["th", "td"], recursive=False)

        for cell in cells:
            classes = cell.get("class", [])
            # Get start time from time-cell
            if "time-cell" in classes:
                time_str = cell.get_text(strip=True)
                continue

            day_attr = cell.get("data-day")
            if not day_attr:
                continue
            day = day_attr[:2].upper()

            event_div = cell.find(class_="event")
            if event_div:
                name_div = event_div.find(class_="event-name")
                info_divs = event_div.find_all(class_="event-info")

                if name_div and len(info_divs) >= 3:
                    title = name_div.get_text(strip=True)

                    time_info = info_divs[-1].get_text(strip=True)
                    time_match = re.search(r"(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})", time_info)
                    start_time = time_match.group(1) if time_match else time_str
                    end_time = time_match.group(2) if time_match else time_str

                    if title not in lesson_dict:
                        lesson = {
                            "teachers": info_divs[0].get_text(strip=True),
                            "location": info_divs[1].get_text(strip=True),
                            "weeks": info_divs[2].get_text(strip=True),
                            "day": day,
                            "startTime": start_time,
                            "endTime": end_time,
                        }
                        lesson_dict[title] = lesson

    return lesson_dict

def get_monday_of_week(first_monday: datetime.datetime, n: int) -> datetime.datetime:
    return first_monday + datetime.timedelta(days=(n - 1) * 7)

def get_day_code(day: str) -> int:
    return {"MO": 0, "TU": 1, "WE": 2, "TH": 3, "FR": 4, "SA": 5, "SU": 6}.get(day, 0)

def format_date_str(dt: datetime.datetime) -> str:
    # simple_ics format for DTSTART without Z (local naive time format matching orig output exactly)
    return dt.strftime("%Y%m%dT%H%M%S")

class Event:
    def __init__(self, cfg):
        self.title = cfg["title"]
        self.begin_date = cfg["begin_date"]
        self.duration_sec = cfg["duration"]
        self.location = cfg.get("location")
        self.rrule_until = cfg["rrule_until"]
        self.alarm_desc = cfg["alarm_desc"]
        self.uid = str(uuid.uuid4())
        self.dtstamp = datetime.datetime.now()
        
    def to_lines(self):
        end_date = self.begin_date + datetime.timedelta(seconds=self.duration_sec)
        
        lines = []
        lines.append(["BEGIN", "VEVENT"])
        lines.append(["UID", self.uid])
        lines.append(["DTSTAMP", format_date_str(self.dtstamp)])
        lines.append(["DTSTART", format_date_str(self.begin_date)])
        lines.append(["DTEND", format_date_str(end_date)])
        lines.append(["SUMMARY", self.title])
        if self.location:
            lines.append(["LOCATION", self.location])
        
        rrule_str = f"FREQ=WEEKLY;UNTIL={format_date_str(self.rrule_until)};"
        lines.append(["RRULE", rrule_str])
        
        lines.append(["BEGIN", "VALARM"])
        lines.append(["TRIGGER", "-PT30M"])
        lines.append(["ACTION", "DISPLAY"])
        lines.append(["DESCRIPTION", self.alarm_desc])
        lines.append(["END", "VALARM"])
        
        lines.append(["END", "VEVENT"])
        return lines

class Calendar:
    def __init__(self, events):
        self.events = events
        
    def to_lines(self):
        lines = []
        lines.append(["BEGIN", "VCALENDAR"])
        lines.append(["VERSION", "2.0"])
        lines.append(["PRODID", "peron/simple_ics"])
        lines.append(["METHOD", "PUBLISH"])
        for evt in self.events:
            lines.extend(evt.to_lines())
        lines.append(["END", "VCALENDAR"])
        return lines

    def to_string(self):
        return "\n".join([":".join(line) for line in self.to_lines()]) + "\n"

def gen_calendar(lessons: dict, first_monday: datetime.datetime) -> Calendar:
    events = []
    
    for title, lesson in lessons.items():
        location = lesson.get("location")
        day = lesson["day"]
        
        btime = [int(x) for x in lesson["startTime"].split(":")]
        etime = [int(x) for x in lesson["endTime"].split(":")]
        duration = (etime[0] * 3600 + etime[1] * 60) - (btime[0] * 3600 + btime[1] * 60)
        
        time_since_monday_sec = get_day_code(day) * 86400 + btime[0] * 3600 + btime[1] * 60
        
        weeks_str = lesson["weeks"][5:]
        weeks = []
        for week_str in weeks_str.split(","):
            parts = [int(x.strip()) for x in week_str.strip().split("-")]
            weeks.append(parts)
            
        for week_duration in weeks:
            first_monday_of_week = get_monday_of_week(first_monday, week_duration[0])
            
            if len(week_duration) >= 2:
                until_date = first_monday_of_week + datetime.timedelta(seconds=86400 * 7 * (week_duration[1] - week_duration[0] + 1))
            else:
                until_date = first_monday_of_week + datetime.timedelta(seconds=86400 * 7)
                
            begin_date = first_monday_of_week + datetime.timedelta(seconds=time_since_monday_sec)
            
            cfg = {
                "title": title,
                "begin_date": begin_date,
                "location": location,
                "duration": duration,
                "rrule_until": until_date,
                "alarm_desc": f"{title} will start in 30 minutes"
            }
            events.append(Event(cfg))
            
    return Calendar(events)

def main():
    parser = argparse.ArgumentParser(description="Convert XJTLU e-Bridge Timetable HTML to ICS format")
    parser.add_argument("-i", "--input", help="Path to the timetable HTML file", default="e-Bridge.html")
    parser.add_argument("-s", "--start-date", help="Start date of Week 1 (YYYY-MM-DD)", required=True)
    parser.add_argument("-o", "--output", help="Output ICS filename", default="timetable.ics")
    
    args = parser.parse_args()
    
    try:
        first_monday = datetime.datetime.strptime(args.start_date, "%Y-%m-%d")
        if first_monday.weekday() != 0:
            print("Warning: The provided start date is not a Monday.")
    except ValueError:
        print("Error: Invalid date format. Please use YYYY-MM-DD.")
        sys.exit(1)
        
    try:
        with open(args.input, "r", encoding="utf-8") as f:
            html_content = f.read()
    except Exception as e:
        print(f"Error reading {args.input}: {e}")
        sys.exit(1)
        
    lessons = parse_timetable(html_content)
    if not lessons:
        print("No lessons found. Please ensure the HTML file contains the correct timetable structure.")
        sys.exit(1)
        
    calendar = gen_calendar(lessons, first_monday)
    
    try:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(calendar.to_string())
        print(f"Success: Generated {args.output} successfully! ({len(calendar.events)} classes mapped)")
    except Exception as e:
        print(f"Error writing to {args.output}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
