import streamlit as st
import csv
from datetime import datetime, timedelta

# Define Event and EventManager classes
class Event:
    def __init__(self, name, date, comments, category, notifications):
        self.name = name
        self.date = date
        self.comments = comments
        self.category = category
        self.notifications = notifications

    def to_dict(self):
        return {
            'name': self.name,
            'date': self.date.strftime('%d-%m-%Y %H:%M'),
            'comments': self.comments,
            'category': self.category,
            'notifications': self.notifications
        }

class EventManager:
    def __init__(self, filename='events.csv'):
        self.filename = filename
        self.events = self.load_events()

    def load_events(self):
        events = []
        try:
            with open(self.filename, mode='r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    row['date'] = datetime.strptime(row['date'], '%d-%m-%Y %H:%M')
                    events.append(Event(row['name'], row['date'], row['comments'], row['category'], row['notifications']))
        except FileNotFoundError:
            pass
        return events

    def save_events(self):
        with open(self.filename, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['name', 'date', 'comments', 'category', 'notifications'])
            writer.writeheader()
            for event in self.events:
                writer.writerow(event.to_dict())

    def add_event(self, name, date, comments, category, notifications):
        event = Event(name, date, comments, category, notifications)
        self.events.append(event)
        self.save_events()

    def remove_event(self, index):
        if 0 <= index < len(self.events):
            del self.events[index]
            self.save_events()

    def filter_events(self, timeframe, category=None):
        now = datetime.now()
        if timeframe == 'today':
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = now.replace(hour=23, minute=59, second=59)
        elif timeframe == 'this_week':
            start = now - timedelta(days=now.weekday())
            end = start + timedelta(days=6, hours=23, minutes=59, seconds=59)
        elif timeframe == 'this_month':
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end = (start + timedelta(days=31)).replace(day=1) - timedelta(seconds=1)
        else:
            return []

        filtered_events = [event for event in self.events if start <= event.date <= end]
        return [event for event in filtered_events if event.category == category] if category else filtered_events

    def summarize_events(self, timeframe):
        now = datetime.now()
        if timeframe == 'today':
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = now.replace(hour=23, minute=59, second=59)
        elif timeframe == 'this_week':
            start = now - timedelta(days=now.weekday())
            end = start + timedelta(days=6, hours=23, minutes=59, seconds=59)
        elif timeframe == 'this_month':
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end = (start + timedelta(days=31)).replace(day=1) - timedelta(seconds=1)
        else:
            return {}

        summary = {}
        for event in self.events:
            if start <= event.date <= end:
                summary[event.category] = summary.get(event.category, 0) + 1

        return summary

# Streamlit pages
def show_welcome_page():
    st.title("Welcome to Our ToDo Page")
    name = st.text_input("Please add your name:")
    if st.button("Go to My ToDo List"):
        if name:
            st.session_state["name"] = name
            st.session_state["page"] = "todo"
        else:
            st.warning("Please enter your name to proceed.")

def show_todo_page():
    st.write(f"Hello {st.session_state['name']}, welcome to your ToDo List!")
    manager = EventManager()

    option = st.sidebar.selectbox("Select an option", ["Add Event", "Remove Event", "List Events", "Filter Events", "Summarize Events"])

    if option == "Add Event":
        st.header("Add a New Event")
        name = st.text_input("Event Name")
        date = st.date_input("Event Date")
        time = st.time_input("Event Time")
        comments = st.text_input("Comments")
        category = st.text_input("Category")
        notifications = st.text_input("Notifications")

        if st.button("Add Event"):
            event_date = datetime.combine(date, time)
            manager.add_event(name, event_date, comments, category, notifications)
            st.success("Event added successfully!")

    elif option == "Remove Event":
        st.header("Remove an Event")
        events = manager.events
        if events:
            event_names = [f"{idx}: {event.name} - {event.date} - {event.category}" for idx, event in enumerate(events)]
            event_to_remove = st.selectbox("Select an event to remove", event_names)
            index = int(event_to_remove.split(":")[0])
            if st.button("Remove Event"):
                manager.remove_event(index)
                st.success("Event removed successfully!")
        else:
            st.write("No events found to remove.")

    elif option == "List Events":
        st.header("Events List")
        events = manager.events
        if not events:
            st.write("No events found.")
        else:
            for idx, event in enumerate(events):
                st.write(f"{idx}: {event.name} - {event.date} - {event.category}")

    elif option == "Filter Events":
        st.header("Filter Events")
        timeframe = st.selectbox("Timeframe", ["today", "this_week", "this_month"])
        category = st.text_input("Category (leave blank for all)")

        if st.button("Filter Events"):
            filtered_events = manager.filter_events(timeframe, category)
            if not filtered_events:
                st.write("No events found for the specified criteria.")
            else:
                for event in filtered_events:
                    st.write(f"{event.name} - {event.date} - {event.category}")

    elif option == "Summarize Events":
        st.header("Summarize Events")
        timeframe = st.selectbox("Timeframe", ["today", "this_week", "this_month"])

        if st.button("Summarize Events"):
            summary = manager.summarize_events(timeframe)
            if not summary:
                st.write("No events found for the specified timeframe.")
            else:
                for category, count in summary.items():
                    st.write(f"{category}: {count} event(s)")

    # Add a button to go back to the welcome page
    if st.button("Back to Welcome Page"):
        st.session_state["page"] = "welcome"

# Initialize session state for page navigation and name
if "page" not in st.session_state:
    st.session_state["page"] = "welcome"

# Display pages based on the current page state
if st.session_state["page"] == "welcome":
    show_welcome_page()
else:
    show_todo_page()
