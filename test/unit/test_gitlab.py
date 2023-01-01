# Copyright (c) 2021 Egor Tensin <Egor.Tensin@gmail.com>
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

    def test_existing_repo(self):
        r = self.gitlab.projects.get('egor-tensin/cgitize-test-repository')
        self.assertEqual(r.name, 'cgitize-test-repository')
        self.assertEqual(r.description, 'Test cgitize repository')
        self.assertEqual(r.namespace['name'], 'Egor Tensin')
        self.assertEqual(r.namespace['path'], 'egor-tensin')
        self.assertEqual(r.web_url, 'https://gitlab.com/egor-tensin/cgitize-test-repository')
        self.assertEqual(r.http_url_to_repo, 'https://gitlab.com/egor-tensin/cgitize-test-repository.git')
        self.assertEqual(r.ssh_url_to_repo, 'git@gitlab.com:egor-tensin/cgitize-test-repository.git')
