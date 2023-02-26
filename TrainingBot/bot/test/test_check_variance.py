from django.test import TestCase
from django.db.models import Avg
from datetime import datetime
from model.models import ResultDayDci, User
from bot.Button import check_variance


class VarianceMonitoringTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            id=1
        )
        self.results = [
            ResultDayDci(
                user=self.user,
                time=datetime(2023, 2, 23, 23, 53, 29),
                calories=150
            ),
            ResultDayDci(
                user=self.user,
                time=datetime(2023, 2, 26, 23, 53, 29),
                calories=550
            ),
            ResultDayDci(
                user=self.user,
                time=datetime(2023, 2, 28, 23, 53, 29),
                calories=500
            ),
            ResultDayDci(
                user=self.user,
                time=datetime(2023, 3, 1, 23, 53, 29),
                calories=600
            ),
            ResultDayDci(
                user=self.user,
                time=datetime(2023, 3, 3, 23, 53, 29),
                calories=0
            ),
            ResultDayDci(
                user=self.user,
                time=datetime(2023, 3, 4, 23, 53, 29),
                calories=0
            )
        ]
        self.right_avg_dci = {
            1: 150,
            2: 550,
            3: 550,
            4: 525,
            5: 550
        }
        self.result_dci = ResultDayDci.objects.bulk_create(self.results)

    def test_right_variance(self):
        self.assertTrue(check_variance(1))

    def test_incorect_variance(self):
        self.result_dci[3].calories = 0
        self.result_dci[3].save()
        self.assertFalse(False)

    def test_incorect_time(self):
        self.result_dci[1].time = datetime(2023, 2, 25, 23, 53, 29)
        self.result_dci[3].save()
        self.assertFalse(False)

    def test_monitoring(self):
        ResultDayDci.objects.all().delete()
        for i in range(5):
            self.results[i].save()
            count_day = ResultDayDci.objects.filter(user=1).count()
            data = ResultDayDci.objects.filter(user=1).order_by('time')
            if count_day == 1:
                avg_dci = data[0].calories
            elif count_day in (2, 3):
                avg_dci = data[1].calories
            else:
                avg_dci = int(
                    (ResultDayDci.objects.filter(user=1)
                    .order_by('time')[1:len(data)-1]
                    .aggregate(Avg('calories'))
                    .get('calories__avg'))
                )
            self.assertEqual(avg_dci, self.right_avg_dci[i+1])
