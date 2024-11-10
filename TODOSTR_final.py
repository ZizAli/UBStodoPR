import streamlit as st
import csv
from datetime import datetime, timedelta
from PIL import Image


# First page view
import streamlit as st

st.markdown("*Our Todolist* is **really** ***cool***.")
st.markdown('''
    :red[Welcome to our page. ] :orange[YOU can] :green[write] :blue[your daily] :violet[tasks in]
    :gray[different] :rainbow[ways] into the :blue-background[ TODOLIST] app.''')
st.markdown("Here's a bouquet &mdash;\
            :tulip::cherry_blossom::rose::hibiscus::sunflower::blossom:")

multi = '''If you want to add or view the to-do list, you can find it in the Selection Options section on the right side of the page. 
There are also options to remove, filter, and summarize.

To start, enter your username and then click on the :red[:blue-background[Go to My To-Do List]] button.

At the bottom of the page, you can find a link to go :blue-background[Back to the Welcome Page].

'''
st.markdown(multi)




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
                    events.append(
                        Event(row['name'], row['date'], row['comments'], row['category'], row['notifications']))
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



def show_welcome_page():
    # CSS for background image
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("file:///{st.session_state.get('background_image')}");
            background-size: cover;
            background-position: center;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title("Welcome to Our ToDo Page")
    name = st.text_input("Please add your name:")

    # Display penguin image with link
    st.markdown(
        f"""
        <a href="file:///{st.session_state.get('penguin_image')}" target="_blank">
            <img src="file:///{st.session_state.get('penguin_image')}" alt="Penguin" style="width:80px; position: absolute; top: 10px; right: 10px;">
        </a>
        """,
        unsafe_allow_html=True
    )

    if st.button("Go to My ToDo List"):
        if name:
            st.session_state["name"] = name
            st.session_state["page"] = "todo"
        else:
            st.warning("Please enter your name to proceed.")


def show_todo_page():
    st.write(f"Hello {st.session_state.get('name', 'User')}, welcome to your ToDo List!")
    manager = EventManager()

    option = st.sidebar.selectbox("Select an option",
                                  ["Add Event", "Remove Event", "List Events", "Filter Events", "Summarize Events"])

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


    if st.button("Back to Welcome Page"):
        st.session_state["page"] = "welcome"



if "page" not in st.session_state:
    st.session_state["page"] = "welcome"
if "background_image" not in st.session_state:
    st.session_state["background_image"] = "background.jpg"  # Your background image path
if "penguin_image" not in st.session_state:
    st.session_state["penguin_image"] = "D:/python/pinguin_53876-57854.jpg"  # Your penguin image path


if st.session_state["page"] == "welcome":
    show_welcome_page()
else:
    show_todo_page()