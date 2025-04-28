from telebot import TeleBot, types
from threading import Thread
import time
import sqlalchemy
import sqlite3


from database import create_all_table
import models

create_all_table()

TOKEN = 
bot = TeleBot(TOKEN)

start_kb = types.InlineKeyboardMarkup()
btn = types.InlineKeyboardButton("Начать игру", callback_data="start_game")
start_kb.row(btn)


@bot.message_handler(commands=["start"])
def handle_start(msg: types.Message):

    bot.send_message(
        msg.chat.id,
        "Привет! Я единственная, неповторимая, лучшая RPG игра в телеграмме",
        reply_markup=start_kb,
    )


@bot.callback_query_handler(lambda call: call.data == "start_game")
def handle_start_game(call: types.CallbackQuery):
    bot.delete_message(call.message.chat.id, call.message.id)
    bot.send_message(
        call.message.chat.id,
        "Поздравляю! Ты начал игру!\n" "Придумай имя своему персонажу: ",
        # reply_markup=kb,
    )
    bot.register_next_step_handler(call.message, process_name)


def process_name(message: types.Message):
    user_name = message.text

    kb = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("Человеческие расы", callback_data="race:человек"),
        types.InlineKeyboardButton("Эльфийские расы", callback_data="race:эльф"),
        types.InlineKeyboardButton("Зверорасы", callback_data="race:зверочеловек"),
    )

    bot.send_message(
        message.chat.id,
        f"Отличное имя, {user_name}! Теперь выбери свою расу",
        reply_markup=kb,
    )


@bot.callback_query_handler(func=lambda callback: callback.data.startswith("race"))
def handle_callback(callback: types.CallbackQuery):
    kb = types.InlineKeyboardMarkup()

    _, race = callback.data.split(":")
    if race == "человек":
        kb.add(
            types.InlineKeyboardButton("Бретонцы", callback_data="subrace:бретонцы"),
            types.InlineKeyboardButton("Имперцы", callback_data="subrace:Имперцы"),
            types.InlineKeyboardButton("Норды", callback_data="subrace:Норды"),
            types.InlineKeyboardButton("Редгарды", callback_data="subrace:Редгарды"),
        )

    if race == "эльф":
        kb.add(
            types.InlineKeyboardButton("Альтмеры (высокие эльфы)", callback_data="subrace:Альтмеры (высокие эльфы)"),
            types.InlineKeyboardButton("Босмеры (лесные эльфы)", callback_data="subrace:Босмеры (лесные эльфы)"),
            types.InlineKeyboardButton( "Данмеры (тёмные эльфы)", callback_data="subrace:Данмеры (тёмные эльфы)" ),
            types.InlineKeyboardButton( "Орки (орсимеры)", callback_data="subrace:Орки (орсимеры)" ),    
        )


    if race == "зверочеловек":
        kb.add(
            types.InlineKeyboardButton("Каджиты", callback_data="subrace:Каджиты"),
            types.InlineKeyboardButton("Аргониане", callback_data="subrace:Аргониане"),
            types.InlineKeyboardButton("Оборотень", callback_data="subrace:Оборотни"),
            types.InlineKeyboardButton("Кентавр", callback_data="subrace:Кентавр"),
        )

    kb.add(types.InlineKeyboardButton("Назад", callback_data="back:race"))

    bot.edit_message_reply_markup(
        callback.message.chat.id, callback.message.id, reply_markup=kb
    )


@bot.callback_query_handler(func=lambda callback: callback.data.startswith("back"))
def handle_back_btn(call: types.CallbackQuery):
    _, target = call.data.split(":")
    if target == "race":
        kb = types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton(
                "Человеческие расы", callback_data="race:человек"),
            types.InlineKeyboardButton("Эльфийские расы", callback_data="race:эльф"),
            types.InlineKeyboardButton("Зверорасы", callback_data="race:зверочеловек"),
        )
        bot.edit_message_reply_markup(
            call.message.chat.id, call.message.id, reply_markup=kb
        )


bot.infinity_polling()
