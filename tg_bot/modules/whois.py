import html
import json
import os
import psutil
import random
import time
import datetime
from typing import Optional, List
import re
import requests
from telegram.error import BadRequest
from telegram import Message, Chat, Update, Bot, MessageEntity
from telegram import ParseMode
from telegram.ext import CommandHandler, run_async, Filters
from telegram.utils.helpers import escape_markdown, mention_html
from tg_bot.modules.helper_funcs.chat_status import user_admin, sudo_plus, is_user_admin
from tg_bot import dispatcher, OWNER_ID, SUDO_USERS, SUPPORT_USERS, DEV_USERS, WHITELIST_USERS
from tg_bot.__main__ import STATS, USER_INFO, TOKEN
from tg_bot.modules.disable import DisableAbleCommandHandler, DisableAbleRegexHandler
from tg_bot.modules.helper_funcs.extraction import extract_user
from tg_bot.modules.helper_funcs.filters import CustomFilters
import tg_bot.modules.sql.users_sql as sql
import tg_bot.modules.helper_funcs.cas_api as cas

@run_async
def whois(bot: Bot, update: Update, args: List[str]):
    message = update.effective_message
    chat = update.effective_chat
    user_id = extract_user(update.effective_message, args)

    if user_id:
        user = bot.get_chat(user_id)

    elif not message.reply_to_message and not args:
        user = message.from_user

    elif not message.reply_to_message and (not args or (
            len(args) >= 1 and not args[0].startswith("@") and not args[0].isdigit() and not message.parse_entities(
        [MessageEntity.TEXT_MENTION]))):
        message.reply_text("I can't extract a user from this.")
        return

    else:
        return
    
    text = (f"<b>ð¨ð¦ðð¥ ðð¡ðð¢ð¥ð ðð§ðð¢ð¡</b>\n"
            f"Éªá´ : <code>{user.id}</code>\n"
            f" â É´á´á´á´: {html.escape(user.first_name)}")

    if user.last_name:
        text += f"\nââÊá´sá´ É´á´á´á´: {html.escape(user.last_name)}"

    if user.username:
        text += f"\nâ á´sá´ÊÉ´á´á´á´: @{html.escape(user.username)}"

    text += f"\nâ ÉªÉ´ÊÉªÉ´á´ á´á´É´á´Éªá´É´: {mention_html(user.id, 'linkð©')}"

    num_chats = sql.get_user_num_chats(user.id)
    text += f"\nâ á´Êá´á´ á´á´á´É´á´: <code>{num_chats}</code>"
    text += "\nâ É´á´ á´Ò á´Êá´ÒÉªÊá´ á´Éªá´s: {}".format(bot.get_user_profile_photos(user.id).total_count)
   
    try:
        user_member = chat.get_member(user.id)
        if user_member.status == 'administrator':
            result = requests.post(f"https://api.telegram.org/bot{TOKEN}/getChatMember?chat_id={chat.id}&user_id={user.id}")
            result = result.json()["result"]
            if "custom_title" in result.keys():
                custom_title = result['custom_title']
                text += f"\nâ This user holds the titleâª <b>{custom_title}</b> here."
    except BadRequest:
        pass

   

    if user.id == OWNER_ID:
        text += "\nð¶ð»ââï¸Uff,ð  á´ÊÉªs á´á´Êsá´É´ Éªs á´Ê á´á´¡É´á´Ê , Éª á´á´É´'á´ á´á´ á´É´Êá´ÊÉªÉ´É¢ á´É¢á´ÉªÉ´sá´ ÊÉªá´! ð !."
        
    elif user.id in DEV_USERS:
        text += "\nð´ââï¸Pling,ð  á´ÊÉªs á´á´Êsá´É´ Éªs á´Ê á´á´á´ á´Êá´á´á´Ê , Éª á´á´É´'á´ á´á´ á´É´Êá´ÊÉªÉ´É¢ á´É¢á´ÉªÉ´sá´ ÊÉªá´! ð  ."
        
    elif user.id in SUDO_USERS:
        text += "\nð´ââï¸Pling,This person is one of my sudo users! " \
                    "Nearly as powerful as my ownerðso watch it.."
        
    elif user.id in SUPPORT_USERS:
        text += "\nð´ââï¸Pling,This person is one of my support users! " \
                        "Not quite a sudo user, but can still gban you off the map."
        
  
       
    elif user.id in WHITELIST_USERS:
        text += "\nð´ââï¸Pling,This person has been whitelisted! " \
                        "That means I'm not allowed to ban/kick them."
    


    text +="\n"
    text += "\nCAS banned: "
    result = cas.banchecker(user.id)
    text += str(result)
    for mod in USER_INFO:
        if mod.__mod_name__ == "Who Is":
            continue

        try:
            mod_info = mod.__user_info__(user.id)
        except TypeError:
            mod_info = mod.__user_info__(user.id, chat.id)
        if mod_info:
            text += "\n" + mod_info
    try:
        profile = bot.get_user_profile_photos(user.id).photos[0][-1]
        bot.sendChatAction(chat.id, "upload_photo")
        bot.send_photo(chat.id, photo=profile, caption=(text), parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    except IndexError:
        update.effective_message.reply_text(text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)

WHOIS_HANDLER = DisableAbleCommandHandler("whois", whois, pass_args=True)
dispatcher.add_handler(WHOIS_HANDLER)