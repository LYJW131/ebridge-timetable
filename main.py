import argparse
import datetime
import re
import uuid
import sys
import json

def format_date_str(dt: datetime.datetime) -> str:
    # simple_ics format for DTSTART without Z (local naive time format matching orig output exactly)
    return dt.strftime("%Y%m%dT%H%M%S")

class Event:
    def __init__(self, cfg):
        self.title = cfg["title"]
        self.begin_date = cfg["begin_date"]
        self.duration_sec = cfg["duration"]
        self.location = cfg.get("location")
        self.description = cfg.get("description")
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
        if self.description:
            lines.append(["DESCRIPTION", self.description])
        
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

def get_monday_of_week(first_monday: datetime.datetime, n: int) -> datetime.datetime:
    return first_monday + datetime.timedelta(days=(n - 1) * 7)

def gen_calendar(items: list, first_monday: datetime.datetime) -> Calendar:
    events = []
    
    for item in items:
        # User defined mappings
        title = item.get("name", "Unnamed Event")
        location = item.get("location")
        if location:
            location = location.strip()
        staff = item.get("staff")
        description = staff if staff else ""
        
        # 0 = Monday
        day_code = int(item["scheduledDay"])
        
        # parse UTC time -> Beijing Time (+8 hours)
        start_utc = datetime.datetime.strptime(item["startTime"], "%Y-%m-%dT%H:%M:%SZ")
        end_utc = datetime.datetime.strptime(item["endTime"], "%Y-%m-%dT%H:%M:%SZ")
        
        start_bjt = start_utc + datetime.timedelta(hours=8)
        end_bjt = end_utc + datetime.timedelta(hours=8)
        
        duration = int((end_bjt - start_bjt).total_seconds())
        time_since_monday_sec = day_code * 86400 + start_bjt.hour * 3600 + start_bjt.minute * 60 + start_bjt.second
        
        weeks_str = str(item.get("weekPattern", ""))
        weeks = []
        for week_str in weeks_str.split(","):
            parts = [int(x) for x in re.findall(r'\d+', week_str)]
            if parts:
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
                "description": description,
                "duration": duration,
                "rrule_until": until_date,
                "alarm_desc": f"{title} will start in 30 minutes"
            }
            events.append(Event(cfg))
            
    return Calendar(events)

def main():
    parser = argparse.ArgumentParser(description="Fetch XJTLU e-Bridge Timetable via Hash or File and convert to ICS format")
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--id", help="The hash ID of your timetable (e.g., 5F5...)")
    group.add_argument("-f", "--file", help="Path to a local timetable JSON file")
    
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
        
    items = []
    if args.id:
        url = f"https://timetableplus.xjtlu.edu.cn/ptapi/api/enrollment/hash/{args.id}/activity"
        try:
            import urllib.request
            import urllib.error
            import ssl
            
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, context=ctx) as response:
                data = response.read().decode('utf-8')
                items = json.loads(data)
        except urllib.error.URLError as e:
            print(f"Error fetching data from API: {e}")
            sys.exit(1)
        except json.JSONDecodeError:
            print("Error: Failed to parse JSON response from the API.")
            sys.exit(1)
    elif args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                items = json.load(f)
        except Exception as e:
            print(f"Error reading JSON from {args.file}: {e}")
            sys.exit(1)
            
    if not isinstance(items, list):
        print("Error: The top-level root of the JSON data should be a list of events.")
        sys.exit(1)
        
    calendar = gen_calendar(items, first_monday)
    
    try:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(calendar.to_string())
        print(f"Success: Generated {args.output} successfully! ({len(calendar.events)} classes mapped)")
    except Exception as e:
        print(f"Error writing to {args.output}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
