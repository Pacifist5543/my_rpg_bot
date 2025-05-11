from telebot import TeleBot, types
from threading import Thread
from threading import Thread
from database import Session
from database import create_all_table
from database import User
import random
from sqlalchemy import update


session = Session()
create_all_table()
way = 0

TOKEN = 
bot = TeleBot(TOKEN)

start_kb = types.InlineKeyboardMarkup()
btn = types.InlineKeyboardButton("Начать игру", callback_data="start_game")
start_kb.row(btn)
kb = types.InlineKeyboardMarkup()
continue_kb = types.InlineKeyboardMarkup()
continue_kb.add(
    types.InlineKeyboardButton("Продолжить", callback_data="contenur_adventure")
)


@bot.message_handler(commands=["start"])
def handle_start(msg: types.Message):

    # Проверяем, есть ли пользователь в базе
    user = session.query(User).filter_by(user_id=msg.from_user.id).first()

    if not user:
        bot.send_message(
            msg.chat.id,
            "Привет! Я единственная, неповторимая, лучшая RPG игра в телеграмме",
            reply_markup=start_kb,
        )
        # Создаем нового пользователя
        new_user = User(
            user_id=msg.from_user.id,
            username=msg.from_user.username,
            race="Не выбран",
        )
        session.add(new_user)
        session.commit()
    else:
        bot.send_message(
            msg.chat.id,
            f"С возвращением, {user.race}, {user.nickname}!",
            reply_markup=continue_kb,
        )

    all_users = session.query(User).all()
    for user in all_users:
        print(f"{user.user_id} ({user.username})")


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
    session.query(User).filter(User.user_id == message.from_user.id).update(
        {"nickname": user_name}
    )
    session.commit()

    kb = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("Человек", callback_data="race:Человек"),
        types.InlineKeyboardButton("Эльф", callback_data="race:Эльф"),
        types.InlineKeyboardButton("Вервольф", callback_data="race:Вервольф"),
        types.InlineKeyboardButton("Вампир", callback_data="race:Вампир"),
        types.InlineKeyboardButton("Скелет", callback_data="race:Скелет"),
    )

    bot.send_message(
        message.chat.id,
        f"Отличное имя, {user_name}! Теперь выбери свою расу:\n"
        "1. Человек\n"
        "⚔️ +10% к урону мечом\n"
        "💼 Начинают с дополнительным золотом\n"
        "🎯 Нет особых слабостей\n"
        "\n"
        "2. Эльф"
        "🌿 +20% к магии\n"
        "🛡️🌿 20% иммунитет к магии\n"
        "⚔️  Слабы к ближнему оружию(на 10% урона больше)\n"
        "\n"
        "3. Вервольф\n"
        "🐺 +25% к урону в ночное время\n"
        "⚔️ Слабы к серебряному оружию(на 15% урона больше )\n"
        "\n"
        "4. Вампир\n"
        "🦇 Пьют кровь врагов (+3HP за удар)\n"
        "🌞 Горят на солнце (-2 HP/ход при свете дня)\n"
        "⚔️ Слабы к серебряному оружию(на 20% урона больше)\n"
        "\n"
        "5. Скелет\n"
        "💀 Иммунитет к дебафам\n"
        "🛡️➖ получают на 10% больше урона\n",
        reply_markup=kb,
    )


