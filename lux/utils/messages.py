from itertools import chain


def error_message(*args, errors=None, trace=None):
    msgs = args
    if errors:
        msgs = chain(args, errors)
    messages = []
    data = {'error': True}
    message = []
    for msg in msgs:
        if isinstance(msg, str):
            message.append(msg)
        elif isinstance(msg, dict):
            if len(msg) == 1 and 'message' in msg:
                message.append(msg['message'])
            elif msg:
                messages.append(msg)
    data['message'] = ' '.join(message)
    if messages:
        data['errors'] = messages
    if trace:
        data['trace'] = trace
    return data
