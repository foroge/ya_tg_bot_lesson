import logging
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters
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
    reply_keyboard = [['/dice', '/timer']]
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    if job_removed:
        await update.message.reply_text('Таймер отменен!')
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    await update.message.reply_text("Выберите опцию:", reply_markup=markup)


async def dice(update, context):
    reply_keyboard = [['/one_x_6', '/two_x_6', "/one_x_20", "/back"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    await update.message.reply_text("Выберите тип кубика:", reply_markup=markup)


async def roll_dice(update, context, sides):
    result = random.randint(1, sides)
    await update.message.reply_text(f"Выпало число: {result}")


async def one_x_6(update, context):
    await roll_dice(update, context, 6)


async def two_x_6(update, context):
    await roll_dice(update, context, 6)
    await roll_dice(update, context, 6)


async def one_x_20(update, context):
    await roll_dice(update, context, 20)


async def timer(update, context):
    reply_keyboard = [['/30_second', '/1_minute', '/5_minute', '/back']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await update.message.reply_text("Выберите время:", reply_markup=markup)


def remove_job_if_exists(name, context):
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


async def set_timer(update, context, duration):
    chat_id = update.effective_message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    context.job_queue.run_once(task, duration, chat_id=chat_id, name=str(chat_id), data=duration)
    global timer_duration
    timer_duration = duration
    text = f'Засек {duration}'
    if job_removed:
        text += ' Старая задача удалена.'
    reply_keyboard = [['/close', '/back']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await update.effective_message.reply_text(text, reply_markup=markup)


async def task(context):
    global timer_duration
    await context.bot.send_message(context.job.chat_id, text=f'{timer_duration} секунд истекло')


async def unset(update, context):
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = 'Таймер отменен!' if job_removed else 'У вас нет активных таймеров'
    await update.message.reply_text(text)
    await timer(update, context)


async def thirty_seconds(update, context):
    await set_timer(update, context, 30)


async def one_minute(update, context):
    await set_timer(update, context, 60)


async def five_minutes(update, context):
    await set_timer(update, context, 300)


def main():
    application = Application.builder().token("5725660391:AAHifkRt5GF6L3g6DLOD3SfQnD2O9wotlC8").build()

    application.add_handler(CommandHandler("close_keyboard", close_keyboard))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("dice", dice))
    application.add_handler(CommandHandler("timer", timer))
    application.add_handler(CommandHandler("one_x_6", one_x_6))
    application.add_handler(CommandHandler("two_x_6", two_x_6))
    application.add_handler(CommandHandler("one_x_20", one_x_20))
    application.add_handler(CommandHandler("back", start))
    application.add_handler(CommandHandler("close", unset))
    application.add_handler(CommandHandler("30_second", thirty_seconds))
    application.add_handler(CommandHandler("1_minute", one_minute))
    application.add_handler(CommandHandler("5_minute", five_minutes))

    # Запускаем приложение.
    application.run_polling()


if __name__ == '__main__':
    main()
