# -*- coding: utf-8 -*-
from StringIO import StringIO
from datetime import date, time, timedelta
import json

from django.test import TestCase
from django.contrib.auth.models import User
from nose.tools import assert_equal, assert_list_equal

import api_calls
from pyconcert.models import Artist, Event
from pyconcert.views import EventsView


ori_urlopen = api_calls.urllib.urlopen


def urlopen_bit_mock(*args, **kwargs):
    response = [{u'url': u'test.com',
                 u'venue': {u'city': u'New York',
                            u'name': u'Webster Hall',
                            u'url': u'test.com',
                            u'country': u'United States',
                            u'region': u'NY',
                            u'longitude':-73.989643,
                            u'latitude': 40.731907,
                            u'id': 1356611},
                 u'ticket_url': u'test.com?app_id=pyconcert',
                 u'on_sale_datetime': None,
                 u'datetime': u'2015-05-13T19:00:00',
                 u'artists': [{u'url': u'test.com/banda',
                               u'mbid': u'b20ebd71-a252-417d-9e1c-3e1763da68f8',
                               u'name': u'ümlautbänd'}],
                 u'ticket_status': u'available',
                 u'id': 1234567}]
    file_like = StringIO(json.dumps(response))
    return file_like


class APITestCase(TestCase):
    def setUp(self):
        api_calls.urllib.urlopen = urlopen_bit_mock

    def tearDown(self):
        api_calls.urllib.urlopen = ori_urlopen

    def test_events_for_artists_bandsintown(self):
        """Test events_for_artists_bandsintown"""
        artists = ["banda", "bandb", "ümlautbänd"]
        location = "new york"
        result = api_calls.events_for_artists_bandsintown(artists, location)
        expected = api_calls.Event(["ümlautbänd"], "Webster Hall", "New York", "United States",
                                   date(2015, 5, 13), time(19), 'test.com?app_id=pyconcert')
        assert_equal(result[0], expected)

    def test_events_for_artists_bandsintown_unicode(self):
        """Test events_for_artists_bandsintown with unicode"""
        artists = [u"ümlautbänd"]
        location = u"nüw york"
        result = api_calls.events_for_artists_bandsintown(artists, location)
        expected = api_calls.Event(["ümlautbänd"], "Webster Hall", "New York", "United States",
                                   date(2015, 5, 13), time(19), 'test.com?app_id=pyconcert')
        assert_equal(result[0], expected)

    def test_event_repr(self):
        """Test utf8 support for event representation."""
        result = api_calls.Event(["ümlautbänd"], "Webster Hall", "New York", "United States",
                                 date(2015, 5, 13), time(19), 'test.com?app_id=pyconcert')
        expected = "Event by ümlautbänd in Webster Hall (New York, United States)."
        assert_equal(result.__repr__(), expected)


class EventsViewTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create()
        self.artist = Artist.objects.create(name="TestArtist",
                                            genre="TestGenre")
        self.artist.subscribers.add(self.user)
        
        self.event1 = Event.objects.create(venue="TestVenue1",
                                           city="TestCity1",
                                           country="TestCountry1",
                                           date=date.today() - timedelta(days=8),
                                           time=time(19),
                                           ticket_url="www.test1.url")
        self.event1.artists.add(self.artist)
        
        self.event2 = Event.objects.create(venue="TestVenue2",
                                           city="TestCity2",
                                           country="TestCountry2",
                                           date=date.today() + timedelta(days=7),
                                           time=time(19),
                                           ticket_url="www.test2.url")
        self.event2.artists.add(self.artist)
        
    def test_correct_events(self):
        target = EventsView()
        filtered_query_set = target._filtered_and_sorted(self.artist.name,
                                                         self.user)
        actual = list(filtered_query_set)
        expected = [self.event2]
        assert_list_equal(actual, expected)