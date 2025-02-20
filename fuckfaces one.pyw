import os
import time
import subprocess
from datetime import datetime, timedelta
from plyer import notification
import keyboard
import threading

# Define the start of Week A (Change this to your actual start date)
WEEK_A_START = datetime(2025, 2, 4)

# File paths
HOME_DIR = os.path.expanduser("~")
SCHEDULE_FILE = os.path.join(HOME_DIR, "todays_schedule.txt")
TRACK_FILE = os.path.join(HOME_DIR, ".daily_notif")

# Period start times (Adjusted for 5-minute early notifications)
PERIOD_TIMES = [
    ("08:50", "Period 1"), ("09:35", "Period 2"), ("10:20", "Period 3"), ("11:05", "Recess"),
    ("11:30", "Period 4"), ("12:15", "Period 5"), ("13:00", "Lunch"),
    ("13:45", "Period 6"), ("14:30", "Period 7"), ("15:15", "End")
]

# Timetable with periods including Lunch and Recess
TIMETABLE = {
    "Week A": {
        "Monday": ["Maths", "PDHPE", "PDHPE", "Recess", "History", "Chapel", "Lunch", "French", "Music"],
        "Tuesday": ["PDHPE", "English", "French", "Recess", "Team Meeting", "Tech", "Lunch", "Tech", "Music"],
        "Wednesday": ["Art", "Maths", "Tech", "Recess", "Science", "Christian Studies", "Lunch", "English", "French"],
        "Thursday": ["French", "Math", "Science", "Recess", "Active Afternoons", "Active Afternoons", "Lunch", "English", "History"],
        "Friday": ["Tech", "History", "Art", "Recess", "Englis", "Science", "Lunch", "History", "Maths"],
    },
    "Week B": {
        "Monday": ["Science", "Tech", "French", "Recess", "History", "Chapel", "Lunch", "English", "Maths"],
        "Tuesday": ["PDHPE", "English", "Assembly", "Recess", "Art", "Science", "Lunch", "Tech", "Music"],
        "Wednesday": ["Maths", "Music", "Wellbeing", "Recess", "Tech", "Tech", "Lunch", "French", "Christian Studies"],
        "Thursday": ["Maths", "Science", "English", "Recess", "Active Afternoons", "Active Afternoons", "Lunch", "History", "PDHPE"],
        "Friday": ["History", "French", "Science", "Recess", "Maths", "English", "Lunch", "History", "Art"],
    },
}



def get_week_type():
    """Determine if it's Week A or Week B."""
    today = datetime.today()
    delta_weeks = (today - WEEK_A_START).days // 7
    return "Week A" if delta_weeks % 2 == 0 else "Week B"

def get_todays_schedule():
    """Get today's subjects and period times."""
    week_type = get_week_type()
    weekday = datetime.today().strftime("%A")
    subjects = TIMETABLE.get(week_type, {}).get(weekday, ["No classes today"])

    # Pair subjects with period times
    return list(zip(PERIOD_TIMES, subjects))

def save_todays_schedule():
    """Save today's schedule to a text file."""
    today_schedule = get_todays_schedule()
    schedule_text = f"Timetable for {datetime.today().strftime('%A')} ({get_week_type()}):\n\n"
    schedule_text += "\n".join([f"{period[1]} - {subject}" for period, subject in today_schedule])

    with open(SCHEDULE_FILE, "w") as file:
        file.write(schedule_text)

def open_schedule_file():
    """Open the schedule file in the default text editor."""
    if os.name == "nt":  # Windows
        os.startfile(SCHEDULE_FILE)
    else:  # Mac/Linux
        subprocess.call(["xdg-open", SCHEDULE_FILE])

def has_notified_today():
    """Check if the morning notification has already been sent."""
    if os.path.exists(TRACK_FILE):
        with open(TRACK_FILE, "r") as file:
            last_date = file.read().strip()
        return last_date == datetime.today().strftime("%Y-%m-%d")
    return False

