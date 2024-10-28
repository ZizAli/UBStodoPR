import csv
from enum import Enum
import os
from datetime import datetime, timedelta


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in progress"
    DONE = "done"


class TaskCategory(Enum):
    WORK = "work"
    PERSONAL = "personal"
    SOCIAL = "social"
    OTHER = "other"


class Task:
    def __init__(self, name, date, duration, comments, category: TaskCategory, status: TaskStatus):
        self.name = name
        self.date = datetime.strptime(date, "%Y-%m-%d").date()
        self.duration = int(duration)
        self.comments = comments
        self.category = category
        self.status = status

    def __repr__(self):
        return (f"[Name: {self.name}] [Date: {self.date}] [Duration: {self.duration} min] "
                f"[Comments: {self.comments}] [Category: {self.category.value}] [Status: {self.status.value}]")


class TaskManager:
    def __init__(self):
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)

    def load_tasks_from_csv(self, filename):
        self.tasks.clear()
        if os.path.exists(filename):
            with open(filename, mode='r') as file:
                reader = csv.DictReader(file)
                expected_headers = {'Name', 'Date', 'Duration', 'Comments', 'Category', 'Status'}

                if not expected_headers.issubset(reader.fieldnames):
                    print(f"Error: CSV file is missing required headers.")
                    return

                for row in reader:
                    try:
                        task = Task(
                            name=row['Name'],
                            date=row['Date'],
                            duration=row['Duration'],
                            comments=row['Comments'],
                            category=TaskCategory[row['Category'].upper()],
                            status=TaskStatus[row['Status'].upper()]
                        )
                        self.add_task(task)
                    except KeyError as e:
                        print(f"KeyError: {e}. Check that the CSV has the correct headers.")
                        break
                    except ValueError as e:
                        print(f"ValueError in parsing data: {e}. Check date format and field values.")
                        break

    def filter_tasks(self, date_range: str, category: TaskCategory = None):
        now = datetime.now().date()

        if date_range == "today":
            start_date = end_date = now
        elif date_range == "this week":
            start_date = now - timedelta(days=now.weekday())
            end_date = start_date + timedelta(days=6)
        elif date_range == "this month":
            start_date = now.replace(day=1)
            next_month = now.replace(day=28) + timedelta(days=4)
            end_date = next_month.replace(day=1) - timedelta(days=1)
        else:
            print("Invalid date range specified.")
            return []

        filtered_tasks = [
            task for task in self.tasks
            if start_date <= task.date <= end_date and (not category or task.category == category)
        ]
        return filtered_tasks

    def summarize_duration_by_category(self, date_range: str):
        filtered_tasks = self.filter_tasks(date_range)
        summary = {}
        for task in filtered_tasks:
            summary[task.category] = summary.get(task.category, 0) + task.duration
        return summary

    def edit_task(self, task_name):
        for task in self.tasks:
            if task.name == task_name:
                print(f"Editing task: {task}")
                task.name = input("Enter new task name (or press Enter to keep the same): ") or task.name
                date_input = input("Enter new task date (YYYY-MM-DD) or press Enter to keep the same: ")
                if date_input:
                    task.date = datetime.strptime(date_input, "%Y-%m-%d").date()
                duration_input = input("Enter new duration (minutes) or press Enter to keep the same: ")
                if duration_input:
                    task.duration = int(duration_input)
                task.comments = input("Enter new comments or press Enter to keep the same: ") or task.comments
                task.category = TaskIO().get_valid_enum_input("Enter new category (work/personal/social/other): ",
                                                              TaskCategory) or task.category
                task.status = TaskIO().get_valid_enum_input("Enter new status (pending/in progress/done): ",
                                                            TaskStatus) or task.status
                print(f"Task updated: {task}")
                return True
        print("Task not found.")
        return False

    def delete_task(self, task_name):
        initial_count = len(self.tasks)
        self.tasks = [task for task in self.tasks if task.name != task_name]
        if len(self.tasks) < initial_count:
            print(f"Task '{task_name}' deleted.")
            return True
        else:
            print("Task not found.")
            return False


class TaskIO:
    def get_valid_enum_input(self, prompt, enum_class):
        valid_options = [e.value for e in enum_class]
        while True:
            user_input = input(prompt).strip().lower()
            if user_input in valid_options:
                return enum_class(next(e for e in enum_class if e.value == user_input))
            print(f"Invalid input! Please choose from: {', '.join(valid_options)}.")

    def get_task_from_input(self):
        name = input("Enter task name: ").strip()
        date = input("Enter task date (YYYY-MM-DD): ").strip()
        duration = input("Enter task duration in minutes: ").strip()
        comments = input("Enter comments: ").strip()
        category = self.get_valid_enum_input("Enter category (work/personal/social/other): ", TaskCategory)
        status = self.get_valid_enum_input("Enter task status (pending/in progress/done): ", TaskStatus)
        return Task(name, date, duration, comments, category, status)

    def write_tasks_to_csv(self, tasks, filename):
        try:
            with open(filename, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Name', 'Date', 'Duration', 'Comments', 'Category', 'Status'])
                for task in tasks:
                    writer.writerow(
                        [task.name, task.date, task.duration, task.comments, task.category.value, task.status.value])
            print(f"Tasks have been saved to {filename}.")
        except Exception as e:
            print(f"Error writing to CSV: {e}")


def main():
    print("My ToDo List Project")
    task_manager = TaskManager()
    csv_file_name = 'Mytask.csv'

    task_manager.load_tasks_from_csv(csv_file_name)

    while True:
        command = input(
            "Type 'exit' to quit, 'add' to add a task, 'inspect' to inspect tasks, 'edit' to edit a task, 'delete' to delete a task: ").strip().lower()
        if command == 'exit':
            print("Exiting the program.")
            break
        elif command == 'add':
            task = TaskIO().get_task_from_input()
            task_manager.add_task(task)
            TaskIO().write_tasks_to_csv(task_manager.tasks, csv_file_name)
        elif command == 'inspect':
            task_manager.load_tasks_from_csv(csv_file_name)
            date_range = input(
                "Which time frame would you like to inspect? (today/this week/this month): ").strip().lower()
            category_input = input(
                "Enter category to filter by (work/personal/social/other or press Enter to skip): ").strip()
            category = TaskCategory[category_input.lower()] if category_input else None
            filtered_tasks = task_manager.filter_tasks(date_range, category)
            if filtered_tasks:
                for task in filtered_tasks:
                    print(task)
            else:
                print("No tasks found.")
            summary = task_manager.summarize_duration_by_category(date_range)
            for cat, duration in summary.items():
                print(f"Category: {cat.value}, Total Duration: {duration} min")
        elif command == 'edit':
            task_name = input("Enter the name of the task to edit: ").strip()
            if task_manager.edit_task(task_name):
                TaskIO().write_tasks_to_csv(task_manager.tasks, csv_file_name)
        elif command == 'delete':
            task_name = input("Enter the name of the task to delete: ").strip()
            if task_manager.delete_task(task_name):
                TaskIO().write_tasks_to_csv(task_manager.tasks, csv_file_name)


if __name__ == "__main__":
    main()
