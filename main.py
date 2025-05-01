from telebot import TeleBot, types
from threading import Thread
import time
import sqlalchemy
import sqlite3
import random
import schedule
from threading import Thread
import time
import config
from database import Session, User


from database import create_all_table
import models

create_all_table()

TOKEN = 
bot = TeleBot(TOKEN)

start_kb = types.InlineKeyboardMarkup()
btn = types.InlineKeyboardButton("Начать игру", callback_data="start_game")
start_kb.row(btn)
kb = types.InlineKeyboardMarkup()


@bot.message_handler(commands=["start"])
def handle_start(msg: types.Message):

    bot.send_message(
        msg.chat.id,
        "Привет! Я единственная, неповторимая, лучшая RPG игра в телеграмме",
        reply_markup=start_kb,
    )

    def handle_start(message):
        session = Session()
    
        # Проверяем, есть ли пользователь в базе
        user = session.query(User).filter_by(user_id=message.from_user.id).first()
        
        if not user:
            # Создаем нового пользователя
            new_user = User(
                user_id=message.from_user.id,
                username=message.from_user.username,
                race='Не выбран',
            )
            session.add(new_user)
            session.commit()
            bot.reply_to(message, "✅ Вы зарегистрированы в игре!")
        else:
            bot.reply_to(message, f"С возвразением, {user.username}!")


@bot.callback_query_handler(lambda call: call.data == "start_game")
def handle_start_game(call: types.CallbackQuery):
    bot.delete_message(call.message.chat.id, call.message.id)
    bot.send_message(
        call.message.chat.id,
        "Поздравляю! Ты начал игру!\n" "Придумай имя своему персонажу: ",
            reply_markup=kb,
    )
    bot.register_next_step_handler(call.message, process_name)


def process_name(message: types.Message):
    user_name = message.text

    kb =types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("люди",callback_data="race:люди"),
        types.InlineKeyboardButton("эльфы",callback_data="race:эльфы"),
        types.InlineKeyboardButton("Вервольфы",callback_data="race:Вервольфы"),
        types.InlineKeyboardButton("Вампиры",callback_data="race:Вампиры"),
        types.InlineKeyboardButton("Скелеты",callback_data="race:Скелеты"),
    )

    bot.send_message(
        message.chat.id,
        f"Отличное имя, {user_name}! Теперь выбери свою расу:\n"
        "1. Люди\n"
"⚔️ +10% к урону мечом\n"
"💼 Начинают с дополнительным золотом\n"
"🎯 Нет особых слабостей\n"
"\n"
"2. Эльфы"
"🌿 +20% к магии\n"
"🛡️🌿 20% иммунитет к магии\n"
"⚔️  Слабы к ближнему оружию(на 10% урона больше)\n"
"\n"
"3. Вервольфы\n"
"🐺 +25% к урону в ночное время\n"
"⚔️ Слабы к серебряному оружию(на 15% урона больше )\n"
"\n"
"4. Вампиры\n"
"🦇 Пьют кровь врагов (+3HP за удар)\n"
"🌞 Горят на солнце (-2 HP/ход при свете дня)\n" \
"⚔️ Слабы к серебряному оружию(на 20% урона больше)\n"
"\n"
"5. Скелеты\n"
"💀 Иммунитет к дебафам\n"
"🛡️➖ получают на 10% больше урона\n",
        reply_markup=kb,
    )


