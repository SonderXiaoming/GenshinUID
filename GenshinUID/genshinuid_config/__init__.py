import re

from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event

from ..utils.database import get_sqla
from ..utils.error_reply import UID_HINT
from .draw_config_card import draw_config_img
from .set_config import set_push_value, set_config_func

sv_self_config = SV('原神配置')


@sv_self_config.on_fullmatch(('gs配置', '原神配置'))
async def send_config_card(bot: Bot, ev: Event):
    await bot.logger.info('开始执行[gs配置]')
    im = await draw_config_img(ev.bot_id)
    await bot.send(im)


@sv_self_config.on_prefix(('gs设置'))
async def send_config_ev(bot: Bot, ev: Event):
    await bot.logger.info('开始执行[设置阈值信息]')

    sqla = get_sqla(ev.bot_id)
    uid = await sqla.get_bind_uid(ev.user_id)
    if uid is None:
        return await bot.send(UID_HINT)

    func = ''.join(re.findall('[\u4e00-\u9fa5]', ev.text.replace('阈值', '')))
    value = re.findall(r'\d+', ev.text)
    value = value[0] if value else None

    if value is None:
        return await bot.send('请输入正确的阈值数字...')

    await bot.logger.info('[设置阈值信息]func: {}, value: {}'.format(func, value))
    im = await set_push_value(ev.bot_id, func, uid, int(value))
    await bot.send(im)


# 开启 自动签到 和 推送树脂提醒 功能
@sv_self_config.on_prefix(('gs开启', 'gs关闭'))
async def open_switch_func(bot: Bot, ev: Event):
    sqla = get_sqla(ev.bot_id)
    user_id = ev.user_id
    config_name = ev.text

    await bot.logger.info(f'[{user_id}]尝试[{ev.command[2:]}]了[{ev.text}]功能')

    if ev.command == 'gs开启':
        query = True
        gid = ev.group_id if ev.group_id else 'on'
    else:
        query = False
        gid = 'off'

    is_admin = ev.user_pm <= 2
    if ev.at and is_admin:
        user_id = ev.at
    elif ev.at:
        return await bot.send('你没有权限...')

    uid = await sqla.get_bind_uid(ev.user_id)
    if uid is None:
        return await bot.send(UID_HINT)

    im = await set_config_func(
        ev.bot_id,
        config_name=config_name,
        uid=uid,
        user_id=user_id,
        option=gid,
        query=query,
        is_admin=is_admin,
    )
    await bot.send(im)
