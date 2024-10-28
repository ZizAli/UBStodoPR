from datetime import datetime, timedelta


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
