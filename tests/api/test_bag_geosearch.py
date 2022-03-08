from unittest import TestCase
from unittest.mock import Mock, patch

from requests import ConnectionError, HTTPError, Timeout, TooManyRedirects

from api.bag_geosearch import BagGeoSearchAPI
from datasets.blackspots.models import Spot


class TestBagGeoSearchAPI(TestCase):

    @patch('api.bag_geosearch.requests')
    def test_get_stadsdeel(self, mocked_requests):
        mocked_response = Mock()
        mocked_response.json.return_value = {
            "features": [
                {
                    "properties": {
                        "display": "0363100012179951",
                        "distance": 5.12088218200184,
                        "id": "0363100012179951",
                        "type": "bag/pand",
                        "uri": "https://api.data.amsterdam.nl/bag/pand/0363100012179951/"
                    }
                },
                {
                    "properties": {
                        "code": "S",
                        "display": "Weesp",
                        "distance": 370.982213404085,
                        "id": "03630930000000",
                        "type": "gebieden/stadsdeel",
                        "uri": "https://api.data.amsterdam.nl/gebieden/stadsdeel/03630930000000/"
                    }
                },
                {
                    "properties": {
                        "code": "00e",
                        "display": "BG-terrein e.o.",
                        "distance": 63.5106864466598,
                        "id": "03630000000082",
                        "type": "gebieden/buurt",
                        "uri": "https://api.data.amsterdam.nl/gebieden/buurt/03630000000082/",
                        "vollcode": "A00e"
                    }
                },
                {
                    "properties": {
                        "display": "Burgwallen-Oude Zijde",
                        "distance": 316.072267962479,
                        "id": "3630012052036",
                        "type": "gebieden/buurtcombinatie",
                        "uri": "https://api.data.amsterdam.nl/gebieden/buurtcombinatie/3630012052036/",
                        "vollcode": "A00"
                    }
                },
                {
                    "properties": {
                        "code": "YA50",
                        "display": "YA50",
                        "distance": 3.28805158335233,
                        "id": "03630012100479",
                        "type": "gebieden/bouwblok",
                        "uri": "https://api.data.amsterdam.nl/gebieden/bouwblok/03630012100479/"
                    }
                },
                {
                    "properties": {
                        "code": "DX01",
                        "display": "Centrum-West",
                        "distance": 854.524957763816,
                        "id": "DX01",
                        "type": "gebieden/gebiedsgerichtwerken",
                        "uri": "https://api.data.amsterdam.nl/gebieden/gebiedsgerichtwerken/DX01/"
                    }
                },
                {
                    "properties": {
                        "display": "Bufferzone",
                        "distance": 176.738989749228,
                        "id": "bufferzone",
                        "type": "gebieden/unesco",
                        "uri": "https://api.data.amsterdam.nl/gebieden/unesco/bufferzone/"
                    }
                },
                {
                    "properties": {
                        "display": "ASD05 G 06726 G 0000",
                        "distance": 5.60334422250985,
                        "id": "NL.KAD.OnroerendeZaak.11460672670000",
                        "type": "kadaster/kadastraal_object",
                        "uri": "https://api.data.amsterdam.nl/brk/object/NL.KAD.OnroerendeZaak.11460672670000/"
                    }
                }
            ],
            "type": "FeatureCollection"
        }
        mocked_requests.get.return_value = mocked_response
        expected_stadsdeel = Spot.Stadsdelen.Weesp
        stadsdeel = BagGeoSearchAPI().get_stadsdeel(lat=52.370216, lon=4.895168)
        self.assertEqual(stadsdeel, expected_stadsdeel)

    @patch('api.bag_geosearch.requests')
    def test_get_stadsdeel_no_response(self, mocked_requests):
        mocked_response = Mock()
        mocked_response.json.return_value = {}
        mocked_requests.get.return_value = mocked_response
        expected_stadsdeel = Spot.Stadsdelen.Geen
        stadsdeel = BagGeoSearchAPI().get_stadsdeel(lat=52.370216, lon=4.895168)
        self.assertEqual(stadsdeel, expected_stadsdeel)

    @patch('api.bag_geosearch.requests')
    def test_get_stadsdeel_json_exception(self, mocked_requests):
        mocked_response = Mock()
        mocked_response.json.side_effect = ValueError()
        mocked_requests.get.return_value = mocked_response
        expected_stadsdeel = Spot.Stadsdelen.BagFout
        stadsdeel = BagGeoSearchAPI().get_stadsdeel(lat=52.370216, lon=4.895168)
        self.assertEqual(stadsdeel, expected_stadsdeel)

    @patch('api.bag_geosearch.requests')
    def test_get_stadsdeel_http_exception(self, mocked_requests):
        for ExceptionClass in [ConnectionError, HTTPError, Timeout, TooManyRedirects]:
            mocked_requests.get.side_effect = ExceptionClass()
            expected_stadsdeel = Spot.Stadsdelen.BagFout
            stadsdeel = BagGeoSearchAPI().get_stadsdeel(lat=52.370216, lon=4.895168)
            self.assertEqual(stadsdeel, expected_stadsdeel)
