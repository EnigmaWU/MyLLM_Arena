import pytest

tasks = []

def add_task(task):
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
    return "Tasks cleared."

# Tests
def test_add_task():
    # Clear the tasks list before testing
    clear_tasks()
    assert add_task("Task 1") == ["Task 1"]
    assert add_task("Task 2") == ["Task 1", "Task 2"]
    assert add_task("Task 3") == ["Task 1", "Task 2", "Task 3"]

def test_remove_task():
    # Clear the tasks list and add tasks for testing
    clear_tasks()
    add_task("Task 1")
    add_task("Task 2")
    add_task("Task 3")

    # Test removing existing tasks
    assert remove_task("Task 2") == ["Task 1", "Task 3"]
    assert remove_task("Task 1") == ["Task 3"]

    # Test removing non-existent task
    assert remove_task("Task 4") == "Task not found."
    assert remove_task("Task 3") == []

def test_list_tasks():
    # Clear the tasks list before testing
    clear_tasks()

    # Test listing tasks when list is empty
    assert list_tasks() == []

    # Add tasks and test listing
    add_task("Task 1")
    add_task("Task 2")
    assert list_tasks() == ["Task 1", "Task 2"]

def test_clear_tasks():
    # Clear the tasks list before testing
    clear_tasks()

    # Add tasks for testing
    add_task("Task 1")
    add_task("Task 2")

    # Test clearing tasks
    assert clear_tasks() == "Tasks cleared."
    assert list_tasks() == []

# Additional edge case tests
def test_add_empty_task():
    # Clear the tasks list before testing
    clear_tasks()
    assert add_task("") == [""]

def test_remove_from_empty_list():
    # Clear the tasks list before testing
    clear_tasks()
    assert remove_task("Non-existent task") == "Task not found."

def test_add_duplicate_tasks():
    # Clear the tasks list before testing
    clear_tasks()
    assert add_task("Task 1") == ["Task 1"]
    assert add_task("Task 1") == ["Task 1", "Task 1"]
    assert add_task("Task 2") == ["Task 1", "Task 1", "Task 2"]


