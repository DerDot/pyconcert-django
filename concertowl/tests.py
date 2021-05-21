# -*- coding: utf-8 -*-
from io import StringIO
from datetime import date, time, timedelta
import json

from django.test import TestCase
from django.contrib.auth.models import User
from nose.tools import assert_equal, assert_list_equal

from concertowl.api_calls import bandsintown
from concertowl.models import Artist, Event
from concertowl.views import EventsView
from eventowl.models import UserProfile


ori_requests_get = bandsintown.requests.get


def requests_get_mock(*args, **kwargs):
    response = [{'url': 'test.com',
                 'venue': {'city': 'New York',
                           'name': 'Webster Hall',
                           'url': 'test.com',
                           'country': 'United States',
                           'region': 'NY',
                           'longitude': -73.989643,
                           'latitude': 40.731907,
                           'id': 1356611},
                 'ticket_url': 'test.com?app_id=concertowl',
                 'on_sale_datetime': None,
                 'datetime': '2015-05-13T19:00:00',
                 'artists': [{'url': 'test.com/banda',
                               'mbid': 'b20ebd71-a252-417d-9e1c-3e1763da68f8',
                               'name': 'ümlautbänd'}],
                 'lineup': ['ümlautbänd'],
                 'ticket_status': 'available',
                 'id': 1234567}]

    class Mock():
        text = json.dumps(response)
    return Mock()


class APITestCase(TestCase):
    def setUp(self):
        bandsintown.requests.get = requests_get_mock

    def tearDown(self):
        bandsintown.urllib.urlopen = ori_requests_get

    def test_events_for_artists_bandsintown(self):
        """Test events_for_artists_bandsintown"""
        artists = ["banda", "bandb", "ümlautbänd"]
        location = "new york"
        result = bandsintown.events_for_artists_bandsintown(artists, location)
        expected = bandsintown.Event(["ümlautbänd"], "Webster Hall", "New York", "United States",
                                     date(2015, 5, 13), time(19), 'test.com?app_id=concertowl')
        assert_equal(result[0], expected)

    def test_events_for_artists_bandsintown_unicode(self):
        """Test events_for_artists_bandsintown with unicode"""
        artists = ["ümlautbänd"]
        location = "new york"
        result = bandsintown.events_for_artists_bandsintown(artists, location)
        expected = bandsintown.Event(["ümlautbänd"], "Webster Hall", "New York", "United States",
                                     date(2015, 5, 13), time(19), 'test.com?app_id=concertowl')
        assert_equal(result[0], expected)

    def test_event_repr(self):
        """Test utf8 support for event representation."""
        result = bandsintown.Event(["ümlautbänd"], "Webster Hall", "New York", "United States",
                                   date(2015, 5, 13), time(19), 'test.com?app_id=concertowl')
        expected = "Event by ümlautbänd in Webster Hall (New York, United States)."
        assert_equal(result.__repr__(), expected)


class EventsViewTest(TestCase):

    def setUp(self):
        TOO_OLD = date.today() - timedelta(days=8)
        NEW_ENOUGH = date.today() + timedelta(days=7)

        USER_CITY = "UserCity"
        OTHER_CITY = "OtherCity"

        self.user = User.objects.create()
        user_profile = UserProfile.objects.create(user=self.user,
                                                  city=USER_CITY)

        self.artist = Artist.objects.create(name="TestArtist",
                                            genre="TestGenre")
        self.artist.subscribers.add(self.user)

        self.event1 = Event.objects.create(venue="TestVenue1",
                                           city=USER_CITY,
                                           country="TestCountry1",
                                           date=TOO_OLD,
                                           time=time(19),
                                           ticket_url="www.test1.url")
        self.event1.artists.add(self.artist)

        self.event2 = Event.objects.create(venue="TestVenue2",
                                           city=USER_CITY,
                                           country="TestCountry2",
                                           date=NEW_ENOUGH,
                                           time=time(19),
                                           ticket_url="www.test2.url")
        self.event2.artists.add(self.artist)

        self.event3 = Event.objects.create(venue="TestVenue3",
                                           city=OTHER_CITY,
                                           country="TestCountry3",
                                           date=NEW_ENOUGH,
                                           time=time(19),
                                           ticket_url="www.test3.url")
        self.event3.artists.add(self.artist)

    def test_correct_events(self):
        target = EventsView()
        filtered_query_set = target._filtered_and_sorted(self.artist.name,
                                                         self.user)
        actual = list(filtered_query_set)
        expected = [self.event2]
        assert_list_equal(actual, expected)
