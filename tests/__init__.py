import os
import json


PATH = os.path.dirname(os.path.abspath(__file__))


def load_fixture(name):
    with open(os.path.join(PATH, 'fixtures', '%s.json' % name), 'r') as file:
        return json.load(file)
