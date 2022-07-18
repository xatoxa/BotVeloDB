import telebot
from telebot import types
import sqlite3

import config

bot = telebot.TeleBot(config.botToken)


@bot.message_handler(commands=['start'])
def start(message):
	db = sqlite3.connect('VeloDB.db', check_same_thread=False)
	c = db.cursor()
	c.execute("""
	SELECT name 
	FROM users 
	WHERE telegram_id = ? AND admin = TRUE""", (message.from_user.id,))
	name = c.fetchone()[0]
	if len(name) > 0:
		bot.send_message(message.chat.id, "Дороу, " + name + "!")
		menu(message)
	c.close()
	db.close()


@bot.message_handler(commands=['menu'])
def menu(message):
	markup = types.InlineKeyboardMarkup(row_width=1)
	buttons = [
		types.InlineKeyboardButton("Велосипеды", callback_data="/velo"),
		#types.InlineKeyboardButton("Запчасти", callback_data="/parts"),
		types.InlineKeyboardButton("Неисправности", callback_data="/problem"),
		types.InlineKeyboardButton("Опасная зона", callback_data="/danger")
	]
	markup.add(*buttons)
	bot.send_message(message.chat.id, "Бот для просмотра и редактирования данных о велосипедах\n\nГлавное меню", reply_markup=markup)


@bot.message_handler(commands=['velo'])
def velo(message):
	markup = types.InlineKeyboardMarkup(row_width=1)
	buttons = [
		types.InlineKeyboardButton("Краткая информация", callback_data="/short_info"),
		types.InlineKeyboardButton("Подробная информация", callback_data="/long_info"),
		types.InlineKeyboardButton("Для заявки на ремонт", callback_data="/broken"),
		types.InlineKeyboardButton("Главное меню", callback_data="/menu")
	]
	markup.add(*buttons)

	bot.send_message(message.chat.id, "Велосипеды", reply_markup=markup)


@bot.message_handler(commands=['short_info'])
def short_info(message):
	text = "Нет велосипедов"
	db = sqlite3.connect('VeloDB.db', check_same_thread=False)
	c = db.cursor()
	c.execute("""
	SELECT number, VIN, condition 
	FROM bikes
	ORDER BY number
	""")
	table = c.fetchall()
	if len(table) > 0:
		text = "Всего велосипедов: " + str(len(table)) + "\n"
		good = 0
		bad = 0
		for row in table:
			if row[2] == 1:
				good += 1
			else:
				bad += 1
		text += "На ходу: " + str(good) + "\n"
		text += "Сломаны: " + str(bad) + "\n\n"

		for row in table:
			num = str(row[0])
			vin = str(row[1])
			cond = " "
			if row[2] == 1:
				cond = "на ходу"
			elif row[2] == 2:
				cond = "требует ремонт"
			elif row[2] == 3:
				cond = "сломан"
			text += f'{num:>3}{vin:^18}{cond:>8}' + '\n'

	c.close()
	db.close()
	bot.send_message(message.chat.id, text)
	markup = types.InlineKeyboardMarkup(row_width=1)
	buttons = [
		types.InlineKeyboardButton("Назад", callback_data="/velo"),
		types.InlineKeyboardButton("Главное меню", callback_data="/menu")
	]
	markup.add(*buttons)
	bot.send_message(message.chat.id, "Краткая информация", reply_markup=markup)


