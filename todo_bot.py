from telebot import types
from models import Note


def register_todo_handlers(bot):

    # --- HANDLER FOR "یادداشت‌ها" BUTTON ---
    @bot.message_handler(func=lambda message: message.text == '📓 یادداشت‌ها')
    def notes_menu(message):
        """
        Displays the menu with options to create a new note or view existing notes.
        
        Parameters:
        - message: The message object that triggered the handler.
        """
        # Create an inline keyboard for sending in a new message
        markup = types.InlineKeyboardMarkup()
        create_note_button = types.InlineKeyboardButton('✍️ ایجاد یادداشت جدید', callback_data='create_note')
        view_notes_button = types.InlineKeyboardButton('📜 دیدن لیست یادداشت‌ها', callback_data='view_notes')
        markup.add(create_note_button, view_notes_button)  # Add inline buttons
        
        bot.send_message(message.chat.id, '🔹 لطفاً یکی از گزینه‌های زیر را انتخاب کنید:', reply_markup=markup)

    # --- CALLBACK HANDLER FOR "ایجاد یادداشت جدید" ---
    @bot.callback_query_handler(func=lambda call: call.data == 'create_note')
    def create_note(call):
        """
        Prompts the user to enter a title for the new note.
        
        Parameters:
        - call: The callback query object.
        """
        bot.answer_callback_query(call.id, text="لطفاً عنوان یادداشت را وارد کنید.")
        bot.send_message(call.message.chat.id, '🔹 لطفاً عنوان یادداشت جدید خود را ارسال کنید.')

        # Next step to get the title
        bot.register_next_step_handler(call.message, process_title, user_id=call.message.chat.id)

    # --- HANDLE TITLE STEP ---
    def process_title(message, user_id):
        """
        Processes the title entered by the user and prompts for the description.
        
        Parameters:
        - message: The message object containing the title.
        - user_id: The ID of the user sending the message.
        """
        title = message.text

        bot.send_message(message.chat.id, '🔹 حالا لطفاً توضیحات یادداشت خود را وارد کنید.')

        # Next step to get the description
        bot.register_next_step_handler(message, process_description, user_id=user_id, title=title)

    # --- HANDLE DESCRIPTION STEP ---
    def process_description(message, user_id, title):
        """
        Processes the description entered by the user and saves the note to the database.
        
        Parameters:
        - message: The message object containing the description.
        - user_id: The ID of the user sending the message.
        - title: The title of the note.
        """
        description = message.text
        
        Note.insert(user_id=user_id, title=title, description=description)
        
        bot.send_message(message.chat.id, f'✅ یادداشت شما ذخیره شد!\n\n'
                                        f'عنوان: {title}\n'
                                        f'توضیحات: {description}')

    # --- CALLBACK HANDLER FOR "دیدن لیست یادداشت‌ها" ---
    @bot.callback_query_handler(func=lambda call: call.data == 'view_notes')
    def view_notes(call, message_id=None):
        """
        Displays a list of the user's notes.
        
        Parameters:
        - call: The callback query object.
        - message_id: Optional message ID to edit the message instead of sending a new one.
        """
        user_id = call.message.chat.id
        notes = Note.filter(user_id=user_id)  # Search for notes for the user
        
        if notes:
            markup = types.InlineKeyboardMarkup()
            for note in notes:
                button = types.InlineKeyboardButton(text=f'📌 {note.title}', callback_data=f'view_note_{note.id}')
                markup.add(button)
            
            text = '📋 لیست یادداشت‌های شما:'
            
            # If message_id exists, edit the current message
            if message_id:
                bot.edit_message_text(text, user_id, message_id, reply_markup=markup)
            else:
                bot.send_message(user_id, text, reply_markup=markup)
        else:
            bot.send_message(user_id, '❌ شما هیچ یادداشتی ندارید.')

    @bot.callback_query_handler(func=lambda call: call.data.startswith('view_note_'))
    def view_note_details(call):
        """
        Displays the details of a specific note.
        
        Parameters:
        - call: The callback query object containing the note ID.
        """
        note_id = call.data.split('_')[2]
        note = Note.filter(id=note_id)

        if note:
            text = f"🔸 <b>{note[0].title}</b>\n\n{note[0].description}"
            markup = types.InlineKeyboardMarkup()
            delete_button = types.InlineKeyboardButton('❌ حذف', callback_data=f'confirm_delete_{note[0].id}_{call.message.message_id}')
            edit_button = types.InlineKeyboardButton('✏️ ویرایش', callback_data=f'edit_note_{note[0].id}')
            back_button = types.InlineKeyboardButton('🔙 بازگشت', callback_data=f'back_to_notes_{call.message.message_id}')

            markup.add(delete_button, edit_button)
            markup.add(back_button)

            # Edit the current message to display note details
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode='HTML')
        else:
            bot.send_message(call.message.chat.id, '❌ این یادداشت وجود ندارد.')

    # --- Note deletion confirmation ---
    @bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_delete_'))
    def confirm_delete(call):
        """
        Confirms the deletion of a note.
        
        Parameters:
        - call: The callback query object containing the note ID and message ID.
        """
        note_id, message_id = call.data.split('_')[2:]
        
        markup = types.InlineKeyboardMarkup()
        yes_button = types.InlineKeyboardButton('✅ بله', callback_data=f'delete_note_{note_id}_{message_id}')
        no_button = types.InlineKeyboardButton('❌ خیر', callback_data=f'view_note_{note_id}')

        markup.add(yes_button, no_button)

        # Edit the current message to show confirmation options
        bot.edit_message_text('⚠️ آیا از حذف این یادداشت مطمئن هستید؟', call.message.chat.id, message_id, reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data.startswith('delete_note_'))
    def delete_note(call):
        """
        Deletes the specified note from the database.
        
        Parameters:
        - call: The callback query object containing the note ID.
        """
        note_id, message_id = call.data.split('_')[2:]
        note = Note.filter(id=note_id)

        if note:
            note.delete()  # Delete the note from the database
            bot.answer_callback_query(call.id, text='✅ یادداشت حذف شد.')
            
            # Check for remaining notes
            remaining_notes = Note.filter(user_id=call.message.chat.id)
            
            if remaining_notes:
                view_notes(call, message_id)  # Edit message to show the list of notes
            else:
                bot.delete_message(call.message.chat.id, message_id)  # Delete the confirmation message
                bot.send_message(call.message.chat.id, '❌ شما هیچ یادداشتی ندارید.')  # Send a new message
        else:
            bot.send_message(call.message.chat.id, '❌ این یادداشت وجود ندارد.')

    # --- Return to notes list (edit message) ---
    @bot.callback_query_handler(func=lambda call: call.data.startswith('back_to_notes_'))
    def back_to_notes(call):
        """
        Returns to the list of notes.
        
        Parameters:
        - call: The callback query object containing the message ID.
        """
        message_id = call.data.split('_')[3]
        view_notes(call, message_id)  # Display the list of notes in the same message

    # --- Edit title (show note details first) ---
    @bot.callback_query_handler(func=lambda call: call.data.startswith('edit_note_'))
    def edit_note(call):
        """
        Prompts the user to edit the title of a note.
        
        Parameters:
        - call: The callback query object containing the note ID.
        """
        note_id = call.data.split('_')[2]
        note = Note.filter(id=note_id)

        if note:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            # Send a message with the current title pre-filled in the input field
            msg = bot.send_message(
                call.message.chat.id,
                '✏️ عنوان جدید را وارد کنید:',
                reply_markup=types.ForceReply(selective=True, input_field_placeholder=note[0].title)
            )
            bot.register_next_step_handler(msg, get_new_desc, note[0].id)
        else:
            bot.send_message(call.message.chat.id, '❌ این یادداشت وجود ندارد.')

    # --- Step 2: Get a new title and request a new description ---
    def get_new_desc(message, note_id):
        """
        Prompts the user to enter new description for a note after changing its title.
        
        Parameters:
        - message: The message object containing the new title.
        - note_id: The ID of the note being edited.
        """
        new_title = message.text
        note = Note.filter(id=note_id)

        if note:
            # Send the current description pre-filled in the input field
            msg = bot.send_message(
                message.chat.id,
                '📝 حالا توضیحات جدید را وارد کنید:',
                reply_markup=types.ForceReply(selective=True, input_field_placeholder=note[0].description)
            )
            bot.register_next_step_handler(msg, update_and_show, note_id, new_title)
        else:
            bot.send_message(message.chat.id, '❌ یادداشت پیدا نشد.')

    # --- Step 3: Get new descriptions and save them in the database ---
    def update_and_show(message, note_id, new_title):
        """
        Updates the note with the new title and description and shows the updated note to the user.
        
        Parameters:
        - message: The message object containing the new description.
        - note_id: The ID of the note being updated.
        - new_title: The new title for the note.
        """
        new_description = message.text
        note = Note.filter(id=note_id)

        if note:
            # Update the note in the database
            note.update(title=new_title, description=new_description)

            # Show confirmation message with the new content
            text = (
                '✅ یادداشت با موفقیت ویرایش شد.\n\n'
                f"🔸 <b>{new_title}</b>\n\n{new_description}"
            )
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            gold_button = types.KeyboardButton('🌦️ مشاهده وضعیت آب و هوا')  
            notes_button = types.KeyboardButton('📓 یادداشت‌ها')
            af_button = types.KeyboardButton('🧩 امکانات جانبی')
            instadwomload = types.KeyboardButton('📥 دانلود از اینستاگرام')
            markup.add(gold_button, notes_button)
            markup.add(instadwomload, af_button)

            bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=markup)
        else:
            bot.send_message(message.chat.id, '❌ خطا در ویرایش یادداشت.')
