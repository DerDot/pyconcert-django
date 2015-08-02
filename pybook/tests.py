# -*- coding: utf-8 -*-
from django.test import TestCase

import api_calls


class APITestCase(TestCase):

    def test_book_releases(self):
        authors = ['terry pratchett', 'neil gaiman', 'ben aaronovitch']
        region = ['US']
        api_calls.book_releases(authors, region)