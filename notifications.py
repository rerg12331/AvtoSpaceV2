import telebot
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import token
from bot.db import Session, User
bot = telebot.TeleBot(token)


def get_user_ids():
    with Session() as session:
        user_ids = session.query(User.user_id).all()
        return [user_id[0] for user_id in user_ids]
    
def send_message(chat_id, message_text):
    try:
        bot.send_message(chat_id, message_text)
    except Exception as e:
        print(f"Failed to send message to {chat_id}: {e}")

def send_to_all_chats(chat_ids, message_text):
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(send_message, chat_id, message_text) for chat_id in chat_ids]
        for future in as_completed(futures):
            future.result()  # Получаем результат или исключение

if __name__ == "__main__":
    
    chat_ids = get_user_ids()  # Список всех chat_id
    message_text = "⚠️На данный момент проходит техническое обслуживание⚠️"

    send_to_all_chats(chat_ids, message_text)
