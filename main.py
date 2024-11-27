from datetime import datetime, timedelta
import csv
import base64
import streamlit as st

# Function to encode an image into base64
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Function to add background color
def add_background_color():
    st.markdown(
        """
        <style>
            body {
                background-color: #d2f5fa;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

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
                        Event(row['name'], row['date'], row['comments'], row['category'], row['notifications'])
                    )
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

    # Filter events based on timeframe and category
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

        # Filter based on category and timeframe
        for event in self.events:
            if start <= event.date < end:
                if category.lower() in event.category.lower() if category else True:
                    filtered_events.append(event)

        return filtered_events

# Page Functions
def show_welcome_page(image_path):
    image_path1 = "pinguin_53876-57854.jpg"
    col1, col2 = st.columns([1.5, 1])  # Adjust column ratio: left (text) : right (image)

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
        f"""
        <style>
        .stApp {{
            background-color: #FFFAFA;
            background-image: url("data:image/jpg;base64,{"pinguin_53876-57854.jpg"}");
            background-position: right;
            background-repeat: no-repeat;
        }}

        /* Add background color to col1 with #5bd2e3 */
        .col1-background {{
            background-color: #5bd2e3; /* Updated background color */
            padding: 20px;
            border-radius: 10px;  /* Optional: Adds rounded corners */
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns([1.5, 1])  # Left (form) and right (image)

    with col1:
        st.markdown('<div class="col1-background">',
                    unsafe_allow_html=True)  # Add custom CSS class for background color

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
                event_names = [f"{idx}: {event.name} - {event.date.strftime('%d-%m-%Y %H:%M')} - {event.category}" for
                               idx, event in enumerate(events)]
                event_to_remove = st.selectbox("Select an event to remove", event_names)
                index = int(event_to_remove.split(":")[0])
                if st.button("Remove Event"):
                    manager.events.pop(index)
                    manager.save_events()
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
                if filtered_events:
                    for event in filtered_events:
                        st.write(f"{event.name} - {event.date.strftime('%d-%m-%Y %H:%M')} - {event.category}")
                else:
                    st.write("No events match the filter criteria.")

        elif option == "Summarize Events":
            events = manager.events

            if not events:
                st.write("No events found.")
            else:
                # Count total number of events
                total_events = len(events)

                # Count events by category
                category_counts = {}
                for event in events:
                    if event.category not in category_counts:
                        category_counts[event.category] = 0
                    category_counts[event.category] += 1

                # Count events by timeframe (today, this week, this month)
                now = datetime.now()
                events_today = sum(1 for event in events if event.date.date() == now.date())
                events_this_week = sum(1 for event in events if event.date >= now - timedelta(
                    days=now.weekday()) and event.date < now - timedelta(days=now.weekday()) + timedelta(weeks=1))
                events_this_month = sum(
                    1 for event in events if event.date.month == now.month and event.date.year == now.year)

                # Display the summary
                st.write(f"Total events: {total_events}")
                st.write(f"Events today: {events_today}")
                st.write(f"Events this week: {events_this_week}")
                st.write(f"Events this month: {events_this_month}")

                st.write("Event count by category:")
                for category, count in category_counts.items():
                    st.write(f"{category}: {count}")

        if st.button("Back to Welcome Page"):
            st.session_state["page"] = "welcome"

        st.markdown('</div>', unsafe_allow_html=True)  # Close custom background div

    with col2:
        encoded_image = get_base64_image(image_path)
        st.markdown(
            f'<img src="data:image/jpg;base64,{encoded_image}" alt="Penguin" style="width:100%; height:auto;">',
            unsafe_allow_html=True,
        )


# Main App Logic
def main():
    st.set_page_config(page_title="ToDo List", layout="wide")
    if "page" not in st.session_state:
        st.session_state["page"] = "welcome"

    image_path = "pinpin.jpg"  # Update with the path to your image
    if st.session_state["page"] == "welcome":
        show_welcome_page(image_path)
    elif st.session_state["page"] == "todo":
        show_todo_page(image_path)

if __name__ == "__main__":
    main()
