import unittest
from src.extraction import masquer_donnees


class TestExtraction(unittest.TestCase):

    def test_masquer_donnees(self):
        self.assertEqual(
            masquer_donnees("client=bob pwd=abc123"),
            "client=bob pwd=[MASQUE]"
        )

        self.assertNotIn(
            "4970123412341234",
            masquer_donnees("card=4970123412341234")
        )


if __name__ == "__main__":
    unittest.main()