
try:
    import inflect
    engine = inflect.engine()
except ImportError:
    inflect = None


class Engine:

    def plural(self, word):
        return '%ss' % word


if inflect is None:

    engine = Engine()