@bot.message_handler(commands=['long_info'])
def long_info(message):
	text = "Нет велосипедов"
	db = sqlite3.connect('VeloDB.db', check_same_thread=False)
	c = db.cursor()
	c.execute("""
	SELECT id, number, VIN, condition 
	FROM bikes
	ORDER BY number
	""")
	table_velo = c.fetchall()
	text_count = ""
	if len(table_velo) > 0:
		text_count = "Всего велосипедов: " + str(len(table_velo)) + "\n"
		good = 0
		bad = 0
		for row in table_velo:
			if row[3] == 1:
				good += 1
			else:
				bad += 1
		text_count += "На ходу: " + str(good) + "\n"
		text_count += "Сломаны: " + str(bad) + "\n\n"
	c.close()
	db.close()
	bot.send_message(message.chat.id, text_count)

	if len(table_velo) > 0:
		text = ""
		for row_velo in table_velo:
			id_velo = str(row_velo[0])
			num = str(row_velo[1])
			vin = str(row_velo[2])
			cond = " "
			if row_velo[3] == 1:
				cond = "на ходу"
			elif row_velo[3] == 2:
				cond = "требует ремонт"
			elif row_velo[3] == 3:
				cond = "сломан"
			text += num + " " + vin + " " + cond + "\n"
			db = sqlite3.connect('VeloDB.db', check_same_thread=False)
			c = db.cursor()
			c.execute("""
			SELECT comment
			FROM problems
			WHERE id_velo = ? AND status = TRUE
			""", (id_velo, ))
			table_problems = c.fetchall()
			c.close()
			db.close()
			if len(table_problems) > 0:
				for row_problems in table_problems:
					text += "\t\t\t" + str(row_problems[0]) + "\n"
	bot.send_message(message.chat.id, text)
	markup = types.InlineKeyboardMarkup(row_width=1)
	buttons = [
		types.InlineKeyboardButton("Назад", callback_data="/velo"),
		types.InlineKeyboardButton("Главное меню", callback_data="/menu")
	]
	markup.add(*buttons)
	bot.send_message(message.chat.id, "Подробная информация", reply_markup=markup)


@bot.message_handler(commands=['broken'])
def broken(message):
	text_count = "Нет велосипедов"
	db = sqlite3.connect('VeloDB.db', check_same_thread=False)
	c = db.cursor()
	c.execute("""
		SELECT number, VIN, condition 
		FROM bikes
		ORDER BY number
		""")
	table = c.fetchall()
	if len(table) > 0:
		text_count = "Всего велосипедов: " + str(len(table)) + "\n"
		good = 0
		bad = 0
		for row in table:
			if row[2] == 1:
				good += 1
			else:
				bad += 1
		text_count += "На ходу: " + str(good) + "\n"
		text_count += "Сломаны: " + str(bad) + "\n\n"
	c.close()
	db.close()
	bot.send_message(message.chat.id, text_count)

	db = sqlite3.connect('VeloDB.db', check_same_thread=False)
	c = db.cursor()
	c.execute("""
		SELECT id, number, VIN 
		FROM bikes
		WHERE condition = 2
		ORDER BY number
		""")
	table_velo = c.fetchall()
	c.close()
	db.close()

	text_info = ""
	if len(table_velo) > 0:
		for row_velo in table_velo:
			id_velo = row_velo[0]
			vin = row_velo[2]
			text_info += f'<b>{vin}</b>\n'
			db = sqlite3.connect('VeloDB.db', check_same_thread=False)
			c = db.cursor()
			c.execute("""
				SELECT comment
				FROM problems
				WHERE id_velo = ? AND status = TRUE
				""", (id_velo,))
			table_problems = c.fetchall()
			c.close()
			db.close()
			if len(table_problems) > 0:
				num = 0
				for row_problems in table_problems:
					num += 1
					text_info += f'\t\t\t{num}) {str(row_problems[0])}\n'
	bot.send_message(message.chat.id, text_info, parse_mode='html')
	markup = types.InlineKeyboardMarkup(row_width=1)
	buttons = [
		types.InlineKeyboardButton("Назад", callback_data="/velo"),
		types.InlineKeyboardButton("Главное меню", callback_data="/menu")
	]
	markup.add(*buttons)
	bot.send_message(message.chat.id, "Для заявки", reply_markup=markup)


@bot.message_handler(commands=['danger'])
def danger(message):
	markup = types.InlineKeyboardMarkup(row_width=1)
	buttons = [
		types.InlineKeyboardButton("Добавить велосипед", callback_data="/add_velo"),
		types.InlineKeyboardButton("Перебить VIN велосипеда", callback_data="/edit_vin_velo"),
		types.InlineKeyboardButton("Удалить велосипед", callback_data="/del_velo"),
		types.InlineKeyboardButton("Добавить пользователя", callback_data="/add_user"),
		types.InlineKeyboardButton("Удалить пользователя", callback_data="/del_user"),
		types.InlineKeyboardButton("Главное меню", callback_data="/menu")
	]
	markup.add(*buttons)

	bot.send_message(message.chat.id, "Опасная зона", reply_markup=markup)


