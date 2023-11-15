import time
import sqlite3
from telethon import TelegramClient, events
from keep_alive import keep_alive

keep_alive()

API_ID = 21250696
API_HASH = '12d4137b3561860cdc4d876966539b36'
session_file = 'my_session'

phone = '+971562588105'

# Connect to SQLite database
conn = sqlite3.connect('conversation_state.db')
cursor = conn.cursor()

# Create a table to store conversation state
cursor.execute('''
    CREATE TABLE IF NOT EXISTS conversation_state (
        user_id INTEGER PRIMARY KEY,
        current_state INTEGER,
        conversation_active INTEGER
    )
''')
conn.commit()

keyword_responses = {
    'تاكيد': "هل تريد الاستمرار؟",
    'لا': "حسنا يمكنك دائما بدا عمليات البيع والشراء عن طريق ادخال كلمة 'بدا'",
    'نعم_شراء': "الرجاء مسح الكود للقيام بالتحويل وبعدها ارسل صورة التحويل ورقم محفظة ال USDT الخاصة بك \n وبعد الانتهاء ادخل كلمة 'تم' لاغلاق العملية",
    'نعم_بيع': "الرجاء مسح الكود للقيام بالتحويل وبعدها ارسل صورة التحويل ورقم محفظة ال زين كاش الخاصة بك \n وبعد الانتهاء ادخل كلمة 'تم' لاغلاق العملية",
    'تم': "نشكركم على تعاملكم معنا, لا تنسوا اجراء الكثير من المعاملات الجديدة عن طريق ادخال كلمة 'بدا'",
    'مساعدة': "نعتذر لك إذا واجهتم مشكلة معينة. سيقوم أحد موظفينا بالتواصل معكم في أسرع وقت ممكن.",
    'شراء': "الرجاء ادخال القيمة التي تريد شراؤها.",
    'بيع': "الرجاء ادخال القيمة التي تريد بيعها.",
    'القيمة': "عظيم! سيرسل لك أحد موظفينا التفاصيل في أقرب وقت.",
    'التحويل': "الرجاء ادخال القيمة على شكل ارقام.",
    'بدا': "الرجاء اختيار نوع العملية: \n 1-شراء USDT \n 2-بيع USDT \n.",
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
                user_id = event.from_id.user_id
                message_text = event.message.text.lower()
                response = None

                # Retrieve conversation state from the database
                cursor.execute('SELECT current_state, conversation_active FROM conversation_state WHERE user_id = ?', (user_id,))
                result = cursor.fetchone()

                if result:
                    current_state, conversation_active = result
                else:
                    # If no entry in the database, initialize with default values
                    current_state = 0
                    conversation_active = False

                if 'تم' in message_text:
                    current_state = 0
                    conversation_active = False
                    response = keyword_responses['تم']
                elif 'بدا' in message_text:
                    current_state = 0
                    conversation_active = True
                    response = keyword_responses['بدا']
                elif 'مساعدة' in message_text:
                    response = keyword_responses['مساعدة']
                else:
                    response = keyword_responses['default']

                if conversation_active:
                    if current_state == 0:
                        if '1' in message_text or 'شراء' in message_text or 'شراء usdt' in message_text:
                            current_state = 1
                            response = keyword_responses['شراء']
                        elif '2' in message_text or 'بيع' in message_text or 'بيع usdt' in message_text:
                            current_state = 4
                            response = keyword_responses['بيع']
                        elif 'مساعدة' in message_text:
                            conversation_active = False
                            response = keyword_responses['مساعدة']
                        else:
                            response = keyword_responses['بدا']

                    elif current_state == 1:
                        if any(word.isdigit() and int(word) >= 1 for word in message_text.split()):
                            current_state = 2
                            response = keyword_responses['القيمة']
                        elif any(word.isalpha() for word in message_text.split()):
                            response = keyword_responses['التحويل']
                        else:
                            response = keyword_responses['التحويل']

                    elif current_state == 2:
                        if 'نعم' in message_text:
                            current_state = 3
                            response = keyword_responses['نعم_شراء']
                            await event.respond(file='code.png')
                        elif 'لا' in message_text:
                            current_state = 0
                            response = keyword_responses['لا']
                            conversation_active = False
                        elif 'مساعدة' in message_text:
                            current_state = 0
                            response = keyword_responses['مساعدة']
                            conversation_active = False
                        else:
                            response = keyword_responses['تاكيد']


                    elif current_state == 4:
                        if any(word.isdigit() and int(word) >= 1 for word in message_text.split()):
                            current_state = 5
                            response = keyword_responses['القيمة']
                        elif any(word.isalpha() for word in message_text.split()):
                            response = keyword_responses['التحويل']
                        else:
                            response = keyword_responses['التحويل']

                    elif current_state == 5:
                        if 'نعم' in message_text:
                            current_state = 6
                            response = keyword_responses['نعم_بيع']
                            await event.respond(file='code.png')
                        elif 'لا' in message_text:
                            current_state = 0
                            response = keyword_responses['لا']
                            conversation_active = False
                        elif 'مساعدة' in message_text:
                            current_state = 0
                            response = keyword_responses['مساعدة']
                            conversation_active = False
                        else:
                            response = keyword_responses['تاكيد']

                # Update conversation state in the database
                cursor.execute('INSERT OR REPLACE INTO conversation_state (user_id, current_state, conversation_active) VALUES (?, ?, ?)', (user_id, current_state, conversation_active))
                conn.commit()

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