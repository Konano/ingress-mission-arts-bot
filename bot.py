import asyncio
# import random
# import time
from http import HTTPStatus
# from typing import cast
# from threading import Thread

import uvicorn
from asgiref.wsgi import WsgiToAsgi
from flask import Flask, Response, abort, make_response, request
from telegram import (BotCommandScopeAllGroupChats, BotCommandScopeChat,
                      Update)
from telegram.ext import (Application, CallbackContext, CallbackQueryHandler,
                          CommandHandler, ContextTypes, ConversationHandler,
                          ExtBot, InlineQueryHandler, JobQueue, MessageHandler,
                          MessageReactionHandler, TypeHandler, filters)
# from telegram.ext.filters import UpdateType

from base import network
from base.config import GROUP, SERVER, WEBHOOK, accessToken, owner
from base.data import localDict
from base.debug import eprint
from base.format import escaped
from base.log import UNICORN_LOGGING_CONFIG, logger

bnrs = localDict('bnrs', default={})


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error for debuging."""
    logger.error("Exception while handling an update: %s", context.error)
    logger.debug(msg="The traceback of the exception:", exc_info=context.error)

    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    logger.debug(update_str)


async def test(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    assert update.message
    await update.message.reply_html(text="This is a test message.")

HEADERS = {
    "accept": "application/json",
    "accept-language": "en",
    "origin": "https://bannergress.com",
    "priority": "u=1, i",
    "referer": "https://bannergress.com/",
    "sec-ch-ua": '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
}


async def query_place(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    assert update.effective_message
    try:
        assert context.args is not None
        resp = await network.get_json('https://api.bannergress.com/places', params={
            "used": "true",
            "collapsePlaces": "true",
            "query": ' '.join(context.args),
            "limit": 9,
            "offset": 0
        }, headers=HEADERS)
        if len(resp) == 0:
            await update.effective_message.reply_text('没有找到相关地点')
            return
        place = resp[0]
        resp = await network.get_json('https://api.bannergress.com/bnrs', params={
            "orderBy": "created",
            "orderDirection": "DESC",
            "online": "true",
            "placeId": place['id'],
            "limit": 31,
            "offset": 0
        }, headers=HEADERS)
        assert len(resp)
        lines = [escaped(place['formattedAddress']), '']
        for bnr in resp[:30]:
            if bnr['id'] in bnrs:
                lines.append(f"📌 [{escaped(bnr['title'])}](https://t.me/IngressMedalArts/{bnrs[bnr['id']]['msgID']})")
            else:
                lines.append(f"📌 `/q {escaped(bnr['title'])}`")
        if len(resp) > 30:
            lines.append(escaped('...'))
        await update.effective_message.reply_text('\n'.join(lines), parse_mode='MarkdownV2', disable_web_page_preview=True)

    except Exception as e:
        await update.effective_message.reply_text('在查询过程中发生错误')
        eprint(e)


async def query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    assert update.effective_message
    try:
        assert context.args is not None
        resp = await network.get_json('https://api.bannergress.com/bnrs', params={
            "orderBy": "relevance",
            "orderDirection": "DESC",
            "online": "true",
            "query": ' '.join(context.args),
            "limit": 31,
            "offset": 0
        }, headers=HEADERS)
        if len(resp) == 0:
            await update.effective_message.reply_text('没有找到相关任务')
            return
        bnr = None
        if len(resp) == 1:
            bnr = resp[0]
        else:
            # 检查是否有任务名完全匹配
            _resp = [b for b in resp if b['title'] == ' '.join(context.args)]
            if len(_resp):
                bnr = _resp[0]
            else:
                # 检测是否有任务名包含关键词
                _resp = [b for b in resp if all(x in b['title'] for x in context.args)]
                if len(_resp) == 1:
                    bnr = _resp[0]
        if bnr is not None:
            if bnr['id'] not in bnrs:
                lines = [
                    f'[{escaped(bnr["title"])}](https://bannergress.com/banner/{bnr["id"]}) / {escaped(bnr["formattedAddress"])}',
                    # '',
                    # '任务路线：',
                    # '任务性质：',
                    # '典型完成时间：',
                    # '建议交通方式：',
                    # '注意方式：',
                ]
                msg = await context.bot.send_message(
                    chat_id='@IngressMedalArts',
                    text='\n'.join(lines),
                    parse_mode='MarkdownV2',
                )
                msgID = msg.message_id
                bnrs[bnr['id']] = bnr
                bnrs[bnr['id']]['msgID'] = msgID
                bnrs.dump()
                # await update.effective_message.reply_text(
                #     text=f'任务已创建: https://t.me/IngressMedalArts/{msgID}'
                # )
            else:
                msgID = bnrs[bnr['id']]['msgID']
                await update.effective_message.reply_text(
                    text=f'任务已存在: https://t.me/IngressMedalArts/{msgID}'
                )
        else:
            lines = []
            for bnr in resp[:30]:
                if bnr['id'] in bnrs:
                    lines.append(f"📌 [{escaped(bnr['title'])}](https://t.me/IngressMedalArts/{bnrs[bnr['id']]['msgID']})")
                else:
                    lines.append(f"📌 `/q {escaped(bnr['title'])}`")
            if len(resp) > 30:
                lines.append(escaped('...'))
            await update.effective_message.reply_text('\n'.join(lines), parse_mode='MarkdownV2', disable_web_page_preview=True)

    except Exception as e:
        await update.effective_message.reply_text('在查询过程中发生错误')
        eprint(e)


async def self_unpin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Unpin the message if it is pinned by the bot itself."""
    assert update.effective_message
    msg = update.effective_message
    try:
        if msg.entities and msg.entities[0].url and 'https://bannergress.com/banner/' in msg.entities[0].url:
            await msg.unpin()
    except Exception as e:
        eprint(e)