@bot.message_handler(commands=['add_velo'])
def add_velo(message):
	markup = types.InlineKeyboardMarkup(row_width=1)
	buttons = [
		types.InlineKeyboardButton("Назад", callback_data="/danger"),
		types.InlineKeyboardButton("Главное меню", callback_data="/menu")
	]
	markup.add(*buttons)
	bot.send_message(message.chat.id, "Добавить велосипед\n\nВводить через пробел в формате:\nномер VIN цифра_состояния\
	(1 - на ходу, 2 - требует ремонт, 3 - сломан)", reply_markup=markup)
	reply = types.ForceReply(selective=False)
	send = bot.send_message(message.chat.id, "Добавление...", reply_markup=reply)
	bot.register_next_step_handler(send, add_velo_send)


def add_velo_send(message):
	if len(message.text) > 0:
		velo_list = message.text.split("\n")
		try:
			for velo in velo_list:
				temp = velo.split()
				db = sqlite3.connect('VeloDB.db', check_same_thread=False)
				c = db.cursor()
				c.execute("""
				INSERT INTO bikes (
				number,
				VIN,
				condition
				)
				VALUES(
				?,
				?,
				?
				)""", (temp[0], temp[1], temp[2]))
				db.commit()
				c.close()
				db.close()
			bot.send_message(message.chat.id, "Добавлено.")
		except sqlite3.Error as error:
			bot.send_message(message.chat.id, "Записи не добавлены, ошибка при работе: " + str(error))
		except IndexError as error:
			bot.send_message(message.chat.id, "Вы ввели недостаточно данных о велосипедах. Ошибка: " + str(error))


@bot.message_handler(commands=['del_velo'])
def del_velo(message):
	markup = types.InlineKeyboardMarkup(row_width=1)
	buttons = [
		types.InlineKeyboardButton("Назад", callback_data="/danger"),
		types.InlineKeyboardButton("Главное меню", callback_data="/menu")
	]
	markup.add(*buttons)
	bot.send_message(message.chat.id, "Удалить велосипед\n\nВведите номер велосипеда.", reply_markup=markup)
	reply = types.ForceReply(selective=False)
	send = bot.send_message(message.chat.id, "Удаление...", reply_markup=reply)
	bot.register_next_step_handler(send, del_velo_send)


def del_velo_send(message):
	if len(message.text) > 0:
		velo_list = message.text.split()
		try:
			for velo in velo_list:
				db = sqlite3.connect('VeloDB.db', check_same_thread=False)
				c = db.cursor()
				c.execute("""
				DELETE FROM bikes
				WHERE number = ?""", (velo, ))
				db.commit()
				c.close()
				db.close()
		except sqlite3.Error as error:
			bot.send_message(message.chat.id, "Записи не удалены, ошибка при работе: " + str(error))


@bot.message_handler(commands=['edit_vin_velo'])
def edit_vin_velo(message):
	markup = types.InlineKeyboardMarkup(row_width=1)
	buttons = [
		types.InlineKeyboardButton("Назад", callback_data="/danger"),
		types.InlineKeyboardButton("Главное меню", callback_data="/menu")
	]
	markup.add(*buttons)
	bot.send_message(message.chat.id, "Редактировать VIN велосипеда\n\nВведите номер велосипеда и новый VIN через пробел.", reply_markup=markup)
	reply = types.ForceReply(selective=False)
	send = bot.send_message(message.chat.id, "Редактирование...", reply_markup=reply)
	bot.register_next_step_handler(send, edit_vin_velo_send)


def edit_vin_velo_send(message):
	if len(message.text) > 0:
		velo_list = message.text.split("\n")
		try:
			for velo in velo_list:
				temp = velo.split(" ")
				db = sqlite3.connect('VeloDB.db', check_same_thread=False)
				c = db.cursor()
				c.execute("""
				UPDATE bikes
				SET VIN = ?
				WHERE number = ?""", (temp[1], temp[0]))
				db.commit()
				c.close()
				db.close()
		except sqlite3.Error as error:
			bot.send_message(message.chat.id, "Записи не изменены, ошибка при работе: " + str(error))
		except IndexError as error:
			bot.send_message(message.chat.id, "Вы ввели недостаточно данных о велосипедах. Ошибка: " + str(error))


