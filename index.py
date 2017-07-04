from bs4 import BeautifulSoup
import urllib2

from telegram.ext import Updater, CommandHandler,InlineQueryHandler,MessageHandler, Filters, Job, JobQueue, RegexHandler,ConversationHandler
from uuid import uuid4
import telegram.replykeyboardmarkup
import telegram.ext
from telegram import ChatAction,InlineQueryResultArticle, ParseMode,InputTextMessageContent
import telegram.keyboardbutton
import telegram.parsemode
import logging
import time
import os
import re
from flask import Flask, jsonify


app = Flask(__name__)


userids=[]
urlBase = "http://www.bowdoin.edu/atreus/views?unit="
mealMarker="&meal="
both_keyboard= telegram.replykeyboardmarkup.ReplyKeyboardMarkup([[telegram.KeyboardButton("thorne"),telegram.KeyboardButton("moulton"),telegram.KeyboardButton("pub")]], resize_keyboard=True)

diningHalls = ["48","49"]
meals =["Breakfast","Lunch","Dinner"]

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

class special:
    def __init__(self,uid,job_queue):
        self.id = uid
        self.job_queue = job_queue
        
def menuItems(hall,meal):
    url = urlBase+hall+mealMarker+meal
    webpage= urllib2.urlopen(url)
    html = webpage.read()
    soup = BeautifulSoup(html, 'html.parser')
    necessaryTags = soup(["h3", "span"])
    necessaryTagsAsStrings = []
    for i in necessaryTags:
        necessaryTagsAsStrings.append(str(i))
##    necessaryTagsPure = []
##    for j in necessaryTagsAsStrings:
##        if j[0:6] =="<span>":
##            necessaryTagsPure.append(j)
##        if j[0:4] =="<h3>":
##            necessaryTagsPure.append(j)
##    necessaryTagsDoublePure = []
    necessaryTagsAsStringsPure=[]
    for j in necessaryTagsAsStrings:
        if j[0:6] =="<span>":

            try:
                textToAppend = j[6:-7]
                necessaryTagsAsStringsPure.append(textToAppend)

            except:
                pass
        if j[0:4] =="<h3>":

            try:
                textToAppend = j[4:-5]+"*"
                necessaryTagsAsStringsPure.append(textToAppend)

            except:
                pass            

    necessaryTagsAsStringsPure.append(hall)
    return necessaryTagsAsStringsPure


def createMenu(menuItems):
    diningHall = ""
    if menuItems[-1] == "48":
        diningHall = "Moulton"
    if menuItems[-1] == "49":
        diningHall = "Thorne"
    del menuItems[-1]
    string = ""
    lastWasTitle = False
    for i in range(len(menuItems)):
        if menuItems[i][-1]=="*":
            stringToAppend = menuItems[i][0:-1].upper()+"\n"
            string = string+stringToAppend
            
            continue
        string = string + menuItems[i]+ "\n"
        if i != len(menuItems)-1:
            if menuItems[i+1][-1]=="*":
                string = string + "\n"
    string = string.replace("&amp;","and")
    return string


moultonBreakfast =createMenu(menuItems("48","Breakfast"))
thorneBreakfast =createMenu(menuItems("49","Breakfast"))

moultonLunch =createMenu(menuItems("48","Lunch"))
thorneLunch =createMenu(menuItems("49","Lunch"))

moultonDinner = createMenu(menuItems("48","Dinner"))
thorneDinner = createMenu(menuItems("49","Dinner"))


@app.route('/moulton')
def moulton():
    x = {'menu': None}
    currenttime= int(time.ctime()[11:19][0:2]) -3
    if currenttime>= 5 and currenttime < 10:
        if moultonBreakfast == '':
            x['menu'] == 'No menus available'
            return x
        x['menu'] == moultonBreakfast
        return x
    elif currenttime>= 10 and currenttime < 14:
        if moultonLunch == '':
            x['menu'] == 'No menus available'
            return x
        x['menu'] == moultonLunch
        return x
    else:
        if moultonDinner == '':
            x['menu'] == 'No menus available'
            return x

        x['menu'] == moultonDinner
        return x




def start(bot, update, job_queue):
    update.message.reply_text('Hi!')
    update.message.reply_text('Which menu do you want to check?',reply_markup=both_keyboard)
    userids.append(update.message.chat_id)
    dayOfMonth = str(int(time.ctime()[8:10])+1)
    if len(dayOfMonth) == 1:
        engTargetTime = time.ctime()[0:8]+"0"+dayOfMonth+" 05:00:00 "+time.ctime()[-4:]
    else:
        engTargetTime = time.ctime()[0:8]+dayOfMonth+" 05:00:00 "+time.ctime()[-4:]        
    numTargetTime = time.mktime(time.strptime(engTargetTime))
    currentTime =  time.time()
    target = numTargetTime-time.time()
    changeMenu = Job(notify,
                        target,
                        repeat=False,
                        context=special(update.message.chat_id,job_queue))
    job_queue.put(changeMenu)
    return
    
def notify(bot,job):
    bot.sendMessage(job.context.id,"Menus updated",reply_markup=both_keyboard)
    target=time.time()+86400
    alarm = Job(notify,
                    target,
                    repeat=False,
                    context=special(job.context.id,job.context.job_queue))
    job.context.job_queue.put(alarm)
    moultonBreakfast =createMenu(menuItems("48","Breakfast"))
    thorneBreakfast =createMenu(menuItems("49","Breakfast"))
    moultonLunch =createMenu(menuItems("48","Lunch"))
    thorneLunch =createMenu(menuItems("49","Lunch"))
    moultonDinner = createMenu(menuItems("48","Dinner"))
    thorneDinner = createMenu(menuItems("49","Dinner"))
    

    return

    

