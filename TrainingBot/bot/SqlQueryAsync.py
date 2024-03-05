from model.models import User, UserStageGuide, InfoUser


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
    id = message.chat.id
    info_user = await InfoUser.objects.aget(user=id)
    return info_user