@bot.message_handler(commands=['problem'])
def problem(message):
	markup = types.InlineKeyboardMarkup(row_width=1)
	buttons = [
		types.InlineKeyboardButton("Добавить", callback_data="/add_problem"),
		types.InlineKeyboardButton("Удалить", callback_data="/del_problem"),
		types.InlineKeyboardButton("Изменить статус велосипеда", callback_data="/edit_status_velo"),
		types.InlineKeyboardButton("Список закрытых", callback_data="/finished_problems"),
		types.InlineKeyboardButton("Главное меню", callback_data="/menu")
	]
	markup.add(*buttons)

	bot.send_message(message.chat.id, "Неисправности", reply_markup=markup)


@bot.message_handler(commands=['edit_vin_velo'])
def edit_status_velo(message):
	markup = types.InlineKeyboardMarkup(row_width=1)
	buttons = [
		types.InlineKeyboardButton("Назад", callback_data="/problem"),
		types.InlineKeyboardButton("Главное меню", callback_data="/menu")
	]
	markup.add(*buttons)
	bot.send_message(message.chat.id, "Редактировать статус велосипеда\n\nВведите номер велосипеда и новый статус через пробел. Статус вводить цифрой: 1 - на ходу, 2 - требует ремонт, 3 - сломан.", reply_markup=markup)
	reply = types.ForceReply(selective=False)
	send = bot.send_message(message.chat.id, "Редактирование...", reply_markup=reply)
	bot.register_next_step_handler(send, edit_status_velo_send)


def edit_status_velo_send(message):
	if len(message.text) > 0:
		velo_list = message.text.split("\n")
		try:
			for velo in velo_list:
				temp = velo.split(" ")
				db = sqlite3.connect('VeloDB.db', check_same_thread=False)
				c = db.cursor()
				c.execute("""
				UPDATE bikes
				SET condition = ?
				WHERE number = ?""", (temp[1], temp[0]))
				db.commit()
				c.close()
				db.close()
		except sqlite3.Error as error:
			bot.send_message(message.chat.id, "Записи не изменены, ошибка при работе: " + str(error))
		except IndexError as error:
			bot.send_message(message.chat.id, "Вы ввели недостаточно данных о велосипедах. Ошибка: " + str(error))

	markup = types.InlineKeyboardMarkup(row_width=1)
	buttons = [
		types.InlineKeyboardButton("Назад", callback_data="/problem"),
		types.InlineKeyboardButton("Главное меню", callback_data="/menu")
	]
	markup.add(*buttons)
	bot.send_message(message.chat.id, "Статус", reply_markup=markup)



@bot.message_handler(commands=['add_problem'])
def add_problem(message):
	markup = types.InlineKeyboardMarkup(row_width=1)
	buttons = [
		types.InlineKeyboardButton("Назад", callback_data="/problem"),
		types.InlineKeyboardButton("Главное меню", callback_data="/menu")
	]
	markup.add(*buttons)
	bot.send_message(message.chat.id, "Добавить неисправность\n\nВводить через пробел в формате: номер_велосипеда неисправность", reply_markup=markup)
	reply = types.ForceReply(selective=False)
	send = bot.send_message(message.chat.id, "Добавление...", reply_markup=reply)
	bot.register_next_step_handler(send, add_problem_send)


def add_problem_send(message):
	if len(message.text) > 0:
		velo_list = message.text.split("\n")
		try:
			for velo in velo_list:
				temp = velo.split(" ", 1)
				db = sqlite3.connect('VeloDB.db', check_same_thread=False)
				c = db.cursor()
				c.execute("""
				INSERT INTO problems (
				id_velo,
				comment,
				status,
				date_start,
				date_finish
				)
				VALUES(
				(SELECT id FROM bikes WHERE number = ?),
				?,
				TRUE,
				date('now'),
				NULL
				)""", (temp[0], temp[1]))
				db.commit()
				c.close()
				c = db.cursor()
				c.execute("""
				UPDATE bikes
				SET condition = 2
				WHERE number = ?""", (temp[0],))
				db.commit()
				c.close()
				db.close()
			bot.send_message(message.chat.id, "Добавлено.")
		except sqlite3.Error as error:
			bot.send_message(message.chat.id, "Записи не добавлены, ошибка при работе: " + str(error))
		except IndexError as error:
			bot.send_message(message.chat.id, "Вы ввели недостаточно данных. Ошибка: " + str(error))

	markup = types.InlineKeyboardMarkup(row_width=1)
	buttons = [
		types.InlineKeyboardButton("Назад", callback_data="/problem"),
		types.InlineKeyboardButton("Главное меню", callback_data="/menu")
	]
	markup.add(*buttons)
	bot.send_message(message.chat.id, "Неисправности", reply_markup=markup)



