import logging
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
import time
import random

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

# Глобальные переменные для хранения времени запуска таймера
timer_start_time = 0
timer_duration = 0


async def close_keyboard(update, context):
    await update.message.reply_text(
        "Ok",
        reply_markup=ReplyKeyboardRemove()
    )


async def start(update, context):
    await update.message.reply_text(
        "Привет. Пройдите небольшой опрос, пожалуйста!\n"
        "Вы можете прервать опрос, послав команду /stop.\n"
        "В каком городе вы живёте?")

    # Число-ключ в словаре states —
    # втором параметре ConversationHandler'а.
    return 1
    # Оно указывает, что дальше на сообщения от этого пользователя
    # должен отвечать обработчик states[1].
    # До этого момента обработчиков текстовых сообщений
    # для этого пользователя не существовало,
    # поэтому текстовые сообщения игнорировались.


# Добавили словарь user_data в параметры.
async def first_response(update, context):
    # Сохраняем ответ в словаре.
    context.user_data['locality'] = update.message.text
    await update.message.reply_text(
        f"Какая погода в городе {context.user_data['locality']}?")
    return 2


# Добавили словарь user_data в параметры.
async def second_response(update, context):
    weather = update.message.text
    logger.info(weather)
    # Используем user_data в ответе.
    await update.message.reply_text(
        f"Спасибо за участие в опросе! Привет, {context.user_data['locality']}!")
    context.user_data.clear()  # очищаем словарь с пользовательскими данными
    return ConversationHandler.END


async def skip(update, context):
    await update.message.reply_text(f"Какая погода у вас за окном?")
    return 3


async def second_alt(update, context):
    weather = update.message.text
    logger.info(weather)
    await update.message.reply_text(
        f"Спасибо за участие в опросе! Привет вам!")
    context.user_data.clear()
    return ConversationHandler.END


async def stop(update, context):
    await update.message.reply_text("Всего доброго!")
    return ConversationHandler.END


def main():
    application = Application.builder().token("5725660391:AAHifkRt5GF6L3g6DLOD3SfQnD2O9wotlC8").build()

    application.add_handler(CommandHandler("close_keyboard", close_keyboard))
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, first_response), CommandHandler('skip', skip)],
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, second_response)],
            3: [MessageHandler(filters.TEXT & ~filters.COMMAND, second_alt)]
        },

        # Точка прерывания диалога. В данном случае — команда /stop.
        fallbacks=[CommandHandler('stop', stop)]
    )

    application.add_handler(conv_handler)
    # Запускаем приложение.
    application.run_polling()


if __name__ == '__main__':
    main()
