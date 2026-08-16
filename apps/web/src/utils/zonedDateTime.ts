type DateParts = {
  year: number;
  month: number;
  day: number;
  hour: number;
  minute: number;
  second: number;
};

function partsAt(value: Date, timezone: string): DateParts {
  const entries = new Intl.DateTimeFormat("en-CA", {
    timeZone: timezone,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hourCycle: "h23",
  })
    .formatToParts(value)
    .filter((part) => part.type !== "literal")
    .map((part) => [part.type, Number(part.value)]);
  const values = Object.fromEntries(entries) as Record<string, number>;
  const part = (name: string): number => {
    const result = values[name];
    if (result === undefined) throw new Error(`Missing ${name} in zoned date.`);
    return result;
  };
  return {
    year: part("year"),
    month: part("month"),
    day: part("day"),
    hour: part("hour"),
    minute: part("minute"),
    second: part("second"),
  };
}

function offsetMinutesAt(instant: number, timezone: string): number {
  const local = partsAt(new Date(instant), timezone);
  const asUtc = Date.UTC(
    local.year,
    local.month - 1,
    local.day,
    local.hour,
    local.minute,
    local.second,
  );
  return Math.round((asUtc - instant) / 60_000);
}

function offsetText(offsetMinutes: number): string {
  const sign = offsetMinutes < 0 ? "-" : "+";
  const absolute = Math.abs(offsetMinutes);
  return `${sign}${String(Math.floor(absolute / 60)).padStart(2, "0")}:${String(absolute % 60).padStart(2, "0")}`;
}

export function localDateTimeInput(value: Date | string, timezone: string): string {
  const local = partsAt(new Date(value), timezone);
  return `${local.year}-${String(local.month).padStart(2, "0")}-${String(local.day).padStart(2, "0")}T${String(local.hour).padStart(2, "0")}:${String(local.minute).padStart(2, "0")}`;
}

export function offsetDateTime(localValue: string, timezone: string): string {
  const match = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})$/.exec(localValue);
  if (match === null) throw new Error("A local date and time is required.");
  const [, year, month, day, hour, minute] = match;
  const wallTime = Date.UTC(Number(year), Number(month) - 1, Number(day), Number(hour), Number(minute));
  let offset = offsetMinutesAt(wallTime, timezone);
  const instant = wallTime - offset * 60_000;
  offset = offsetMinutesAt(instant, timezone);
  return `${localValue}:00${offsetText(offset)}`;
}