@bot.message_handler(commands=['del_problem'])
def del_problem(message):
	markup = types.InlineKeyboardMarkup(row_width=1)
	buttons = [
		types.InlineKeyboardButton("Назад", callback_data="/problem"),
		types.InlineKeyboardButton("Главное меню", callback_data="/menu")
	]
	markup.add(*buttons)
	bot.send_message(message.chat.id, "Удалить неисправность\n\nВведите номер велосипеда.", reply_markup=markup)
	reply = types.ForceReply(selective=False)
	send = bot.send_message(message.chat.id, "...", reply_markup=reply)
	bot.register_next_step_handler(send, del_problem_send)


def del_problem_send(message):
	markup = types.InlineKeyboardMarkup(row_width=1)
	buttons = [
		types.InlineKeyboardButton("Назад", callback_data="/problem"),
		types.InlineKeyboardButton("Главное меню", callback_data="/menu")
	]
	markup.add(*buttons)
	bot.send_message(message.chat.id, "Удалить неисправность\n\nВведите номер(а) неисправности(ей).", reply_markup=markup)

	if len(message.text) > 0:
		velo = message.text
		text = "Нет данных"
		try:
			db = sqlite3.connect('VeloDB.db', check_same_thread=False)
			c = db.cursor()
			c.execute("""
			SELECT id, comment, date_start
			FROM problems
			WHERE id_velo = (SELECT id FROM bikes WHERE number = ?) AND status = TRUE""", (velo, ))
			table = c.fetchall()
			if len(table) > 0:
				text = ""
				for row in table:
					text += f'{row[0]:<5}{row[1]}{row[2]:>12}\n'
			c.close()
			db.close()
			bot.send_message(message.chat.id, text)
			reply = types.ForceReply(selective=False)
			send = bot.send_message(message.chat.id, "...", reply_markup=reply)
			bot.register_next_step_handler(send, del_problem_finish_send)
		except sqlite3.Error as error:
			bot.send_message(message.chat.id, "ошибка при работе: " + str(error))


def del_problem_finish_send(message):
	if len(message.text) > 0:
		problems = message.text.split()
		try:
			for problem in problems:
				db = sqlite3.connect('VeloDB.db', check_same_thread=False)
				c = db.cursor()
				c.execute("""
				UPDATE problems
				SET status = FALSE, date_finish = date('now')
				WHERE id = ?
				""", (problem, ))
				db.commit()
				c.close()

				c = db.cursor()
				c.execute("""
				UPDATE bikes
				SET condition = 1
				WHERE
					id = (	SELECT id_velo 
							FROM problems 
							WHERE id = ?) 
					AND (	SELECT COUNT(*) 
							FROM problems 
							WHERE status = TRUE 
								AND id_velo = (	SELECT id_velo 
												FROM problems 
												WHERE id = ?)) = 0""",
						  (problem, problem))
				db.commit()
				c.close()
				db.close()
		except sqlite3.Error as error:
			bot.send_message(message.chat.id, "Записи не добавлены, ошибка при работе: " + str(error))
		except IndexError as error:
			bot.send_message(message.chat.id, "Вы ввели недостаточно данных. Ошибка: " + str(error))

	markup = types.InlineKeyboardMarkup(row_width=1)
	buttons = [
		types.InlineKeyboardButton("Назад", callback_data="/problem"),
		types.InlineKeyboardButton("Главное меню", callback_data="/menu")
	]
	markup.add(*buttons)
	bot.send_message(message.chat.id, "Удалить неисправность", reply_markup=markup)


@bot.message_handler(commands=['finished_problems'])
def finished_problems(message):
	text = "Нет данных"
	db = sqlite3.connect('VeloDB.db', check_same_thread=False)
	c = db.cursor()
	try:
		c.execute("""
			SELECT bikes.number, problems.comment, problems.date_start, problems.date_finish
			FROM bikes, problems
			WHERE bikes.id = problems.id_velo AND problems.status = FALSE
			ORDER BY problems.date_finish, bikes.number
			""")
		table = c.fetchall()
		if len(table) > 0:
			text = ""
			for row in table:
				num = str(row[0])
				comment = str(row[1])
				date_start = str(row[2])
				date_finish = str(row[3])
				text += f'{num} {comment} {date_start} -> {date_finish}\n'
	except sqlite3.Error as error:
		print(error)
	finally:
		c.close()
		db.close()
		bot.send_message(message.chat.id, text)

		markup = types.InlineKeyboardMarkup(row_width=1)
		buttons = [
			types.InlineKeyboardButton("Назад", callback_data="/problem"),
			types.InlineKeyboardButton("Главное меню", callback_data="/menu")
		]
		markup.add(*buttons)
		bot.send_message(message.chat.id, "Завершённые неисправности", reply_markup=markup)


