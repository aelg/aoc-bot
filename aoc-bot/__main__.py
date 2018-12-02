import os
import aiohttp
import pprint

from aiohttp import web

from gidgethub import routing, sansio
from gidgethub import aiohttp as gh_aiohttp

router = routing.Router()

@router.register("pull_request", action="opened")
async def pr_opened_event(event, gh, *args, **kwargs):
    """
    Whenever an issue is opened, greet the author and say thanks.
    """
    patch_url = event.data["pull_request"]["patch_url"]
    author = event.data["pull_request"]["user"]["login"]
    print('PR opened by ' + author)
    print('PR patch at ' + patch_url)

    patch = await gh.getitem(patch_url)

    print(patch)

    filenames = map(lambda s : s[6:], filter(lambda s: s.startswith('+++ b/') or s.startswith('--- a/'), patch.splitlines()))
    print(list(filenames))


async def main(request):
    # read the GitHub webhook payload
    body = await request.read()

    # our authentication token and secret
    secret = os.environ.get("GH_SECRET")
    gh_user = os.environ.get("GH_USER")
    oauth_token = os.environ.get("GH_AUTH")

    print("A request!")
    # a representation of GitHub webhook event
    event = sansio.Event.from_http(request.headers, body, secret=secret)

    # handle the event
    async with aiohttp.ClientSession() as session:
        gh = gh_aiohttp.GitHubAPI(session, gh_user,
                                  oauth_token=oauth_token)

        # call the appropriate callback for the event
        await router.dispatch(event, gh)

    # return a "Success"
    return web.Response(status=200)


if __name__ == "__main__":
    app = web.Application()
    app.router.add_post("/", main)
    port = os.environ.get("PORT")
    if port is not None:
        port = int(port)
    else:
        port = 8080

    web.run_app(app, port=port)
