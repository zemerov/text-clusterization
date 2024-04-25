import os
from time import sleep
from loguru import logger
from manager import Manager

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

COMPANY_NAME = 0

TOP_COMPANIES_KEYBOARD = [
    ["Пятёрочка", "Магнит", "Красное&Белое"],
    ["Wildberries", "Ozon", "Вкусно — и точка"],
    ["Перекрёсток", "Fix Price", "Лукойл"],
    ["СберБанк", "Леруа Мерлен", "Дикси"],
]


analytics_manager = Manager()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about their gender."""

    await update.message.reply_text(
        """Добрый день!
Я бот, помогающий анализировать отзывы, которые люди оставляют на организации! 
Напишите название компании, отзывы на которую необходимо проанализировать. 
Можно выбрать на клавиатуре или написать название самостоятельно.""",
        reply_markup=ReplyKeyboardMarkup(
            TOP_COMPANIES_KEYBOARD,
            one_time_keyboard=True,
            input_field_placeholder="Напишите название компании",
            resize_keyboard=True,
        ),
    )

    return COMPANY_NAME


async def construct_report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    company_name = update.message.text
    # TODO добавить проверку на наличие компании в датасете
    logger.info(f"Пользователь: {user.id}; Название компании: {company_name}")

    await update.message.reply_text(
        f"Отлично, мы начали кластеризацию отзывов на компанию {company_name}",
        reply_markup=ReplyKeyboardRemove(),
    )

    resulting_file_paths = analytics_manager.get_report(company_name)
    await update.message.reply_text("Ваш отчет готов!")

    for path in resulting_file_paths:
        with open(path, 'rb') as file:
            if path.suffix == ".png":
                await update.message.reply_photo(file)
            elif path.suffix == ".csv":
                await update.message.reply_document(file)
            else:
                logger.warning(f"Unsupported file extension {path.suffix}. Skip file: {path}")



    await update.message.reply_text(
        """Теперь вы можете снова написать название компании, отзывы на которую необходимо проанализировать.
Можно выбрать на клавиатуре или написать название самостоятельно.""",
        reply_markup=ReplyKeyboardMarkup(
            TOP_COMPANIES_KEYBOARD,
            one_time_keyboard=True,
            input_field_placeholder="Напишите название компании:",
            resize_keyboard=True,
        ),
    )

    return COMPANY_NAME


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    token = os.environ["BOT_TOKEN"]
    application = Application.builder().token(token).build()

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            COMPANY_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, construct_report)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    logger.info("Starting conversation...")

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
