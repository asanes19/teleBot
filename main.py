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
# Initialize the current state for each user
user_states = {}

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
async def handle_new_message(event):

    user_id = event.from_id

    # Check if the user ID is in the user_states dictionary
    if user_id not in user_states:
        # If the user ID is not in the user_states dictionary, add it and initialize the current state to START
        user_states[user_id] = CONVERSATION_STATES['START']

    # Get the current state for the user
    current_state = user_states[user_id]

    # Check the user's ID and send the appropriate response
    if current_state == CONVERSATION_STATES['START']:
        if event.message.text == 'بدا':
            response = keyword_responses['بدا']
            current_state = CONVERSATION_STATES['BUY_SELL_CHOICE']
        elif event.message.text == 'مساعدة':
            response = keyword_responses['مساعدة']
        else:
            response = keyword_responses['default']
    elif current_state == CONVERSATION_STATES['BUY_SELL_CHOICE']:
        if event.message.text == '1' or event.message.text == 'شراء' or event.message.text == 'شراء usdt':
            response = keyword_responses['شراء']
            current_state = CONVERSATION_STATES['ENTER_VALUE']
        elif event.message.text == '2' or event.message.text == 'بيع' or event.message.text == 'بيع usdt':
            response = keyword_responses['بيع']
            current_state = CONVERSATION_STATES['ENTER_VALUE']
        else:
            response = keyword_responses['بدا']
    elif current_state == CONVERSATION_STATES['ENTER_VALUE']:
        if event.message.text == 'نعم':
            response = keyword_responses['نعم']
            current_state = CONVERSATION_STATES['CONFIRM']
            await event.respond(file='code.png')
        elif event.message.text == 'لا':
            response = keyword_responses['لا']
            current_state = CONVERSATION_STATES['START']
        else:
            response = keyword_responses['تاكيد']

    # Update the current state for the user
        user_states[user_id] = current_state

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
