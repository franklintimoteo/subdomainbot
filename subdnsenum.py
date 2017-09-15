from collections import deque, namedtuple
import threading
import time
from os import getenv, chdir
from telebot import TeleBot, util
from telebot.apihelper import ApiException
from subbrute import subbrute


api_key = getenv('BOT_DNS')
if not api_key: exit('Api key not found on env!')
bot = TeleBot(api_key)


fila = deque(maxlen=10) # type: deque
User = namedtuple('User',['uid','domain']) # type: namedtuple

@bot.message_handler(commands=['sub', 'Sub'])
def order_consult_subdomain(msg):
    if msg.chat.type != 'private':
        return bot.send_message(msg.chat.id, 'Somente em privado.')
    elif len(fila) >= fila.maxlen:
        return bot.send_message(msg.chat.id,
                'Estamos com o máximo de {} pessoas na fila, aguarde alguns instantes!'.format(fila.maxlen))
    
    target = util.extract_arguments(msg.text)
    if not target: 
        bot.send_message(msg.chat.id, 'Não entendi domínio.')
    elif user_in_deque(msg.from_user.id):
        bot.send_message(msg.chat.id, 'Você já tem um pedido em espera!')
    else:
        user_order = User(uid=msg.from_user.id, domain=target)
        fila.append(user_order)
        bot.send_message(msg.chat.id, "Sua consulta ao domínio %s foi adicionada a fila!\nTamanho da fila: %s." %(target, len(fila)))

def user_in_deque(uid):
    for u in fila:
        if u.uid == uid:
            return True
            
def consult_subdomains_in_deque():
    subnames = set()
    while True:
        if not fila:
            time.sleep(5)
        else:
            user_order = fila.pop()
            domain, uid = user_order.domain, user_order.uid
            try:
                bot.send_message(uid, 'Começando a procurar os subdomínios de %s aguarde os envios. Tempo médio: 30 min.' %domain)
                for sub in subbrute.run(domain, query_type="ANY", subdomains='subbrute/names_small.txt'):
                    
                    if sub[0] not in subnames:
                        subnames.add(sub[0])
                        bot.send_message(uid, sub[0])
                bot.send_message(uid, 'Consulta finalizada!')
            except ApiException as error:
                print("erro ao enviar mensagem -- ", error)

def start_bot():
    bot.polling(none_stop=False, timeout=60)
    
threading.Thread(target=start_bot, name='startbot').start()
print('Executando bot...')
consult_subdomains_in_deque()



