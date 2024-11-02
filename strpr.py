


import streamlit as st
import csv
from datetime import datetime

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

    def list_events(self):
        return self.events

# Streamlit app
def main():
    st.title("My TODO List")

    manager = EventManager()

    with st.sidebar:
        option = st.selectbox("Select an option", ["Add Event", "List Events"])

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

    elif option == "List Events":
        st.header("Events List")
        events = manager.list_events()
        if not events:
            st.write("No events found.")
        else:
            for idx, event in enumerate(events):
                st.write(f"[{idx}] {event.name} - {event.date} - {event.category}")

if __name__ == '__main__':
    main()


