from datetime import datetime, timezone, timedelta
from model.models import User


async def get_user_datetime(offset=None, utc_datetime=None, user=None):
    if utc_datetime is None:
        return datetime.now(timezone(timedelta(hours=offset)))
    else:
        offset = user.offset
        return utc_datetime + timedelta(hours=offset)


async def get_normal_dci(id, phase1, cur_day):
    user = await User.objects.aget(id=id)
    user_target = await user.target.alast()

    if cur_day > phase1:
        return user_target.dci * (1 - user_target.percentage_decrease / 100)
    else:
        if cur_day % 7 == 0:
            number_week = cur_day // 7
        else:
            number_week = cur_day // 7 + 1
        tmp = user_target.cur_dci - 100 * number_week
        if tmp < user_target.dci:
            tmp = user_target.dci
        return tmp
