from boost import Boost
from database import Session, User
import random
from telebot import types
from telebot import TeleBot, types
TOKEN = "7676744631:AAE8xq355W1p3yXrHVn-p4jkL6MUzkjcBDQ"
bot = TeleBot(TOKEN)


def calc_fight_result(enemy_damage, enemy_defence, enemy_hp, player_id, player_damage, player_defence, player_hp):
    session = Session()
    user = session.query(User).filter(User.user_id == player_id).first()

    boosts: list[Boost] = user.boosts

class BattleSystem:
    def __init__(self):
        self.min_accuracy = 30  # Минимальный шанс попадания
        self.max_accuracy = 95  # Максимальный шанс попадания
    
    def calculate_hit(self, attacker, defender):
        """Расчет попадания с учетом меткости и уклонения"""
        # Базовый шанс попадания (меткость атакующего минус ловкость защищающегося)
        hit_chance = attacker['accuracy'] - defender['agility'] * 0.5
        
        # Ограничиваем шанс попадания
        hit_chance = max(self.min_accuracy, min(self.max_accuracy, hit_chance))
        
        # Случайный бросок
        roll = random.randint(1, 100)
        return roll <= hit_chance
    
    def calculate_damage(self, attacker, defender):
        """Расчет урона с учетом брони"""
        # Базовый урон
        base_damage = attacker['attack']
        
        # Критический удар (5% шанс)
        is_critical = random.randint(1, 100) <= 5
        if is_critical:
            base_damage *= 1.5  # +50% урона
        
        # Учет брони (каждый пункт брони уменьшает урон на 1)
        armor_reduction = defender['armor']
        final_damage = max(1, base_damage - armor_reduction)  # Минимальный урон - 1
        
        return final_damage, is_critical
    
    def battle_round(self, player, enemy):
        """Один раунд боя"""
        results = []
        
        # Атака игрока
        if self.calculate_hit(player, enemy):
            damage, is_critical = self.calculate_damage(player, enemy)
            enemy['health'] -= damage
            crit_text = " (КРИТ!)" if is_critical else ""
            results.append(f"✅ Вы попали! Урон: {damage}{crit_text}")
        else:
            results.append("❌ Вы промахнулись!")
        
        # Проверка смерти врага
        if enemy['health'] <= 0:
            results.append(f"☠️ {enemy['name']} повержен!")
            return results
        
        # Атака врага
        if self.calculate_hit(enemy, player):
            damage, is_critical = self.calculate_damage(enemy, player)
            player['health'] -= damage
            crit_text = " (КРИТ!)" if is_critical else ""
            results.append(f"⚔️ {enemy['name']} атакует! Урон: {damage}{crit_text}")
        else:
            results.append(f"🛡️ {enemy['name']} промахнулся!")
        
        return results

# Пример использования в боте
battle_system = BattleSystem()

@bot.callback_query_handler(func=lambda call: call.data == "start_battle")
def start_battle(callback):
    # Статистика игрока (должны браться из БД)
    player = {
        'name': "Игрок",
        'health': 100,
        'attack': 15,
        'accuracy': 80,  # Шанс попадания в %
        'agility': 10,   # Ловкость (влияет на уклонение)
        'armor': 5       # Броня (снижает получаемый урон)
    }
    
    # Создаем противника
    enemy = {
        'name': "Гоблин",
        'health': 50,
        'attack': 10,
        'accuracy': 70,
        'agility': 15,
        'armor': 3
    }
    
    # Создаем клавиатуру для боя
    battle_kb = types.InlineKeyboardMarkup()
    battle_kb.add(
        types.InlineKeyboardButton("Атаковать", callback_data="battle_attack"),
        types.InlineKeyboardButton("Защищаться", callback_data="battle_defend"),
        types.InlineKeyboardButton("Сбежать", callback_data="battle_flee")
    )
    
    bot.send_message(
        callback.message.chat.id,
        f"⚔️ *Бой с {enemy['name']}!*\n"
        f"Ваше HP: {player['health']} | Противник: {enemy['health']}",
        parse_mode="Markdown",
        reply_markup=battle_kb
    )

@bot.callback_query_handler(func=lambda call: call.data == "battle_attack")
def battle_attack(callback):
    # Получаем текущие данные боя (на практике нужно хранить в БД или кэше)
    player = {...}  # Загружаем данные игрока
    enemy = {...}   # Загружаем данные врага
    
    # Проводим раунд боя
    battle_log = battle_system.battle_round(player, enemy)
    
    # Формируем сообщение
    message = "⚔️ *Результаты раунда:*\n" + "\n".join(battle_log)
    message += f"\n\nВаше HP: {player['health']} | {enemy['name']}: {enemy['health']}"
    
    # Проверяем конец боя
    if enemy['health'] <= 0:
        message += "\n\n🎉 *Вы победили!*"
        # Выдаем награду и т.д.
    elif player['health'] <= 0:
        message += "\n\n💀 *Вы погибли...*"
    else:
        # Продолжаем бой
        battle_kb = types.InlineKeyboardMarkup()
        battle_kb.add(
            types.InlineKeyboardButton("Атаковать", callback_data="battle_attack"),
            types.InlineKeyboardButton("Использовать зелье", callback_data="use_potion")
        )
        bot.edit_message_text(
            message,
            callback.message.chat.id,
            callback.message.message_id,
            reply_markup=battle_kb,
            parse_mode="Markdown"
        )
        return
    
    bot.edit_message_text(
        message,
        callback.message.chat.id,
        callback.message.message_id,
        parse_mode="Markdown"
    )


