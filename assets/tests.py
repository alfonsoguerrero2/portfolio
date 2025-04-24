
# Create your tests here.
# myapp/tests/test_api.py

from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse

class PortfolioSummaryLiveDataTest(TestCase):
    fixtures = ['assets/fixtures/portfolios.json']  # Optional: Load fixtures if you use them

    def setUp(self):
        self.client = APIClient()

    def test_summary_for_two_weeks_in_2022(self):
        # Define the URL and query parameters
        url = reverse('portfolio-summary')
        params = {
            'initial_date': '2022-03-10',
            'end_date': '2022-03-24'
        }

        # Make the API call
        response = self.client.get(url, params)

        # Check basic response status and structure
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.data, list))
        self.assertEqual(len(response.data), 15)  # 15 days inclusive

        # Sample spot check on first day's data
        first_day = response.data[0]
        self.assertIn('date', first_day)
        self.assertIn('portfolio_1', first_day)
        self.assertIn('portfolio_2', first_day)

        # Optional: log to inspect structure
        print(first_day)

        # Ensure portfolios have expected keys
        for day in response.data:
            self.assertIn('total_value', day['portfolio_1'])
            self.assertIn('weights', day['portfolio_1'])
            self.assertIn('total_value', day['portfolio_2'])
            self.assertIn('weights', day['portfolio_2'])
