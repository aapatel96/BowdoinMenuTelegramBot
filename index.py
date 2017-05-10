from bs4 import BeautifulSoup
import urllib2
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, Job, JobQueue, RegexHandler,ConversationHandler
import telegram.replykeyboardmarkup
import telegram.ext
from telegram import ChatAction
import telegram.keyboardbutton
import telegram.parsemode
import logging
import time


userids=[]
urlBase = "http://www.bowdoin.edu/atreus/views?unit="
mealMarker="&meal="
both_keyboard= telegram.replykeyboardmarkup.ReplyKeyboardMarkup([[telegram.KeyboardButton("thorne"),telegram.KeyboardButton("moulton")]], resize_keyboard=True)

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

    

def thorne(bot, update,args):
    currenttime= int(time.ctime()[11:19][0:2])
    bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
    if currenttime>= 5 and currenttime < 10:
        update.message.reply_text(thorneBreakfast, parse_mode=telegram.ParseMode.HTML)
    if currenttime>= 10 and currenttime < 14:
        update.message.reply_text(thorneLunch, parse_mode=telegram.ParseMode.HTML)
    else:
        update.message.reply_text(thorneDinner, parse_mode=telegram.ParseMode.HTML)



def moulton(bot, update,args):
    currenttime= int(time.ctime()[11:19][0:2])
    bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
    if currenttime>= 5 and currenttime < 10:
        update.message.reply_text(moultonBreakfast, parse_mode=telegram.ParseMode.HTML)
    if currenttime>= 10 and currenttime < 14:
        update.message.reply_text(moultonLunch, parse_mode=telegram.ParseMode.HTML)
    else:
        update.message.reply_text(moultonDinner, parse_mode=telegram.ParseMode.HTML)

def thorneR(bot, update):
    print 5
    currenttime= int(time.ctime()[11:19][0:2])
    print 6
    if currenttime>= 5 and currenttime < 10:
        print 7
        update.message.reply_text(thorneBreakfast)
    if currenttime>= 10 and currenttime < 14:
        print 7
        update.message.reply_text(thorneLunch)
    else:
        print 7
        update.message.reply_text(thorneDinner)



def moultonR(bot, update):
    print 5
    currenttime= int(time.ctime()[11:19][0:2])
    print 6
    if currenttime>= 5 and currenttime < 10:
        print 7
        update.message.reply_text(moultonBreakfast)
    if currenttime>= 10 and currenttime < 14:
        print 7
        update.message.reply_text(moultonLunch)
    else:
        print 7
        update.message.reply_text(moultonDinner)

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
    dp.add_handler(CommandHandler("thorne", thorne,pass_args=True))
    dp.add_handler(RegexHandler('^(thorne)$',thorneR))
    dp.add_handler(RegexHandler('^(moulton)$',moultonR))
    dp.add_handler(CommandHandler("moulton", moulton,pass_args=True))


    

    # on noncommand i.e message - echo the message on Telegram

    dp.add_error_handler(error)

    

    # log all errors
    #dp.add_error_handler(error)

    # Start the Bot
    updater.start_webhook(listen="0.0.0.0",
                      port=PORT,
                      url_path=TOKEN)
    updater.bot.set_webhook("https://bowdoinmenu.herokuapp.com/" + TOKEN)
    updater.idle()


if __name__ == '__main__':
    main()


