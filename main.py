import telebot
import sqlite3
from telebot import types
from config import bot

bot = bot


def users_check(chat_id):
    """Проверка наличия пользователя в базе данных"""
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users WHERE id = ?", (chat_id,))
    result = cur.fetchone()
    conn.close()
    if result[0] > 0:
        return True
    else:
        return False
    
def post_check(num):
    """Проверка номера в базе данных"""
    conn = sqlite3.connect("killed.db")
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM killed WHERE phone = ?", (num,))
    result = cur.fetchone()
    conn.close()
    if result[0] > 0:
        return True
    else:
        return False
    
def social_check(social):
    """Проверка ссылкок на наличие в базе данных"""
    conn = sqlite3.connect("killed.db")
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM killed WHERE social_networks = ?", (social,))
    result = cur.fetchone()
    conn.close()
    if result[0] > 0:
        return True
    else:
        return False

def create_killed_table():
    """Создание базы данных"""
    conn = sqlite3.connect("killed.db")
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS killed (phone TEXT, name TEXT, social_networks TEXT, tags TEXT, other_data TEXT)")
    conn.commit()
    conn.close()

@bot.message_handler(commands=['start'])
def start(message):
    """Функция старт"""
    chat_id = message.chat.id
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    create_killed_table()
    cur.execute("CREATE TABLE IF NOT EXISTS killed (id INTEGER, name TEXT, username TEXT)")
    conn.commit()

    is_existing = users_check(chat_id)
    
    if is_existing == False:
        bot.send_message(message.chat.id, f"Приветствую, {message.from_user.first_name}. Получите информацию о других пользователях и добавьте свою!")
        cur.execute("INSERT INTO users (id, name, username) VALUES (?, ?, ?)", (chat_id, message.from_user.first_name, message.from_user.username))
        conn.commit()

    elif is_existing == True:
        bot.send_message(message.chat.id, f"Рад вас снова видеть, {message.from_user.first_name}. Получите информацию о других пользователях и добавьте свою!")
    
    conn.close()
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    btn1 = types.KeyboardButton("🎯Просмотреть дневную подборку😈")
    btn2 = types.KeyboardButton("✅Запостить данные🗂️")
    btn3 = types.KeyboardButton("🎰Поиск🪬")
    
    markup.add(btn1, btn2, btn3)

    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)

@bot.message_handler(content_types=['text'])
def buttons(message):
    """Кнопки и их работа"""
    if message.text == "✅Запостить данные🗂️":
        chat_id = message.chat.id
        bot.send_message(chat_id, "Введите номер телефона:")
        bot.register_next_step_handler(message, process_phone)

    elif message.text == "🎰Поиск🪬":
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        btn1 = types.KeyboardButton("📱 Номер 📞")
        btn2 = types.KeyboardButton("🗂️ ФИО ⚰️")
        btn3 = types.KeyboardButton("🖥️ Ссылка на соц. сеть 💵")
        btn4 = types.KeyboardButton("🖋️ Другие данные 🔓")
        markup.add(btn1, btn2, btn3, btn4)
        bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAEKru1lRkbUK_zVzZNknekzMyEriTwaCgAC_ScAArMdyEgmJ6P4H0WIVzME")
        bot.send_message(message.chat.id, "Выберите параметр для поиска:", reply_markup=markup)
        bot.register_next_step_handler(message, search_buttons)
def search_buttons(message):
    if message.text == "📱 Номер 📞":
        bot.send_message(message.chat.id, "Введите номер:")
        bot.register_next_step_handler(message, search_phone)
    elif message.text == "🖥️ Ссылка на соц. сеть 💵":
        bot.send_message(message.chat.id, "Введите ссылку на соц сети:")
        bot.register_next_step_handler(message, social_network_search)