@bot.callback_query_handler(func=lambda callback: callback.data.startswith("race"))
def handle_callback(callback: types.CallbackQuery):
    _, race = callback.data.split(":")
    
    if race == "люди":
        # Создаем клавиатуру для продолжения
        continue_kb = types.InlineKeyboardMarkup()
        continue_kb.add(types.InlineKeyboardButton("Продолжить", callback_data="start_adventure"))
        
        # Отправляем сообщение с предысторией
        bot.send_message(
            callback.message.chat.id,
            "Ну вот теперь ты точно начал игру!\n\n" 
            "📜 *Предыстория:*\n"
            "Ты всю жизнь служил королю верой и правдой, но в один момент провалил одно единственное, "
            "но очень важное задание.\n\n"
            "Король приказал казнить тебя, но тебе удалось сбежать и скрыться в толпе людей в салуне, "
            "где ты немного выпил.\n\n"
            "После этого тебя во второй раз нашли стражи, но и в этот раз тебе удалось сбежать. "
            "Ты убежал далеко в лес, где отключился, а когда проснулся - понял, что тебя ограбили. "
            "Оставили тебе только меч и 5 золотых, которые они не нашли.\n\n"
            "Так и началась твоя история...",
            parse_mode="Markdown",
            reply_markup=continue_kb
        )
        
        # Удаляем предыдущее сообщение с выбором расы
        bot.delete_message(callback.message.chat.id, callback.message.message_id)


    elif race == "эльфы":
        # Создаем клавиатуру для продолжения
        continue_kb = types.InlineKeyboardMarkup()
        continue_kb.add(types.InlineKeyboardButton("Продолжить", callback_data="start_adventure"))
        
        # Отправляем сообщение с предысторией
        bot.send_message(
            callback.message.chat.id,    "🌿 *Ну вот теперь ты точно начал игру!*\n\n"
    "📖 *Предыстория:*\n"
    "Ты - лесной эльф 🌳, который всю жизнь провёл в древних рощах. "
    "Ты хорошо овладел каждым типом магии, но тебе еще сть куда стемиться.\n"
    "🍃 Ты настолько погрузился в гормонию с лесом что мог разговаривать с деревьями...\n\n"
    "🔥 *Чёрный день:*\n"
    "Люди подожгли твой родной лес 🌲🔥. Ты видел, как гибнут вековые деревья, "
    "а твои сородичи бегут в ужасе...\n\n"
    "🚶 *Новый путь:*\n"
    "С пеплом в волосах и болью в сердце 💔 ты покинул это место. "
    "Теперь ты странник без дома, но с твёрдой целью в сердце.\n\n"
    "✨ *И именно с этого момента начинается твоё настоящее приключение...*"
        )
        # Удаляем предыдущее сообщение с выбором расы
        bot.delete_message(callback.message.chat.id, callback.message.message_id)


    elif race == "Вервольфы":
        # Создаем клавиатуру для продолжения
        continue_kb = types.InlineKeyboardMarkup()
        continue_kb.add(types.InlineKeyboardButton("Продолжить", callback_data="start_adventure"))
        
        # Отправляем сообщение с предысторией
        bot.send_message(
            callback.message.chat.id,
    "🐺 Ну вот теперь ты точно начал игру!\n\n"
    "📜 Предыстория: днем ты обычный житель города 🏙️, но ночью ты превращаешься в свирепого волка 🌕!\n"
    "😤 Но ты всю ночь вынужден прятаться в огромном замке Дракулы 🏰...\n\n"
    "💢 Наконец ты устал от этого двуличия 😫, хотел показать людям, что во втором обличии ты безопасен 👐,\n"
    "🔥 но они не захотели тебя слушать — хотели сжечь! 😱\n"
    "🏃 Ты смог убежать... и теперь намерен отомстить! ⚔️\n\n"
    "🚀 Вот так ты и начнешь свое приключение!",
    parse_mode="Markdown")
        # Удаляем предыдущее сообщение с выбором расы
        bot.delete_message(callback.message.chat.id, callback.message.message_id)


        
    elif race == "Скелеты":
        # Создаем клавиатуру для продолжения
        continue_kb = types.InlineKeyboardMarkup()
        continue_kb.add(types.InlineKeyboardButton("Продолжить", callback_data="start_adventure"))
        
        # Отправляем сообщение с предысторией
        bot.send_message(
            callback.message.chat.id,"🦴 *Ну вот теперь ты точно начал игру!*\n\n"
    "📜 *Предыстория:*\n"
    "Ты был обычным смертным, страстно желавшим обрести бессмертие. Но коварная ведьма обманом наложила на тебя "
    "роковое проклятие, превратив в ходячий скелет.\n\n"
    "☠️ *Твои отчаянные попытки:*\n"
    "• Пил смертельные яды... но они просто вытекали сквозь ребра\n"
    "• Прыгал с высочайших утёсов... но кости собирались вновь\n"
    "• Умолял магов стереть твою душу... но проклятие оказалось сильнее\n\n"
    "💀 *Теперь ты обречён:*\n"
    "Вечно существовать в жутком полумраке между жизнью и смертью, "
    "где нет ни покоя, ни забвения...\n\n"
    "🌑 *И именно с этого момента начинаются твои поиски...*",
    parse_mode="Markdown"
)

        bot.delete_message(callback.message.chat.id, callback.message.message_id)


    elif race == "Вампиры":
        # Создаем клавиатуру для продолжения
        continue_kb = types.InlineKeyboardMarkup()
        continue_kb.add(types.InlineKeyboardButton("Продолжить", callback_data="start_adventure"))
        
        # Выбираем случайную предысторию
        backstories = [
            # Первый вариант (ваш оригинальный)
            "Ну вот теперь ты точно начал игру!\n\n"
            "📜 *Предыстория:*\n"
            "Ты когда-то был смертным, но однажды ночью тебя нашли древние вампиры - или, может, ты сам искал силу, "
            "продав душу за бессмертие?\n\n"
            "Теперь ты и твоя душа принадлежите тьме. Солнце жжёт твою кожу, святая вода оставляет ожоги, "
            "а в зеркалах не отражается душа... только пустота.\n\n"
            "Но жажда крови - не просто проклятие, а дар. Ты чувствуешь, как жизнь других пульсирует в их венах, "
            "зовёт тебя, манит...\n\n"
            "Вот так ты и начнёшь своё приключение.",
            
            # Второй вариант (ваш расширенный)
            '*📜 Путь в Бессмертие:*\n'
'Будучи обворованным и отчаявшимся, ты поверил \n'
'незнакомцу в алых одеждах. Его обещания *золота и власти* \n'
'привели тебя в замок, где:\n'

'*👑 В зале с паутиной на троне сидел... Он.*\n'
'"Хочешь ли ты *вечности*?" — прошелестели его губы. \n'
'Твой кивок стал роковым. \n'

'*🦇 Преображение:*\n'
'Его клыки впились в шею... Боль сменилась *экстазом*, \n'
'а наутро — *агонией* первого солнечного луча. \n'

'*💀 Теперь ты знаешь правду:*\n'
'Тот незнакомец был *Дракулой*, \n'
'а твоя "награда" — вечная жажда крови.'
        ]
        
        # Выбираем случайную историю
        selected_story = random.choice(backstories)
        
        # Отправляем сообщение
        bot.send_message(
            callback.message.chat.id,
            selected_story,
            parse_mode="Markdown",
            reply_markup=continue_kb
        )
        
        # Удаляем предыдущее сообщение
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        


