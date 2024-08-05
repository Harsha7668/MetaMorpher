import math, time
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import heroku3
import os


#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
async def progress_message(current, total, process_type, message, start, file_name, username, task_type):
    now = time.time()
    diff = now - start
    if round(diff % 5.00) == 0 or current == total:
        percentage = current * 100 / total
        speed = humanbytes(current / diff) + "/s"
        elapsed_time_ms = round(diff * 1000)
        time_to_completion_ms = round((total - current) / (current / diff)) * 1000
        estimated_total_time_ms = elapsed_time_ms + time_to_completion_ms

        elapsed_time = TimeFormatter(elapsed_time_ms)
        estimated_total_time = TimeFormatter(estimated_total_time_ms)

        progress = "{0}{1}".format(
            ''.join(["■" for i in range(math.floor(percentage / 5))]),
            ''.join(["□" for i in range(20 - math.floor(percentage / 5))])
        )
        tmp = f"{progress}\nProgress: {round(percentage, 2)}%\n{humanbytes(current)} of {humanbytes(total)}\nSpeed: {speed}\nETA: {estimated_total_time if estimated_total_time != '' else '0 s'}"

        try:
            await message.edit(
                text=f"{process_type} for {task_type} by {username} ({file_name})\n\n{tmp}",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🌟 Jᴏɪɴ Us 🌟", url="https://t.me/Sunrises24botupdates")]])
            )
        except Exception as e:
            print(f"Error editing message: {e}")


# Helper functions
def humanbytes(size):
    # Converts size in bytes to a human-readable format
    if not size:
        return ""
    power = 2**10
    n = 0
    power_labels = {0: '', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
    while size > power:
        size /= power
        n += 1
    return f"{round(size, 2)} {power_labels[n]}B"

def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(milliseconds, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = (
        (f"{days}d, " if days else "") +
        (f"{hours}h, " if hours else "") +
        (f"{minutes}m, " if minutes else "") +
        (f"{seconds}s" if seconds else "")
    )
    return tmp




#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
def convert(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%d:%02d:%02d" % (hour, minutes, seconds)

#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
# Define heroku_restart function
async def heroku_restart():
    HEROKU_API = "HRKU-987b360b-e27e-43bf-b4e8-026e4c07521e"
    HEROKU_APP_NAME = "infinitystartrename24bot"
    x = None
    if not HEROKU_API or not HEROKU_APP_NAME:
        x = None
    else:
        try:
            acc = heroku3.from_key(HEROKU_API)
            bot = acc.apps()[HEROKU_APP_NAME]
            bot.restart()
            x = True
        except Exception as e:
            print(e)
            x = False
    return x

#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
#for merging downloading media
async def download_media(msg, sts):
    c_time = time.time()
    try:
        file_path = await msg.download(
            progress=progress_message,
            progress_args=(0, 0, "media_file", sts, c_time, msg.from_user.username, "Downloading Media")  # Match progress_message arguments
        )
        await msg.reply_text(f"✅ Media downloaded successfully: {os.path.basename(file_path)}")
        return file_path
    except Exception as e:
        await sts.edit(f"❌ Error downloading media: {e}")
        raise

#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24        
# Recursive function to upload file
async def upload_files(bot, chat_id, directory, base_path=""):
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isfile(item_path):
            try:
                await bot.send_document(chat_id, document=item_path, caption=item)
            except Exception as e:
                print(f"Error uploading {item}: {e}")
        elif os.path.isdir(item_path):
            await upload_files(bot, chat_id, item_path, base_path=os.path.join(base_path, item))