def process_phone(message):
    """Обработка номера с проверкой"""
    global chat_id
    chat_id = message.chat.id
    global num
    num = message.text  
    is_posted = post_check(num)  
    if not is_posted:
        bot.send_message(chat_id, "Введите имя:")
        bot.register_next_step_handler(message, process_name)  
    else:
        bot.send_message(chat_id, "Такой пост уже существует!")
        
def process_name(message):
    """Обработка ФИО"""
    try:
        chat_id = message.chat.id
        global name
        name = message.text
        bot.send_message(chat_id, "Укажите ссылки на соц. сети:")
        bot.register_next_step_handler(message, process_social_networks)
    except Exception as e:
        bot.send_message(chat_id, "Что-то пошло не так. Введите ФИО еще раз.")
        
def process_social_networks(message):
    """Обработка ссылoк на соц. сети с проверкой"""
    try:
        global social
        social = message.text
        is_posted = social_check(social)  
        if not is_posted:
            bot.send_message(chat_id, "Укажите тэги к записи:")
            bot.register_next_step_handler(message, process_tags)
        else:
            bot.send_message(chat_id, "Такой пост уже существует!")
    except Exception as e:
        bot.send_message(chat_id, "Что-то пошло не так. Введите ссылки на соц. сети еще раз.")

def process_tags(message):
    """Добавление тэгов в базу данных"""
    try:
        global tags
        tags = message.text
        bot.send_message(message.chat.id, "Введите другие данные:")
        bot.register_next_step_handler(message, process_otherdata)
    except Exception:
        bot.send_message(chat_id, "Что-то пошло не так.")
        
def process_otherdata(message):
    """Обработка других данных"""
    try:
        other_data = message.text
        save_data(chat_id, num, name, social, tags, other_data)
    except Exception as e:
        pass

def save_data(chat_id, num, name, social, tags, other_data):
    """Сохранение всей информации"""
    try:
        conn = sqlite3.connect("killed.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO killed (phone, name, social_networks, tags, other_data) VALUES (?, ?, ?, ?, ?)",
                    (num, name, social, tags, other_data))
        conn.commit()
        conn.close()
        bot.send_message(chat_id, "Данные успешно сохранены.")
    except Exception as e:
        bot.send_message(chat_id, "Что-то пошло не так. Введите другие данные еще раз.")

def search_phone(message):
    """Поиск номера в базе данных"""
    num = message.text
    con = sqlite3.connect("killed.db")
    cur = con.cursor()

    cur.execute("SELECT * FROM killed WHERE phone = ?", (num,))
    res = cur.fetchall()

    con.close()

    if res:
        result_str = "Результаты:\n"
        for row in res:
            result_str += f"Имя: {row[1]}\nСоц. сети: {row[2]}\nДругие данные: {row[3]}\n\n"
        bot.send_message(message.chat.id, result_str)
    else:
        bot.send_message(message.chat.id, "Ничего не найдено.")

def social_network_search(message):
    try:
        input_text = message.text
        urls = [url.strip() for url in input_text.split(",")]

        con = sqlite3.connect("killed.db")
        cur = con.cursor()

        results = []

        for url in urls:
            cur.execute("SELECT * FROM killed WHERE social_networks LIKE ? OR tags LIKE ?", ('%' + url + '%', '%' + url + '%'))
            res = cur.fetchall()

            if res:
                result = f"Результаты для ссылки {url}:\n"
                for entry in res:
                    result += f"Номер: {entry[0]}\nИмя: {entry[1]}\nСсылки на соц сети: {entry[2]}\nДругие данные: {entry[3]}\nТэги: {entry[4]}\n\n"
                results.append(result)

        con.close()

        if results:
            result_message = "\n".join(results)
            bot.send_message(message.chat.id, result_message)
        else:
            bot.send_message(message.chat.id, "Ничего не найдено.")

    except Exception as e:
        bot.send_message(message.chat.id, "Ошибка, попробуйте еще раз.")
#Починить выво
if __name__ == '__main__':
    bot.infinity_polling(none_stop=True)