# @bot.callback_query_handler(func=lambda callback: callback.data.startswith("race"))
# def handle_callback(callback: types.CallbackQuery):
#     kb = types.InlineKeyboardMarkup()

#     _, race = callback.data.split(":")
#     if race == "человек":
#         kb.add(
#             types.InlineKeyboardButton("Бретонцы", callback_data="subrace:бретонцы"),
#             types.InlineKeyboardButton("Имперцы", callback_data="subrace:Имперцы"),
#             types.InlineKeyboardButton("Норды", callback_data="subrace:Норды"),
#             types.InlineKeyboardButton("Редгарды", callback_data="subrace:Редгарды"),
#         )

#     if race == "эльф":
#         kb.add(
#             types.InlineKeyboardButton("Альтмеры (высокие эльфы)", callback_data="subrace:Альтмеры (высокие эльфы)"),
#             types.InlineKeyboardButton("Босмеры (лесные эльфы)", callback_data="subrace:Босмеры (лесные эльфы)"),
#             types.InlineKeyboardButton( "Данмеры (тёмные эльфы)", callback_data="subrace:Данмеры (тёмные эльфы)" ),
#             types.InlineKeyboardButton( "Орки (орсимеры)", callback_data="subrace:Орки (орсимеры)" ),    
#         )


#     if race == "зверочеловек":
#         kb.add(
#             types.InlineKeyboardButton("Каджиты", callback_data="subrace:Каджиты"),
#             types.InlineKeyboardButton("Аргониане", callback_data="subrace:Аргониане"),
#             types.InlineKeyboardButton("Оборотень", callback_data="subrace:Оборотень"),
#             types.InlineKeyboardButton("Кентавр", callback_data="subrace:Кентавр"),
#         )
#         if subrace == "Каджиты":
#             description = (
#             "Бафы расы:\n"
#             "наносят повышенный урон без оружия (15 урона),\n"
#             "могут обыскивать самые темные закоулки при помощи ночного зрения"
#         )
#     elif subrace == "Аргониане":
#         description = "Описание аргониан..."
#     # Добавьте описания для других подрас
    
#     kb = types.InlineKeyboardMarkup()
#     kb.add(types.InlineKeyboardButton("Назад", callback_data="back:race"))
    
#     bot.edit_message_text(
#         chat_id=callback.message.chat.id,
#         message_id=callback.message.id,
#         text=f"{subrace}\n\n{description}",
#         reply_markup=kb
#     )

#     kb.add(types.InlineKeyboardButton("Назад", callback_data="back:race"))

#     bot.edit_message_reply_markup(
#         callback.message.chat.id, callback.message.id, reply_markup=kb
#     )


# @bot.callback_query_handler(func=lambda callback: callback.data.startswith("back"))
# def handle_back_btn(call: types.CallbackQuery):
#     _, target = call.data.split(":")
#     if target == "race":
#         kb = types.InlineKeyboardMarkup().add(
#             types.InlineKeyboardButton("Человеческие расы", callback_data="race:человек"),
#             types.InlineKeyboardButton("Эльфийские расы", callback_data="race:эльф"),
#             types.InlineKeyboardButton("Зверорасы", callback_data="race:зверочеловек"),
#         )
#         bot.edit_message_reply_markup(
#             call.message.chat.id, call.message.id, reply_markup=kb
#         )


bot.infinity_polling()
