# -*- coding: utf-8 -*-
from datetime import date, timedelta

from django.test import TestCase
from django.contrib.auth.models import User
from nose.tools import assert_list_equal

from . import api_calls
from bookowl.models import Author, Book
from bookowl.views import EventsView
        
        
class EventsViewTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create()
        self.author = Author.objects.create(name="TestAuthor")
        self.author.subscribers.add(self.user)
        
        self.book1 = Book.objects.create(title="TestTitle1",
                                         isbn="TestIsbn1",
                                         date=date.today() - timedelta(days=8),
                                         buy_url="www.test1.url")
        self.book1.authors.add(self.author)
        
        self.book2 = Book.objects.create(title="TestTitle2",
                                         isbn="TestIsbn2",
                                         date=date.today() + timedelta(days=8),
                                         buy_url="www.test2.url")
        self.book2.authors.add(self.author)
        
    def test_correct_events(self):
        target = EventsView()
        filtered_query_set = target._filtered_and_sorted(self.author.name,
                                                         self.user)
        actual = list(filtered_query_set)
        expected = [self.book2]
        assert_list_equal(actual, expected)