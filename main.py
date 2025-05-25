from telebot import TeleBot, types
from threading import Thread
from threading import Thread
from models import Session
from models import create_all_table
from models import User
from boost import Boost
import random
from sqlalchemy import update
from models import Base, engine


way = 0

TOKEN = "7676744631:AAE8xq355W1p3yXrHVn-p4jkL6MUzkjcBDQ"
bot = TeleBot(TOKEN)

start_kb = types.InlineKeyboardMarkup()
btn = types.InlineKeyboardButton("Начать игру", callback_data="start_game")
start_kb.row(btn)
kb = types.InlineKeyboardMarkup()
continue_kb = types.InlineKeyboardMarkup()
continue_kb.add(
    types.InlineKeyboardButton("Продолжить", callback_data="contenur_adventure")
)

BASE_DAMAGE = 5
BASE_DEFENSE = 5
BASE_HEALTH = 100


users_states = {}


@bot.message_handler(commands=["start"])
def handle_start(msg: types.Message):
    session = Session()
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


Base.metadata.create_all(engine)
create_all_table()


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
    session = Session()
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
    session = Session()
    session.query(User).filter(User.user_id == callback.from_user.id).update(
        {"race": race}
    )
    session.commit()

    if race == "Человек":
        # Создаем клавиатуру для продолжения
        continue_kb = types.InlineKeyboardMarkup()
        continue_kb.add(
            types.InlineKeyboardButton("Продолжить", callback_data="continue_adventure")
        )

        human_boost = Boost(
            title='Бонус от рассы "Человек"', damage=0.1, user_id=callback.from_user.id
        )
        session.add(human_boost)
        session.commit()

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
            types.InlineKeyboardButton(
                "Продолжить", callback_data="continue_adventure_razvilka"
            )
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
            types.InlineKeyboardButton("Продолжить", callback_data="continue_adventure")
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
            types.InlineKeyboardButton("Продолжить", callback_data="continue_adventure")
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
        BASE_HEALTH -= 20

        bot.delete_message(callback.message.chat.id, callback.message.message_id)

    elif race == "Вампир":
        # Создаем клавиатуру для продолжения
        continue_kb = types.InlineKeyboardMarkup()
        continue_kb.add(
            types.InlineKeyboardButton("Продолжить", callback_data="continue_adventure")
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


@bot.callback_query_handler(
    func=lambda callback: callback.data.startswith("continue_adventure")
)
def handle_adventure_choice(callback: types.CallbackQuery):
    *_, direction_elf = callback.data.split("_")
    session = Session()
    user = session.query(User).filter(User.user_id == callback.from_user.id).first()
    continue_kb = types.InlineKeyboardMarkup()  # Создаем клавиатуру по умолчанию

    if user.race == "Эльф":
        # Основная развилка
        if direction_elf == "razvilka":
            story = "Выберите направление:"
            continue_kb.row(
                types.InlineKeyboardButton(
                    "Налево", callback_data="continue_adventure_left"
                ),
                types.InlineKeyboardButton(
                    "Направо", callback_data="continue_adventure_right"
                ),
            )

        # Левый путь
        elif direction_elf == "left":
            story = "Ты пошел налево и увидел таинственный холм...\nПодняться на него?"
            continue_kb.row(
                types.InlineKeyboardButton(
                    "Да", callback_data="continue_adventure_holmup"
                ),
                types.InlineKeyboardButton(
                    "Нет", callback_data="continue_adventure_notholm"
                ),
            )

        # Подъем на холм
        elif direction_elf == "holmup":
            story = "На вершине холма ты нашел древний эльфийский артефакт!\nТеперь твои сила и защита увеличены."
            BASE_DAMAGE += 10
            BASE_DEFENSE += 15
            session.commit()
            continue_kb.add(
                types.InlineKeyboardButton(
                    "Продолжить путь", callback_data="continue_adventure_afterhill"
                )
            )

        # Обход холма
        elif direction_elf == "notholm":
            story = "Ты обошел холм стороной и продолжил путь через лес."
            continue_kb.add(
                types.InlineKeyboardButton(
                    "Идти дальше", callback_data="continue_adventure_afterhill"
                )
            )

        # Правый путь
        elif direction_elf == "right":
            story = "Ты пошел направо...\nи встретил разбойников!"
            continue_kb.row(
                types.InlineKeyboardButton(
                    "Сражаться", callback_data="continue_adventure_fight"
                ),
                types.InlineKeyboardButton(
                    "Убежать", callback_data="continue_adventure_run"
                ),
            )

        # Бой с разбойниками
        elif direction_elf == "fight":
            if BASE_DAMAGE >= 20:
                story = "Ты победил разбойников и нашел у них карту сокровищ!"
                BASE_DAMAGE += 5  # Награда за победу
                BASE_DEFENSE += 5
                session.commit()
                continue_kb.add(
                    types.InlineKeyboardButton(
                        "Следовать по карте",
                        callback_data="continue_adventure_treasure",
                    )
                )
            else:
                story = "Разбойники оказались слишком сильными! Ты едва спасся.\nВернуться на развилку?"
                continue_kb.add(
                    types.InlineKeyboardButton(
                        "Вернуться", callback_data="continue_adventure_razvilka"
                    )
                )

        # Убегание от разбойников
        elif direction_elf == "run":
            story = "Ты успешно убежал и вернулся на развилку."
            continue_kb.add(
                types.InlineKeyboardButton(
                    "Выбрать путь снова", callback_data="continue_adventure_razvilka"
                )
            )

        # Находка сокровища
        elif direction_elf == "treasure":
            story = "По карте ты нашел древний эльфийский артефакт!\nТеперь ты готов к финальной битве."
            BASE_DAMAGE += 15
            BASE_DEFENSE +=10
            session.commit()
            continue_kb.add(
                types.InlineKeyboardButton(
                    "Идти к финальной битве",
                    callback_data="continue_adventure_finalfight",
                )
            )

        # Путь после холма
        elif direction_elf == "afterhill":
            story = "Ты вышел на поляну, где стоит поджигатель леса!\nОн виновен в гибели твоего дома."
            continue_kb.add(
                types.InlineKeyboardButton(
                    "Атаковать", callback_data="continue_adventure_finalfight"
                )
            )

        # Финальный бой
        elif direction_elf == "finalfight":
            if BASE_DAMAGE >= 30 and BASE_DEFENSE >= 30:
                story = "После долгого боя ты побеждаешь поджигателя!\nОн умоляет о пощаде..."
                continue_kb.row(
                    types.InlineKeyboardButton(
                        "Пощадить", callback_data="elf_end_mercy"
                    ),
                    types.InlineKeyboardButton("Казнить", callback_data="elf_end_kill"),
                )
            else:
                story = "Тебе не хватило сил... Поджигатель оказался слишком сильным.\nПопробовать еще раз?"
                continue_kb.add(
                    types.InlineKeyboardButton(
                        "Попробовать снова",
                        callback_data="continue_adventure_afterhill",
                    )
                )

        # Концовки
        elif direction_elf == "elf_end_mercy":
            story = "Ты пощадил врага, но заставил его восстановить лес.\nСпустя годы лес снова расцвел.\n\n✨ Ты завершил свое приключение как мудрый эльф!"
            continue_kb = None

        elif direction_elf == "elf_end_kill":
            story = "Ты казнил поджигателя, отомстив за свой дом.\nНо лес так и не восстановился...\n\n⚔️ Ты завершил свое приключение как воин-эльф!"
            continue_kb = None

        # Обработка неверных путей
        else:
            story = "Кажется, ты заблудился... Вернемся на последнюю развилку."
            continue_kb.add(
                types.InlineKeyboardButton(
                    "Вернуться", callback_data="continue_adventure_razvilka"
                )
            )

        # Удаление предыдущего сообщения и отправка нового
        try:
            bot.delete_message(callback.message.chat.id, callback.message.message_id)
        except:
            pass  # Если сообщение уже удалено или недоступно

        # Отправка нового сообщения
        if continue_kb:
            bot.send_message(callback.message.chat.id, story, reply_markup=continue_kb)
        else:
            bot.send_message(callback.message.chat.id, story)

        # Обработка боя с разбойниками
    if direction_elf == "fight":
        if BASE_DAMAGE >= 30 and BASE_DEFENSE >= 35:
            story = "Ты победил разбойников и нашел у них карту сокровищ!"
            continue_kb = types.InlineKeyboardMarkup()
            continue_kb.add(
                types.InlineKeyboardButton(
                    "Следовать по карте", callback_data="continue_adventure_treasure"
                )
            )
        else:
            story = "Разбойники оказались слишком сильными... Конец твоего пути."
            continue_kb = None

        if direction_elf == "run":
            story = "Ты успешно убежал и вернулся на развилку."
            continue_kb = types.InlineKeyboardMarkup()
            continue_kb.add(
                types.InlineKeyboardButton(
                    "Выбрать путь снова", callback_data="continue_adventure_razvilka"
                )
            )

        if direction_elf == "treasure":
            story = "По карте ты нашел древний эльфийский артефакт!\nТеперь ты готов к финальной битве."
            BASE_DAMAGE += 15
            BASE_DEFENSE += 10
            continue_kb = types.InlineKeyboardMarkup()
            continue_kb.add(
                types.InlineKeyboardButton(
                    "Идти к финальной битве",
                    callback_data="continue_adventure_finalfight",
                )
            )

        # Отправка сообщения с историей и клавиатурой
        if continue_kb:
            bot.send_message(callback.message.chat.id, story, reply_markup=continue_kb)
        else:
            bot.send_message(callback.message.chat.id, story)


@bot.callback_query_handler(
    func=lambda callback: callback.data.startswith("human_adventure")
)
def handle_human_adventure(callback: types.CallbackQuery):
    *_, direction_people = callback.data.split("_")
    session = Session()
    user = session.query(User).filter(User.user_id == callback.from_user.id).first()
    continue_kb = types.InlineKeyboardMarkup()

    if user.race == "Человек":
        # Начальная развилка
        if direction_people == "start":
            story = (
                "Ты - обычный человек в королевстве Альмерия. "
                "Сегодня утром в твою деревню напали бандиты.\n\n"
                "Что будешь делать?"
            )
            continue_kb.row(
                types.InlineKeyboardButton(
                    "Сражаться", callback_data="human_adventure_fight"
                ),
                types.InlineKeyboardButton(
                    "Бежать в город", callback_data="human_adventure_run"
                ),
            )

        # Вариант 1: Сражение с бандитами
        elif direction_people == "fight":
            if BASE_DAMAGE>= 5:
                story = (
                    "Ты героически сражался и отбил атаку!\n"
                    "Деревенский староста даёт тебе меч (+5 к урону).\n"
                    "Теперь нужно решить что делать дальше."
                )
                BASE_DAMAGE += 5
                session.commit()
                continue_kb.row(
                    types.InlineKeyboardButton(
                        "Идти в город за помощью", callback_data="human_adventure_city"
                    ),
                    types.InlineKeyboardButton(
                        "Преследовать бандитов", callback_data="human_adventure_chase"
                    ),
                )
            else:
                story = (
                    "Бандиты оказались сильнее... Ты тяжело ранен.\n"
                    "Придётся отступить в город за помощью."
                )
                BASE_HEALTH -= 20
                session.commit()
                continue_kb.add(
                    types.InlineKeyboardButton(
                        "Идти в город", callback_data="human_adventure_city"
                    )
                )

        # Вариант 2: Бегство в город
        elif direction_people == "run":
            story = (
                "Ты успешно добрался до города.\n"
                "В таверне ты слышишь разговоры о набегах бандитов.\n"
                "Что будешь делать?"
            )
            continue_kb.row(
                types.InlineKeyboardButton(
                    "Наняться в городскую стражу", callback_data="human_adventure_guard"
                ),
                types.InlineKeyboardButton(
                    "Искать информацию", callback_data="human_adventure_info"
                ),
            )

        # Развилка в городе
        elif direction_people == "city":
            story = "Ты прибыл в город. Здесь кипит жизнь.\n" "Куда отправишься?"
            continue_kb.row(
                types.InlineKeyboardButton(
                    "В таверну", callback_data="human_adventure_tavern"
                ),
                types.InlineKeyboardButton(
                    "К замку", callback_data="human_adventure_castle"
                ),
                types.InlineKeyboardButton(
                    "На рынок", callback_data="human_adventure_market"
                ),
            )

        # Преследование бандитов
        elif direction_people == "chase":
            story = (
                "Ты выследил бандитов до их лагеря.\n"
                "Видишь их главаря и пленных из деревни.\n"
                "Как поступишь?"
            )
            continue_kb.row(
                types.InlineKeyboardButton(
                    "Атаковать сразу", callback_data="human_adventure_attack"
                ),
                types.InlineKeyboardButton(
                    "Подождать ночи", callback_data="human_adventure_night"
                ),
                types.InlineKeyboardButton(
                    "Вернуться за помощью", callback_data="human_adventure_city"
                ),
            )

        # Атака на лагерь
        elif direction_people == "attack":
            if BASE_DAMAGE >= 15:
                story = (
                    "Ты побеждаешь бандитов и освобождаешь пленных!\n"
                    "Жители дарят тебе кольчугу (+10 к защите).\n"
                    "Теперь ты местный герой!"
                )
                BASE_DEFENSE += 10
                session.commit()
                continue_kb.add(
                    types.InlineKeyboardButton(
                        "Закончить приключение", callback_data="human_adventure_goodend"
                    )
                )
            else:
                story = (
                    "Бандитов оказалось слишком много...\n"
                    "Тебя берут в плен. Попробовать сбежать?"
                )
                continue_kb.row(
                    types.InlineKeyboardButton(
                        "Попытаться сбежать", callback_data="human_adventure_escape"
                    ),
                    types.InlineKeyboardButton(
                        "Ждать помощи", callback_data="human_adventure_wait"
                    ),
                )

        # Ночная атака
        elif direction_people == "night":
            story = (
                "Ночью ты незаметно проникаешь в лагерь.\n"
                "Тебе удаётся освободить пленных!\n"
                "Что будешь делать дальше?"
            )
            continue_kb.row(
                types.InlineKeyboardButton(
                    "Поджечь лагерь", callback_data="human_adventure_fire"
                ),
                types.InlineKeyboardButton(
                    "Тихо уйти", callback_data="human_adventure_leave"
                ),
            )

        # Работа в страже
        elif direction_people == "guard":
            story = (
                "Ты поступаешь на службу в городскую стражу.\n"
                "После месяца тренировок твои навыки улучшились!\n"
                "+7 к урону, +5 к защите"
            )
            BASE_DAMAGE += 7
            BASE_DEFENSE += 5
            session.commit()
            continue_kb.add(
                types.InlineKeyboardButton(
                    "Отправиться на задание", callback_data="human_adventure_mission"
                )
            )

        # Поиск информации
        elif direction_people == "info":
            story = (
                "Ты узнаёшь, что бандиты работают на барона Крега.\n"
                "Он хочет свергнуть короля!\n"
                "Что будешь делать?"
            )
            continue_kb.row(
                types.InlineKeyboardButton(
                    "Доложить властям", callback_data="human_adventure_report"
                ),
                types.InlineKeyboardButton(
                    "Расследовать самому", callback_data="human_adventure_investigate"
                ),
            )

        # Хорошая концовка
        elif direction_people == "goodend":
            story = (
                "Ты стал героем королевства!\n"
                "Король награждает тебя землями и титулом.\n\n"
                "🏰 Ты завершил приключение как настоящий герой!"
            )
            continue_kb = None

        # Плохая концовка (плен)
        elif direction_people == "capture":
            story = (
                "Бандиты продали тебя в рабство...\n\n"
                "⛓️ Твоё приключение закончилось неудачно."
            )
            continue_kb = None

        # Обработка неверных путей
        else:
            story = "Кажется, ты выбрал несуществующий путь. Вернёмся в город."
            continue_kb.add(
                types.InlineKeyboardButton(
                    "В город", callback_data="human_adventure_city"
                )
            )

        # Удаление предыдущего сообщения
        try:
            bot.delete_message(callback.message.chat.id, callback.message.message_id)
        except:
            pass

        # Отправка нового сообщения
        if continue_kb:
            bot.send_message(callback.message.chat.id, story, reply_markup=continue_kb)
        else:
            bot.send_message(callback.message.chat.id, story)

    bot.send_message(
        callback.message.chat.id, story, parse_mode="Markdown", reply_markup=continue_kb
    )


@bot.callback_query_handler(
    func=lambda callback: callback.data.startswith("skeleton_adventure")
)
def handle_skeleton_adventure(callback: types.CallbackQuery):
    *_, direction_skelet = callback.data.split("_")
    session = Session()
    user = session.query(User).filter(User.user_id == callback.from_user.id).first()
    continue_kb = types.InlineKeyboardMarkup()

    if user.race == "Скелет":
        # Начальная развилка
        if direction_skelet == "awaken":
            story = (
                "Ты пробуждаешься в древней гробнице. Кости твоего тела скрипят, а в глазницах мерцают \n"
                "зелёные огоньки. Перед тобой три прохода:\n\n"
                "1️⃣ Прямо - тусклый свет\n"
                "2️⃣ Налево - слышен скрежет металла\n"
                "3️⃣ Направо - пахнет свежим воздухом"
            )
            continue_kb.row(
                types.InlineKeyboardButton(
                    "Прямо", callback_data="skeleton_adventure_forward"
                ),
                types.InlineKeyboardButton(
                    "Налево", callback_data="skeleton_adventure_left"
                ),
                types.InlineKeyboardButton(
                    "Направо", callback_data="skeleton_adventure_right"
                ),
            )

        # Путь прямо
        elif direction_skelet == "forward":
            story = (
                "Ты находишь древний алтарь некроманта. На нём лежит:\n"
                "1️⃣ Проклятый меч (+3 к урону, но -1 к защите)\n"
                "2️⃣ Книга заклинаний (+2 к магии)\n"
                "3️⃣ Пройти мимо"
            )
            continue_kb.row(
                types.InlineKeyboardButton(
                    "Взять меч", callback_data="skeleton_adventure_cursed_sword"
                ),
                types.InlineKeyboardButton(
                    "Взять книгу", callback_data="skeleton_adventure_spellbook"
                ),
            )
            continue_kb.add(
                types.InlineKeyboardButton(
                    "Пройти мимо", callback_data="skeleton_adventure_ignore_altar"
                )
            )

        # Взятие проклятого меча
        elif direction_skelet == "cursed_sword":
            story = (
                "Ты взял меч, и почувствовал как твои кости наполняются силой!\n"
                "Но защита немного ослабла..."
            )
            BASE_DAMAGE += 5
            BASE_DEFENSE -= 5
            session.commit()
            continue_kb.add(
                types.InlineKeyboardButton(
                    "Идти дальше", callback_data="skeleton_adventure_deep_tomb"
                )
            )

        # Взятие книги заклинаний
        elif direction_skelet == "spellbook":
            story = (
                "Ты изучил древние заклинания некроманта!\n"
                "Теперь ты можешь призывать слабых скелетов."
            )
            user.magic += 0.2
            session.commit()
            continue_kb.add(
                types.InlineKeyboardButton(
                    "Идти дальше", callback_data="skeleton_adventure_deep_tomb"
                )
            )

        # Игнорирование алтаря
        elif direction_skelet == "ignore_altar":
            story = "Ты проходишь мимо алтаря, сохраняя нейтралитет."
            continue_kb.add(
                types.InlineKeyboardButton(
                    "Идти дальше", callback_data="skeleton_adventure_deep_tomb"
                )
            )

        # Путь налево
        elif direction_skelet == "left":
            story = (
                "Ты находишь комнату с боевыми скелетами!\n"
                "Они принимают тебя за своего командира.\n"
                "Что будешь делать?"
            )
            continue_kb.row(
                types.InlineKeyboardButton(
                    "Возглавить отряд", callback_data="skeleton_adventure_lead"
                ),
                types.InlineKeyboardButton(
                    "Атаковать их", callback_data="skeleton_adventure_fight"
                ),
                types.InlineKeyboardButton(
                    "Уйти", callback_data="skeleton_adventure_awaken"
                ),
            )

        # Возглавление отряда
        elif direction_skelet == "lead":
            story = (
                "Скелеты признают твоё превосходство!\n"
                "Теперь у тебя есть отряд из 3 скелетов.\n"
                "+5 к общей силе отряда"
            )
            BASE_DAMAGE += 5
            session.commit()
            continue_kb.add(
                types.InlineKeyboardButton(
                    "Идти к выходу", callback_data="skeleton_adventure_exit"
                )
            )

        # Бой со скелетами
        elif direction_skelet == "fight":
            if BASE_DAMAGE >= 6:
                story = "Ты побеждаешь скелетов и забираешь их оружие!\n" "+3 к урону"
                BASE_DAMAGE += 3
                session.commit()
            else:
                story = "Скелеты оказались сильнее! Тебя вышвыривают обратно."
            continue_kb.add(
                types.InlineKeyboardButton(
                    "Вернуться", callback_data="skeleton_adventure_awaken"
                )
            )

        # Путь направо
        elif direction_skelet == "right":
            story = (
                "Ты чувствуешь свежий воздух! Это выход...\n"
                "Но его охраняет гигантский скелет-страж.\n"
                "Как поступишь?"
            )
            continue_kb.row(
                types.InlineKeyboardButton(
                    "Сразиться", callback_data="skeleton_adventure_guardian"
                ),
                types.InlineKeyboardButton(
                    "Попытаться обмануть", callback_data="skeleton_adventure_trick"
                ),
                types.InlineKeyboardButton(
                    "Отступить", callback_data="skeleton_adventure_awaken"
                ),
            )

        # Бой со стражем
        elif direction_skelet == "guardian":
            if BASE_DAMAGE >= 7:
                story = (
                    "Ты побеждаешь стража и выходишь на свободу!\n"
                    "На солнце твои кости начинают светиться..."
                )
                continue_kb.add(
                    types.InlineKeyboardButton(
                        "Завершить приключение",
                        callback_data="skeleton_adventure_sun_end",
                    )
                )
            else:
                story = "Страж слишком силён! Тебя отбрасывает назад."
                continue_kb.add(
                    types.InlineKeyboardButton(
                        "Вернуться", callback_data="skeleton_adventure_awaken"
                    )
                )

        # Обман стража
        elif direction_skelet == "trick":
            story = (
                "Ты притворяешься слугой Некроманта и проходишь!\n"
                "Теперь ты на свободе, но кто-то ищет самозванца..."
            )
            continue_kb.add(
                types.InlineKeyboardButton(
                    "Продолжить", callback_data="skeleton_adventure_hide"
                )
            )

        # Глубокие катакомбы
        elif direction_skelet == "deep_tomb":
            story = (
                "Ты попадаешь в главный зал гробницы.\n"
                "Перед тобой саркофаг Древнего Короля.\n"
                "Что будешь делать?"
            )
            continue_kb.row(
                types.InlineKeyboardButton(
                    "Открыть", callback_data="skeleton_adventure_open_sarcophagus"
                ),
                types.InlineKeyboardButton(
                    "Обыскать комнату", callback_data="skeleton_adventure_search"
                ),
                types.InlineKeyboardButton(
                    "Уйти", callback_data="skeleton_adventure_exit"
                ),
            )

        # Открытие саркофага
        elif direction_skelet == "open_sarcophagus":
            story = "Ты пробуждаешь Древнего Короля!\n" "Он предлагает тебе выбор:"
            continue_kb.row(
                types.InlineKeyboardButton(
                    "Стать его генералом", callback_data="skeleton_adventure_general"
                ),
                types.InlineKeyboardButton(
                    "Украсть его меч", callback_data="skeleton_adventure_steal"
                ),
                types.InlineKeyboardButton(
                    "Отказаться", callback_data="skeleton_adventure_refuse"
                ),
            )

        # Концовки
        elif direction_skelet == "sun_end":
            story = (
                "Твои кости под солнечным светом превращаются в светящийся кристалл!\n\n"
                "💀 Ты становишься Легендарным Светящимся Скелетом!"
            )
            continue_kb = None

        elif direction_skelet == "general":
            story = (
                "Ты возглавляешь армию нежити!\n\n"
                "👑 Ты стал Генералом Костяного Легиона!"
            )
            continue_kb = None

        elif direction_skelet == "steal":
            if BASE_DAMAGE >= 10:
                story = (
                    "Ты успешно крадёшь меч и сбегаешь!\n\n"
                    "🗡️ Теперь ты Владелец Клинка Мрака!"
                )
            else:
                story = "Король ловит тебя и превращает в прах...\n\n☠️ Конец."
            continue_kb = None

        # Обработка неверных путей
        else:
            story = "Твои кости скрипят от недоумения... Возвращаемся назад."
            continue_kb.add(
                types.InlineKeyboardButton(
                    "В начало", callback_data="skeleton_adventure_awaken"
                )
            )

        # Удаление предыдущего сообщения
        try:
            bot.delete_message(callback.message.chat.id, callback.message.message_id)
        except:
            pass

        # Отправка нового сообщения
        if continue_kb:
            bot.send_message(callback.message.chat.id, story, reply_markup=continue_kb)
        else:
            bot.send_message(callback.message.chat.id, story)


@bot.callback_query_handler(
    func=lambda callback: callback.data.startswith("werewolf_adventure")
)
def handle_werewolf(callback: types.CallbackQuery):
    *_, direction_wervolf = callback.data.split("_")
    session = Session()
    user = session.query(User).filter(User.user_id == callback.from_user.id).first()
    kb = types.InlineKeyboardMarkup()

    if user.race != "Вервольф":
        bot.answer_callback_query(
            callback.id, "Эта история не для твоей расы!", show_alert=True
        )
        return

    # ====== ОСНОВНЫЕ ВЕТКИ ======
    if direction_wervolf == "start":
        msg = """*Лунный свет пробивается сквозь тучи.* Ты просыпаешься в лесу с:
- Обострёнными чувствами
- Когтями, покрытыми свежей кровью
- Жаждой охоты

Куда направишься?"""
        kb.row(
            types.InlineKeyboardButton(
                "🏚️ К заброшенной деревне", callback_data="werewolf_village"
            ),
            types.InlineKeyboardButton(
                "🌳 Вглубь леса", callback_data="werewolf_forest"
            ),
        )
        kb.add(
            types.InlineKeyboardButton(
                "💧 К реке смыть кровь", callback_data="werewolf_river"
            )
        )

    # ====== ВЕТКА ДЕРЕВНИ ======
    elif direction_wervolf == "village":
        msg = """Деревня кажется пустой, но ты чувствуешь:
1) Запах страха из сарая 🐷
2) Металлический дух у таверны ⚔️
3) Травяной аромат из избы 🧙"""
        kb.row(
            types.InlineKeyboardButton("🐷 Сарай", callback_data="werewolf_pigs"),
            types.InlineKeyboardButton("⚔️ Таверна", callback_data="werewolf_hunters"),
        )
        kb.add(types.InlineKeyboardButton("🧙 Изба", callback_data="werewolf_witch"))

    elif direction_wervolf == "pigs":
        msg = "В сарае ты находишь свинью. Твои действия?"
        kb.row(
            types.InlineKeyboardButton("🩸 Убить", callback_data="werewolf_kill_pig"),
            types.InlineKeyboardButton(
                "👃 Обнюхать", callback_data="werewolf_sniff_pig"
            ),
        )

    elif direction_wervolf == "kill_pig":
        BASE_DAMAGE += 2
        msg = "*Разрываешь добычу когтями!* Но шум привлёк внимание."
        kb.add(
            types.InlineKeyboardButton(
                "⚠️ Приготовиться", callback_data="werewolf_alert"
            )
        )

    # ====== ВЕТКА ЛЕСА ======
    elif direction_wervolf == "forest":
        msg = """В лесной чаще ты обнаруживаешь:
1) Волчью тропу 🐺
2) Медвежью берлогу 🐻
3) Древний дуб 🌳"""
        kb.row(
            types.InlineKeyboardButton("🐺 Волки", callback_data="werewolf_pack"),
            types.InlineKeyboardButton("🐻 Медведь", callback_data="werewolf_bear"),
        )
        kb.add(types.InlineKeyboardButton("🌳 Дуб", callback_data="werewolf_oak"))

    elif direction_wervolf == "pack":
        if user.animalism < 0.3:
            msg = "Стая не принимает тебя! Они рычат и прогоняют."
            kb.add(
                types.InlineKeyboardButton("😾 Уйти", callback_data="werewolf_forest")
            )
        else:
            msg = "Волки признают в тебе сородича! +0.4 к контролю формы"
            user.animalism += 0.4
            kb.add(
                types.InlineKeyboardButton(
                    "🐕 Следовать за стаей", callback_data="werewolf_den"
                )
            )

    # ====== ВЕТКА РЕКИ ======
    elif direction_wervolf == "river":
        msg = """У реки ты видишь:
1) Свое отражение 🌊
2) Следы крови 🩸
3) Рыбацкую лодку 🚣"""
        kb.row(
            types.InlineKeyboardButton(
                "🌊 Отражение", callback_data="werewolf_reflection"
            ),
            types.InlineKeyboardButton("🩸 Следы", callback_data="werewolf_blood"),
        )
        kb.add(types.InlineKeyboardButton("🚣 Лодка", callback_data="werewolf_boat"))

    elif direction_wervolf == "reflection":
        msg = "Ты видишь в воде свое истинное обличье! Что делаешь?"
        kb.row(
            types.InlineKeyboardButton("🌕 Принять", callback_data="werewolf_accept"),
            types.InlineKeyboardButton("👤 Отрицать", callback_data="werewolf_deny"),
        )

    # ====== ОБРАБОТКА ОШИБОК ======
    else:
        msg = "*Рычит* Неизвестный выбор... Возвращаю к началу."
        kb.add(
            types.InlineKeyboardButton(
                "🔙 Начать заново", callback_data="werewolf_start"
            )
        )

    # ====== ОБНОВЛЕНИЕ ДАННЫХ ======
    session.commit()
    bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text=msg,
        reply_markup=kb,
        parse_mode="Markdown",
    )


