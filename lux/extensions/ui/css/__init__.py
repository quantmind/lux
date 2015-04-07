from . import main
from . import navbar
from . import forms


def add_css(all):
    main.add_css(all)
    navbar.add_css(all)
    forms.add_css(all)
