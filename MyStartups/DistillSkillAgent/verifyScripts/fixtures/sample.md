# Sample Markdown Document

This is a sample markdown document for testing myDistillSkillAgent.

## Clean Code Principles

Clean code is code that is easy to read, understand, and maintain.

### Meaningful Names

Use intention-revealing names. Choose names that express what the variable, function, or class does.

**Steps:**
1. Use pronounceable names
2. Use searchable names
3. Avoid mental mapping
4. Don't add gratuitous context

**Why:** Names are everywhere in software. We should take care with them.

### Functions Should Do One Thing

Functions should do one thing. They should do it well. They should do it only.

**Steps:**
1. Extract until you can't extract anymore
2. Keep functions small (less than 20 lines)
3. One level of abstraction per function

**Example:**
```python
# Bad
def process_user_data(user):
    validate_user(user)
    save_to_database(user)
    send_email(user)

# Good - separate concerns
def register_user(user):
    validate_user(user)
    save_user(user)
    notify_user(user)
```

## Testing Best Practices

Write tests first, code second. Tests are documentation.

### Test-Driven Development (TDD)

TDD is a development process relying on software requirements being converted to test cases.

**Process:**
1. Write a failing test
2. Write minimal code to pass
3. Refactor while keeping tests passing

**Benefits:**
- Better design
- Confidence in changes
- Living documentation
