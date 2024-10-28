import csv
from enum import Enum
import os
from datetime import datetime, timedelta


class Weekday(Enum):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


class TimeFrame(Enum):
    TODAY = "today"
    THIS_WEEK = "this week"
    THIS_MONTH = "this month"


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in progress"
    DONE = "done"


class Severity(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TaskCategory(Enum):
    WORK = "work"
    PERSONAL = "personal"
    SOCIAL = "social"
    OTHER = "other"


class Task:
    def __init__(self, description, severity, deadline: Weekday, time_frame: TimeFrame, category: TaskCategory,
                 status: TaskStatus):
        self.description = description
        self.severity = severity
        self.deadline = deadline
        self.time_frame = time_frame
        self.category = category
        self.status = status
        self.deadline_date = self.calculate_deadline_date()

    def calculate_deadline_date(self):
        today = datetime.now()
        weekday_index = list(Weekday).index(self.deadline)
        days_until_deadline = (weekday_index - today.weekday()) % 7
        deadline_date = today + timedelta(days=days_until_deadline)
        return deadline_date

    def is_due(self):
        return self.deadline_date >= datetime.now()

    def __repr__(self):
        return (f"[Description: {self.description}] [Severity: {self.severity.value}] "
                f"[Deadline: {self.deadline_date.strftime('%Y-%m-%d')}] [Time Frame: {self.time_frame.value}] "
                f"[Category: {self.category.value}] [Status: {self.status.value}]")


class TaskManager:
    def __init__(self):
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)

    def load_tasks_from_csv(self, filename):
       #program is not loading from csv file
        self.tasks.clear()
        if os.path.exists(filename):
            with open(filename, mode='r') as file:
                reader = csv.DictReader(file)
                if reader.fieldnames != ['Description', 'Severity', 'Deadline (Weekday)', 'Time Frame', 'Category',
                                         'Status']:
                    print("Error: CSV file has incorrect headers.")
                    return
                for row in reader:
                    try:
                        task = Task(
                            description=row['Description'],
                            severity=Severity[row['Severity'].upper()],
                            deadline=Weekday[row['Deadline (Weekday)'].upper()],
                            time_frame=TimeFrame[row['Time Frame'].upper()],
                            category=TaskCategory[row['Category'].upper()],
                            status=TaskStatus[row['Status'].upper()]
                        )
                        self.add_task(task)
                    except KeyError as e:
                        print(f"KeyError: {e}. Check that the CSV has the correct headers.")
                        break

    def filter_tasks(self, time_frame: TimeFrame, category: TaskCategory = None):
        now = datetime.now()
        filtered_tasks = []

        for task in self.tasks:
            if category and task.category != category:
                continue

            if time_frame == TimeFrame.TODAY:
                if task.is_due() and task.deadline_date.date() == now.date():
                    filtered_tasks.append(task)
            elif time_frame == TimeFrame.THIS_WEEK:
                if task.is_due() and now.date() <= task.deadline_date.date() < (now + timedelta(days=7)).date():
                    filtered_tasks.append(task)
            elif time_frame == TimeFrame.THIS_MONTH:
                if task.is_due() and task.deadline_date.month == now.month:
                    filtered_tasks.append(task)

        return filtered_tasks

    def summarize_status(self):
        summary = {status: 0 for status in TaskStatus}
        for task in self.tasks:
            summary[task.status] += 1
        return summary


class TaskIO:
    def get_valid_enum_input(self, prompt, enum_class):
        valid_options = [e.value for e in enum_class]
        while True:
            user_input = input(prompt).strip().lower()
            if user_input in valid_options:
                return enum_class(next(e for e in enum_class if e.value == user_input))
            print(f"Invalid input! Please choose from: {', '.join(valid_options)}.")

    def get_task_from_input(self):
        description = input("Please add task description: ").strip()
        severity = self.get_valid_enum_input("Please add severity (high/medium/low): ", Severity)
        deadline = self.get_valid_enum_input("Please add the deadline (weekday): ", Weekday)
        time_frame = self.get_valid_enum_input("Please add the time frame (today/this week/this month): ", TimeFrame)
        category = self.get_valid_enum_input("Please add the category (work/personal/social/other): ", TaskCategory)
        status = self.get_valid_enum_input("Please add the task status (pending/in progress/done): ", TaskStatus)

        return Task(description, severity, deadline, time_frame, category, status)

    def write_tasks_to_csv(self, tasks, filename):
        file_exists = os.path.exists(filename)
        try:
            with open(filename, mode='a', newline='') as file:
                writer = csv.writer(file)
                if not file_exists:
                    writer.writerow(
                        ['Description', 'Severity', 'Deadline (Weekday)', 'Time Frame', 'Category', 'Status'])
                for task in tasks:
                    writer.writerow([task.description, task.severity.value, task.deadline.value,
                                     task.time_frame.value, task.category.value, task.status.value])
            print(f"Tasks have been appended to {filename}.")
        except Exception as e:
            print(f"Error writing to CSV: {e}")


def main():
    print("My ToDo List Project")
    task_manager = TaskManager()
    csv_file_name = 'Mytask.csv'
    task_manager.load_tasks_from_csv(csv_file_name)

    while True:
        command = input("Type 'exit' to quit or press Enter to continue: ").strip().lower()
        if command == 'exit':
            print("Exiting the program.")
            break

        task = TaskIO().get_task_from_input()
        task_manager.add_task(task)
        TaskIO().write_tasks_to_csv([task], csv_file_name)

        task_manager.load_tasks_from_csv(csv_file_name)

        time_frame = TaskIO().get_valid_enum_input(
            "Which time frame would you like to inspect? (today/this week/this month): ", TimeFrame)
        category_input = input(
            "Enter category to filter by (work/personal/social/other or press Enter to skip): ").strip()
        category = None
        if category_input:
            try:
                category = TaskCategory[category_input.upper()]
            except KeyError:
                print(
                    f"Invalid category '{category_input}'. Please enter a valid category (work/personal/social/other).")

        filtered_tasks = task_manager.filter_tasks(time_frame, category)
        if filtered_tasks:
            print(f"Tasks for {time_frame.value}{' in category: ' + category.value if category else ''}:")
            for task in filtered_tasks:
                print(task)
        else:
            print(f"No tasks found for {time_frame.value}{' in category: ' + (category.value if category else 'N/A')}.")

        summary = task_manager.summarize_status()
        print("Status Summary:")
        for status, count in summary.items():
            print(f"Status: {status.value}, Count: {count}")


if __name__ == "__main__":
    main()
