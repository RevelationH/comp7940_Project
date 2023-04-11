import os

import telebot
import requests
from io import BytesIO
import datetime
import openai
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

openai.api_key = os.environ["openai_api_key"]
BOT_TOKEN = os.environ["BOT_TOKEN"]
rapid_api_key = os.environ["rapid_api_key"]
rapid_api_host = os.environ["rapid_api_host"]
firebase_api_key = os.environ["firebase_api_key"]
google_translate_url = os.environ["google_translate_url"]
firebase_url = os.environ["firebase_url"]

bot = telebot.TeleBot(BOT_TOKEN)

cred = credentials.Certificate("./hlxchatbot-firebase-adminsdk-uyu0n-50811b0183.json")
firebase_admin.initialize_app(cred, {
    'apiKey': firebase_api_key,
    'databaseURL': firebase_url
})

def time_check(message):
    user_id = message.from_user.id
    ref = db.reference()
    current_time = str(datetime.date.today())
    if ref.get() is None:
        ref.child("users").child(str(user_id)).set({"time": str(0), "last_time": current_time})
        return False
    else:
        if ref.child("users").child(str(user_id)).get() is None:
            ref.child("users").child(str(user_id)).set({"time": str(0), "last_time": str(current_time)})
            return False
        else:
            data_time =  str(ref.child("users").child(str(user_id)).child("last_time").get())
            time_value = int(ref.child("users").child(str(user_id)).child("time").get())
            time_value = time_value + 1
            if data_time == current_time:
                if time_value >= 99:
                    return True
                else:
                    new_data = {
                        "time": time_value,
                        "last_time": str(current_time)
                    }
                    ref.child("users").child(str(user_id)).update(new_data)
                    return False
            else:
                new_data = {
                    "time": str(0),
                    "last_time": str(current_time)
                }
                ref.child("users").child(str(user_id)).update(new_data)

@bot.message_handler(commands=["start", "hello"])
def send_welcome(message):
    print("start")
    usage_restrictions = time_check(message)
    if usage_restrictions:
        bot.send_message(message.chat.id, "You have reached the number of uses for the day")
        return
    print("Bot start!")
    bot.send_message(message.chat.id, "Hello, I am CrazyBot!\n"
                                      "Please give me a command!\n"
                                      "/chat: Let's chat! Anything is OK\n"
                                      "/image: I can give you a image based on your description\n"
                                      "/translate: I can translate your content from english to Chinese\n"
                                      "\n"
                                      "So, what do you want today?")

@bot.message_handler(commands=["chat"])
def chat_command_handler(message):
    bot.send_message(message.chat.id, "Let's chat! Please tell me what you want to talk to me.")
    bot.send_message(message.chat.id, "If you want to end the function, type: /stop")
    bot.register_next_step_handler(message, handle_chat_input)

def handle_chat_input(message):
    input_text = message.text
    print("chat message:", input_text)
    if input_text == '/stop':
        bot.send_message(message.chat.id, "The chat is disabled, please enter another command")
        return

    usage_restrictions = time_check(message)
    if usage_restrictions:
        bot.send_message(message.chat.id, "You have reached the number of uses for the day")
        return

    input_text = message.text
    messages = [
        {"role": "user", "content": input_text}
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=100
    )

    generated_text = response['choices'][0]['message']['content']

    bot.send_message(message.chat.id, generated_text)
    print("Chat finish")

    bot.register_next_step_handler(message, handle_chat_input)

@bot.message_handler(commands=["image"])
def image_command_handler(message):
    bot.send_message(message.chat.id, "Ok! Give me some hints about the image.")
    bot.send_message(message.chat.id, "If you want to end the function, type: /stop")

    bot.register_next_step_handler(message, handle_image_input)

def handle_image_input(message):
    input_text = message.text
    print("image message:", input_text)

    if input_text == '/stop':
        bot.send_message(message.chat.id, "The image generation is disabled, please enter another command")
        return

    usage_restrictions = time_check(message)
    if usage_restrictions:
        bot.send_message(message.chat.id, "You have reached the number of uses for the day")
        return

    response = openai.Image.create(prompt=input_text, model="image-alpha-001")
    image_url = response['data'][0]['url']
    image_data = requests.get(image_url).content
    image_bytesio = BytesIO(image_data)
    bot.send_photo(chat_id=message.chat.id, photo=image_bytesio)

    bot.register_next_step_handler(message, handle_image_input)

    print("image finish")

@bot.message_handler(commands=["translate"])
def trans_command_handler(message):
    bot.send_message(message.chat.id, "Please give me the content.")
    bot.send_message(message.chat.id, "If you want to end the function, type: /stop")

    bot.register_next_step_handler(message, handle_trans_input)

def handle_trans_input(message):
    input_text = message.text
    print("translate text:", input_text)

    if input_text == '/stop':
        bot.send_message(message.chat.id, "The translation is disabled, please enter another command")
        return

    usage_restrictions = time_check(message)
    if usage_restrictions:
        bot.send_message(message.chat.id, "You have reached the number of uses for the day")
        return

    url = google_translate_url

    target_language = "zh-CN"
    payload = f"q={input_text}&target={target_language}"
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "application/gzip",
        "X-RapidAPI-Key": rapid_api_key,
        "X-RapidAPI-Host": rapid_api_host
    }

    response = requests.request("POST", url, data=payload, headers=headers)
    response_json = response.json()

    translated_text = response_json["data"]["translations"][0]["translatedText"]
    print("Translated Text:", translated_text)

    bot.send_message(message.chat.id, translated_text)
    bot.register_next_step_handler(message, handle_trans_input)

@bot.message_handler(func=lambda msg: True)
def error_command_handler(message):
    bot.send_message(message.chat.id, "Unknown command, please choose one command as follow\n"
                                      "Please give me a command!\n"
                                      "/chat: Let's chat! Anything is OK\n"
                                      "/image: I can give you a image based on your description\n"
                                      "/translate: I can translate your content from english to Chinese\n")

if __name__ == '__main__':
    bot.infinity_polling()


