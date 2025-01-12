import instaloader
from telebot import types
import os
import shutil


loader = instaloader.Instaloader()

def register_instadownloader_handlers(bot):
    """
    Register Instagram downloader handlers for the bot.

    This function sets up message handlers to download Instagram posts or reels
    when the user sends a valid Instagram link.
    
    Args:
        bot (TeleBot): The TeleBot instance to register handlers with.
    """
    @bot.message_handler(func=lambda message: message.text == '📥 دانلود از اینستاگرام')
    def send_message_download(message):
        """
        Prompt user to send an Instagram post or reel link.

        Sends a message to the user asking for the Instagram post/reel link
        and registers the next step handler to process the download.

        Args:
            message (types.Message): User's message triggering the download prompt.
        """
        msg = bot.send_message(message.chat.id, '🔗 لطفاً لینک پست یا ریلز اینستاگرام را ارسال کنید:')
        bot.register_next_step_handler(msg, download_instagram_post)

        
    def download_instagram_post(message):
        """
        Download and send Instagram post or reel based on provided link.

        Takes the link provided by the user, attempts to download the post or reel,
        and sends the media file (video/image) back to the user. If a caption is present,
        it will be included with the media. The function handles errors gracefully.

        Args:
            message (types.Message): Message containing the Instagram link.
        """
        url = message.text
        caption_video = ""
        if 'instagram.com' in url:
            try:
                shortcode = url.split('/')[-2]
                post = instaloader.Post.from_shortcode(loader.context, shortcode)

                # Create download directory
                download_path = f'downloads'
                
                # Download the post
                loader.download_post(post, target='downloads')

                # Retrieve the latest downloaded files
                files = sorted(
                    [f for f in os.listdir(download_path) if f.endswith(('.mp4', '.jpg', '.txt'))],
                    key=lambda x: os.path.getmtime(os.path.join(download_path, x)),
                    reverse=True
                )
                print(files)

                if files:
                    cover = os.path.join(download_path, files[0])
                    video = os.path.join(download_path, files[1])
                    caption = os.path.join(download_path, files[2])
                    # print(latest_video)

                    # Read the caption if available
                    with open(caption, 'r', encoding='utf-8') as file:
                        lines = ''
                        for line in file.readlines():
                            lines += line.strip() + '\n'
                        caption_video = lines
                    
                    # Send video or image to the user
                    if video.endswith('.mp4'):
                        with open(video, 'rb') as video:
                            bot.send_video(message.chat.id, video, caption=caption_video)

                    if cover.endswith('.jpg'):
                        with open(cover, 'rb') as cover:
                            bot.send_photo(message.chat.id, cover, caption="کاور ریلز")        
                    
                    
                    # Clean up the download folder after sending
                    download_folder = 'downloads'
                    if os.path.exists(download_folder): shutil.rmtree(download_folder)

                else:
                    bot.send_message(message.chat.id, '❌ فایل مناسب پیدا نشد.')
            except Exception as e:
                bot.send_message(message.chat.id, f'❌ مشکلی در دانلود پست رخ داد:\n{str(e)}')
        else:
            bot.send_message(message.chat.id, '❌ لطفاً لینک معتبر اینستاگرام وارد کنید.')
