from unittest import TestCase
from unittest.mock import Mock, patch

from requests import ConnectionError, HTTPError, Timeout, TooManyRedirects

from api.bag_geosearch import BagGeoSearchAPI
from datasets.blackspots.models import Spot


class TestBagGeoSearchAPI(TestCase):
    @patch("api.bag_geosearch.requests")
    def test_get_stadsdeel(self, mocked_requests):
        mocked_response = Mock()
        mocked_response.json.return_value = {
            "features": [
                {
                    "properties": {
                        "code": "S",
                        "display": "Weesp",
                        "distance": 3408.38652445197,
                        "id": "03630930000000",
                        "type": "gebieden/stadsdeel",
                        "uri": "https://api.data.amsterdam.nl/gebieden/stadsdeel/03630930000000/",
                    }
                }
            ],
            "type": "FeatureCollection",
        }
        mocked_requests.get.return_value = mocked_response
        expected_stadsdeel = Spot.Stadsdelen.Weesp
        stadsdeel = BagGeoSearchAPI().get_stadsdeel(lat=52.370216, lon=4.895168)
        self.assertEqual(stadsdeel, expected_stadsdeel)

    @patch("api.bag_geosearch.requests")
    def test_get_unexpected_stadsdeel(self, mocked_requests):
        mocked_response = Mock()
        mocked_response.json.return_value = {
            "features": [
                {
                    "properties": {
                        "code": "QQ",
                        "display": "Nonexistent",
                        "distance": 3408.38652445197,
                        "id": "03630931234567",
                        "type": "gebieden/stadsdeel",
                        "uri": "https://api.data.amsterdam.nl/gebieden/stadsdeel/03630931234567/",
                    }
                }
            ],
            "type": "FeatureCollection",
        }
        mocked_requests.get.return_value = mocked_response
        expected_stadsdeel = Spot.Stadsdelen.BagFout
        stadsdeel = BagGeoSearchAPI().get_stadsdeel(lat=52.370216, lon=4.895168)
        self.assertEqual(stadsdeel, expected_stadsdeel)

    @patch("api.bag_geosearch.requests")
    def test_get_stadsdeel_no_response(self, mocked_requests):
        mocked_response = Mock()
        mocked_response.json.return_value = {}
        mocked_requests.get.return_value = mocked_response
        expected_stadsdeel = Spot.Stadsdelen.Geen
        stadsdeel = BagGeoSearchAPI().get_stadsdeel(lat=52.370216, lon=4.895168)
        self.assertEqual(stadsdeel, expected_stadsdeel)

    @patch("api.bag_geosearch.requests")
    def test_get_stadsdeel_json_exception(self, mocked_requests):
        mocked_response = Mock()
        mocked_response.json.side_effect = ValueError()
        mocked_requests.get.return_value = mocked_response
        expected_stadsdeel = Spot.Stadsdelen.BagFout
        stadsdeel = BagGeoSearchAPI().get_stadsdeel(lat=52.370216, lon=4.895168)
        self.assertEqual(stadsdeel, expected_stadsdeel)

    @patch("api.bag_geosearch.requests")
    def test_get_stadsdeel_http_exception(self, mocked_requests):
        for ExceptionClass in [ConnectionError, HTTPError, Timeout, TooManyRedirects]:
            mocked_requests.get.side_effect = ExceptionClass()
            expected_stadsdeel = Spot.Stadsdelen.BagFout
            stadsdeel = BagGeoSearchAPI().get_stadsdeel(lat=52.370216, lon=4.895168)
            self.assertEqual(stadsdeel, expected_stadsdeel)
