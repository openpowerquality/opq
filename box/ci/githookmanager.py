import github
import os


class GitHookManager:
    def __init__(self):
        token = os.environ['GITHUB_TOKEN']
        self.github = github.Github(token)

    def updateHookUrlUser(self, repo, url,  hname = "web"):
        config = {"url": url, "content_type": "json"}
        repo =  self.github.get_user().get_repo(repo)
        hooks = repo.get_hooks()
        filtered_hooks = filter(lambda x: x.name == hname, hooks)
        if len(filtered_hooks) > 0:
            hook = filtered_hooks[0]
            hook.edit(hname, config, events=["push"], active=True)
        else:
            hook = repo.create_hook(hname, config, events=["push"], active=True)