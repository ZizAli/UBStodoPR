import csv
from datetime import datetime, timedelta
import streamlit as st
import base64

# Function to encode an image into base64
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Class for Event and EventManager
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
        """Method to remove an event by its index."""
        if 0 <= index < len(self.events):
            self.events.pop(index)
            self.save_events()

    def filter_events(self, timeframe="today", category=""):
        now = datetime.now()
        filtered_events = []

        if timeframe == "today":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
        elif timeframe == "this_week":
            start = now - timedelta(days=now.weekday())  # Start of this week (Monday)
            end = start + timedelta(weeks=1)
        elif timeframe == "this_month":
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end = (start.replace(month=start.month % 12 + 1, day=1) if start.month < 12 else start.replace(month=1, year=start.year+1))

        # Filter events based on category and timeframe
        for event in self.events:
            if start <= event.date < end:
                if category.lower() in event.category.lower() if category else True:
                    filtered_events.append(event)

        return filtered_events

    def summarize_events(self, timeframe):
        now = datetime.now()
        summary = {}

        # Define the time range based on the selected timeframe
        if timeframe == "today":
            start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_time = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        elif timeframe == "this_week":
            start_time = now - timedelta(days=now.weekday())  # Start of this week (Monday)
            end_time = start_time + timedelta(days=6, hours=23, minutes=59, seconds=59)
        elif timeframe == "this_month":
            start_time = datetime(now.year, now.month, 1)  # First day of this month
            end_time = datetime(now.year, now.month, 1) + timedelta(days=31)  # Rough end of the month
            end_time = end_time.replace(hour=23, minute=59, second=59, microsecond=999999)

        # Filter events within the time range
        for event in self.events:
            if start_time <= event.date <= end_time:
                category = event.category
                if category not in summary:
                    summary[category] = 0
                summary[category] += 1

        return summary

# Page Functions
def show_welcome_page(image_path):
    image_path1 = "pinguin_53876-57854.jpg"
    col1, col2 = st.columns([1.5, 1])

    with col1:
        st.title("Welcome to the ToDo List App!")
        st.markdown("*Our Todolist* is **really** ***cool***.")
        st.markdown(
            ":red[Welcome to our page.] "
            ":orange[YOU can] :green[write] :blue[your daily] :violet[tasks in] "
            ":gray[different] :rainbow[ways] into the :blue-background[ TODOLIST] app."
            )
        st.markdown("Here's a bouquet &mdash; :tulip::cherry_blossom::rose::hibiscus::sunflower::blossom:")

        multi = '''
        If you want to add or view the to-do list, you can find it in the Selection Options section on the right side of the page.
        There are also options to remove, filter, and summarize.

        To start, enter your username and then click on the :red[Go to My To-Do List] button.

        At the bottom of the page, you can find a link to go :blue-background[Back to the Welcome Page].
        '''
        st.markdown(multi)
        name = st.text_input("Enter your name:")
        if st.button("Go to My ToDo List"):
            if name:
                st.session_state["name"] = name
                st.session_state["page"] = "todo"
            else:
                st.warning("Please enter your name to proceed.")

    with col2:
        encoded_image = get_base64_image(image_path1)
        st.markdown(
            f'<img src="data:image/jpg;base64,{encoded_image}" alt="Penguin" style="width:100%; height:auto;">',
            unsafe_allow_html=True,
        )

def show_todo_page(image_path):
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #CAEEED;  /* Light blue background */
        }
        </style>
        """, unsafe_allow_html=True
    )

    col1, col2 = st.columns([1.5, 1])

    with col1:
        st.subheader(f"Hello {st.session_state.get('name', 'User')}, welcome to your ToDo List!")
        manager = EventManager()

        option = st.selectbox("Select an option",
                              ["Add Event", "Remove Event", "List Events", "Filter Events", "Summarize Events"])

        if option == "Add Event":
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
            events = manager.events
            if events:
                event_names = [f"{idx}: {event.name} - {event.date.strftime('%d-%m-%Y %H:%M')} - {event.category}" for idx, event in enumerate(events)]
                event_to_remove = st.selectbox("Select an event to remove", event_names)
                index = int(event_to_remove.split(":")[0])
                if st.button("Remove Event"):
                    manager.remove_event(index)
                    st.success("Event removed successfully!")
            else:
                st.write("No events found to remove.")

        elif option == "List Events":
            events = manager.events
            if not events:
                st.write("No events found.")
            else:
                for idx, event in enumerate(events):
                    st.write(f"{idx}: {event.name} - {event.date.strftime('%d-%m-%Y %H:%M')} - {event.category}")

        elif option == "Filter Events":
            timeframe = st.selectbox("Timeframe", ["today", "this_week", "this_month"])
            category = st.text_input("Category (leave blank for all)")

            if st.button("Filter Events"):
                filtered_events = manager.filter_events(timeframe, category)
                if not filtered_events:
                    st.write("No events found for the specified criteria.")
                else:
                    for event in filtered_events:
                        st.write(f"{event.name} - {event.date.strftime('%d-%m-%Y %H:%M')} - {event.category}")

        elif option == "Summarize Events":
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

    with col2:
        encoded_image = get_base64_image(image_path)
        st.markdown(
            f'<img src="data:image/jpg;base64,{encoded_image}" alt="Penguin" style="width:100%; height:100%;">',
            unsafe_allow_html=True,
        )

def main():
    st.set_page_config(page_title="ToDo List", layout="wide")
    if "page" not in st.session_state:
        st.session_state["page"] = "welcome"

    image_path = "pinpin.jpg"
    if st.session_state["page"] == "welcome":
        show_welcome_page(image_path)
    elif st.session_state["page"] == "todo":
        show_todo_page(image_path)

if __name__ == "__main__":
    main()
