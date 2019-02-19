import os.path


DEFAULT_OWNER = 'Egor Tensin'
DEFAULT_GITHUB_USER = 'egor-tensin'
DEFAULT_BITBUCKET_USER = 'egor-tensin'


class Repo:
    @staticmethod
    def extract_repo_name(repo_id):
        return os.path.basename(repo_id)

    def __init__(self, repo_id, clone_url, owner=None, desc=None,
                 homepage=None):
        self.repo_id = repo_id
        self.repo_name = self.extract_repo_name(repo_id)
        self.clone_url = clone_url
        if owner is None:
            owner = DEFAULT_OWNER
        self.owner = owner
        if desc is None:
            if homepage is not None:
                desc = homepage
            elif clone_url is not None:
                desc = clone_url
            else:
                desc = self.repo_name
        self.desc = desc
        self.homepage = homepage


class GithubRepo(Repo):
    def __init__(self, repo_id, clone_url=None, owner=None, desc=None,
                 homepage=None, github_user=DEFAULT_GITHUB_USER):
        if clone_url is None:
            clone_url = self.build_clone_url(github_user, repo_id)
        if homepage is None:
            homepage = self.build_homepage_url(github_user, repo_id)
        super().__init__(repo_id, clone_url, owner=owner, desc=desc,
                         homepage=homepage)

    @staticmethod
    def build_clone_url(user, repo_id):
        name = Repo.extract_repo_name(repo_id)
        return f'ssh://git@github.com/{user}/{name}.git'

    @staticmethod
    def build_homepage_url(user, repo_id):
        name = Repo.extract_repo_name(repo_id)
        return f'https://github.com/{user}/{name}'


class BitbucketRepo(Repo):
    def __init__(self, repo_id, clone_url=None, owner=None, desc=None,
                 homepage=None, bitbucket_user=DEFAULT_BITBUCKET_USER):
        if clone_url is None:
            clone_url = self.build_clone_url(bitbucket_user, repo_id)
        if homepage is None:
            homepage = self.build_homepage_url(bitbucket_user, repo_id)
        super().__init__(repo_id, clone_url, owner=owner, desc=desc,
                         homepage=homepage)

    @staticmethod
    def build_clone_url(user, repo_id):
        name = Repo.extract_repo_name(repo_id)
        return f'ssh://git@bitbucket.org/{user}/{name}.git'

    @staticmethod
    def build_homepage_url(user, repo_id):
        name = Repo.extract_repo_name(repo_id)
        return f'https://bitbucket.org/{user}/{name.lower()}'
