from .readers import MarkdownReader, register_reader, Markdown
from .contents import Content

reveal_src = '//cdnjs.cloudflare.com/ajax/libs/reveal.js/2.6.2'


class Slide(Content):

    def on_html(self, app, doc):
        ctx = {'reveal_src': reveal_src}
        text = app.render_template('reveal.js', context=ctx)
        doc.body.embedded_js.append(text)


@register_reader
class Slides(MarkdownReader):
    content = Slide
    slide_start = '--- slide'
    file_extensions = ['slides']

    def read(self, source_path, name, **params):
        with open(source_path, encoding='utf-8') as text:
            raw = text.read()
            doc, slides = self.slides(raw)
        md = Markdown(extensions=self.extensions)
        meta = md.Meta
        body = ['<div class="slides">']
        for slide in slides:
            body.append('<section>')
            md = Markdown(extensions=self.extensions)
            slide = md.convert(slide)
            body.append(slide)
            body.append('</section>')
        body.append('</div')
        body = '\n'.join(body)
        return self.process(body, meta, source_path, name, **params)

    def slides(self, raw):
        doc = []
        slides = []
        slide = None
        for line in raw.split('\n'):
            if line == self.slide_start:
                if slide:
                    slides.append('\n'.join(slide))
                slide = []
                continue
            if slide is None:
                doc.append(line)
                continue
            else:
                slide.append(line)
        if slide:
            slides.append('\n'.join(slide))
        return '\n'.join(doc), slides
