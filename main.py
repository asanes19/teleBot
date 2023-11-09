import time
from telethon import TelegramClient, events
from keep_alive import keep_alive
keep_alive()

API_ID = 21250696
API_HASH = '12d4137b3561860cdc4d876966539b36'
session_file = 'my_session'

phone = '+971562588105'


# Define the possible states of the conversation
CONVERSATION_STATES = {
    'START': 0,
    'BUY_SELL_CHOICE': 1,
    'ENTER_VALUE': 2,
    'CONFIRM': 3,
}

# Initialize the current state as 'START'
current_state = CONVERSATION_STATES['START']

# Indicate if the conversation is active
conversation_active = False

keyword_responses = {
    'تاكيد': "هل تريد الاستمرار؟",
    'لا': "حسنا يمكنك دائما بدا عمليات البيع والشراء عن طريق ادخال كلمة 'بدا'",
    'نعم': "الرجاء مسح الكود للقيام بالتحويل وادخال كلمة 'تم' بعد الانتهاء.",
    'تم': "نشكركم على تعاملكم معنا, لا تنسوا اجراء الكثير من المعاملات الجديدة عن طريق ادخال كلمة 'بدا'",
    'مساعدة': "نعتذر لك إذا واجهتم مشكلة معينة. سيقوم أحد موظفينا بالتواصل معكم في أسرع وقت ممكن.",
    'شراء': "الرجاء ادخال القيمة التي تريد شراؤها.",
    'بيع': "الرجاء ادخال القيمة التي تريد بيعها.",
    'القيمة': "عظيم! سيرسل لك أحد موظفينا التفاصيل في أقرب وقت.",
    'التحويل': "الرجاء ادخال القيمة على شكل ارقام.",
    'بدا': "الرجاء اختيار نوع العملية:\n1- شراء USDT\n2- بيع USDT",
    'default': "مرحبًا بكم عزيزي العميل، نحن هنا لمساعدتك. إذا كنت ترغب في إجراء عملية بيع أو شراء، يُرجى إدخال كلمة 'بدا'. وإذا واجهتكم مشكلة، يُرجى إدخال كلمة 'مساعدة'، وسيتواصل معكم أحد موظفينا في أقرب وقت. نشكركم على تفهمكم."
}

if __name__ == '__main__':
    client = TelegramClient('my_session', API_ID, API_HASH, sequential_updates=True)
    @client.on(events.NewMessage(incoming=True))
    async def handle_new_message(event):
        global current_state, conversation_active
        if event.is_private:
            from_ = await event.client.get_entity(event.from_id)
            if not from_.bot:
                message_text = event.message.text.lower()
                response = None

                if 'تم' in message_text:
                    current_state = CONVERSATION_STATES['START']
                    conversation_active = False
                    response = keyword_responses['تم']
                elif 'بدا' in message_text:
                    conversation_active = True
                    response = keyword_responses['بدا']
                elif 'مساعدة' in message_text:
                    response = keyword_responses['مساعدة']
                else:
                    response = keyword_responses['default']

                if conversation_active:
                    if current_state == CONVERSATION_STATES['START']:
                        if '1' in message_text or 'شراء' in message_text or 'شراء usdt' in message_text:
                            current_state = CONVERSATION_STATES['BUY_SELL_CHOICE']
                            response = keyword_responses['شراء']
                        elif '2' in message_text or 'بيع' in message_text or 'بيع usdt' in message_text:
                            current_state = CONVERSATION_STATES['BUY_SELL_CHOICE']
                            response = keyword_responses['بيع']
                        else:
                            response = keyword_responses['بدا']

                    elif current_state == CONVERSATION_STATES['BUY_SELL_CHOICE']:
                        if any(word.isdigit() and int(word) >= 1 for word in message_text.split()):
                            current_state = CONVERSATION_STATES['ENTER_VALUE']
                            response = keyword_responses['القيمة']
                        elif any(word.isalpha() for word in message_text.split()):
                            response = keyword_responses['التحويل']
                        else:
                            response = keyword_responses['التحويل']


                    elif current_state == CONVERSATION_STATES['ENTER_VALUE']:
                        if 'نعم' in message_text:
                            current_state = CONVERSATION_STATES['CONFIRM']
                            response = keyword_responses['نعم']
                            await event.respond(file='code.png')
                        elif 'لا' in message_text:
                            current_state = CONVERSATION_STATES['START']
                            response = keyword_responses['لا']
                            conversation_active = False
                        else:
                            response = keyword_responses['تاكيد']

                if response:
                    print(time.asctime(), '-', event.message, '-', current_state)
                    time.sleep(1)
                    await event.respond(response)
                else:
                    default_response = keyword_responses['default']
                    await event.respond(default_response)
    print(time.asctime(), '-', 'Auto-replying...')
    client.start(phone)
    client.run_until_disconnected()
    print(time.asctime(), '-', 'Stopped!')
