from model import ClassPredictor
from telegram_token import token
import torch
from config import reply_texts, shrooms_dict
import numpy as np
from PIL import Image
from io import BytesIO

model = ClassPredictor()


# функция, которая возвращает полное наименование гриба (лат.+рус.)
def get_full_name(classname):
    return shrooms_dict[classname] + ' (' + classname + ')'


def send_prediction_on_photo(bot, update):
    chat_id = update.message.chat_id

    print("Got image from {}".format(chat_id))

    # получаем информацию о картинке
    image_info = update.message.photo[-1]
    image_file = bot.get_file(image_info)
    image_stream = BytesIO()
    image_file.download(out=image_stream)

    class_, prob_ = model.predict(image_stream)

    # создадим кнопки для получения доп. информации
    keyboard = [[telegram.InlineKeyboardButton("Инфо о грибе",
                                               url='https://ru.wikipedia.org/wiki/'
                                               + str(class_).replace(' ', '_')),
                 telegram.InlineKeyboardButton("Другие фото",
                                               url='https://www.google.com/search?q='
                                               + str(class_).replace(' ', '+') + '&tbm=isch')]]
    reply_markup = telegram.InlineKeyboardMarkup(keyboard)

    # теперь отправим результат
    bot.sendMessage(chat_id=update.message.chat_id,
                    text='<b>' + get_full_name(str(class_)) + '</b>, вероятность: {}%'.format(prob_),
                    parse_mode='HTML',
                    reply_markup=reply_markup)

    print("Sent Answer to user, predicted: {}".format(class_))


def start(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text=reply_texts['hello'], parse_mode='Markdown')
    bot.sendMessage(chat_id=update.message.chat_id, text=reply_texts['guide'])


def shrooms_list(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text=reply_texts['shrooms_list'])


def conversation(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=reply_texts['reg_answer'])


def unknown(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=reply_texts['unknown_command'])


if __name__ == '__main__':
    from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, CallbackQueryHandler
    import telegram
    import logging

    # Включим самый базовый логгинг, чтобы видеть сообщения об ошибках
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

    updater = Updater(token=token)

    # регистрируем обработчики
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.photo, send_prediction_on_photo))
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('list', shrooms_list))
    dp.add_handler(MessageHandler(Filters.text, conversation))
    dp.add_handler(MessageHandler(Filters.command, unknown))
    dp.add_handler(CallbackQueryHandler(menu_actions))

    updater.start_polling()  # start the bot