def mark_as_notified():
    """Mark the day as notified."""
    with open(TRACK_FILE, "w") as file:
        file.write(datetime.today().strftime("%Y-%m-%d"))

def show_morning_notification():
    """Show a notification with the full day's schedule."""
    if not has_notified_today():
        save_todays_schedule()
        week_type = get_week_type()
        today_schedule = get_todays_schedule()
        schedule_text = "\n".join([f"{period[1]} - {subject}" for period, subject in today_schedule])

        notification.notify(
            title=f"Good morning! {week_type} - {datetime.today().strftime('%A')}",
            message=f"Click to view your full schedule.\n\n{schedule_text}",
            app_name="Timetable Notifier",
            timeout=10  # Keeps the notification visible for 10 seconds
        )

        # Open the schedule file when the notification is clicked
        time.sleep(10)  # Wait to allow the user to click
        open_schedule_file()
        mark_as_notified()

def show_period_notification(period_name, subject):
    """Send a notification 5 minutes before a period starts."""
    notification.notify(
        title=f"{period_name} in 5 minutes!",
        message=f"Get ready for {subject}",
        app_name="Timetable Notifier"
    )

from datetime import datetime, timedelta

def get_next_period():
    now = datetime.now()  # Current datetime
    today = now.strftime('%A')
    week_type = get_week_type()
    periods_subjects = TIMETABLE.get(week_type, {}).get(today, [])

    # Convert each period start time to a datetime object for today and add 5 minutes
    period_starts = []
    for start_time, period_name in PERIOD_TIMES:
        # Parse the time (e.g., "08:50") and set the date to today
        dt = datetime.strptime(start_time, '%H:%M').replace(year=now.year, month=now.month, day=now.day)
        dt += timedelta(minutes=5)  # Add 5 minutes to the start time
        period_starts.append((dt, period_name))

    # Define the duration of a period (adjust if needed)
    period_duration = timedelta(minutes=45)
    # Create list of period end times
    period_ends = [(dt + period_duration) for dt, _ in period_starts]

    # Check if we're currently in a period
    for i, ((start_dt, period_name), end_dt) in enumerate(zip(period_starts, period_ends)):
        print(f"Checking period: {period_name} ({start_dt.strftime('%H:%M')} - {end_dt.strftime('%H:%M')})")
        if start_dt <= now < end_dt:
            # We are currently in period i.
            if i + 1 < len(period_starts):
                next_start_dt, next_period_name = period_starts[i + 1]
                subject = periods_subjects[i] if i < len(periods_subjects) else "No subject"
                print(f"Currently in {period_name}, next is {next_period_name} at {next_start_dt.strftime('%H:%M')}")
                return period_name, subject, next_start_dt.strftime('%H:%M')
            else:
                print("End of the day reached.")
                return "No more periods today!", None, None

    # If we're not currently in any period, find the next upcoming period
    for i, (start_dt, period_name) in enumerate(period_starts):
        if now < start_dt:
            subject = periods_subjects[i] if i < len(periods_subjects) else "No subject"
            return period_name, subject, start_dt.strftime('%H:%M')

    return None, None, None


# Listen for 'timetable' and send notification
def on_time_typed():
    """Triggered when 'time' is typed."""
    next_period, subject, start_time = get_next_period()
    if next_period:
        # Send notification
        notification.notify(
            title="Next Period Notification",
            message=f"Next period: {next_period}, Subject: {subject}, Starts at: {start_time}",
            app_name="Timetable Notifier"
        )
    else:
        notification.notify(
            title="No More Periods",
            message="No more periods left today.",
            app_name="Timetable Notifier"
        )


# Send morning notification (if not already sent)
show_morning_notification()

# Then start listening for the word 'timetable'
keyboard.add_word_listener('timetable', on_time_typed)
keyboard.wait()

