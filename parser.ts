import { Day, HTMLDocument } from "./deps.ts";

export const DAYS: Day[] = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"];

export function parseTimetable(document: HTMLDocument) {
  const customDays: Day[] = [];

  const lessonDict: { [title: string]: Lesson } = {};

  const table = document.querySelector(".timetable")!;
  const thead = table.querySelector("thead")!;
  const tbody = table.querySelector("tbody")!;

  // Parse header row to get day columns
  const headerRow = thead.querySelector("tr")!;
  for (const cell of headerRow.children) {
    const day = cell.textContent.trim().slice(0, 2).toUpperCase() as Day;
    const colSpan = cell.getAttribute("colspan") ?? "1";
    let i = parseInt(colSpan);
    do {
      customDays.push(day);
    } while (--i);
  }

  // Walk through every body row
  const rows = tbody.children;

  for (let row_i = 0; row_i < rows.length; ++row_i) {
    const row = rows[row_i];

    // Time will be set later
    let time = "";

    const cells = row.children;

    for (let col_i = 0; col_i < cells.length; ++col_i) {
      const cell = cells[col_i];

      // Get start time from time-cell
      if (cell.className.includes("time-cell")) {
        time = cell.textContent.trim();
        continue;
      }

      // Use data-day attribute to determine the day of week
      const dayAttr = cell.getAttribute("data-day");
      if (!dayAttr) continue;
      const day = dayAttr.slice(0, 2).toUpperCase() as Day;

      // Handle lesson cells that contain an event
      const eventDiv = cell.querySelector(".event");
      if (eventDiv) {
        const nameDiv = eventDiv.querySelector(".event-name");
        const infoDivs = eventDiv.querySelectorAll(".event-info");

        if (nameDiv && infoDivs.length >= 3) {
          const title = nameDiv.textContent.trim();

          // Parse time range from the last event-info (e.g. "09:00 - 10:50")
          const timeInfo = infoDivs[infoDivs.length - 1].textContent.trim();
          const timeMatch = timeInfo.match(/(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})/);
          const startTime = timeMatch ? timeMatch[1] : time;
          const endTime = timeMatch ? timeMatch[2] : time;

          const lessonRef = lessonDict[title];

          if (lessonRef === undefined) {
            const lesson: Lesson = {
              teachers: infoDivs[0].textContent.trim(),
              location: infoDivs[1].textContent.trim(),
              weeks: infoDivs[2].textContent.trim(),
              day,
              startTime,
              endTime,
            };
            lessonDict[title] = lesson;
          }
        }
      }
    }
  }

  return lessonDict;
}

export type Lesson = {
  teachers: string;
  location: string;
  weeks: string;
  day: Day;
  startTime: string;
  endTime: string;
};
