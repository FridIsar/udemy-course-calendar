from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from icalendar import Calendar, Event

import re

def extract_minutes(duration_str):
    # Regular expression to find hours and minutes
    pattern = re.compile(r'(?:(\d+) h )?(\d+) min|\d+ min')

    match = pattern.search(duration_str)
    if match:
        hours, minutes = match.groups()
        hours = int(hours) if hours else 0
        minutes = int(minutes) if minutes else 0
        total_minutes = hours * 60 + minutes
        return total_minutes
    else:
        return None

# Read HTML content from a file
with open('ext.html', 'r', encoding='utf-8') as file:
    html_content = file.read()

soup = BeautifulSoup(html_content, 'html.parser')

# Extract content from spans with class "section--section-title--wcp90"
title_spans = soup.find_all('span', 
class_='section--section-title--wcp90')
title_content = [span.text for span in title_spans]

# Extract content from spans with class "ud-text-sm 
# section--hidden-on-mobile--38HTe section--section-content--jXmra"
content_spans = soup.find_all('span', class_='ud-text-sm section--hidden-on-mobile--38HTe section--section-content--jXmra')
content_content = [span.text for span in content_spans]

# Extract minutes from each duration string
duration_minutes = [extract_minutes(duration) for duration in content_content]

event_data = dict(zip(title_content, duration_minutes))

initial_start_time = datetime.now().replace(hour=15, minute=0, second=0, microsecond=0)

# Create a new calendar
cal = Calendar()

# Initialize the start time
start_time = initial_start_time

# Iterate through the dictionary and create events
for event_name, duration_minutes in event_data.items():
    # Create an event
    event = Event()

    # Set the event summary (name)
    event.add('summary', event_name)

    # Set the event start and end times
    end_time = start_time + timedelta(minutes=duration_minutes)
    event.add('dtstart', start_time)
    event.add('dtend', end_time)

    # Add the event to the calendar
    cal.add_component(event)

    # Update the start time for the next event
    if duration_minutes < 50 and end_time.time() < datetime.strptime('16:40', '%H:%M').time():
        # If the duration is short and the end time is before 7:40 pm, start the next event on the same day
        start_time = end_time
    else:
        # Otherwise, start the next event on the next day at 6 pm
        start_time = (start_time + timedelta(days=1)).replace(hour=15, minute=0, second=0, microsecond=0)

# Save the calendar to a file
with open('calendar.ics', 'wb') as f:
    f.write(cal.to_ical())

print("Calendar created and saved to 'calendar.ics'")
