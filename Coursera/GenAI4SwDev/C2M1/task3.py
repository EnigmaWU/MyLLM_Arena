tasks = []

def add_task(task):
    if not task:
      raise ValueError("Task cannot be empty.")
    else:
      tasks.append(task)
    return tasks

def remove_task(task):
    if task in tasks:
        tasks.remove(task)
        return tasks
    else:
        return "Task not found."

def list_tasks():
    return tasks

def clear_tasks():
    tasks.clear()
    print(tasks)
    return "Tasks cleared."