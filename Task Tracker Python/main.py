import argparse
import json
import pathlib
import shutil
from typing import List, Dict

class Task:
    def __init__(self, description: str, completed: bool = False):
        self.description = description
        self.completed = completed

    def to_dict(self) -> Dict:
        return {"description": self.description, "completed": self.completed}

    @classmethod
    def from_dict(cls, data: Dict):
        return cls(description=data["description"], completed=data.get("completed", False))

    def __str__(self):
        status = "✓" if self.completed else "☐"
        return f"{status} {self.description}"

class TaskTracker:
    def __init__(self):
        self.tasks_file = pathlib.Path(__file__).parent / "tasks.json"
        self.tasks: List[Task] = self.load_tasks()

    def load_tasks(self) -> List[Task]:
        if not self.tasks_file.exists():
            self.tasks_file.parent.mkdir(parents=True, exist_ok=True)
            self.save_tasks()
            return []
        
        if not self.tasks_file.is_file():
            print(f"Warning: {self.tasks_file} exists but is not a file. Creating new tasks file.")
            self.save_tasks()
            return []
        
        try:
            with open(self.tasks_file, "r") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return [Task.from_dict(item) for item in data]
                else:
                    print(f"Warning: Invalid format in tasks file. Expected list, got {type(data)}. Creating backup.")
                    self.create_backup()
                    return []
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"Error loading tasks file: {e}. Creating backup.")
            self.create_backup()
            return []

    def create_backup(self):
        backup_path = self.tasks_file.with_suffix('.bak')
        try:
            shutil.copy2(self.tasks_file, backup_path)
            print(f"Created backup of corrupted file: {backup_path}")
        except Exception as e:
            print(f"Failed to create backup: {e}")

    def save_tasks(self):
        try:
            with open(self.tasks_file, "w") as f:
                json.dump([task.to_dict() for task in self.tasks], f, indent=4)
        except IOError as e:
            print(f"Error saving tasks: {e}")
        except Exception as e:
            print(f"Unexpected error saving tasks: {e}")

    def add_task(self, description: str):
        if not description.strip():
            print("Error: Task description cannot be empty.")
            return
        task = Task(description.strip())
        self.tasks.append(task)
        self.save_tasks()
        print(f"Task added: {task}")

    def list_tasks(self):
        if not self.tasks:
            print("No tasks found.")
            return
        
        print("\nYour Tasks:")
        print("-" * 40)
        for i, task in enumerate(self.tasks, 1):
            print(f"{i}. {task}")
        print("-" * 40)

    def complete_task(self, task_index: int):
        if not self.tasks:
            print("No tasks found.")
            return
        if task_index < 1 or task_index > len(self.tasks):
            print(f"Error: Invalid task index. Please choose a number between 1 and {len(self.tasks)}.")
            return
        self.tasks[task_index - 1].completed = True
        self.save_tasks()
        print(f"Task {task_index} marked as completed: {self.tasks[task_index - 1]}")

    def remove_task(self, task_index: int):
        if not self.tasks:
            print("No tasks found.")
            return
        if task_index < 1 or task_index > len(self.tasks):
            print(f"Error: Invalid task index. Please choose a number between 1 and {len(self.tasks)}.")
            return
        removed_task = self.tasks.pop(task_index - 1)
        self.save_tasks()
        print(f"Task removed: {removed_task}")

    def in_progress_tasks(self):
        if not self.tasks:
            print("No tasks found.")
            return
        
        print("\nIn Progress Tasks:")
        print("-" * 40)
        for i, task in enumerate(self.tasks, 1):
            if not task.completed:
                print(f"{i}. {task}")
        print("-" * 40)

def main():
    parser = argparse.ArgumentParser(description="Simple Task Tracker")
    parser.add_argument("-a", "--add", type=str, help="Add a new task")
    parser.add_argument("-l", "--list", action="store_true", help="List all tasks")
    parser.add_argument("-c", "--complete", type=int, help="Complete a task by index")
    parser.add_argument("-r", "--remove", type=int, help="Remove a task by index")
    parser.add_argument("-i", "--in-progress", action="store_true", help="List in progress tasks")
    args = parser.parse_args()

    try:
        task_tracker = TaskTracker()
    except Exception as e:
        print(f"Critical error initializing task tracker: {e}")
        print("Please check your tasks file or try running with different permissions.")
        return

    if args.add:
        task_tracker.add_task(args.add)
    elif args.list:
        task_tracker.list_tasks()
    elif args.complete is not None:
        task_tracker.complete_task(args.complete)
    elif args.remove is not None:
        task_tracker.remove_task(args.remove)
    elif args.in_progress:
        task_tracker.in_progress_tasks()
    else:
        parser.print_help()

if  __name__ == "__main__":
    main()