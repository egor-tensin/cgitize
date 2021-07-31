# Copyright (c) 2021 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "cgitize" project.
# For details, see https://github.com/egor-tensin/cgitize.
# Distributed under the MIT License.

import unittest

from github import Github, GithubException


class GitHubTests(unittest.TestCase):
    def setUp(self):
        self.github = Github()

    def test_nonexistent_repo(self):
        with self.assertRaises(GithubException):
            self.github.get_repo('doesnot/exist')

    def test_existing_repo(self):
        r = self.github.get_repo('egor-tensin/cgitize-test-repository')
        self.assertEqual(r.name, 'cgitize-test-repository')
        self.assertEqual(r.description, 'Test cgitize repository')
        self.assertEqual(r.owner.name, 'Egor Tensin')
        self.assertEqual(r.owner.login, 'egor-tensin')
        self.assertEqual(r.html_url, 'https://github.com/egor-tensin/cgitize-test-repository')
        self.assertEqual(r.clone_url, 'https://github.com/egor-tensin/cgitize-test-repository.git')
        self.assertEqual(r.ssh_url, 'git@github.com:egor-tensin/cgitize-test-repository.git')
