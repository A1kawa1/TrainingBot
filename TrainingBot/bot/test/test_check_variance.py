from django.test import TestCase
from django.db.models import Avg
from datetime import date
from model.models import ResultDayDci, User
from bot.Button import analise_data


class VarianceMonitoringTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            id=1
        )
        cls.results = [
            ResultDayDci(
                user=cls.user,
                date=date(2023, 2, 23),
                calories=150
            ),
            ResultDayDci(
                user=cls.user,
                date=date(2023, 2, 26),
                calories=550
            ),
            ResultDayDci(
                user=cls.user,
                date=date(2023, 2, 28),
                calories=500
            ),
            ResultDayDci(
                user=cls.user,
                date=date(2023, 3, 1),
                calories=600
            ),
            ResultDayDci(
                user=cls.user,
                date=date(2023, 3, 3),
                calories=0
            ),
            ResultDayDci(
                user=cls.user,
                date=date(2023, 3, 4),
                calories=0
            )
        ]
        cls.right_avg_dci = {
            1: 150,
            2: 550,
            3: 550,
            4: 525,
            5: 550
        }
        cls.result_dci = ResultDayDci.objects.bulk_create(cls.results)

    def tearDown(self):
        ResultDayDci.objects.all().delete()

    def test_right_variance(self):
        self.assertTrue(analise_data([100, 500, 600, 100, 600]))
        self.assertTrue(analise_data([100, 500, 600, 700]))
        self.assertTrue(analise_data([100, 0, 500, 600, 100, 700]))
        self.assertTrue(analise_data([100, 0, 0, 600, 700, 600]))
        self.assertTrue(analise_data([100, 500, 600, 100, 300, 450, 400, 500]))
        self.assertTrue(analise_data([100, 500, 600, 100, 300, 400, 500, 500]))

    def test_incorect_variance(self):
        self.assertFalse(analise_data([100, 500, 600, 100, 300, 500, 400, 500]))
        self.assertFalse(analise_data([100, 0, 500, 600, 100, 10, 700]))

    def test_monitoring(self):
        ResultDayDci.objects.all().delete()
        for i in range(5):
            VarianceMonitoringTest.results[i].save()
            count_day = ResultDayDci.objects.filter(user=1).count()
            data = ResultDayDci.objects.filter(user=1).order_by('date')
            if count_day == 1:
                avg_dci = data[0].calories
            elif count_day in (2, 3):
                avg_dci = data[1].calories
            else:
                avg_dci = int(
                    (ResultDayDci.objects.filter(user=1)
                    .order_by('date')[1:len(data)-1]
                    .aggregate(Avg('calories'))
                    .get('calories__avg'))
                )
            self.assertEqual(avg_dci, self.right_avg_dci[i+1])
