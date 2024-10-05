tasks = []

def add_task(task):
    if task:
        tasks.append(task)
        return f"Task '{task}' added."
    else:
        return "Task cannot be empty."

def remove_task(task):
    if task in tasks:
        tasks.remove(task)
        return f"Task '{task}' removed."
    else:
        return "Task not found."

def list_tasks():
    return tasks

# Example usage
print(add_task("Buy groceries"))
print(add_task("Read a book"))
print(list_tasks())
print(remove_task("Read a book"))
print(list_tasks())