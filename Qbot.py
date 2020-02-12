# reading of bot token
from config import TOKEN
# management of end of execution (terminal)
import sys
import signal
# setting of sleep for MessageLoop
import time
# OS routines
import os

# Translation of QRcodes
from qrcode import QRCode
# Management of bytes stream
from io import BytesIO
# decryption of QRcode
from pyzbar.pyzbar import decode
# opening of Images
from PIL import Image

# Management of Telegram Bot
import telepot
# Management of arrival of messages through a infinite loop
from telepot.loop import MessageLoop
# management of inline keyboard
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

# Secure Socket Layer (request for HTTPS)
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


# modes of execution
modes = {'qr':'QRcode mode', 'bar':'Barcode mode', '':'No mode selected'}

# keyboard created for the management of the types of the services
keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="QRcode", callback_data='qr'),
     InlineKeyboardButton(text="Barcode", callback_data='bar')],
    [InlineKeyboardButton(text="About", callback_data='info')]
])

'''
Print the type of service set in this moment
'''
def type_now(id):
    # read the last required type of service
    filename = 'Users/type_' + str(id) + '.txt'

    if (not os.path.isfile(filename)):
        type = ''
    else:
        f = open(filename, 'r')
        type = (f.readlines())[0].strip("\n")
        f.close()

    return modes[type]


'''
Handler of standard chat messages
'''
def handle_chat(message):
   # content_type = type of message (photo, msg, ...)
   # chat_id = user id of person that sent the msg
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

   #qrcode translations
   if(type == 'qr'):
      if content_type == 'photo':
          bot.sendMessage(chat_id, "Identification of the message")
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
          bot.sendMessage(chat_id, "Select what you want to do", reply_markup=keyboard)

      elif content_type == 'text':
          bot.sendMessage(chat_id, "Generazione QR Code")
          bot.sendPhoto(chat_id, create_QR(message))

          f = open(filename, 'w')
          type = f.write('\n')
          f.close()
          bot.sendMessage(chat_id, "Select what you want to do", reply_markup=keyboard)

      else:
          bot.sendMessage(chat_id, "Select what you want to do", reply_markup=keyboard)

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
   elif(type==''):
      bot.sendMessage(chat_id, "Select what you want to do", reply_markup = keyboard)


'''
Management of the keyboard requests
'''
def handle_query(message):
   # query_id = id of the query (used for answer on the top of the screen)
   # from_id = id of the user that press the button
   # query_data = id of the button pressed (InlineKeyboardButton id selected)
   query_id, from_id, query_data = telepot.glance(message, flavor = 'callback_query')

   filename = 'Users/type_'+str(from_id)+'.txt'

   if query_data == 'qr':
      f = open(filename, 'w')
      type = f.write('qr\n')
      f.close()
      bot.answerCallbackQuery(query_id, text=modes[query_data])

   elif(query_data == 'bar'):
      f = open(filename, 'w')
      type = f.write('bar\n')
      f.close()
      bot.answerCallbackQuery(query_id, text=modes[query_data])

   elif(query_data == 'info'):
       f = open('information.txt', 'r')
       information = f.read()
       f.close()
       bot.sendMessage(from_id, information)
       bot.sendMessage(from_id, "Select what you want to do", reply_markup=keyboard)

#bot.setWebhook()

def handler_termination(signal, frame):
    files = [f for f in os.listdir('Users') if f.endswith('.txt')]

    for f in files:
        os.remove('Users/'+f)

    sys.exit(0)


# Management of Ctrl + C by adding ASR (Asynchronus Service Routine) for the corresponding signal
signal.signal(signal.SIGINT, handler_termination)


'''
Execution of the bot and definition of functions w.r.t. the type of requests
'''
MessageLoop(bot, {"chat": handle_chat, "callback_query": handle_query}).run_as_thread()

while 1:
   time.sleep(10)

