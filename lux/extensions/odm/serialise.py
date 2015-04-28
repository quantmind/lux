import json
from datetime import date

from sqlalchemy.ext.declarative import DeclarativeMeta


class DateTimeJSONEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()
        else:
            return super().default(obj)


def tojson(obj, exclude=None, decoder=None):
    exclude = set(exclude or ())
    decoder = decoder or DateTimeJSONEncoder
    fields = {}
    for field in dir(obj):
        if (field.startswith('_') or field == 'metadata' or
                field in exclude):
            continue
        try:
            data = obj.__getattribute__(field)
            json.dumps(data)
        except TypeError:
            try:
                data = json.dumps(data, cls=decoder)
            except TypeError:
                continue
        except Exception:
            continue
        else:
            fields[field] = data
    # a json-encodable dict
    return fields
