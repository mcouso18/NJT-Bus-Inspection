import sys
import os
import json
import datetime

# Add parent directory to path to import InteractivePrompt
parent_dir = os.path.dirname(os.getcwd())
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from interactive_prompt import InteractivePrompt

class TaskManager:
    def __init__(self, file_path="tasks.json"):
        self.file_path = file_path
        self.tasks = self.load_tasks()
    
    def load_tasks(self):
        """Load tasks from JSON file"""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Error reading {self.file_path}. Starting with empty task list.")
                return []
        return []
    
    def save_tasks(self):
        """Save tasks to JSON file"""
        with open(self.file_path, 'w') as f:
            json.dump(self.tasks, f, indent=2)
    
    def add_task(self, title, description="", due_date=None, priority="medium"):
        """Add a new task"""
        task = {
            "id": len(self.tasks) + 1,
            "title": title,
            "description": description,
            "created_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "due_date": due_date,
            "priority": priority,
            "completed": False
        }
        self.tasks.append(task)
        self.save_tasks()
        return task
    
    def list_tasks(self, show_completed=False):
        """List all tasks"""
        result = []
        for task in self.tasks:
            if show_completed or not task["completed"]:
                result.append(task)
        return result
    
    def complete_task(self, task_id):
        """Mark a task as completed"""
        for task in self.tasks:
            if task["id"] == task_id:
                task["completed"] = True
                self.save_tasks()
                return True
        return False
    
    def delete_task(self, task_id):
        """Delete a task"""
        for i, task in enumerate(self.tasks):
            if task["id"] == task_id:
                del self.tasks[i]
                self.save_tasks()
                return True
        return False

def format_task_list(tasks):
    """Format tasks for display"""
    if not tasks:
        return "No tasks found."
    
    result = []
    for task in tasks:
        status = "✓" if task["completed"] else "□"
        priority_symbol = {
            "high": "🔴",
            "medium": "🟡",
            "low": "🟢"
        }.get(task["priority"].lower(), "⚪")
        
        due_date = task.get("due_date", "No due date")
        result.append(f"{task['id']}. {status} {priority_symbol} {task['title']} (Due: {due_date})")
    
    return "\n".join(result)

def main():
    print("Starting Task Manager...")
    
    # Initialize the task manager
    task_manager = TaskManager(os.path.join(os.getcwd(), "workspace", "tasks.json"))
    
    # Create the prompt window
    prompt = InteractivePrompt()
    
    while True:
        # Display menu
        menu = """
Task Manager
------------
1. List tasks
2. Add new task
3. Complete task
4. Delete task
5. Exit
"""
        choice = prompt.get_input(menu + "\nEnter your choice (1-5):")
        
        if choice == "1":
            # List tasks
            show_completed = prompt.get_input("Show completed tasks? (y/n):").lower() == "y"
            tasks = task_manager.list_tasks(show_completed)
            prompt.get_input(format_task_list(tasks) + "\n\nPress Enter to continue...")
        
        elif choice == "2":
            # Add new task
            title = prompt.get_input("Enter task title:")
            description = prompt.get_input("Enter task description (optional):")
            due_date = prompt.get_input("Enter due date (YYYY-MM-DD) or leave blank:")
            priority = prompt.get_input("Enter priority (high/medium/low):")
            
            if not due_date:
                due_date = None
                
            task = task_manager.add_task(title, description, due_date, priority)
            prompt.get_input(f"Task added: {task['title']}\n\nPress Enter to continue...")
        
        elif choice == "3":
            # Complete task
            tasks = task_manager.list_tasks(False)
            prompt.get_input(format_task_list(tasks) + "\n\nPress Enter to continue...")
            
            task_id = prompt.get_input("Enter the ID of the task to mark as completed:")
            try:
                task_id = int(task_id)
                if task_manager.complete_task(task_id):
                    prompt.get_input("Task marked as completed!\n\nPress Enter to continue...")
                else:
                    prompt.get_input("Task not found.\n\nPress Enter to continue...")
            except ValueError:
                prompt.get_input("Invalid task ID.\n\nPress Enter to continue...")
        
        elif choice == "4":
            # Delete task
            tasks = task_manager.list_tasks(True)
            prompt.get_input(format_task_list(tasks) + "\n\nPress Enter to continue...")
            
            task_id = prompt.get_input("Enter the ID of the task to delete:")
            try:
                task_id = int(task_id)
                if task_manager.delete_task(task_id):
                    prompt.get_input("Task deleted!\n\nPress Enter to continue...")
                else:
                    prompt.get_input("Task not found.\n\nPress Enter to continue...")
            except ValueError:
                prompt.get_input("Invalid task ID.\n\nPress Enter to continue...")
        
        elif choice == "5":
            # Exit
            break
        
        else:
            prompt.get_input("Invalid choice. Press Enter to try again...")
    
    # Close the window
    prompt.close()
    print("Task Manager closed.")

if __name__ == "__main__":
    main()