@bot.callback_query_handler(func=lambda callback: callback.data.startswith("race"))
def handle_callback(callback: types.CallbackQuery):
    _, race = callback.data.split(":")

    session.query(User).filter(User.user_id == callback.from_user.id).update(
        {"race": race}
    )
    session.commit()

    if race == "Человек":
        # Создаем клавиатуру для продолжения
        continue_kb = types.InlineKeyboardMarkup()
        continue_kb.add(
            types.InlineKeyboardButton("Продолжить", callback_data="start_adventure")
        )

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
            reply_markup=continue_kb,
        )

        # Удаляем предыдущее сообщение с выбором расы
        bot.delete_message(callback.message.chat.id, callback.message.message_id)

    elif race == "Эльф":
        # Создаем клавиатуру для продолжения
        continue_kb = types.InlineKeyboardMarkup()
        continue_kb.add(
            types.InlineKeyboardButton("Продолжить", callback_data="start_adventure")
        )

        # Отправляем сообщение с предысторией
        bot.send_message(
            callback.message.chat.id,
            "🌿 *Ну вот теперь ты точно начал игру!*\n\n"
            "📖 *Предыстория:*\n"
            "Ты - лесной Эльф 🌳, который всю жизнь провёл в древних рощах. "
            "Ты хорошо овладел каждым типом магии, но тебе еще сть куда стемиться.\n"
            "🍃 Ты настолько погрузился в гормонию с лесом что мог разговаривать с деревьями...\n\n"
            "🔥 *Чёрный день:*\n"
            "Люди подожгли твой родной лес 🌲🔥. Ты видел, как гибнут вековые деревья, "
            "а твои сородичи бегут в ужасе...\n\n"
            "🚶 *Новый путь:*\n"
            "С пеплом в волосах и болью в сердце 💔 ты покинул это место. "
            "Теперь ты странник без дома, но с твёрдой целью в сердце.\n\n"
            "✨ *И именно с этого момента начинается твоё настоящее приключение...*",
            parse_mode="Markdown",
            reply_markup=continue_kb,
        )
        # Удаляем предыдущее сообщение с выбором расы
        bot.delete_message(callback.message.chat.id, callback.message.message_id)

    elif race == "Вервольф":
        # Создаем клавиатуру для продолжения
        continue_kb = types.InlineKeyboardMarkup()
        continue_kb.add(
            types.InlineKeyboardButton("Продолжить", callback_data="start_adventure")
        )

        # Отправляем сообщение с предысторией
        bot.send_message(
            callback.message.chat.id,
            "🐺 Ну вот теперь ты точно начал игру!\n\n"
            "📜 Предыстория: днем ты обычный житель города 🏙️, но ночью ты превращаешься в свирепого волка 🌕!\n"
            "😤 Но ты всю ночь вынужден прятаться в огромном замке Дракулы 🏰...\n\n"
            "💢 Наконец ты устал от этого двуличия, хотел показать людям, что во втором обличии ты безопасен 👐,\n"
            "🔥 но они не захотели тебя слушать — хотели сжечь! 😱\n"
            "🏃 Ты смог убежать... и теперь намерен отомстить! ⚔️\n\n"
            "🚀 Вот так ты и начнешь свое приключение!",
            parse_mode="Markdown",
            reply_markup=continue_kb,
        )
        # Удаляем предыдущее сообщение с выбором расы
        bot.delete_message(callback.message.chat.id, callback.message.message_id)

    elif race == "Скелет":
        # Создаем клавиатуру для продолжения
        continue_kb = types.InlineKeyboardMarkup()
        continue_kb.add(
            types.InlineKeyboardButton("Продолжить", callback_data="start_adventure")
        )

        # Отправляем сообщение с предысторией
        bot.send_message(
            callback.message.chat.id,
            "🦴 *Ну вот теперь ты точно начал игру!*\n\n"
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
            parse_mode="Markdown",
            reply_markup=continue_kb,
        )

        bot.delete_message(callback.message.chat.id, callback.message.message_id)

    elif race == "Вампир":
        # Создаем клавиатуру для продолжения
        continue_kb = types.InlineKeyboardMarkup()
        continue_kb.add(
            types.InlineKeyboardButton("Продолжить", callback_data="start_adventure")
        )

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
            "*📜 Путь в Бессмертие:*\n"
            "Будучи обворованным и отчаявшимся, ты поверил \n"
            "незнакомцу в алых одеждах. Его обещания *золота и власти* \n"
            "привели тебя в замок, где:\n"
            "*👑 В зале с паутиной на троне сидел... Он.*\n"
            '"Хочешь ли ты *вечности*?" — прошелестели его губы. \n'
            "Твой кивок стал роковым. \n"
            "*🦇 Преображение:*\n"
            "Его клыки впились в шею... Боль сменилась *экстазом*, \n"
            "а наутро — *агонией* первого солнечного луча. \n"
            "*💀 Теперь ты знаешь правду:*\n"
            "Тот незнакомец был *Дракулой*, \n"
            'а твоя "награда" — вечная жажда крови.',
        ]

        # Выбираем случайную историю
        selected_story = random.choice(backstories)

        # Отправляем сообщение
        bot.send_message(
            callback.message.chat.id,
            selected_story,
            parse_mode="Markdown",
            reply_markup=continue_kb,
        )

        # Удаляем предыдущее сообщение
        bot.delete_message(callback.message.chat.id, callback.message.message_id)


