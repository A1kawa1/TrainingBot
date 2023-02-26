from django.test import TestCase
from datetime import datetime
from model.models import ResultDayDci, User
from bot.Button import check_variance


class VarianceTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            id=1
        )
        results = [
            ResultDayDci(
                user=VarianceTest.user,
                time=datetime(2023, 2, 23, 23, 53, 29),
                calories=0
            ),
            ResultDayDci(
                user=VarianceTest.user,
                time=datetime(2023, 2, 25, 23, 53, 29),
                calories=550
            ),
            ResultDayDci(
                user=VarianceTest.user,
                time=datetime(2023, 2, 28, 23, 53, 29),
                calories=500
            ),
            ResultDayDci(
                user=VarianceTest.user,
                time=datetime(2023, 3, 1, 23, 53, 29),
                calories=0
            ),
            ResultDayDci(
                user=VarianceTest.user,
                time=datetime(2023, 3, 3, 23, 53, 29),
                calories=0
            ),
            ResultDayDci(
                user=VarianceTest.user,
                time=datetime(2023, 3, 4, 23, 53, 29),
                calories=0
            )
        ]
        cls.result_dci = ResultDayDci.objects.bulk_create(results)

    def test_variance(self):
        self.assertTrue(check_variance(1))