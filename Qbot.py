from config import TOKEN
import sys
import time
import os
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from qrcode import QRCode
from io import BytesIO
from pyzbar.pyzbar import decode
from PIL import Image
import ssl


bot = telepot.Bot(TOKEN)

def create_QR(msg):
    qr = QRCode()
    qr.add_data(msg['text'])
    qr.make(fit=True)
    qr_img = qr.make_image()

    img = BytesIO()
    qr_img.save(img)
    img.seek(0)

    return img


def read_QR(msg,id):
    bot.download_file(msg['photo'][-1]['file_id'], "QRcodes/file.png")
    img = Image.open("QRcodes/file.png")
    qr_txt = decode(img)
    return qr_txt

try:
   _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
   # Legacy Python that doesn't verify HTTPS certificates by default
   pass
else:
   # Handle target environment that doesn't support HTTPS verification
   ssl._create_default_https_context = _create_unverified_https_context

def handle_chat(message):
   content_type, chat_type, chat_id = telepot.glance(message, flavor = 'chat')

   keyboard = InlineKeyboardMarkup(inline_keyboard = [
        [InlineKeyboardButton(text="Help", callback_data='help')],
   ])

   if content_type == 'photo':
       bot.sendMessage(chat_id, "Identificazione messaggio")
       qr_txt = read_QR(message, id)

       if len(qr_txt)>0:
           for txt in qr_txt:
               bot.sendMessage(chat_id, ""+str(txt.data))
       else:
           bot.sendMessage(chat_id, "Nessun QR Code trovato")

   elif content_type == 'text':
       bot.sendMessage(chat_id, "Generazione QR Code")
       bot.sendPhoto(chat_id, create_QR(message))

   else:
       bot.sendMessage(chat_id, "Non lavoro con questi dati", reply_markup = keyboard)



def handle_query(message):
   query_id, from_id, query_data = telepot.glance(message, flavor = 'callback_query')

   bot.answerCallbackQuery(query_id, text="Solo foto o messaggi")


#bot.setWebhook()
MessageLoop(bot, {"chat": handle_chat, "callback_query": handle_query}).run_as_thread()

while 1:
   time.sleep(10)
