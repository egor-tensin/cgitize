from pull.repo import BitbucketRepo, GithubRepo, Repo


MY_REPOS = (
    GithubRepo('xyz'),
    GithubRepo('foo/bar', user='test', via_ssh=False),

    BitbucketRepo('xyz'),
    BitbucketRepo('foo/bar', desc='Foo (Bar)'),

    Repo('tmp/tmp', clone_url='https://example.com/tmp.git', owner='John Doe'),
)