@bot.callback_query_handler(func=lambda callback: callback.data.startswith("start_adventure"))
def handle_callback(callback: types.CallbackQuery):
    user = session.query(User).filter(User.user_id == callback.from_user.id).first()
    
    if user.race == "Эльф":  # Используйте единообразное написание
        continue_kb = types.InlineKeyboardMarkup()
        continue_kb.add(types.InlineKeyboardButton("Налево", callback_data="continue_adventure_left"))
        continue_kb.add(types.InlineKeyboardButton("Направо", callback_data="continue_adventure_right"))
        continue_kb.add(types.InlineKeyboardButton("Прямо", callback_data="continue_adventure_line"))
        continue_kb.add(types.InlineKeyboardButton("Назад", callback_data="continue_adventure_back"))
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        bot.send_message(
            callback.message.chat.id,
            "Выбери куда пойдёшь:",
            reply_markup=continue_kb
        )

@bot.callback_query_handler(func=lambda callback: callback.data.startswith("continue_adventure"))
def handle_adventure_choice(callback: types.CallbackQuery):
    *_, direction = callback.data.split("_")
    user = session.query(User).filter(User.user_id == callback.from_user.id).first()

    if user.race == "Эльф":  # Исправлено на единственное число

        
        if direction == 'left':
            continue_kb = types.InlineKeyboardMarkup()
            continue_kb.add(types.InlineKeyboardButton("Идти дальше", callback_data="continue_adventure_con")),
            *_, direction1 = callback.data.split("_"),
            continue_kb.add(types.InlineKeyboardButton("Вернуться назад", callback_data="continue_adventure_razvilka")),
            story = 'Ты пошел налево..,\n' \
            'но пока нечего не встретил'
            bot.delete_message(callback.message.chat.id, callback.message.message_id)
        elif direction == 'right':
            story = 'Ты пошел направо...\n' \
            'упал в яму и умер'
            bot.delete_message(callback.message.chat.id, callback.message.message_id)
        elif direction == 'line':
            story = 'Ты пошел прямо...\n' \
            'встретил людей и они тебя убили'
            bot.delete_message(callback.message.chat.id, callback.message.message_id)
        elif direction == 'back':
            story = 'Ты пошел назад...\n' \
            'и сгорел'
            continue_kb = types.InlineKeyboardMarkup()
            continue_kb.add(types.InlineKeyboardButton("Вернуться на развилку", callback_data="continue_adventure_razvilka"))
            bot.delete_message(callback.message.chat.id, callback.message.message_id)

        elif direction == "razvilka":
            story = "Выберите направление:"
            continue_kb = types.InlineKeyboardMarkup()
            continue_kb.add(types.InlineKeyboardButton("Налево", callback_data="continue_adventure_left"))
            continue_kb.add(types.InlineKeyboardButton("Направо", callback_data="continue_adventure_right"))
            continue_kb.add(types.InlineKeyboardButton("Прямо", callback_data="continue_adventure_line"))
            continue_kb.add(types.InlineKeyboardButton("Назад", callback_data="continue_adventure_back"))
            bot.delete_message(callback.message.chat.id, callback.message.message_id)

        if direction1 == "con":
            story = "Ты увидел холм...\n" \
            "Подняться ?"
            continue_kb.add(types.InlineKeyboardButton("Нет", callback_data="continue_adventure_con")),
            continue_kb.add(types.InlineKeyboardButton("Да", callback_data="continue_adventure_holmup")),
            *_, direction2 = callback.data.split("_")

        if direction2 == "Нет":
            pass


        bot.send_message(
            callback.message.chat.id,
            story,
            parse_mode="Markdown",
            reply_markup=continue_kb
        )


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
