import csv
from datetime import datetime, timedelta


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

    def edit_event(self, index, **kwargs):
        for key, value in kwargs.items():
            if value is not None:
                setattr(self.events[index], key, value)
        self.save_events()

    def remove_event(self, index):
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

    def list_events(self):
        return self.events


def main():
    manager = EventManager()

    while True:
        print("\nOptions: add, edit, remove, list, filter, exit")
        option = input("Choose an option: ").strip().lower()

        if option == 'add':
            name = input("Event name: ")
            date_str = input("Event date (DD-MM-YYYY HH:MM): ")
            try:
                date = datetime.strptime(date_str, '%d-%m-%Y %H:%M')
            except ValueError:
                print("Invalid date format. Please try again.")
                continue
            comments = input("Comments: ")
            category = input("Category: ")
            notifications = input("Notifications: ")
            manager.add_event(name, date, comments, category, notifications)

        elif option == 'edit':
            index = int(input("Event index to edit: "))
            if index < 0 or index >= len(manager.events):
                print("Invalid index. Please try again.")
                continue

            name = input("New event name (leave blank for no change): ") or None
            date_str = input("New event date (leave blank for no change, DD-MM-YYYY HH:MM): ")
            date = datetime.strptime(date_str, '%d-%m-%Y %H:%M') if date_str else None
            comments = input("New comments (leave blank for no change): ") or None
            category = input("New category (leave blank for no change): ") or None
            notifications = input("New notifications (leave blank for no change): ") or None
            manager.edit_event(index, name=name, date=date, comments=comments, category=category,
                               notifications=notifications)

        elif option == 'remove':
            index = int(input("Event index to remove: "))
            if index < 0 or index >= len(manager.events):
                print("Invalid index. Please try again.")
                continue
            manager.remove_event(index)

        elif option == 'list':
            events = manager.list_events()
            if not events:
                print("No events found.")
            else:
                for idx, event in enumerate(events):
                    print(f"[{idx}] {event.name} - {event.date} - {event.category}")

        elif option == 'filter':
            while True:
                timeframe = input("Timeframe (today, this_week, this_month): ").strip().lower()
                category = input("Category (leave blank for all): ").strip()

                if timeframe in ['today', 'this_week', 'this_month']:
                    events = manager.filter_events(timeframe, category or None)
                    if not events:
                        print("No events found for the specified criteria.")
                    else:
                        for event in events:
                            print(f"{event.name} - {event.date} - {event.category}")
                    break
                else:
                    print("Invalid timeframe. Please try again.")

        elif option == 'exit':
            break


if __name__ == '__main__':
    main()
