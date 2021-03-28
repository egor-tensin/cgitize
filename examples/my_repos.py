from cgitize.repo import Bitbucket, GitHub, Repo


MY_REPOS = (
    GitHub('xyz'),
    GitHub('foo/bar', user='test', via_ssh=False),

    Bitbucket('xyz'),
    Bitbucket('foo/bar', desc='Foo (Bar)'),

    Repo('tmp/tmp', clone_url='https://example.com/tmp.git', owner='John Doe'),
)
