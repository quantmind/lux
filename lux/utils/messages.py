from itertools import chain


def error_message(*args, errors=None):
    msgs = args
    if errors:
        msgs = chain(args, errors)
    messages = []
    data = {'errors': messages}
    for msg in msgs:
        if isinstance(msg, str):
            msg = {'message': msg}
        messages.append(msg)
    return data
