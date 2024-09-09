from telebot import types

def generate_menu(start_index=0, items = []):
    keyboard = types.InlineKeyboardMarkup()
    
    for i in range(start_index, min(start_index + 5, len(items))):
        item = items[i]
        text_name = f"{i+1}. {item['name']} - {item['distance']:.2f} km"
        keyboard.add(types.InlineKeyboardButton(text=text_name, callback_data=f"item_{i}"))
    
    # Добавляем кнопки "Назад" и "Вперёд"
    navigation_buttons = []
    
    if start_index > 0:
        navigation_buttons.append(types.InlineKeyboardButton("⬅️ Назад", callback_data=f"back_{start_index}"))
    
    if start_index + 5 < len(items):
        navigation_buttons.append(types.InlineKeyboardButton("Вперёд ➡️", callback_data=f"next_{start_index}"))
    
    keyboard.row(*navigation_buttons)
    
    return keyboard