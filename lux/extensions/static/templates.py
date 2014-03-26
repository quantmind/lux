from lux import Template, PageTemplate, Context


DEFAULT_TEMPLATE = PageTemplate(Context('header'),
                                Context('main'),
                                Context('footer'))
