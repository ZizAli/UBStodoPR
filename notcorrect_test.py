import unittest


# class MyTestCase(unittest.TestCase):
#     def test_something(self):
#         self.assertEqual(True, False)  # add assertion here


import unittest
from datetime import datetime
from unittest.mock import patch, mock_open
from todostr import Event, EventManager

class TestEvent(unittest.TestCase):
    def test_event_to_dict(self):
        event = Event(
            name="Meeting",
            date=datetime(2024, 11, 22, 15, 0),
            comments="Discuss project",
            category="Work",
            notifications="Email"
        )
        expected_dict = {
            'name': "Meeting",
            'date': "22-11-2024 15:00",
            'comments': "Discuss project",
            'category': "Work",
            'notifications': "Email"
        }
        self.assertEqual(event.to_dict(), expected_dict)

class TestEventManager(unittest.TestCase):
    @patch("builtins.open", new_callable=mock_open, read_data="name,date,comments,category,notifications\n")
    def test_load_events_empty(self):
        manager = EventManager("test_events.csv")
        self.assertEqual(manager.events, [])

    @patch("builtins.open", new_callable=mock_open, read_data="name,date,comments,category,notifications\nMeeting,22-11-2024 15:00,Discuss project,Work,Email\n")
    def test_load_events_with_data(self):
        manager = EventManager("test_events.csv")
        self.assertEqual(len(manager.events), 1)
        self.assertEqual(manager.events[0].name, "Meeting")

    @patch("builtins.open", new_callable=mock_open)
    def test_save_events(self, mock_file):
        manager = EventManager("test_events.csv")
        manager.add_event(
            name="Meeting",
            date=datetime(2024, 11, 22, 15, 0),
            comments="Discuss project",
            category="Work",
            notifications="Email"
        )
        manager.save_events()
        mock_file().write.assert_called()
#
    def test_add_event(self):
        manager = EventManager()
        manager.add_event(
            name="Meeting",
            date=datetime(2024, 11, 22, 15, 0),
            comments="Discuss project",
            category="Work",
            notifications="Email"
        )
        self.assertEqual(len(manager.events), 1)
        self.assertEqual(manager.events[0].name, "Meeting")

    def test_remove_event(self):
        manager = EventManager()
        manager.add_event(
            name="Meeting",
            date=datetime(2024, 11, 22, 15, 0),
            comments="Discuss project",
            category="Work",
            notifications="Email"
        )
        manager.remove_event(0)
        self.assertEqual(len(manager.events), 0)

    def test_filter_events(self):
        manager = EventManager()
        now = datetime.now()
        manager.add_event(
            name="Today Event",
            date=now,
            comments="Today's task",
            category="Work",
            notifications="Email"
        )
        filtered_events = manager.filter_events("today")
        self.assertEqual(len(filtered_events), 1)
        self.assertEqual(filtered_events[0].name, "Today Event")

    def test_summarize_events(self):
        manager = EventManager()
        now = datetime.now()
        manager.add_event(
            name="Work Task",
            date=now,
            comments="Task details",
            category="Work",
            notifications="Email"
        )
        manager.add_event(
            name="Personal Task",
            date=now,
            comments="Personal task details",
            category="Personal",
            notifications="None"
        )
        summary = manager.summarize_events("today")
        self.assertEqual(summary.get("Work"), 1)
        self.assertEqual(summary.get("Personal"), 1)

if __name__ == "__main__":
    unittest.main()
