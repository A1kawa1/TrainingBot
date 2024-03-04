from model.models import *


async def get_user(param):
    res_data = []
    data = User.objects.values_list(param, flat=True)
    async for value in data:
        res_data.append(value)
    return data


async def get_stage(id):
    user_stage_guide = await UserStageGuide.objects.aget(user=id)
    return user_stage_guide.stage


async def get_info(message):
    if message.from_user.is_bot:
        id = message.chat.id
    else:
        id = message.from_user.id

    info_user = await InfoUser.objects.aget(user=id)
    return info_user
