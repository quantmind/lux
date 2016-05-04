import tests.admin.test_app as app


class AngularAdminTest(app.AdminTest):
    config_params = {'HTML5_NAVIGATION': True}

    async def test_angular_sitemap(self):
        request = await self.client.get('/admin/blog')
        jscontext = request.html_document.jscontext
        pages = jscontext.get('pages')
        self.assertTrue(pages)
        updates = pages.get('admin_blog_update')
        self.assertTrue(updates)
        self.assertEqual(updates['url'], '/admin/blog/:id')
        self.assertEqual(updates['templateUrl'],
                         '/admin/blog/:id?template=ui')
