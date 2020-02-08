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
import cv2
from PIL import Image
import ssl


#definition of bot using the TOKEN
bot = telepot.Bot(TOKEN)

'''
Convertion from text to QR_code
'''
def create_QR(msg):
    qr = QRCode()
    print(msg['text'])
    qr.add_data(msg['text'])
    qr.make(fit=True)
    qr_img = qr.make_image()

    img = BytesIO()
    qr_img.save(img)
    img.seek(0)

    return img


'''
Convertion from QR_code to text
'''
def read_QR(msg,id):
    #one saved image for each user that send a QRcode translation request
    filename = "QRcodes/file"+str(id)+".png"
    bot.download_file(msg['photo'][-1]['file_id'], filename)
    img = Image.open(filename)
    qr_txt = decode(img)
    #delete the element previously saved for the translation
    os.remove(filename)
    return qr_txt


'''
Extablishing an HTTPS connection
'''
try:
   _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
   # Legacy Python that doesn't verify HTTPS certificates by default
   pass
else:
   # Handle target environment that doesn't support HTTPS verification
   ssl._create_default_https_context = _create_unverified_https_context


'''
Handler of standard chat messages
'''
def handle_chat(message):
   content_type, chat_type, chat_id = telepot.glance(message, flavor = 'chat')

   filename = 'Users/type_'+str(chat_id)+'.txt'

   #if the user file doesn't exist, create it
   if(not os.path.isfile(filename)):
      f = open(filename, 'w')
      type = f.write('\n')
      f.close()

   #read the last required type of service
   f = open(filename, 'r')
   type = (f.readlines())[0].strip("\n")
   f.close()

   #keyboard created for the management of the types of the services
   keyboard = InlineKeyboardMarkup(inline_keyboard = [
        [InlineKeyboardButton(text="QRcode", callback_data='qr'), InlineKeyboardButton(text="Barcode", callback_data='bar')],
        [InlineKeyboardButton(text="Cryptography", callback_data='crypto'), InlineKeyboardButton(text="Programming", callback_data='programming')],
        [InlineKeyboardButton(text="Help", callback_data='help')]
   ])

   #qrcode translations
   if(type == 'qr'):
      if content_type == 'photo':
          bot.sendMessage(chat_id, "Identificazione messaggio")
          qr_txt = read_QR(message, chat_id)

          print(len(qr_txt))
          if len(qr_txt)>0:
              for txt in qr_txt:
                  bot.sendMessage(chat_id, str(txt.data.decode('utf8')))

          else:
              bot.sendMessage(chat_id, "Nessun QR Code trovato")

          f = open(filename, 'w')
          type = f.write('\n')
          f.close()

      elif content_type == 'text':
          bot.sendMessage(chat_id, "Generazione QR Code")
          bot.sendPhoto(chat_id, create_QR(message))

          f = open(filename, 'w')
          type = f.write('\n')
          f.close()

      else:
          bot.sendMessage(chat_id, "Change what you want to do\n or send me a photo or a text", reply_markup = keyboard)

   #barcode translations
   elif type == 'bar':
      if content_type == 'photo':
          bot.sendMessage(chat_id, "Identificazione messaggio")
          qr_txt = read_QR(message, id)

          f = open(filename, 'w')
          type = f.write('\n')
          f.close()

      else:
          bot.sendMessage(chat_id, "Change what you want to do\n or send me a text", reply_markup = keyboard)

   #no pendent services
   if(type==''):
      bot.sendMessage(chat_id, "Select what you want to do", reply_markup = keyboard)


'''
Management of the keyboard requests
'''
def handle_query(message):
   query_id, from_id, query_data = telepot.glance(message, flavor = 'callback_query')

   filename = 'Users/type_'+str(from_id)+'.txt'

   if query_data == 'qr':
      f = open(filename, 'w')
      type = f.write('qr\n')
      f.close()
      bot.answerCallbackQuery(query_id, text='QRcode mode')

   elif(query_data == 'bar'):
      f = open(filename, 'w')
      type = f.write('bar\n')
      f.close()
      bot.answerCallbackQuery(query_id, text='BarCode mode')

   elif(query_data == 'crypto'):
      bot.answerCallbackQuery(query_id, text='Cryptography applications')

   elif(query_data == 'programming'):
      bot.answerCallbackQuery(query_id, text='Programming notes')

   else:
      bot.answerCallbackQuery(query_id, text='QRcode generator/analysis, Barcode analysis\n Crypto and IT notes')


#bot.setWebhook()

'''
Execution of the bot and definition of functions w.r.t. the type of requests
'''
MessageLoop(bot, {"chat": handle_chat, "callback_query": handle_query}).run_as_thread()

while 1:
   time.sleep(10)
