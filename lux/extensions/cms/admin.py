from lux.extensions import admin
from lux.forms import Layout, Fieldset, Submit

from .views import PageCRUD, TemplateCRUD, PageForm, TemplateForm


#    CLASSES FOR ADMIN
class CmsAdmin(admin.CRUDAdmin):
    '''Admin views for the cms
    '''
    section = 'cms'


@admin.register(PageCRUD.model)
class PageAdmin(CmsAdmin):
    '''Admin views for html pages
    '''
    icon = 'fa fa-sitemap'
    form = Layout(PageForm,
                  Fieldset(all=True),
                  Submit('Add new page'))
    editform = Layout(PageForm,
                      Fieldset(all=True),
                      Submit('Update page'))


@admin.register(TemplateCRUD.model)
class TemplateAdmin(CmsAdmin):
    icon = 'fa fa-file-code-o'
    form = Layout(TemplateForm,
                  Fieldset(all=True),
                  Submit('Add new template'))
    editform = Layout(TemplateForm,
                      Fieldset(all=True),
                      Submit('Update template'))
