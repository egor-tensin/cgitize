# Copyright (c) 2021 Egor Tensin <egor@tensin.name>
# This file is part of the "cgitize" project.
# For details, see https://github.com/egor-tensin/cgitize.
# Distributed under the MIT License.

import os
import unittest

from github import Auth, Github, GithubException


class GitHubTests(unittest.TestCase):
    def setUp(self):
        self.github = Github(auth=Auth.Token(os.environ.get('CGITIZE_GITHUB_TOKEN')))

    def test_nonexistent_repo(self):
        with self.assertRaises(GithubException):
            self.github.get_repo('doesnot/exist')

    def test_public_repo(self):
        r = self.github.get_repo('cgitize-test/public')
        self.assertEqual(r.name, 'public')
        self.assertEqual(r.description, 'Public test cgitize repository')
        self.assertEqual(r.owner.name, 'Test cgitize user')
        self.assertEqual(r.owner.login, 'cgitize-test')
        self.assertEqual(r.html_url, 'https://github.com/cgitize-test/public')
        self.assertEqual(r.clone_url, 'https://github.com/cgitize-test/public.git')
        self.assertEqual(r.ssh_url, 'git@github.com:cgitize-test/public.git')

    def test_private_repo(self):
        r = self.github.get_repo('cgitize-test/private')
        self.assertEqual(r.name, 'private')
        self.assertEqual(r.description, 'Private test cgitize repository')
        self.assertEqual(r.owner.name, 'Test cgitize user')
        self.assertEqual(r.owner.login, 'cgitize-test')
        self.assertEqual(r.html_url, 'https://github.com/cgitize-test/private')
        self.assertEqual(r.clone_url, 'https://github.com/cgitize-test/private.git')
        self.assertEqual(r.ssh_url, 'git@github.com:cgitize-test/private.git')

    def test_user(self):
        # This is a bad way to get user's repositories: it'll return only
        # public ones for on particular reason.
        rs = self.github.get_user('cgitize-test').get_repos()
        self.assertEqual(len([r for r in rs if r.name == 'public']), 1)
        self.assertEqual(len([r for r in rs if r.name == 'private']), 0)

    def test_user_authenticated(self):
        # This is the way instead:
        rs = self.github.get_user().get_repos()
        self.assertEqual(len([r for r in rs if r.name == 'public']), 1)
        self.assertEqual(len([r for r in rs if r.name == 'private']), 1)


class GitHubTestPrivateRepo(unittest.TestCase):
    def setUp(self):
        self.github = Github()

    def test_private_repo(self):
        with self.assertRaises(GithubException):
            self.github.get_repo('cgitize-test/private')
