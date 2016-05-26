from tests.oauth import OAuthTest
from tests.oauth.github import GithubMixin


class TestGithub(OAuthTest, GithubMixin):

    async def test_oauths(self):
        request = await self.client.get('/')
        oauths = request.cache.oauths
        self.assertTrue(oauths)
