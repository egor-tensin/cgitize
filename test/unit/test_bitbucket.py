# Copyright (c) 2021 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "cgitize" project.
# For details, see https://github.com/egor-tensin/cgitize.
# Distributed under the MIT License.

import unittest

from atlassian.bitbucket.cloud import Cloud
from requests.exceptions import HTTPError


class BitbucketTests(unittest.TestCase):
    def setUp(self):
        self.bitbucket = Cloud(cloud=True)

    def test_nonexistent_repo(self):
        with self.assertRaises(HTTPError):
            self.bitbucket.repositories.get('doesnot', 'exist')

    def test_existing_repo(self):
        r = self.bitbucket.repositories.get('egor-tensin', 'cgitize-test-repository')
        self.assertEqual(r.name, 'cgitize-test-repository')
        self.assertEqual(r.description, 'Test cgitize repository')

        self.assertEqual(r.data['owner']['display_name'], 'Egor Tensin')
        self.assertEqual(r.data['owner']['nickname'], 'egor-tensin')

        self.assertEqual(r.get_link('html'), 'https://bitbucket.org/egor-tensin/cgitize-test-repository')

        clone_urls = [link for link in r.data['links']['clone'] if link['name'] == 'https']
        self.assertEqual(len(clone_urls), 1)
        self.assertEqual(clone_urls[0]['href'], 'https://bitbucket.org/egor-tensin/cgitize-test-repository.git')

        ssh_urls = [link for link in r.data['links']['clone'] if link['name'] == 'ssh']
        self.assertEqual(len(ssh_urls), 1)
        self.assertEqual(ssh_urls[0]['href'], 'git@bitbucket.org:egor-tensin/cgitize-test-repository.git')
