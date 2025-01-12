from telebot import types
from io import BytesIO
from PIL import Image
import qrcode


def register_af_handlers(bot):
    @bot.message_handler(func=lambda message: message.text == '🧩 امکانات جانبی')
    def notes_menu(message):
        """
        Displays the menu with options for QR code generation or image compression.
        
        Parameters:
        - message: The message object that triggered the handler.
        """
        # Create an inline keyboard for sending in a new message
        markup = types.InlineKeyboardMarkup(row_width=1)
        create_qrcode_button = types.InlineKeyboardButton('📲ساخت کی یو آر کد', callback_data='create_qrcode')
        compress_button = types.InlineKeyboardButton('📉کاهش حجم تصویر', callback_data='compress')
        markup.add(create_qrcode_button, compress_button)  # Add inline buttons
        
        bot.send_message(message.chat.id, '🔹 لطفاً یکی از گزینه‌های زیر را انتخاب کنید:', reply_markup=markup)

    # Operation for "Create QR Code"
    @bot.callback_query_handler(func=lambda call: call.data == 'create_qrcode')
    def handle_create_qrcode(call):
        """
        Asks the user to send text to be converted into a QR code.
        
        Parameters:
        - call: The callback query object.
        """
        bot.send_message(call.message.chat.id, "لطفاً متنی که می‌خواهید به کیو آر کد تبدیل کنید را ارسال کنید.")
        bot.register_next_step_handler(call.message, generate_qrcode)
    
    # Generate QR code
    def generate_qrcode(message):
        """
        Generates a QR code from the provided text and sends it to the user.
        
        Parameters:
        - message: The message object containing the text for QR code.
        """
        qr_data = message.text
        qr_image = qrcode.make(qr_data)
        
        # Save QR code as bytes
        byte_io = BytesIO()
        qr_image.save(byte_io)
        byte_io.seek(0)
        
        # Send QR code to the user
        bot.send_photo(message.chat.id, byte_io)

    @bot.callback_query_handler(func=lambda call: call.data == 'compress')
    def handle_compress(call):
        """
        Asks the user to send an image for compression.
        
        Parameters:
        - call: The callback query object.
        """
        bot.send_message(call.message.chat.id, "لطفاً تصویری که می‌خواهید حجم آن کاهش یابد را ارسال کنید.")
        bot.register_next_step_handler(call.message, compress_image)
    
    # Compress image
    def compress_image(message):
        """
        Compresses the sent image by reducing its quality and sends the compressed image to the user.
        
        Parameters:
        - message: The message object containing the image to compress.
        """
        if message.photo:
            file_id = message.photo[-1].file_id  # Get the largest photo size
            file_info = bot.get_file(file_id)
            file = bot.download_file(file_info.file_path)
            
            # Convert file to PIL image object
            image = Image.open(BytesIO(file))
            
            # Compress by reducing quality
            output_io = BytesIO()
            image.save(output_io, format='JPEG', quality=30)  # Reduce quality to 30
            output_io.seek(0)
            
            # Send compressed image to the user
            bot.send_photo(message.chat.id, output_io, caption="✅ تصویر با موفقیت کاهش حجم داده شد.")

        else:
            bot.send_message(message.chat.id, "لطفاً یک تصویر ارسال کنید.")
