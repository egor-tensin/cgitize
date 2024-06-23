# Copyright (c) 2021 Egor Tensin <egor@tensin.name>
# This file is part of the "cgitize" project.
# For details, see https://github.com/egor-tensin/cgitize.
# Distributed under the MIT License.

import os
import unittest

from atlassian.bitbucket.cloud import Cloud
from requests.exceptions import HTTPError


class BitbucketTests(unittest.TestCase):
    def setUp(self):
        self.bitbucket = Cloud(
            username=os.environ.get('CGITIZE_BITBUCKET_USERNAME'),
            password=os.environ.get('CGITIZE_BITBUCKET_TOKEN'),
            cloud=True)

    def test_nonexistent_repo(self):
        with self.assertRaises(HTTPError):
            self.bitbucket.repositories.get('doesnot', 'exist')

    def test_public_repo(self):
        r = self.bitbucket.repositories.get('cgitize-test-workspace', 'public')
        self.assertEqual(r.name, 'public')
        self.assertEqual(r.description, 'Public test cgitize repository')

        self.assertEqual(r.data['workspace']['name'], 'Test cgitize workspace')
        self.assertEqual(r.data['workspace']['slug'], 'cgitize-test-workspace')

        self.assertEqual(r.get_link('html'), 'https://bitbucket.org/cgitize-test-workspace/public')

        clone_urls = [link for link in r.data['links']['clone'] if link['name'] == 'https']
        self.assertEqual(len(clone_urls), 1)
        self.assertEqual(clone_urls[0]['href'], 'https://cgitize-test@bitbucket.org/cgitize-test-workspace/public.git')

        ssh_urls = [link for link in r.data['links']['clone'] if link['name'] == 'ssh']
        self.assertEqual(len(ssh_urls), 1)
        self.assertEqual(ssh_urls[0]['href'], 'git@bitbucket.org:cgitize-test-workspace/public.git')

    def test_private_repo(self):
        r = self.bitbucket.repositories.get('cgitize-test-workspace', 'private')
        self.assertEqual(r.name, 'private')
        self.assertEqual(r.description, 'Private test cgitize repository')

        self.assertEqual(r.data['workspace']['name'], 'Test cgitize workspace')
        self.assertEqual(r.data['workspace']['slug'], 'cgitize-test-workspace')

        self.assertEqual(r.get_link('html'), 'https://bitbucket.org/cgitize-test-workspace/private')

    def test_user(self):
        w = self.bitbucket.workspaces.get('cgitize-test-workspace')
        self.assertEqual(len([r for r in w.repositories.each() if r.name == 'public']), 1)
        self.assertEqual(len([r for r in w.repositories.each() if r.name == 'private']), 1)


class BitbucketTestPrivateRepo(unittest.TestCase):
    def setUp(self):
        self.bitbucket = Cloud(cloud=True)

    def test_private_repo(self):
        with self.assertRaises(HTTPError):
            self.bitbucket.repositories.get('cgitize-test-workspace', 'private')
