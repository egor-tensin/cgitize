# Copyright (c) 2021 Egor Tensin <egor@tensin.name>
# This file is part of the "cgitize" project.
# For details, see https://github.com/egor-tensin/cgitize.
# Distributed under the MIT License.

import os
import unittest

from gitlab import Gitlab
from gitlab.exceptions import GitlabGetError


class GitLabTests(unittest.TestCase):
    def setUp(self):
        self.gitlab = Gitlab(
            'https://gitlab.com',
            private_token=os.environ.get('CGITIZE_GITLAB_TOKEN'))

    def test_nonexistent_repo(self):
        with self.assertRaises(GitlabGetError):
            self.gitlab.projects.get('doesnot/exist')

    def test_public_repo(self):
        r = self.gitlab.projects.get('cgitize-test/public')
        self.assertEqual(r.name, 'public')
        self.assertEqual(r.description, 'Public test cgitize repository')
        self.assertEqual(r.namespace['name'], 'Test cgitize user')
        self.assertEqual(r.namespace['path'], 'cgitize-test')
        self.assertEqual(r.web_url, 'https://gitlab.com/cgitize-test/public')
        self.assertEqual(r.http_url_to_repo, 'https://gitlab.com/cgitize-test/public.git')
        self.assertEqual(r.ssh_url_to_repo, 'git@gitlab.com:cgitize-test/public.git')

    def test_private_repo(self):
        r = self.gitlab.projects.get('cgitize-test/private')
        self.assertEqual(r.name, 'private')
        self.assertEqual(r.description, 'Private test cgitize repository')
        self.assertEqual(r.namespace['name'], 'Test cgitize user')
        self.assertEqual(r.namespace['path'], 'cgitize-test')
        self.assertEqual(r.web_url, 'https://gitlab.com/cgitize-test/private')
        self.assertEqual(r.http_url_to_repo, 'https://gitlab.com/cgitize-test/private.git')
        self.assertEqual(r.ssh_url_to_repo, 'git@gitlab.com:cgitize-test/private.git')

    def test_user(self):
        u = self.gitlab.users.list(username='cgitize-test')
        self.assertEqual(len(u), 1)
        u = u[0]

        rs = u.projects.list()
        self.assertEqual(len([r for r in rs if r.name == 'public']), 1)
        self.assertEqual(len([r for r in rs if r.name == 'private']), 1)


class GitLabTestPrivateRepo(unittest.TestCase):
    def setUp(self):
        self.gitlab = Gitlab('https://gitlab.com')

    def test_private_repo(self):
        with self.assertRaises(GitlabGetError):
            self.gitlab.projects.get('cgitize-test/private')
