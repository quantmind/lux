import tests.admin.test_app as app


class AngularAdminTest(app.AdminTest):
    config_params = {'HTML5_NAVIGATION': True}

    async def test_angular_sitemap(self):
        request = await self.client.get('/admin/blogs')
        jscontext = request.html_document.jscontext
        pages = jscontext.get('pages')
        self.assertTrue(pages)
        updates = pages.get('admin_blogs_update')
        self.assertTrue(updates)
        self.assertEqual(updates['url'], '/admin/blogs/:id')
        self.assertEqual(updates['templateUrl'],
                         '/admin/blogs/:id?template=ui')