@bot.callback_query_handler(
    func=lambda callback: callback.data.startswith("vampire_adventure")
)
def handle_werewolf(callback: types.CallbackQuery):
    *_, direction_vamp = callback.data.split("_")
    session = Session()
    user = session.query(User).filter(User.user_id == callback.from_user.id).first()
    kb = types.InlineKeyboardMarkup()
    if user.race == "Вампир":
        """Начало игры - вампир пробуждается"""
        response_text = """🦇 Ты пробуждаешься в своём склепе. Выбери действие:"""
        kb.row(
            types.InlineKeyboardButton("🧛 Охота", callback_data="vampire_hunt"),
            types.InlineKeyboardButton("🏰 Бал", callback_data="vampire_ball"),
        )
        kb.add(types.InlineKeyboardButton("🛡️ Защита", callback_data="vampire_defense"))

    # ====== ВЕТКА ОХОТЫ ======
    elif direction_vamp == "hunt":
        """Выбор места для охоты за кровью"""
        response_text = """Где будем охотиться?"""
        kb.row(
            types.InlineKeyboardButton("🏙️ Улицы", callback_data="vampire_streets"),
            types.InlineKeyboardButton("🏥 Больница", callback_data="vampire_hospital"),
        )
        kb.add(types.InlineKeyboardButton("🧛 Соперник", callback_data="vampire_duel"))

    elif direction_vamp == "streets":
        """Охота на городских улицах"""
        boost = Boost(title="Уличная охота", damage=0.1, blood=15)
        session.add(boost)
        response_text = f"""Ты напился крови прохожих! Получено:
+{boost.damage*100}% к урону
+{boost.blood} к запасу крови"""
        kb.add(
            types.InlineKeyboardButton("🌆 Продолжить", callback_data="vampire_night")
        )

    elif direction_vamp == "hospital":
        """Охота в больнице (легкая добыча)"""
        boost = Boost(title="Больничный перекус", blood=25, defense=-0.1)
        session.add(boost)
        response_text = f"""Ты нашел легкую добычу, но стал неосторожен:
+{boost.blood} крови
-{abs(boost.defense)*100}% к защите"""
        kb.add(types.InlineKeyboardButton("💉 Далее", callback_data="vampire_night"))

    # ====== ВЕТКА БАЛА ======
    elif direction_vamp == "ball":
        """Светское мероприятие для вампиров"""
        response_text = """На балу ты видишь:"""
        kb.row(
            types.InlineKeyboardButton("👩 Дама", callback_data="vampire_lady"),
            types.InlineKeyboardButton("🧐 Охотник", callback_data="vampire_hunter"),
        )
        kb.add(types.InlineKeyboardButton("🍷 Вино", callback_data="vampire_wine"))

    elif direction_vamp == "wine":
        """Особое вампирское вино"""
        boost = Boost(title="Эликсир крови", blood=10, health=20)
        session.add(boost)
        response_text = f"""Ты выпил магическое вино:
+{boost.blood} крови
+{boost.health} здоровья"""
        kb.add(
            types.InlineKeyboardButton("💃 Продолжить", callback_data="vampire_dance")
        )

    # ====== ВЕТКА ЗАЩИТЫ ======
    elif direction_vamp == "defense":
        """Защита территории"""
        response_text = """Кто угрожает твоим владениям?"""
        kb.row(
            types.InlineKeyboardButton(
                "🐺 Оборотни", callback_data="vampire_werewolves"
            ),
            types.InlineKeyboardButton("🔫 Охотники", callback_data="vampire_hunters"),
        )

    elif direction_vamp == "werewolves":
        """Бой с оборотнями"""
        boost = Boost(title="Победа над оборотнями", damage=0.15, health=-25)
        session.add(boost)
        response_text = f"""Ты победил, но получил раны:
+{boost.damage*100}% к урону
{boost.health} к здоровью"""
        kb.add(
            types.InlineKeyboardButton("🏡 Вернуться", callback_data="vampire_awaken")
        )

    # ====== СПЕЦИАЛЬНЫЕ СОБЫТИЯ ======
    elif direction_vamp == "blood_moon":
        """Кровавая луна усиливает способности"""
        boost = Boost(title="Кровавая луна", damage=0.25, defense=0.2)
        session.add(boost)
        response_text = f"""🌕 Луна дарует силу!
+{boost.damage*100}% к урону
+{boost.defense*100}% к защите"""
        kb.add(
            types.InlineKeyboardButton("🦇 Использовать", callback_data="vampire_power")
        )

    # ====== КОНЦОВКИ ======
    elif direction_vamp == "win":
        """Победа в сюжете"""
        boost = Boost(title="Повелитель ночи", damage=0.5, defense=0.5)
        session.add(boost)
        response_text = f"""👑 Ты стал Вампирским Лордом!
+{boost.damage*100}% к урону
+{boost.defense*100}% к защите"""
        kb = None

    # ====== ОБРАБОТКА ОШИБОК ======
    else:
        response_text = "🩸 Неизвестное действие..."
        kb.add(
            types.InlineKeyboardButton(
                "🔄 Начать заново", callback_data="vampire_awaken"
            )
        )

    # Удаляем предыдущее сообщение
    try:
        bot.delete_message(callback.message.chat.id, callback.message.message_id)

    except Exception as e:
        error_msg = f"🦇 Ошибка: {str(e)}"
        bot.send_message(callback.message.chat.id, error_msg)
        kb.add(
            types.InlineKeyboardButton(
                "🔄 Перезапустить", callback_data="vampire_awaken"
            )
        )

    # Отправляем ответ
    if kb:
        bot.send_message(callback.message.chat.id, response_text, reply_markup=kb)
    else:
        bot.send_message(callback.message.chat.id, response_text)

    session.close()


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
