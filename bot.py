import telebot # библиотека telebot
from config import token # импорт токена

bot = telebot.TeleBot(token) 

@bot.message_handler(commands=['start'])
def start(message):
    help_text = """Привет! Я бот для управления чатом.

Доступные команды:
/start - показать это сообщение
/ban - забанить пользователя (ответить на сообщение)
/unban - разбанить пользователя (ответить на сообщение)

Автоматические правила:
- Голосовые сообщения автоматически банят отправителя (кроме администраторов)"""
    bot.reply_to(message, help_text)

@bot.chat_member_handler()
def greet_new_member(chat_member):
    if chat_member.new_chat_member.status == 'member' and chat_member.old_chat_member.status in ['left', 'kicked']:
        user = chat_member.new_chat_member.user
        username = user.username
        if username:
            bot.send_message(chat_member.chat.id, f"Добро пожаловать, @{username}!")
        else:
            bot.send_message(chat_member.chat.id, f"Добро пожаловать, {user.first_name}!")

@bot.message_handler(commands=['ban'])
def ban_user(message):
    if message.reply_to_message: #проверка на то, что эта команда была вызвана в ответ на сообщение
        chat_id = message.chat.id # сохранение id чата
        # проверка прав администратора у того, кто вызывает команду
        try:
            caller_status = bot.get_chat_member(chat_id, message.from_user.id).status
            if caller_status not in ['administrator', 'creator']:
                bot.reply_to(message, "Только администраторы могут использовать эту команду.")
                return
        except:
            bot.reply_to(message, "Ошибка при проверке прав.")
            return

        # сохранение id и статуса пользователя, отправившего сообщение
        if not message.reply_to_message.from_user:
            bot.reply_to(message, "Не удалось получить информацию о пользователе.")
            return
        user_id = message.reply_to_message.from_user.id
        try:
            user_status = bot.get_chat_member(chat_id, user_id).status
        except:
            bot.reply_to(message, "Ошибка при получении статуса пользователя.")
            return

        # проверка пользователя
        if user_status == 'administrator' or user_status == 'creator':
            bot.reply_to(message, "Невозможно забанить администратора.")
        else:
            try:
                bot.ban_chat_member(chat_id, user_id) # пользователь с user_id будет забанен в чате с chat_id
                username = message.reply_to_message.from_user.username
                if username:
                    bot.reply_to(message, f"Пользователь @{username} был забанен.")
                else:
                    bot.reply_to(message, f"Пользователь был забанен.")
            except Exception as e:
                bot.reply_to(message, f"Ошибка при бане: {e}")
    else:
        bot.reply_to(message, "Эта команда должна быть использована в ответ на сообщение пользователя, которого вы хотите забанить.")

@bot.message_handler(commands=['unban'])
def unban_user(message):
    if message.reply_to_message:
        chat_id = message.chat.id
        # проверка прав администратора у того, кто вызывает команду
        try:
            caller_status = bot.get_chat_member(chat_id, message.from_user.id).status
            if caller_status not in ['administrator', 'creator']:
                bot.reply_to(message, "Только администраторы могут использовать эту команду.")
                return
        except:
            bot.reply_to(message, "Ошибка при проверке прав.")
            return

        if not message.reply_to_message.from_user:
            bot.reply_to(message, "Не удалось получить информацию о пользователе.")
            return
        user_id = message.reply_to_message.from_user.id

        try:
            bot.unban_chat_member(chat_id, user_id)
            username = message.reply_to_message.from_user.username
            if username:
                bot.reply_to(message, f"Пользователь @{username} был разбанен.")
            else:
                bot.reply_to(message, f"Пользователь был разбанен.")
        except Exception as e:
            bot.reply_to(message, f"Ошибка при разбане: {e}")
    else:
        bot.reply_to(message, "Эта команда должна быть использована в ответ на сообщение пользователя, которого вы хотите разбанить.")

@bot.message_handler(content_types=['voice'])
def ban_voice_message(message):
    chat_id = message.chat.id
    # проверка прав администратора у отправителя голосового сообщения
    try:
        user_status = bot.get_chat_member(chat_id, message.from_user.id).status
        if user_status in ['administrator', 'creator']:
            return  # администраторы могут отправлять голосовые сообщения
    except:
        return

    try:
        bot.ban_chat_member(chat_id, message.from_user.id)
        username = message.from_user.username
        if username:
            bot.reply_to(message, f"Пользователь @{username} был забанен за отправку голосового сообщения.")
        else:
            bot.reply_to(message, f"Пользователь был забанен за отправку голосового сообщения.")
    except Exception as e:
        bot.reply_to(message, f"Ошибка при бане: {e}")

bot.infinity_polling(none_stop=True)
