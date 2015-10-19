from django.test import TestCase
from mixer.backend.django import mixer

from pyconcert.models import Artist
from eventowl.utils import django_helpers


class UtilsTestCase(TestCase):
    
    def setUp(self):
        self.genre = 'hardcore'
        self.artist = mixer.blend(Artist, genre=self.genre)
    
    def test_set_if_different_same(self):
        actual = django_helpers.set_if_different(self.artist, 'genre', self.genre)
        
        expected = False
        self.assertEqual(actual, expected)
        
    def test_set_if_different_different(self):
        expected_genre = 'metal'
        actual_changed = django_helpers.set_if_different(self.artist, 'genre', expected_genre)
        
        expected_changed = True
        self.assertEqual(actual_changed, expected_changed)
        
        actual_genre = self.artist.genre
        self.assertEqual(actual_genre, expected_genre)