@bot.message_handler(commands=['add_user'])
def add_user(message):
	markup = types.InlineKeyboardMarkup(row_width=1)
	buttons = [
		types.InlineKeyboardButton("Назад", callback_data="/danger"),
		types.InlineKeyboardButton("Главное меню", callback_data="/menu")
	]
	markup.add(*buttons)
	bot.send_message(message.chat.id, "Добавить пользователя.\nУкажите id и имя пользователя через пробел. ", reply_markup=markup)

	reply = types.ForceReply(selective=False)
	send = bot.send_message(message.chat.id, "...", reply_markup=reply)
	bot.register_next_step_handler(send, add_user_send)


def add_user_send(message):
	user = message.text.split(" ", 1)
	try:
		db = sqlite3.connect('VeloDB.db', check_same_thread=False)
		c = db.cursor()
		c.execute("""
		INSERT INTO users (
			telegram_id,
			name,
			admin
		)
		VALUES(
			?,
			?,
			FALSE
		)""", (user[0], user[1]))
		db.commit()
		c.close()
		db.close()
	except sqlite3.Error as error:
		bot.send_message(message.chat.id, "Записи не добавлены, ошибка при работе: " + str(error))
	except IndexError as error:
		bot.send_message(message.chat.id, "Вы ввели недостаточно данных. Ошибка: " + str(error))

	markup = types.InlineKeyboardMarkup(row_width=1)
	buttons = [
		types.InlineKeyboardButton("Назад", callback_data="/danger"),
		types.InlineKeyboardButton("Главное меню", callback_data="/menu")
	]
	markup.add(*buttons)
	bot.send_message(message.chat.id, "Добавление пользователя.", reply_markup=markup)


@bot.message_handler(commands=['del_user'])
def del_user(message):
	markup = types.InlineKeyboardMarkup(row_width=1)
	buttons = [
		types.InlineKeyboardButton("Назад", callback_data="/danger"),
		types.InlineKeyboardButton("Главное меню", callback_data="/menu")
	]
	markup.add(*buttons)
	bot.send_message(message.chat.id, "И шо ты тут забыл?", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
	if call.data == "/velo":
		answer(call)
		bot.clear_step_handler(call.message)
		velo(call.message)
	elif call.data == "/menu":
		answer(call)
		bot.clear_step_handler(call.message)
		menu(call.message)
	elif call.data == "/short_info":
		answer(call)
		short_info(call.message)
	elif call.data == "/long_info":
		answer(call)
		long_info(call.message)
	elif call.data == "/broken":
		answer(call)
		broken(call.message)
	elif call.data == "/danger":
		answer(call)
		bot.clear_step_handler(call.message)
		danger(call.message)
	elif call.data == "/add_velo":
		answer(call)
		add_velo(call.message)
	elif call.data == "/del_velo":
		answer(call)
		del_velo(call.message)
	elif call.data == "/edit_vin_velo":
		answer(call)
		edit_vin_velo(call.message)
	elif call.data == "/problem":
		answer(call)
		bot.clear_step_handler(call.message)
		problem(call.message)
	elif call.data == "/add_problem":
		answer(call)
		add_problem(call.message)
	elif call.data == "/del_problem":
		answer(call)
		del_problem(call.message)
	elif call.data == "/edit_status_velo":
		answer(call)
		edit_status_velo(call.message)
	elif call.data == "/finished_problems":
		answer(call)
		finished_problems(call.message)
	elif call.data == "/add_user":
		answer(call)
		add_user(call.message)
	elif call.data == "/del_user":
		answer(call)
		del_user(call.message)


def answer(call):
	bot.answer_callback_query(call.id)
	bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id)
	bot.send_message(call.message.chat.id, "Переход:\n\n" + call.data)


bot.infinity_polling()
