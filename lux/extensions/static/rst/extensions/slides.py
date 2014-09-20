import re

from markdown import Extension
from markdown.treeprocessors import Treeprocessor
from markdown.preprocessors import Preprocessor

# Global Vars
slide_start = '--- slide'
META_RE = re.compile(r'^[ ]{0,3}(?P<key>[A-Za-z0-9_-]+):\s*(?P<value>.*)')


class SlidePreprocessor(Preprocessor):

    def run(self, lines):
        """ Parse Meta-Data and store in Markdown.Meta. """
        slide = False
        slides = 0
        slide_attrs = None
        new_lines = []
        for line in lines:
            if line == slide_start:
                if slide:
                    slides.append(slide)
                slide = True
                slides += 1
                slide_attrs = {}
                continue
            if slide_attrs is None:
                new_lines.append(line)
            else:
                m1 = META_RE.match(line)
                if m1:
                    key = m1.group('key').lower().strip()
                    value = m1.group('value').strip()
                    slide_attrs[key] = value
                else:
                    new_lines.append(self.slide(slide_attrs))
                    new_lines = None


    def slide(self, attrs):
        return '<div class="step">'


class SlideExtension(Extension):

    def __init__(self, *args, **kwargs):
        # define default configs
        self.config = {
            'class': [None, "Additional class for the slide element"]
            }

        super(SlideExtension, self).__init__(*args, **kwargs)

    def extendMarkdown(self, md, md_globals):
        """ Add SlidePostprocessor to Markdown instance. """
        md.preprocessors.add("meta", SlidePreprocessor(md), "_begin")


def makeExtension(*args, **kwargs):
  return SlideExtension(*args, **kwargs)
