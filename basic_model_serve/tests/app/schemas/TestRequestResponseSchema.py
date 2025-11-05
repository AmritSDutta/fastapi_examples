import unittest
from pydantic import ValidationError

from app.schemas.request_response import PredictRequest


class TestRequestResponseSchema(unittest.TestCase):

    def test_valid_request(self):
        req = PredictRequest(features=[5.1, 3.5, 1.4, 0.2])
        self.assertEqual(req.features, [5.1, 3.5, 1.4, 0.2])
        self.assertEqual(len(req.features), 4)

    def test_invalid_request(self):
        with self.assertRaises(ValidationError) as cm:
            req = PredictRequest(features=[5.1, 3.5, 1.4])  # passing 3 float instead of 4
        exc = cm.exception
        self.assertTrue(exc.errors())
        self.assertIsInstance(exc, ValidationError)


if __name__ == "__main__":
    unittest.main()
