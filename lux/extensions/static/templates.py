from lux import Template, PageTemplate, Context


page1 = PageTemplate(Context('header'),
                     Context('body'),
                     Context('footer'))



DEFAULT_TEMPLATES = {'page': page1}
