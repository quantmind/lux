# Providers

Lux uses several services such HTTP client, websocket clients and so forth.
Providers are a way to specify the handler which provide a given service:

To override a provider, create a ``LuxExtension`` and implement the ``on_config``
method:
```python
    def on_config(self, app):
        import requests
        app.providers('Http') = lambda _: requests.Session()
```
