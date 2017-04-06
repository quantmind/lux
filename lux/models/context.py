import threading

_ = threading.local()
_.stack = {}


def set(key, value):
    stack = _.stack.get(key)
    if stack is None:
        stack = []
        _.stack[key] = stack
    stack.append(value)


def get(key):
    stack = _.stack.get(key)
    return stack[-1] if stack else None


def pop(key):
    return _.stack.get(key).pop()