def thorneR(bot, update):
    currenttime= int(time.ctime()[11:19][0:2]) -3
    if currenttime>= 5 and currenttime < 10:
        if thorneBreakfast == '':
            update.message.reply_text('No menus available')
            return
        update.message.reply_text(thorneBreakfast)
    elif currenttime>= 10 and currenttime < 14:
        if thorneLunch == '':
            update.message.reply_text('No menus available')
            return
        update.message.reply_text(thorneLunch)
    else:
        if thorneDinner == '':
            update.message.reply_text('No menus available')
            return
        update.message.reply_text(thorneDinner)



def moultonR(bot, update):
    currenttime= int(time.ctime()[11:19][0:2]) -3
    if currenttime>= 5 and currenttime < 10:
        if moultonBreakfast == '':
            update.message.reply_text('No menus available')
            return
        update.message.reply_text(moultonBreakfast)
    elif currenttime>= 10 and currenttime < 14:
        if moultonLunch == '':
            update.message.reply_text('No menus available')
            return
        update.message.reply_text(moultonLunch)
    else:
        if moultonDinner == '':
            update.message.reply_text('No menus available')
            return
        update.message.reply_text(moultonDinner)



def pubR(bot, update):
    bot.send_document(chat_id=update.message.chat_id, document=open('magees-menu.pdf', 'rb'))
def escape_markdown(text):
    """Helper function to escape telegram markup symbols"""
    escape_chars = '\*_`\['
    return re.sub(r'([%s])' % escape_chars, r'\\\1', text)


def inlinequery(bot, update):
    print update
    query = update.inline_query.query
    results = list()


    currenttime= int(time.ctime()[11:19][0:2]) -3
##    if update.inline_query.query.lower() == "t" or update.inline_query.query.lower() == "th" or update.inline_query.query.lower() == "tho" or update.inline_query.query.lower() == "thor" or update.inline_query.query.lower() == "thorn" or update.inline_query.query.lower() == "thorne":
    stringt = ''
    if currenttime>= 5 and currenttime < 10:
        if thorneBreakfast == '':
            stringt = 'No menus available'
        else:
           stringt = thorneBreakfast
    elif currenttime>= 10 and currenttime < 14:
        if thorneLunch == '':
            stringt = 'No menus available'
        else:
            stringt = thorneLunch
    else:
        if thorneDinner == '':
            stringt = 'No menus available'
        else:
            stringt = thorneDinner

    stringm = ''
    
    if currenttime>= 5 and currenttime < 10:
        if moultonBreakfast == '':
            stringm = 'No menus available'
        else:
           string = moultonBreakfast
    elif currenttime>= 10 and currenttime < 14:
        if moultonLunch == '':
            stringm = 'No menus available'
        else:
            stringm = moultonLunch
    else:
        if moultonDinner == '':
            stringm='No menus available'
        else:
            stringm = moultonDinner
    if update.inline_query.query== '':
        results.append(InlineQueryResultArticle(id=uuid4(),
                                                title="Thorne",
                                                input_message_content=InputTextMessageContent(stringt),thumb_url="http://i.imgur.com/VzZfFo3.jpg",thumb_width=100,thumb_height=100))
        results.append(InlineQueryResultArticle(id=uuid4(),
                                                title="Moulton",
                                                input_message_content=InputTextMessageContent(stringm),thumb_url="http://i.imgur.com/IvyPNey.png",thumb_width=100,thumb_height=100))

        update.inline_query.answer(results)

    if update.inline_query.query.lower() == "m" or update.inline_query.query.lower() == "mo" or update.inline_query.query.lower() == "mou" or update.inline_query.query.lower() == "moul" or update.inline_query.query.lower() == "moult" or update.inline_query.query.lower() == "moulto" or update.inline_query.query.lower() == "moulton":
        results.append(InlineQueryResultArticle(id=uuid4(),
                                                title="Moulton",
                                                input_message_content=InputTextMessageContent(stringm),thumb_url="http://i.imgur.com/IvyPNey.png",thumb_width=100,thumb_height=100))

        update.inline_query.answer(results)

    if update.inline_query.query.lower() == "t" or update.inline_query.query.lower() == "th" or update.inline_query.query.lower() == "tho" or update.inline_query.query.lower() == "thor" or update.inline_query.query.lower() == "thorn" or update.inline_query.query.lower() == "thorne":
        results.append(InlineQueryResultArticle(id=uuid4(),
                                                title="Thorne",
                                                input_message_content=InputTextMessageContent(stringt),thumb_url="http://i.imgur.com/VzZfFo3.jpg",thumb_width=100,thumb_height=100))
        update.inline_query.answer(results)



def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))   



def main():
    TOKEN = "366760118:AAGVzekBzcYvr9sYQeamUQsgfZzquw23Kno"
    updater = Updater(TOKEN)
    PORT = int(os.environ.get('PORT', '5000'))

    # Create the EventHandler and pass it your bot's token.
    updater = Updater(TOKEN)
    # job_q= updater.job_queue

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start, pass_job_queue=True))
    dp.add_handler(RegexHandler('^(thorne)$',thorneR))
    dp.add_handler(RegexHandler('^(moulton)$',moultonR))
    dp.add_handler(RegexHandler('^(pub)$',pubR))
    dp.add_handler(InlineQueryHandler(inlinequery))


    

    # on noncommand i.e message - echo the message on Telegram

    dp.add_error_handler(error)

    

    # log all errors
    #dp.add_error_handler(error)

    # Start the Bot
##    updater.start_polling()
    
    updater.start_webhook(listen="0.0.0.0",
                      port=PORT,
                      url_path=TOKEN)
    updater.bot.set_webhook("https://bowdoinmenu.herokuapp.com/" + TOKEN)
    
    updater.idle()


if __name__ == '__main__':
    main()


