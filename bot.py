import requests
from dotenv import load_dotenv
import os
import redis

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Filters, Updater
from telegram.ext import CallbackQueryHandler, CommandHandler, \
    MessageHandler, CallbackContext

from moltin_api import get_products, add_product, \
    get_cart_items, get_product, \
    get_main_image, delete_cart_items, \
    create_customer


load_dotenv()
_database = None
database = {}


def get_moltin_token():
    moltin_client_id = os.getenv('MOLTIN_CLIENT_ID')
    data = {
        'client_id': moltin_client_id,
        'grant_type': 'implicit',
    }

    response = requests.post('https://api.moltin.com/oauth/access_token', data=data)
    response.raise_for_status()
    response = response.json()
    return response['access_token']


MOLTIN_TOKEN = get_moltin_token()


def start(update: Update, context: CallbackContext):
    products = get_products(MOLTIN_TOKEN)
    keyboard = [
        [InlineKeyboardButton(product['name'], callback_data=product['id'])]
        for product in products
    ]
    keyboard.append([InlineKeyboardButton('Корзина', callback_data='Корзина')])
    update.message.reply_text(
        text='Привет!',
        reply_markup=InlineKeyboardMarkup(keyboard)
        )
    return 'HANDLE_MENU'


def handle_basket(update: Update, context: CallbackContext):
    query = update.callback_query
    chat_id=query.message.chat_id 
    items = get_cart_items(MOLTIN_TOKEN, chat_id)['data']
    items_keyboard = [[InlineKeyboardButton('В меню', callback_data='В меню')]]
    items_keyboard.append(
        [InlineKeyboardButton('Оплатить', callback_data='Оплатить')]
    )
    if items:
        text = ''
        for item in items:
            text += '{}\n{}\n{} за кг\n{}шт в корзине стоимостью {}\n\n'.format(
                item['name'],
                item['description'],
                item['meta']['display_price']['with_tax']['unit']['formatted'],
                item['quantity'],
                item['meta']['display_price']['with_tax']['value']['formatted']
            )
            items_keyboard.append(
                [InlineKeyboardButton(f'Убрать из корзины {item["name"]}', callback_data=item['id'])]
            )
            
            update.callback_query.message.reply_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(items_keyboard)
            )
    else:
        update.callback_query.message.reply_text(
            text='Корзина пуста',
            reply_markup=InlineKeyboardMarkup(items_keyboard)
        )


def handle_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    chat_id=query.message.chat_id
    if query.data == 'Корзина':
        handle_basket(update, context)
        return 'HANDLE_CART'
    product = get_product(MOLTIN_TOKEN, query.data)
    text = '{}\n\n{}\n{}\n'.format(
        product['name'],
        product['meta']['display_price']['with_tax']['formatted'],
        product['description']
    )
    image_id = product['relationships']['main_image']['data']['id']
    image_link = get_main_image(image_id, MOLTIN_TOKEN)
    products_weights = [1, 3, 5]
    product_id = query.data
    keyboard = [
        [InlineKeyboardButton(product_weight, callback_data=f'{product_weight}|{product_id}') \
            for product_weight in products_weights],
        [InlineKeyboardButton('Корзина', callback_data='Корзина')],
        [InlineKeyboardButton('Назад', callback_data='Назад')]
    ]

    context.bot.send_photo(
        photo=image_link,
        caption=text,
        chat_id=chat_id,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    context.bot.delete_message(
        chat_id=chat_id,
        message_id=query.message.message_id,
    )

    return 'HANDLE_DESCRIPTION'


def handle_description(update: Update, context: CallbackContext):
    query = update.callback_query
    chat_id = query.message.chat_id

    if query.data == 'Назад':
        
        products = get_products(MOLTIN_TOKEN)
        keyboard = [
            [InlineKeyboardButton(product['name'], callback_data=product['id'])]
            for product in products
        ]
        update.callback_query.message.reply_text(
            text='Назад',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return 'HANDLE_MENU'
    
    if query.data == 'Корзина':
        handle_basket(update, context)
        return 'HANDLE_CART'
    
    quantity, product_id = query.data.split('|')

    add_product(
        MOLTIN_TOKEN,
        cart_id=chat_id,
        product_id=product_id,
        quantity=int(quantity)
    )
    return 'HANDLE_MENU'


def handle_cart(update: Update, context: CallbackContext):
    query = update.callback_query
    chat_id = query.message.chat_id

    if query.data == 'В меню':
        products = get_products(MOLTIN_TOKEN)
        keyboard = [
            [InlineKeyboardButton(product['name'], callback_data=product['id'])]
            for product in products
        ]
        keyboard.append([InlineKeyboardButton('Корзина', callback_data='Корзина')])
        update.callback_query.message.reply_text(
            text='Возврат в меню.',
            reply_markup=InlineKeyboardMarkup(keyboard)
            )
        return 'HANDLE_MENU'

    elif query.data == 'Оплатить':
        update.callback_query.message.reply_text(
            text='Введите пожалуйста ваш email'
        )
        return 'WAITING_EMAIL'

    else:
        delete_cart_items(MOLTIN_TOKEN, chat_id, query.data)
        products = get_products(MOLTIN_TOKEN)
        keyboard = [
            [InlineKeyboardButton(product['name'], callback_data=product['id'])]
            for product in products
        ]
        keyboard.append([InlineKeyboardButton('Корзина', callback_data='Корзина')])
        update.callback_query.message.reply_text(
            text='В меню',
            reply_markup=InlineKeyboardMarkup(keyboard)
            )
        return 'HANDLE_MENU'


def waiting_email(update: Update, context: CallbackContext):
    user_reply = update.message.text
    chat_id = update.message.from_user.id
    name = update.message.from_user.username
    if user_reply:
        create_customer(MOLTIN_TOKEN, name, email=user_reply)
        products = get_products(MOLTIN_TOKEN)
        keyboard = [
            [InlineKeyboardButton(product['name'], callback_data=product['id'])]
            for product in products
        ]
        keyboard.append([InlineKeyboardButton('Корзина', callback_data='Корзина')])
        update.message.reply_text(
            text='Email сохранен.Возврат в меню.',
            reply_markup=InlineKeyboardMarkup(keyboard)
            )
        return 'HANDLE_MENU'


def handle_users_reply(update: Update, context: CallbackContext):
    db = get_database_connection()
    
    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
    else:
        return

    if user_reply == '/start':
        user_state = 'START'
    else:
        user_state = db.get(chat_id)
    
    states_functions = {
        'START': start,
        'HANDLE_MENU': handle_menu,
        'HANDLE_DESCRIPTION': handle_description,
        'HANDLE_CART': handle_cart,
        'WAITING_EMAIL': waiting_email
    }
    state_handler = states_functions[user_state]
    next_state = state_handler(update, context)
    db.set(chat_id, next_state)


def get_database_connection():
    global _database
    if _database is None:
        database_host = os.getenv("REDIS_HOST")
        database_port = os.getenv("REDIS_PORT")
        _database = redis.Redis(
            host=database_host, 
            port=database_port,
            decode_responses=True
        )
    return _database


def main():
    token = os.getenv("TELEGRAM_TOKEN")
    updater = Updater(token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))
    updater.start_polling()


if __name__ == '__main__':
    main()