async def main() -> None:
    """Set up PTB application and a web application for handling the incoming requests."""
    # Here we set updater to None because we want our custom webhook server to handle the updates
    # and hence we don't need an Updater instance
    app = Application.builder().token(
        accessToken).updater(None).read_timeout(20).build()

    app.add_error_handler(error_handler)

    user_owner = filters.Chat(owner)
    main_group = filters.Chat(GROUP['main'])
    filter = user_owner | main_group

    # job: JobQueue = app.job_queue
    # jk = {"misfire_grace_time": None}  # job_kwargs

    # register handlers
    app.add_handler(CommandHandler('test', test, filters=filter))
    app.add_handler(CommandHandler('p', query_place, filters=filter))
    app.add_handler(CommandHandler('q', query, filters=filter))

    app.add_handler(MessageHandler(filters.IS_AUTOMATIC_FORWARD & main_group, self_unpin))
    
    commands = []
    commands.append(('q', '查询任务', 1))
    commands.append(('p', '根据城市查询任务（英文地名）', 2))
    await app.bot.set_my_commands(commands, scope=BotCommandScopeChat(owner))
    await app.bot.set_my_commands(commands, scope=BotCommandScopeChat(GROUP['main']))

    # Pass webhook settings to telegram
    await app.bot.set_webhook(**WEBHOOK)

    # Set up webserver
    flask_app = Flask(__name__)

    @flask_app.post("/telegram")
    async def telegram() -> Response:
        """Handle incoming Telegram updates by putting them into the `update_queue`"""
        if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != WEBHOOK["secret_token"]:
            abort(HTTPStatus.FORBIDDEN, "Where are you from?")
        await app.update_queue.put(Update.de_json(data=request.json, bot=app.bot))
        return Response(status=HTTPStatus.OK)

    @flask_app.get("/healthcheck")
    async def health() -> Response:
        """For the health endpoint, reply with a simple plain text message."""
        response = make_response(
            "The bot is still running fine :)", HTTPStatus.OK)
        response.mimetype = "text/plain"
        return response

    webserver = uvicorn.Server(
        config=uvicorn.Config(
            app=WsgiToAsgi(flask_app),
            log_config=UNICORN_LOGGING_CONFIG,
            **SERVER,
        )
    )

    # Run application and webserver together
    async with app:
        await app.start()
        await webserver.serve()
        await app.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
