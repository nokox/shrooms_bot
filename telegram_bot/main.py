from model import ClassPredictor
from telegram_token import token
import torch
from config import reply_texts, shrooms_dict
import numpy as np
from PIL import Image
from io import BytesIO


model = ClassPredictor()


def get_full_name(classname):
    return shrooms_dict[classname]+' ('+classname+')'


def send_prediction_on_photo(bot, update):
    chat_id = update.message.chat_id

    print("Got image from {}".format(chat_id))

    # получаем информацию о картинке
    image_info = update.message.photo[-1]
    image_file = bot.get_file(image_info)
    image_stream = BytesIO()
    image_file.download(out=image_stream)

    class_, prob_ = model.predict(image_stream)

    # теперь отправим результат
    bot.sendMessage(chat_id=update.message.chat_id,
                    text='<b>' + get_full_name(str(class_)) + '</b>, вероятность: {}%'.format(prob_),
                    parse_mode='HTML')
    print("Sent Answer to user, predicted: {}".format(class_))


def start(bot, update):
    # подробнее об объекте update: https://core.telegram.org/bots/api#update
    bot.sendMessage(chat_id=update.message.chat_id, text=reply_texts['hello'], parse_mode='Markdown')
    bot.sendMessage(chat_id=update.message.chat_id, text=reply_texts['guide'])
    bot.sendMessage(chat_id=update.message.chat_id, text=reply_texts['warning'])


def shrooms_list(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text=reply_texts['shrooms_list'])


def conversation(bot, update):
    # bot.send_message(chat_id=update.message.chat_id, text=last_prediction)
    bot.send_message(chat_id=update.message.chat_id, text=reply_texts['reg_answer'])


def unknown(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=reply_texts['unknown_command'])


if __name__ == '__main__':
    from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
    import logging

    # Включим самый базовый логгинг, чтобы видеть сообщения об ошибках
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

    updater = Updater(token=token)
    updater.dispatcher.add_handler(MessageHandler(Filters.photo, send_prediction_on_photo))

    start_handler = CommandHandler('start', start)  # этот обработчик реагирует только на команду /start
    list_handler = CommandHandler('list', shrooms_list)  # этот обработчик реагирует только на команду /list
    echo_handler = MessageHandler(Filters.text, conversation)  # реагирует на любой текст
    unknown_handler = MessageHandler(Filters.command, unknown)


    # регистрируем обработчики
    updater.dispatcher.add_handler(start_handler)
    updater.dispatcher.add_handler(list_handler)
    updater.dispatcher.add_handler(echo_handler)
    updater.dispatcher.add_handler(unknown_handler)

    updater.start_polling()  # start the bot


