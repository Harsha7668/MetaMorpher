#TG : @Sunrises_24
#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
import subprocess
import os
import time
import shutil
import zipfile
import tarfile
import ffmpeg
from pyrogram.types import Message
from pyrogram.types import Document, Video
from pyrogram import Client, filters
from pyrogram.enums import MessageMediaType
from pyrogram.errors import MessageNotModified
from main.utils import progress_message, humanbytes
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup,CallbackQuery
from config import AUTH_USERS, ADMIN, CAPTION, GROUP
from main.utils import heroku_restart, upload_files, download_media
import aiohttp
from pyrogram.errors import RPCError, FloodWait
import asyncio
from main.ffmpeg import remove_all_tags, change_video_metadata, generate_sample_video, add_photo_attachment, merge_videos, unzip_file, extract_audio_stream, extract_subtitle_stream, extract_video_stream, extract_audios_from_file, extract_subtitles_from_file, extract_video_from_file, get_mediainfo
from googleapiclient.http import MediaFileUpload
from main.gdrive import upload_to_google_drive, extract_id_from_url, copy_file, get_files_in_folder, drive_service
from googleapiclient.errors import HttpError
from Database.database import db
import datetime
from datetime import timedelta
import psutil
from pymongo.errors import PyMongoError
from yt_dlp import YoutubeDL
from html_telegraph_poster import TelegraphPoster

# Initialize Telegraph
telegraph = TelegraphPoster(use_api=True)
telegraph.create_api_token("MediaInfoBot")


# Global variables
START_TIME = datetime.datetime.now()

merge_state = {}

FILE_SIZE_LIMIT = 2000 * 1024 * 1024  # 2000 MB in bytes

# Initialize global settings variables
METADATA_ENABLED = True 
PHOTO_ATTACH_ENABLED = True
MIRROR_ENABLED = True
RENAME_ENABLED = True
REMOVETAGS_ENABLED = True
CHANGE_INDEX_ENABLED = True 
MERGE_ENABLED = True
EXTRACT_ENABLED = True
GOFILE_ENABLED = True





#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
# Command handler to start the interaction (only in admin)
@Client.on_message(filters.command("bsettings") & filters.chat(ADMIN))
async def bot_settings_command(_, msg):
    await display_bot_settings_inline(msg)


# Inline function to display user settings with inline buttons
async def display_bot_settings_inline(msg):
    global METADATA_ENABLED, PHOTO_ATTACH_ENABLED, MIRROR_ENABLED, RENAME_ENABLED, REMOVETAGS_ENABLED, CHANGE_INDEX_ENABLED

    metadata_status = "✅ Enabled" if METADATA_ENABLED else "❌ Disabled"
    photo_attach_status = "✅ Enabled" if PHOTO_ATTACH_ENABLED else "❌ Disabled"
    mirror_status = "✅ Enabled" if MIRROR_ENABLED else "❌ Disabled"
    rename_status = "✅ Enabled" if RENAME_ENABLED else "❌ Disabled"
    removealltags_status = "✅ Enabled" if REMOVETAGS_ENABLED else "❌ Disabled"
    change_index_status = "✅ Enabled" if CHANGE_INDEX_ENABLED else "❌ Disabled"
    merge_video_status = "✅ Enabled" if MERGE_ENABLED else "❌ Disabled"    
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            
            [InlineKeyboardButton("💠", callback_data="sunrises24_bot_updates")],            
            [InlineKeyboardButton(f"{rename_status} Change Rename 📝", callback_data="toggle_rename")],
            [InlineKeyboardButton(f"{removealltags_status} Remove All Tags 📛", callback_data="toggle_removealltags")],
            [InlineKeyboardButton(f"{metadata_status} Change Metadata ☄️", callback_data="toggle_metadata")],            
            [InlineKeyboardButton(f"{change_index_status} Change Index ♻️", callback_data="toggle_change_index")],
            [InlineKeyboardButton(f"{merge_video_status} Merge Video 🎞️", callback_data="toggle_merge_video")],
            [InlineKeyboardButton(f"{photo_attach_status} Attach Photo 🖼️", callback_data="toggle_photo_attach")],                        
            [InlineKeyboardButton(f"{mirror_status} Mirror 💽", callback_data="toggle_mirror")],            
            [InlineKeyboardButton("Close ❌", callback_data="del")],
            [InlineKeyboardButton("💠", callback_data="sunrises24_bot_updates")]
        ]
    )

    await msg.reply_text("Use inline buttons to manage your settings:", reply_markup=keyboard)


#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
@Client.on_callback_query(filters.regex("del"))
async def closed(bot, msg):
    try:
        await msg.message.delete()
    except:
        return

# Callback query handlers

@Client.on_callback_query(filters.regex("^toggle_rename$"))
async def toggle_rename_callback(_, callback_query):
    global RENAME_ENABLED

    RENAME_ENABLED = not RENAME_ENABLED
    await update_settings_message(callback_query.message)

@Client.on_callback_query(filters.regex("^toggle_removealltags$"))
async def toggle_removealltags_callback(_, callback_query):
    global REMOVETAGS_ENABLED

    REMOVETAGS_ENABLED = not REMOVETAGS_ENABLED
    await update_settings_message(callback_query.message)

@Client.on_callback_query(filters.regex("^toggle_metadata$"))
async def toggle_metadata_callback(_, callback_query):
    global METADATA_ENABLED

    METADATA_ENABLED = not METADATA_ENABLED
    await update_settings_message(callback_query.message)


@Client.on_callback_query(filters.regex("^toggle_photo_attach$"))
async def toggle_photo_attach_callback(_, callback_query):
    global PHOTO_ATTACH_ENABLED

    PHOTO_ATTACH_ENABLED = not PHOTO_ATTACH_ENABLED
    await update_settings_message(callback_query.message)


@Client.on_callback_query(filters.regex("^toggle_mirror$"))
async def toggle_multitask_callback(_, callback_query):
    global MIRROR_ENABLED

    MIRROR_ENABLED = not MIRROR_ENABLED
    await update_settings_message(callback_query.message)

@Client.on_callback_query(filters.regex("^toggle_change_index$"))
async def toggle_change_index_callback(_, callback_query):
    global CHANGE_INDEX_ENABLED

    CHANGE_INDEX_ENABLED = not CHANGE_INDEX_ENABLED
    await update_settings_message(callback_query.message)

@Client.on_callback_query(filters.regex("^toggle_merge_video$"))
async def toggle_merge_video_callback(_, callback_query):
    global MERGE_ENABLED

    MERGE_ENABLED = not MERGE_ENABLED
    await update_settings_message(callback_query.message)
    
# Callback query handler for the "sunrises24_bot_updates" button
@Client.on_callback_query(filters.regex("^sunrises24_bot_updates$"))
async def sunrises24_bot_updates_callback(_, callback_query):
    await callback_query.answer("MADE BY @SUNRISES24BOTUPDATES ❤️", show_alert=True)    


async def update_settings_message(message):
    global METADATA_ENABLED, PHOTO_ATTACH_ENABLED, MIRROR_ENABLED, RENAME_ENABLED, REMOVETAGS_ENABLED, CHANGE_INDEX_ENABLED

    metadata_status = "✅ Enabled" if METADATA_ENABLED else "❌ Disabled"
    photo_attach_status = "✅ Enabled" if PHOTO_ATTACH_ENABLED else "❌ Disabled"
    mirror_status = "✅ Enabled" if MIRROR_ENABLED else "❌ Disabled"
    rename_status = "✅ Enabled" if RENAME_ENABLED else "❌ Disabled"
    removealltags_status = "✅ Enabled" if REMOVETAGS_ENABLED else "❌ Disabled"
    change_index_status = "✅ Enabled" if CHANGE_INDEX_ENABLED else "❌ Disabled"
    merge_video_status = "✅ Enabled" if MERGE_ENABLED else "❌ Disabled"    
      
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton("💠", callback_data="sunrises24_bot_updates")],            
            [InlineKeyboardButton(f"{rename_status} Change Rename 📝", callback_data="toggle_rename")],
            [InlineKeyboardButton(f"{removealltags_status} Remove All Tags 📛", callback_data="toggle_removealltags")],
            [InlineKeyboardButton(f"{metadata_status} Change Metadata ☄️", callback_data="toggle_metadata")],            
            [InlineKeyboardButton(f"{change_index_status} Change Index ♻️", callback_data="toggle_change_index")],
            [InlineKeyboardButton(f"{merge_video_status} Merge Video 🎞️", callback_data="toggle_merge_video")],
            [InlineKeyboardButton(f"{photo_attach_status} Attach Photo 🖼️", callback_data="toggle_photo_attach")],                        
            [InlineKeyboardButton(f"{mirror_status} Mirror 💽", callback_data="toggle_mirror")],            
            [InlineKeyboardButton("Close ❌", callback_data="del")],
            [InlineKeyboardButton("💠", callback_data="sunrises24_bot_updates")]
        ]
    )

    await message.edit_text("Use inline buttons to manage your settings:", reply_markup=keyboard)
    
    

@Client.on_callback_query(filters.regex("^set_sample_video_duration_"))
async def set_sample_video_duration(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    duration_str = callback_query.data.split("_")[-1]
    duration = int(duration_str)
    
    # Save sample video duration to database
    await db.save_sample_video_settings(user_id, duration, "screenshots setting")  # Adjusted the parameter from 'duration' to 'duration_str'
    
    await callback_query.answer(f"Sample video duration set to {duration} seconds.")
    await display_user_settings(client, callback_query.message, edit=True)


@Client.on_callback_query(filters.regex("^sample_video_option$"))
async def sample_video_option(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    current_duration = await db.get_sample_video_settings(user_id)
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"Sample Video 150s {'✅' if current_duration == 150 else ''}", callback_data="set_sample_video_duration_150")],
        [InlineKeyboardButton(f"Sample Video 120s {'✅' if current_duration == 120 else ''}", callback_data="set_sample_video_duration_120")],
        [InlineKeyboardButton(f"Sample Video 90s {'✅' if current_duration == 90 else ''}", callback_data="set_sample_video_duration_90")],
        [InlineKeyboardButton(f"Sample Video 60s {'✅' if current_duration == 60 else ''}", callback_data="set_sample_video_duration_60")],
        [InlineKeyboardButton(f"Sample Video 30s {'✅' if current_duration == 30 else ''}", callback_data="set_sample_video_duration_30")],
        [InlineKeyboardButton("Back", callback_data="back_to_settings")]
    ])
    
    await callback_query.message.edit_text(f"Sample Video Duration Settings\nCurrent duration: {current_duration}", reply_markup=keyboard)
  

# Callback query handler for returning to user settings
@Client.on_callback_query(filters.regex("^back_to_settings$"))
async def back_to_settings(client, callback_query: CallbackQuery):
    await display_user_settings(client, callback_query.message, edit=True)

@Client.on_message(filters.command("usersettings") & filters.chat(GROUP))
async def display_user_settings(client, msg, edit=False):
    user_id = msg.from_user.id
    
    current_duration = await db.get_sample_video_duration(user_id)
    current_screenshots = await db.get_screenshots_count(user_id)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💠", callback_data="sunrises24_bot_updates")],
        [InlineKeyboardButton("Sample Video Settings 🎞️", callback_data="sample_video_option")],
        [InlineKeyboardButton("Screenshots Settings 📸", callback_data="screenshots_option")],
        [InlineKeyboardButton("Thumbnail Settings 📄", callback_data="thumbnail_settings")],
        [InlineKeyboardButton("View Metadata ✨", callback_data="preview_metadata")],
        [InlineKeyboardButton("Attach Photo 📎", callback_data="attach_photo"),
         InlineKeyboardButton("View Photo ✨", callback_data="preview_photo")],
        [InlineKeyboardButton("View Photo Post ✨", callback_data="preview_photo_post")],        
        [InlineKeyboardButton("Delete Photo  Post ❌", callback_data="delete_photo_post")],
        [InlineKeyboardButton("View Gofile API Key 🔗", callback_data="preview_gofilekey")],
        [InlineKeyboardButton("View Google Drive Folder ID 📂", callback_data="preview_gdrive")],
        [InlineKeyboardButton("Close ❌", callback_data="del")]
    ])
    
    if edit:
        await msg.edit_text(f"User Settings\nCurrent sample video duration: {current_duration}\nCurrent screenshots setting: {current_screenshots}", reply_markup=keyboard)
    else:
        await msg.reply(f"User Settings\nCurrent sample video duration: {current_duration}\nCurrent screenshots setting: {current_screenshots}", reply_markup=keyboard)


@Client.on_callback_query(filters.regex("^screenshots_option$"))
async def screenshots_option(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    current_screenshots = await db.get_screenshots_count(user_id)  # Default to 5 if not set
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"Screenshots 1 {'✅' if current_screenshots == 1 else ''}", callback_data="set_screenshots_1")],
        [InlineKeyboardButton(f"Screenshots 2 {'✅' if current_screenshots == 2 else ''}", callback_data="set_screenshots_2")],
        [InlineKeyboardButton(f"Screenshots 3 {'✅' if current_screenshots == 3 else ''}", callback_data="set_screenshots_3")],
        [InlineKeyboardButton(f"Screenshots 4 {'✅' if current_screenshots == 4 else ''}", callback_data="set_screenshots_4")],
        [InlineKeyboardButton(f"Screenshots 5 {'✅' if current_screenshots == 5 else ''}", callback_data="set_screenshots_5")],
        [InlineKeyboardButton(f"Screenshots 6 {'✅' if current_screenshots == 6 else ''}", callback_data="set_screenshots_6")],
        [InlineKeyboardButton(f"Screenshots 7 {'✅' if current_screenshots == 7 else ''}", callback_data="set_screenshots_7")],
        [InlineKeyboardButton(f"Screenshots 8 {'✅' if current_screenshots == 8 else ''}", callback_data="set_screenshots_8")],
        [InlineKeyboardButton(f"Screenshots 9 {'✅' if current_screenshots == 9 else ''}", callback_data="set_screenshots_9")],
        [InlineKeyboardButton(f"Screenshots 10 {'✅' if current_screenshots == 10 else ''}", callback_data="set_screenshots_10")],
        [InlineKeyboardButton("Back", callback_data="back_to_settings")]
    ])
    
    await callback_query.message.edit_text(f"Screenshots Settings\nCurrent number: {current_screenshots}", reply_markup=keyboard)
    
@Client.on_callback_query(filters.regex("^set_screenshots_"))
async def set_screenshots(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    num_str = callback_query.data.split("_")[-1]
    num_screenshots = int(num_str)
    
    # Save screenshots count to database
    await db.save_screenshots_count(user_id, num_screenshots)
    
    await callback_query.answer(f"Number of screenshots set to {num_screenshots}.")
    await display_user_settings(client, callback_query.message, edit=True)



@Client.on_callback_query(filters.regex("^attach_photo$"))
async def inline_attach_photo_callback(_, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    
    # Update user settings to indicate attachment request
    await db.update_user_settings(user_id, {"attach_photo": True})
    
    await callback_query.message.edit_text("Please send a photo to be attached using the setphoto command.")




@Client.on_message(filters.private & filters.command("setphoto"))
async def set_photo(bot, msg):
    reply = msg.reply_to_message
    if not reply or not reply.photo:
        return await msg.reply_text("Please reply to a photo with the setphoto command")

    # Extract custom name from the command
    if len(msg.command) < 2:
        return await msg.reply_text("Please provide a custom name for the photo.")
    
    custom_name = msg.command[1]  # The custom name is the second part of the command
    user_id = msg.from_user.id
    photo_file_id = reply.photo.file_id

    try:
        # Download the photo file
        photo_path = await bot.download_media(photo_file_id)
        
        # Save the photo with the custom name
        custom_photo_path = f"{custom_name}.jpg"
        os.rename(photo_path, custom_photo_path)

        # Save the custom photo path to the database
        await db.save_attach_photo(user_id, custom_photo_path)
        await msg.reply_text(f"Photo saved successfully with the name: {custom_name}.jpg")

    except Exception as e:
        await msg.reply_text(f"Error saving photo: {e}")


    
@Client.on_callback_query(filters.regex("^preview_photo$"))
async def inline_preview_photo_callback(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    
    # Retrieve the attachment path from the database
    attachment_file_id = await db.get_attach_photo(user_id)
    
    if not attachment_file_id:
        await callback_query.message.reply_text("No photo has been attached yet.")
        return
    
    try:
        await callback_query.message.reply_photo(photo=attachment_file_id, caption="Attached Photo")
    except Exception as e:
        await callback_query.message.reply_text(f"Failed to send photo: {str(e)}")

@Client.on_callback_query(filters.regex("^thumbnail_settings$"))
async def inline_thumbnail_settings(client, callback_query: CallbackQuery):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[            
            [InlineKeyboardButton("View Thumbnail", callback_data="view_thumbnail")],
            [InlineKeyboardButton("Delete Thumbnail", callback_data="delete_thumbnail")],
            [InlineKeyboardButton("Back to Settings", callback_data="back_to_settings")]
        ]
    )
    await callback_query.message.edit_text("Thumbnail Settings:", reply_markup=keyboard)




@Client.on_callback_query(filters.regex("delete_photo_post"))
async def delete_photo_callback(client: Client, query: CallbackQuery):
    user_id = query.from_user.id
    result = await db.delete_photo(user_id)
    await query.message.edit_text(result)

@Client.on_callback_query(filters.regex("preview_photo_post"))
async def preview_photo_callback(client: Client, query: CallbackQuery):
    user_id = query.from_user.id
    
    saved_photo = await db.get_saved_photo(user_id)

    if saved_photo:
        await client.send_photo(query.message.chat.id, saved_photo, caption="Here is your saved photo.")
    else:
        await query.message.edit_text("No photo found. Please save a photo first.")


@Client.on_message(filters.command("setthumbnail") & filters.chat(GROUP))
async def set_thumbnail_command(client, message):
    user_id = message.from_user.id

    # Check if thumbnail already exists
    thumbnail_file_id = await db.get_thumbnail(user_id)
    if thumbnail_file_id:
        await message.reply("You already have a permanent thumbnail set. Send a new photo to update it.")
    else:
        await message.reply("Send a photo to set as your permanent thumbnail.")

@Client.on_message(filters.photo & filters.chat(GROUP))
async def set_thumbnail_handler(client, message):
    user_id = message.from_user.id
    photo_file_id = message.photo.file_id

    # Save thumbnail file ID to database
    await db.save_thumbnail(user_id, photo_file_id)
    
    await message.reply("Your permanent thumbnail is updated. If the bot is restarted, the new thumbnail will be preserved.")
    
@Client.on_callback_query(filters.regex("^view_thumbnail$"))
async def view_thumbnail(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    thumbnail_file_id = await db.get_thumbnail(user_id)

    if not thumbnail_file_id:
        await callback_query.message.reply_text("You don't have any thumbnail.")
        return

    try:
        await callback_query.message.reply_photo(photo=thumbnail_file_id, caption="This is your current thumbnail")
    except Exception as e:
        await callback_query.message.reply_text("An error occurred while trying to view your thumbnail.")

@Client.on_callback_query(filters.regex("^delete_thumbnail$"))
async def delete_thumbnail(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    thumbnail_file_id = await db.get_thumbnail(user_id)

    try:
        if thumbnail_file_id:
            await db.delete_thumbnail(user_id)
            await callback_query.message.reply_text("Your thumbnail was removed ❌")
        else:
            await callback_query.message.reply_text("You don't have any thumbnail ‼️")
    except Exception as e:
        await callback_query.message.reply_text("An error occurred while trying to remove your thumbnail. Please try again later.")



@Client.on_callback_query(filters.regex("^preview_gdrive$"))
async def inline_preview_gdrive(bot, callback_query):
    user_id = callback_query.from_user.id
    
    # Retrieve Google Drive folder ID from the database
    gdrive_folder_id = await db.get_gdrive_folder_id(user_id)
    
    if not gdrive_folder_id:
        return await callback_query.message.reply_text(f"Google Drive Folder ID is not set for user `{user_id}`. Use /gdriveid {{your_gdrive_folder_id}} to set it.")
    
    await callback_query.message.reply_text(f"Current Google Drive Folder ID for user `{user_id}`: {gdrive_folder_id}")

@Client.on_message(filters.command("setmetadata") & filters.chat(GROUP))
async def set_metadata_command(client, msg):
    # Extract titles from the command message
    if len(msg.command) < 2:
        await msg.reply_text("Invalid command format. Use: setmetadata video_title | audio_title | subtitle_title")
        return
    
    titles = msg.text.split(" ", 1)[1].split(" | ")
    if len(titles) != 3:
        await msg.reply_text("Invalid number of titles. Use: setmetadata video_title | audio_title | subtitle_title")
        return
    
    # Store the titles in the database
    user_id = msg.from_user.id
    await db.save_metadata_titles(user_id, titles[0].strip(), titles[1].strip(), titles[2].strip())
    
    await msg.reply_text("Metadata titles set successfully ✅.")

@Client.on_message(filters.command("gofilesetup") & filters.private)
async def set_gofile_api_key(bot, msg):
    user_id = msg.from_user.id
    args = msg.text.split(" ", 1)
    if len(args) != 2:
        return await msg.reply_text("Usage: /gofilesetup {your_api_key}")
    
    api_key = args[1].strip()
    
    # Save Gofile API key to the database
    await db.save_gofile_api_key(user_id, api_key)
    
    await msg.reply_text("Your Gofile API key has been set successfully.✅")

@Client.on_message(filters.private & filters.command("gdriveid"))
async def setup_gdrive_id(bot, msg: Message):
    user_id = msg.from_user.id
    args = msg.text.split(" ", 1)
    if len(args) != 2:
        return await msg.reply_text("Usage: /gdriveid {your_gdrive_folder_id}")
    
    gdrive_folder_id = args[1].strip()
    
    # Save Google Drive folder ID to the database
    await db.save_gdrive_folder_id(user_id, gdrive_folder_id)
    
    await msg.reply_text(f"Google Drive folder ID set to: {gdrive_folder_id} for user `{user_id}`\n\nGoogle Drive folder ID set successfully✅!")

@Client.on_callback_query(filters.regex("^preview_metadata$"))
async def inline_preview_metadata_callback(_, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    
    # Fetch metadata titles from the database
    titles = await db.get_metadata_titles(user_id)
    
    if not titles or not any(titles.values()):
        await callback_query.message.reply_text("Metadata titles are not fully set. Please set all titles first.")
        return
    
    preview_text = f"Video Title: {titles.get('video_title', '')}\n" \
                   f"Audio Title: {titles.get('audio_title', '')}\n" \
                   f"Subtitle Title: {titles.get('subtitle_title', '')}"
    
    await callback_query.message.reply_text(f"Current Metadata Titles:\n\n{preview_text}")

@Client.on_callback_query(filters.regex("^preview_gofilekey$"))
async def inline_preview_gofile_api_key(bot, callback_query):
    user_id = callback_query.from_user.id
    
    # Fetch Gofile API key from the database
    api_key = await db.get_gofile_api_key(user_id)
    
    if not api_key:
        return await callback_query.message.reply_text(f"Gofile API key is not set for user `{user_id}`. Use /gofilesetup {{your_api_key}} to set it.")
    
    await callback_query.message.reply_text(f"Current Gofile API Key for user `{user_id}`: {api_key}")


@Client.on_message(filters.command("savephotopost") & filters.chat(GROUP))
async def save_photo(bot: Client, msg: Message):
    user_id = msg.from_user.id
    reply = msg.reply_to_message
    if not reply or not reply.photo:
        return await msg.reply_text("Please reply to a photo to save.")

    photo = reply.photo
    result = await db.save_photo(user_id, photo.file_id)
    await msg.reply_text(result)
    

async def generate_task_list(page, tasks_per_page):
    tasks = await db.list_tasks(page, tasks_per_page)
    if not tasks:
        return "📄 **Task List** 📄\n\nNo tasks available."

    text = "📄 **Task List** 📄\n\n"
    for task in tasks:
        text += (
            f"Task ID: {task['_id']}\n"
            f"User: {task['username']} ({task['user_id']})\n"
            f"Type: {task['task_type']}\n"
            f"Status: {task['status']}\n\n"
        )
    return text

@Client.on_message(filters.command("tasklist") & filters.chat(GROUP))
async def task_list(bot, msg: Message):
    page = 1
    tasks_per_page = 2
    text = await generate_task_list(page, tasks_per_page)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Refresh", callback_data="tasklist_refresh"),
         InlineKeyboardButton("Next", callback_data=f"tasklist_next_{page}")]
    ])
    await msg.reply_text(text, reply_markup=keyboard)

@Client.on_callback_query(filters.regex(r"tasklist_(next|prev)_(\d+)"))
async def tasklist_navigation_callback(bot, callback_query):
    action, page = callback_query.data.split("_")[-2:]
    page = int(page)

    if action == 'next':
        page += 1
    elif action == 'prev':
        page -= 1

    tasks_per_page = 2
    text = await generate_task_list(page, tasks_per_page)

    # Handle button visibility
    prev_button = InlineKeyboardButton("Previous", callback_data=f"tasklist_prev_{page-1}") if page > 1 else None
    next_button = InlineKeyboardButton("Next", callback_data=f"tasklist_next_{page+1}")
    refresh_button = InlineKeyboardButton("Refresh", callback_data="tasklist_refresh")

    keyboard = InlineKeyboardMarkup([
        [prev_button, next_button] if prev_button else [next_button],
        [refresh_button]
    ])

    await callback_query.edit_message_text(text, reply_markup=keyboard)

@Client.on_callback_query(filters.regex(r"tasklist_refresh"))
async def tasklist_refresh_callback(bot, callback_query):
    page = 1  # Refresh should always show the first page
    tasks_per_page = 2
    text = await generate_task_list(page, tasks_per_page)

    # Handle button visibility
    refresh_button = InlineKeyboardButton("Refresh", callback_data="tasklist_refresh")
    next_button = InlineKeyboardButton("Next", callback_data=f"tasklist_next_{page + 1}")

    keyboard = InlineKeyboardMarkup([
        [refresh_button, next_button]
    ])

    await callback_query.edit_message_text(text, reply_markup=keyboard)

@Client.on_message(filters.command("cleanuptasks") & filters.chat(GROUP))
async def cleanup_tasks(bot, msg: Message):
    deleted_count = await db.delete_completed_tasks()
    await msg.reply_text(f"Deleted {deleted_count} completed tasks.")



@Client.on_message(filters.command("mirror") & filters.chat(GROUP))
async def mirror_to_google_drive(bot, msg: Message):
    global MIRROR_ENABLED
    
    if not MIRROR_ENABLED:
        return await msg.reply_text("The mirror feature is currently disabled.")

    user_id = msg.from_user.id
    username = msg.from_user.username or msg.from_user.first_name
    
    # Retrieve the user's Google Drive folder ID
    gdrive_folder_id = await db.get_gdrive_folder_id(user_id)
    
    if not gdrive_folder_id:
        return await msg.reply_text("Google Drive folder ID is not set. Please use the /gdriveid command to set it.")

    reply = msg.reply_to_message
    if len(msg.command) < 2 or not reply:
        return await msg.reply_text("Please reply to a file with the new filename and extension.")

    media = reply.document or reply.audio or reply.video
    if not media:
        return await msg.reply_text("Please reply to a file with the new filename and extension.")

    new_name = msg.text.split(" ", 1)[1]
    original_file_name = media.file_name

    # Add task to the database
    task_id = await db.add_task(user_id, username, "Mirror", "Queued")
    
    # Notify all users about the new task
    await bot.send_message(GROUP, f"Mirror Task is added by {username} ({user_id})")

    try:
        # Show progress message for downloading
        sts = await msg.reply_text("🚀 Downloading...")
        
        # Update task status
        await db.update_task_status(task_id, "Downloading")
        
        # Download the file
        downloaded_file = await bot.download_media(
            message=reply, 
            file_name=new_name, 
            progress=progress_message, 
            progress_args=("Downloading", sts, time.time(), original_file_name, username, "Mirror")
        )
        
        filesize = os.path.getsize(downloaded_file)
        
        # Once downloaded, update the message to indicate uploading
        await sts.edit("💠 Uploading...")
        
        start_time = time.time()

        # Update task status
        await db.update_task_status(task_id, "Uploading")

        # Upload file to Google Drive
        file_metadata = {'name': new_name, 'parents': [gdrive_folder_id]}
        media = MediaFileUpload(downloaded_file, resumable=True)

        # Upload with progress monitoring
        request = drive_service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink')
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                current_progress = status.progress() * 100
                await progress_message(current_progress, 100, "Uploading to Google Drive", sts, start_time, original_file_name, username, "Mirror")
        
        file_id = response.get('id')
        file_link = response.get('webViewLink')

        # Prepare caption for the uploaded file
        if CAPTION:
            caption_text = CAPTION.format(file_name=new_name, file_size=humanbytes(filesize))
        else:
            caption_text = f"Uploaded File: {new_name}\nSize: {humanbytes(filesize)}"

        # Send the Google Drive link to the user
        button = [
            [InlineKeyboardButton("☁️ CloudUrl ☁️", url=f"{file_link}")]
        ]
        await msg.reply_text(
            f"File successfully mirrored and uploaded to Google Drive!\n\n"
            f"Google Drive Link: [View File]({file_link})\n\n"
            f"Uploaded File: {new_name}\n"
            f"Size: {humanbytes(filesize)}",
            reply_markup=InlineKeyboardMarkup(button)
        )
        os.remove(downloaded_file)
        await sts.delete()
        await db.update_task_status(task_id, "Completed")

    except Exception as e:
        await sts.edit(f"Error: {e}")
        await db.update_task_status(task_id, "Failed")

#Rename Command
@Client.on_message(filters.command("rename") & filters.chat(GROUP))
async def rename_file(bot, msg):
    if len(msg.command) < 2 or not msg.reply_to_message:
        return await msg.reply_text("Please reply to a file, video, or audio with the new filename and extension (e.g., .mkv, .mp4, .zip).")

    reply = msg.reply_to_message
    media = reply.document or reply.audio or reply.video
    if not media:
        return await msg.reply_text("Please reply to a file, video, or audio with the new filename and extension (e.g., .mkv, .mp4, .zip).")

    new_name = msg.text.split(" ", 1)[1]
    user_id = msg.from_user.id
    username = msg.from_user.username or msg.from_user.first_name  # Get the username or first name

    # Add task to the database
    task_id = await db.add_task(user_id, username, "Rename", "Queued")
    
    # Notify all users about the new task
    await bot.send_message(GROUP, f"Rename Task is added by {username} ({user_id})")

    try:
        # Show progress message for downloading
        sts = await msg.reply_text("🚀 Downloading...")
        
        # Update task status
        await db.update_task_status(task_id, "Downloading")
        
        # Download the file
        downloaded_file = await reply.download(file_name=new_name, progress=progress_message, progress_args=("🚀 Download Started... ⚡️", sts, time.time(), new_name, username, "Rename"))
        filesize = humanbytes(media.file_size)
        
        # Prepare caption for the uploaded file
        if CAPTION:
            try:
                cap = CAPTION.format(file_name=new_name, file_size=filesize)
            except KeyError as e:
                return await sts.edit(text=f"Caption error: unexpected keyword ({e})")
        else:
            cap = f"{new_name}\n\n🌟 Size: {filesize}"

        # Retrieve thumbnail from the database
        thumbnail_file_id = await db.get_thumbnail(user_id)
        og_thumbnail = None
        if thumbnail_file_id:
            try:
                og_thumbnail = await bot.download_media(thumbnail_file_id)
            except Exception:
                pass
        else:
            if hasattr(media, 'thumbs') and media.thumbs:
                try:
                    og_thumbnail = await bot.download_media(media.thumbs[0].file_id)
                except Exception:
                    pass

        # Update task status for uploading
        await sts.edit("💠 Uploading...")
        start_time = time.time()
        await db.update_task_status(task_id, "Uploading")

        if os.path.getsize(downloaded_file) > FILE_SIZE_LIMIT:
            file_link = await upload_to_google_drive(downloaded_file, new_name, sts)
            await msg.reply_text(f"File uploaded to Google Drive!\n\n📁 **File Name:** {new_name}\n💾 **Size:** {filesize}\n🔗 **Link:** {file_link}")
        else:
            try:
                await bot.send_document(msg.chat.id, document=downloaded_file, thumb=og_thumbnail, caption=cap, progress=progress_message, progress_args=("💠 Upload Started... ⚡", sts, start_time, new_name, username, "Rename"))
            except Exception as e:
                return await sts.edit(f"Error: {e}")

        os.remove(downloaded_file)
        await sts.delete()
        await db.update_task_status(task_id, "Completed")

    except Exception as e:
        await sts.edit(f"Error: {e}")
        await db.update_task_status(task_id, "Failed")



#Change Metadata Code
@Client.on_message(filters.command("changemetadata") & filters.chat(GROUP))
async def change_metadata(bot, msg: Message):
    global METADATA_ENABLED

    if not METADATA_ENABLED:
        return await msg.reply_text("Metadata changing feature is currently disabled.")

    user_id = msg.from_user.id
    username = msg.from_user.username or msg.from_user.first_name

    # Fetch metadata titles from the database
    metadata_titles = await db.get_metadata_titles(user_id)
    video_title = metadata_titles.get('video_title', '')
    audio_title = metadata_titles.get('audio_title', '')
    subtitle_title = metadata_titles.get('subtitle_title', '')

    if not any([video_title, audio_title, subtitle_title]):
        return await msg.reply_text("Metadata titles are not set. Please set metadata titles using `/setmetadata video_title audio_title subtitle_title`.")

    reply = msg.reply_to_message
    if not reply:
        return await msg.reply_text("Please reply to a media file with the metadata command\nFormat: `changemetadata -n filename.mkv`")

    if len(msg.command) < 3 or msg.command[1] != "-n":
        return await msg.reply_text("Please provide the filename with the `-n` flag\nFormat: `changemetadata -n filename.mkv`")

    new_name = " ".join(msg.command[2:]).strip()

    if not new_name.lower().endswith(('.mkv', '.mp4', '.avi')):
        return await msg.reply_text("Invalid file extension. Please use a valid video file extension (e.g., .mkv, .mp4, .avi).")

    media = reply.document or reply.audio or reply.video
    if not media:
        return await msg.reply_text("Please reply to a valid media file (audio, video, or document) with the metadata command.")

    # Add task to the database
    task_id = await db.add_task(user_id, username, "Change Metadata", "Queued")
    await bot.send_message(GROUP, f"Change Metadata Task is added by {username} ({user_id})")

    sts = await msg.reply_text("🚀 Downloading media... ⚡")
    c_time = time.time()

    try:
        # Update task status
        await db.update_task_status(task_id, "Downloading")

        # Download the file
        downloaded = await reply.download(progress=progress_message, progress_args=("🚀 Download Started... ⚡️", sts, c_time, new_name, username, "Change Metadata"))

        output_file = new_name

        await safe_edit_message(sts, "💠 Changing metadata... ⚡")
        try:
            change_video_metadata(downloaded, video_title, audio_title, subtitle_title, output_file)
        except Exception as e:
            await safe_edit_message(sts, f"Error changing metadata: {e}")
            os.remove(downloaded)
            return

        # Retrieve thumbnail from the database
        thumbnail_file_id = await db.get_thumbnail(user_id)
        file_thumb = None
        if thumbnail_file_id:
            try:
                file_thumb = await bot.download_media(thumbnail_file_id)
            except Exception:
                pass
        else:
            if hasattr(media, 'thumbs') and media.thumbs:
                try:
                    file_thumb = await bot.download_media(media.thumbs[0].file_id)
                except Exception:
                    file_thumb = None

        filesize = os.path.getsize(output_file)
        filesize_human = humanbytes(filesize)
        cap = f"{output_file}\n\n🌟 Size: {filesize_human}"

        await safe_edit_message(sts, "💠 Uploading... ⚡")
        c_time = time.time()

        # Update task status for uploading
        await db.update_task_status(task_id, "Uploading")

        if filesize > FILE_SIZE_LIMIT:
            file_link = await upload_to_google_drive(output_file, new_name, sts)
            button = [[InlineKeyboardButton("☁️ CloudUrl ☁️", url=f"{file_link}")]]
            await msg.reply_text(
                f"**File successfully changed metadata and uploaded to Google Drive!**\n\n"
                f"**Google Drive Link**: [View File]({file_link})\n\n"
                f"**Uploaded File**: {new_name}\n"
                f"**Request User:** {msg.from_user.mention}\n\n"
                f"**Size**: {filesize_human}",
                reply_markup=InlineKeyboardMarkup(button)
            )
        else:
            try:
                await bot.send_document(msg.chat.id, document=output_file, thumb=file_thumb, caption=cap, progress=progress_message, progress_args=("💠 Upload Started... ⚡", sts, c_time, new_name, username, "Change Metadata"))
            except Exception as e:
                return await safe_edit_message(sts, f"Error: {e}")

        os.remove(downloaded)
        os.remove(output_file)
        if file_thumb and os.path.exists(file_thumb):
            os.remove(file_thumb)
        await sts.delete()
        await db.update_task_status(task_id, "Completed")

    except Exception as e:
        await sts.edit(f"Error: {e}")
        await db.update_task_status(task_id, "Failed")


@Client.on_message(filters.command("multitaskfile") & filters.chat(GROUP))
async def filemultitask(bot, msg: Message):
    global METADATA_ENABLED, CHANGE_INDEX_ENABLED

    if not (METADATA_ENABLED and CHANGE_INDEX_ENABLED):
        return await msg.reply_text("One or more required features are currently disabled.")

    user_id = msg.from_user.id
    username = msg.from_user.username or msg.from_user.first_name

    # Fetch metadata titles from the database
    metadata_titles = await db.get_metadata_titles(user_id)
    video_title = metadata_titles.get('video_title', '')
    audio_title = metadata_titles.get('audio_title', '')
    subtitle_title = metadata_titles.get('subtitle_title', '')

    if not any([video_title, audio_title, subtitle_title]):
        return await msg.reply_text("Metadata titles are not set. Please set metadata titles using `/setmetadata video_title audio_title subtitle_title`.")

    reply = msg.reply_to_message
    if not reply:
        return await msg.reply_text("Please reply to a media file with the change command\nFormat: `/change a-2 -m -n filename.mkv`")

    if len(msg.command) < 5 or '-m' not in msg.command or '-n' not in msg.command:
        return await msg.reply_text("Please provide the correct format\nFormat: `/change a-2 -m -n filename.mkv`")

    index_cmd = msg.command[1]
    metadata_flag_index = msg.command.index('-m')
    output_flag_index = msg.command.index('-n')
    output_filename = " ".join(msg.command[output_flag_index + 1:]).strip()

    if not output_filename.lower().endswith(('.mkv', '.mp4', '.avi')):
        return await msg.reply_text("Invalid file extension. Please use a valid video file extension (e.g., .mkv, .mp4, .avi).")

    media = reply.document or reply.audio or reply.video
    if not media:
        return await msg.reply_text("Please reply to a valid media file (audio, video, or document) with the change command.")

    # Add task to the database
    task_id = await db.add_task(user_id, username, "Change Index and Metadata", "Queued")
    await bot.send_message(GROUP, f"Change Index and Metadata Task is added by {username} ({user_id})")

    sts = await msg.reply_text("🚀 Downloading media... ⚡")
    c_time = time.time()
    try:
        # Update task status
        await db.update_task_status(task_id, "Downloading")

        downloaded = await reply.download(progress=progress_message, progress_args=("🚀 Download Started... ⚡️", sts, c_time, output_filename, msg.from_user.username or msg.from_user.first_name, "Change Index and Metadata"))
    except Exception as e:
        await safe_edit_message(sts, f"Error downloading media: {e}")
        return

    # Output file path (temporary file)
    intermediate_file = os.path.splitext(downloaded)[0] + "_indexed" + os.path.splitext(downloaded)[1]

    index_params = index_cmd.split('-')
    stream_type = index_params[0]
    indexes = [int(i) - 1 for i in index_params[1:]]

    # Construct the FFmpeg command to modify indexes
    ffmpeg_cmd = ['ffmpeg', '-i', downloaded, '-map', '0:v']  # Always map video stream

    for idx in indexes:
        ffmpeg_cmd.extend(['-map', f'0:{stream_type}:{idx}'])

    # Copy all subtitle streams if they exist
    ffmpeg_cmd.extend(['-map', '0:s?'])
    ffmpeg_cmd.extend(['-c', 'copy', intermediate_file, '-y'])

    await safe_edit_message(sts, "💠 Changing audio indexing... ⚡")
    process = await asyncio.create_subprocess_exec(*ffmpeg_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        await safe_edit_message(sts, f"❗ FFmpeg error: {stderr.decode('utf-8')}")
        os.remove(downloaded)
        if os.path.exists(intermediate_file):
            os.remove(intermediate_file)
        return

    output_file = output_filename

    await safe_edit_message(sts, "💠 Changing metadata... ⚡")
    try:
        change_video_metadata(intermediate_file, video_title, audio_title, subtitle_title, output_file)
    except Exception as e:
        await safe_edit_message(sts, f"Error changing metadata: {e}")
        os.remove(downloaded)
        os.remove(intermediate_file)
        return

    # Retrieve thumbnail from the database
    thumbnail_file_id = await db.get_thumbnail(user_id)
    file_thumb = None
    if thumbnail_file_id:
        try:
            file_thumb = await bot.download_media(thumbnail_file_id)
        except Exception:
            pass
    else:
        if hasattr(media, 'thumbs') and media.thumbs:
            try:
                file_thumb = await bot.download_media(media.thumbs[0].file_id)
            except Exception:
                file_thumb = None

    filesize = os.path.getsize(output_file)
    filesize_human = humanbytes(filesize)
    cap = f"{output_filename}\n\n🌟 Size: {filesize_human}"

    await safe_edit_message(sts, "💠 Uploading... ⚡")
    c_time = time.time()

    # Update task status for uploading
    await db.update_task_status(task_id, "Uploading")

    if filesize > FILE_SIZE_LIMIT:
        file_link = await upload_to_google_drive(output_file, output_filename, sts)
        button = [[InlineKeyboardButton("☁️ CloudUrl ☁️", url=f"{file_link}")]]
        await msg.reply_text(
            f"**File successfully changed audio index and metadata, then uploaded to Google Drive!**\n\n"
            f"**Google Drive Link**: [View File]({file_link})\n\n"
            f"**Uploaded File**: {output_filename}\n"
            f"**Request User:** {msg.from_user.mention}\n\n"
            f"**Size**: {filesize_human}",
            reply_markup=InlineKeyboardMarkup(button)
        )
    else:
        try:
            await bot.send_document(
                msg.chat.id,
                document=output_file,
                file_name=output_filename,
                thumb=file_thumb,
                caption=cap,
                progress=progress_message,
                progress_args=("💠 Upload Started... ⚡", sts, c_time, output_filename, msg.from_user.username or msg.from_user.first_name, "Change Index and Metadata")
            )
        except Exception as e:
            return await safe_edit_message(sts, f"Error: {e}")

    os.remove(downloaded)
    os.remove(intermediate_file)
    os.remove(output_file)
    if file_thumb and os.path.exists(file_thumb):
        os.remove(file_thumb)
    await sts.delete()
    await db.update_task_status(task_id, "Completed")

@Client.on_message(filters.command("attachphoto") & filters.chat(GROUP))
async def attach_photo(bot, msg: Message):
    global PHOTO_ATTACH_ENABLED

    if not PHOTO_ATTACH_ENABLED:
        return await msg.reply_text("Photo attachment feature is currently disabled.")

    user_id = msg.from_user.id
    username = msg.from_user.username or msg.from_user.first_name

    # Add a new task to the user tasks schema
    task_id = await db.add_task(user_id, username, "Attach Photo", "Queued")
    await bot.send_message(GROUP, f"Attach Photo Task is added by {username} ({user_id})")

    reply = msg.reply_to_message
    if not reply:
        await db.update_task_status(task_id, "Failed")
        return await msg.reply_text("Please reply to a media file with the attach photo command and specify the output filename\nFormat: `attachphoto -n filename.mkv`")

    command_text = " ".join(msg.command[1:]).strip()
    if "-n" not in command_text:
        await db.update_task_status(task_id, "Failed")
        return await msg.reply_text("Please provide the output filename using the `-n` flag\nFormat: `attachphoto -n filename.mkv`")

    filename_part = command_text.split('-n', 1)[1].strip()
    new_name = filename_part if filename_part else None

    if not new_name:
        await db.update_task_status(task_id, "Failed")
        return await msg.reply_text("Please provide a valid filename\nFormat: `attachphoto -n filename.mkv`")

    if not new_name.lower().endswith(('.mkv', '.mp4', '.avi')):
        await db.update_task_status(task_id, "Failed")
        return await msg.reply_text("Invalid file extension. Please use a valid video file extension (e.g., .mkv, .mp4, .avi).")

    media = reply.document or reply.audio or reply.video
    if not media:
        await db.update_task_status(task_id, "Failed")
        return await msg.reply_text("Please reply to a valid media file (audio, video, or document) with the attach photo command.")

    sts = await msg.reply_text("🚀 Downloading media... ⚡")
    c_time = time.time()
    try:
        await db.update_task_status(task_id, "Downloading")
        downloaded = await reply.download(
            progress=progress_message, 
            progress_args=("🚀 Download Started... ⚡️", sts, c_time, new_name, username, "Attach Photo")
        )
    except Exception as e:
        await safe_edit_message(sts, f"Error downloading media: {e}")
        await db.update_task_status(task_id, "Failed")
        return

    # Retrieve attachment from the database
    attachment_file_path = await db.get_attach_photo(msg.from_user.id)
    if not attachment_file_path:
        await safe_edit_message(sts, "Please send a photo to be attached using the `setphoto` command.")
        os.remove(downloaded)
        await db.update_task_status(task_id, "Failed")
        return

    # Ensure the attachment exists and download it if necessary
    attachment_path = attachment_file_path
    if not os.path.exists(attachment_path):
        await safe_edit_message(sts, "Attachment not found.")
        os.remove(downloaded)
        await db.update_task_status(task_id, "Failed")
        return

    output_file = new_name

    await safe_edit_message(sts, "💠 Adding photo attachment... ⚡")
    try:
        # Function to add photo attachment (assume it's defined elsewhere)
        add_photo_attachment(downloaded, attachment_path, output_file)
    except Exception as e:
        await safe_edit_message(sts, f"Error adding photo attachment: {e}")
        os.remove(downloaded)
        await db.update_task_status(task_id, "Failed")
        return

    # Retrieve thumbnail from the database
    thumbnail_file_id = await db.get_thumbnail(msg.from_user.id)
    file_thumb = None
    if thumbnail_file_id:
        try:
            file_thumb = await bot.download_media(thumbnail_file_id)
        except Exception:
            pass
    else:
        if hasattr(media, 'thumbs') and media.thumbs:
            try:
                file_thumb = await bot.download_media(media.thumbs[0].file_id)
            except Exception as e:
                print(e)
                file_thumb = None

    filesize = os.path.getsize(output_file)

    await safe_edit_message(sts, "🔼 Uploading modified file... ⚡")
    await db.update_task_status(task_id, "Uploading")
    try:
        # Upload to Google Drive if file size exceeds the limit
        if filesize > FILE_SIZE_LIMIT:
            # Function to upload to Google Drive (assume it's defined elsewhere)
            file_link = await upload_to_google_drive(output_file, os.path.basename(output_file), sts)
            button = [[InlineKeyboardButton("☁️ CloudUrl ☁️", url=f"{file_link}")]]
            await msg.reply_text(
                f"**File successfully changed metadata and uploaded to Google Drive!**\n\n"
                f"**Google Drive Link**: [View File]({file_link})\n\n"
                f"**Uploaded File**: {new_name}\n"
                f"**Request User:** {msg.from_user.mention}\n\n"
                f"**Size**: {humanbytes(filesize)}",
                reply_markup=InlineKeyboardMarkup(button)
            )
        else:
            # Send modified file to user's PM
            await bot.send_document(
                msg.from_user.id,
                document=output_file,
                thumb=file_thumb,
                caption="Here is your file with the photo attached.",
                progress=progress_message,
                progress_args=("🔼 Upload Started... ⚡️", sts, c_time, new_name, username, "Attach Photo")
            )

            # Notify in the group about the upload
            await msg.reply_text(
                f"┏📥 **File Name:** {new_name}\n"
                f"┠💾 **Size:** {humanbytes(filesize)}\n"
                f"┠♻️ **Mode:** Attach Photo\n"
                f"┗🚹 **Request User:** {msg.from_user.mention}\n\n"
                f"❄ **File has been sent to your PM in the bot!**"
            )

        await sts.delete()
        await db.update_task_status(task_id, "Completed")
    except Exception as e:
        await safe_edit_message(sts, f"Error uploading modified file: {e}")
        await db.update_task_status(task_id, "Failed")
    finally:
        os.remove(downloaded)
        os.remove(output_file)
        if file_thumb and os.path.exists(file_thumb):
            os.remove(file_thumb)
        if os.path.exists(attachment_path):
            os.remove(attachment_path)

@Client.on_message(filters.command("changeindexaudio") & filters.chat(GROUP))
async def change_index_audio(bot, msg):
    global CHANGE_INDEX_ENABLED

    if not CHANGE_INDEX_ENABLED:
        return await msg.reply_text("The changeindexaudio feature is currently disabled.")

    user_id = msg.from_user.id
    username = msg.from_user.username or msg.from_user.first_name

    # Add a new task to the user tasks schema
    task_id = await db.add_task(user_id, username, "Change Index Audio", "Queued")
    await bot.send_message(GROUP, f"Change Index Audio Task is added by {username} ({user_id})")

    reply = msg.reply_to_message
    if not reply:
        await db.update_task_status(task_id, "failed")
        return await msg.reply_text("Please reply to a media file with the index command\nFormat: `/changeindexaudio a-3 -n filename.mkv` (Audio)")

    if len(msg.command) < 3:
        await db.update_task_status(task_id, "failed")
        return await msg.reply_text("Please provide the index command with a filename\nFormat: `/changeindexaudio a-3 -n filename.mkv` (Audio)")

    index_cmd = None
    new_name = None

    # Extract index command and output filename from the command
    for i in range(1, len(msg.command)):
        if msg.command[i] == "-n":
            new_name = " ".join(msg.command[i + 1:])  # Join all the parts after the flag
            break

    index_cmd = " ".join(msg.command[1:i])  # Get the index command before the flag

    if not new_name:
        await db.update_task_status(task_id, "failed")
        return await msg.reply_text("Please provide a filename using the `-n` flag.")

    if not index_cmd or not index_cmd.startswith("a-"):
        await db.update_task_status(task_id, "failed")
        return await msg.reply_text("Invalid format. Use `/changeindexaudio a-3 -n filename.mkv` for audio.")

    media = reply.document or reply.audio or reply.video
    if not media:
        await db.update_task_status(task_id, "failed")
        return await msg.reply_text("Please reply to a valid media file (audio, video, or document) with the index command.")

    sts = await msg.reply_text("🚀 Downloading media... ⚡")
    c_time = time.time()
    try:
        # Download the media file
        await db.update_task_status(task_id, "Downloading")
        downloaded = await reply.download(progress=progress_message, progress_args=("🚀 Download Started... ⚡️", sts, c_time, new_name, username, "Change Index Audio"))
    except Exception as e:
        await sts.edit(f"Error downloading media: {e}")
        await db.update_task_status(task_id, "failed")
        return

    # Output file path (temporary file)
    output_file = os.path.splitext(downloaded)[0] + "_indexed" + os.path.splitext(downloaded)[1]

    index_params = index_cmd.split('-')
    stream_type = index_params[0]
    indexes = [int(i) - 1 for i in index_params[1:]]

    # Construct the FFmpeg command to modify indexes
    ffmpeg_cmd = ['ffmpeg', '-i', downloaded, '-map', '0:v']  # Always map video stream

    for idx in indexes:
        ffmpeg_cmd.extend(['-map', f'0:{stream_type}:{idx}'])

    # Copy all subtitle streams if they exist
    ffmpeg_cmd.extend(['-map', '0:s?'])

    ffmpeg_cmd.extend(['-c', 'copy', output_file, '-y'])

    await sts.edit("💠 Changing audio indexing... ⚡")
    process = await asyncio.create_subprocess_exec(*ffmpeg_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        await sts.edit(f"❗ FFmpeg error: {stderr.decode('utf-8')}")
        os.remove(downloaded)
        if os.path.exists(output_file):
            os.remove(output_file)
        await db.update_task_status(task_id, "failed")
        return

    # Thumbnail handling
    thumbnail_file_id = await db.get_thumbnail(msg.from_user.id)

    if thumbnail_file_id:
        try:
            file_thumb = await bot.download_media(thumbnail_file_id)
        except Exception as e:
            file_thumb = None
    else:
        file_thumb = None

    filesize = os.path.getsize(output_file)
    filesize_human = humanbytes(filesize)
    cap = f"{new_name}\n\n🌟 Size: {filesize_human}"

    await sts.edit("💠 Uploading... ⚡")
    c_time = time.time()
    await db.update_task_status(task_id, "Uploading")

    if filesize > FILE_SIZE_LIMIT:
        file_link = await upload_to_google_drive(output_file, new_name, sts)
        button = [[InlineKeyboardButton("☁️ CloudUrl ☁️", url=f"{file_link}")]]
        await msg.reply_text(
            f"**File successfully changed audio index and uploaded to Google Drive!**\n\n"
            f"**Google Drive Link**: [View File]({file_link})\n\n"
            f"**Uploaded File**: {new_name}\n"
            f"**Request User:** {msg.from_user.mention}\n\n"
            f"**Size**: {filesize_human}",
            reply_markup=InlineKeyboardMarkup(button)
        )
    else:
        try:
            await bot.send_document(
                msg.chat.id,
                document=output_file,
                file_name=new_name,  # Apply the new file name here
                thumb=file_thumb,
                caption=cap,
                progress=progress_message,
                progress_args=("💠 Upload Started... ⚡️", sts, c_time, new_name, username, "Change Index Audio")
            )
        except Exception as e:
            await sts.edit(f"Error: {e}")
            await db.update_task_status(task_id, "failed")
            return

    # Clean up downloaded and temporary files
    os.remove(downloaded)
    os.remove(output_file)
    if file_thumb and os.path.exists(file_thumb):
        os.remove(file_thumb)
    await sts.delete()
    await db.update_task_status(task_id, "completed")

@Client.on_message(filters.command("changeindexsub") & filters.chat(GROUP))
async def change_index_subtitle(bot, msg):
    global CHANGE_INDEX_ENABLED

    if not CHANGE_INDEX_ENABLED:
        return await msg.reply_text("The changeindexsub feature is currently disabled.")

    user_id = msg.from_user.id
    username = msg.from_user.username or msg.from_user.first_name

    # Add a new task to the user tasks schema
    task_id = await db.add_task(user_id, username, "Change Index Subtitle", "Queued")
    await bot.send_message(GROUP, f"Change Index Subtitle Task is added by {username} ({user_id})")

    reply = msg.reply_to_message
    if not reply:
        await db.update_task_status(task_id, "failed")
        return await msg.reply_text("Please reply to a media file with the index command\nFormat: `/changeindexsub s-3 -n filename.mkv` (Subtitle)")

    if len(msg.command) < 3:
        await db.update_task_status(task_id, "failed")
        return await msg.reply_text("Please provide the index command with a filename\nFormat: `/changeindexsub s-3 -n filename.mkv` (Subtitle)")

    index_cmd = None
    new_name = None

    # Extract index command and output filename from the command
    for i in range(1, len(msg.command)):
        if msg.command[i] == "-n":
            new_name = " ".join(msg.command[i + 1:])  # Join all the parts after the flag
            break

    index_cmd = " ".join(msg.command[1:i])  # Get the index command before the flag

    if not new_name:
        await db.update_task_status(task_id, "failed")
        return await msg.reply_text("Please provide a filename using the `-n` flag.")

    if not index_cmd or not index_cmd.startswith("s-"):
        await db.update_task_status(task_id, "failed")
        return await msg.reply_text("Invalid format. Use `/changeindexsub s-3 -n filename.mkv` for subtitles.")

    media = reply.document or reply.audio or reply.video
    if not media:
        await db.update_task_status(task_id, "failed")
        return await msg.reply_text("Please reply to a valid media file (audio, video, or document) with the index command.")

    sts = await msg.reply_text("🚀 Downloading media... ⚡")
    c_time = time.time()
    try:
        # Download the media file
        await db.update_task_status(task_id, "Downloading")
        downloaded = await reply.download(progress=progress_message, progress_args=("🚀 Download Started... ⚡️", sts, c_time, new_name, username, "Download"))
    except Exception as e:
        await safe_edit_message(sts, f"Error downloading media: {e}")
        await db.update_task_status(task_id, "failed")
        return

    # Output file path (temporary file)
    output_file = os.path.splitext(downloaded)[0] + "_indexed" + os.path.splitext(downloaded)[1]

    index_params = index_cmd.split('-')
    stream_type = index_params[0]
    indexes = [int(i) - 1 for i in index_params[1:]]

    # Construct the FFmpeg command to modify indexes
    ffmpeg_cmd = ['ffmpeg', '-i', downloaded]

    for idx in indexes:
        ffmpeg_cmd.extend(['-map', f'0:{stream_type}:{idx}'])

    # Copy all audio and video streams
    ffmpeg_cmd.extend(['-map', '0:v?', '-map', '0:a?', '-c', 'copy', output_file, '-y'])

    await safe_edit_message(sts, "💠 Changing subtitle indexing... ⚡")
    process = await asyncio.create_subprocess_exec(*ffmpeg_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        await safe_edit_message(sts, f"❗ FFmpeg error: {stderr.decode('utf-8')}")
        os.remove(downloaded)
        await db.update_task_status(task_id, "failed")
        return

    # Thumbnail handling
    thumbnail_file_id = await db.get_thumbnail(msg.from_user.id)

    if thumbnail_file_id:
        try:
            file_thumb = await bot.download_media(thumbnail_file_id)
        except Exception as e:
            file_thumb = None
    else:
        file_thumb = None

    filesize = os.path.getsize(output_file)
    filesize_human = humanbytes(filesize)
    cap = f"{new_name}\n\n🌟 Size: {filesize_human}"

    await safe_edit_message(sts, "💠 Uploading... ⚡")
    c_time = time.time()
    await db.update_task_status(task_id, "Uploading")

    if filesize > FILE_SIZE_LIMIT:
        file_link = await upload_to_google_drive(output_file, new_name, sts)
        button = [[InlineKeyboardButton("☁️ CloudUrl ☁️", url=f"{file_link}")]]
        await msg.reply_text(
            f"**File successfully changed subtitle index and uploaded to Google Drive!**\n\n"
            f"**Google Drive Link**: [View File]({file_link})\n\n"
            f"**Uploaded File**: {new_name}\n"
            f"**Request User:** {msg.from_user.mention}\n\n"
            f"**Size**: {filesize_human}",
            reply_markup=InlineKeyboardMarkup(button)
        )
    else:
        try:
            await bot.send_document(
                msg.chat.id,
                document=output_file,
                file_name=new_name,  # Apply the new file name here
                thumb=file_thumb,
                caption=cap,
                progress=progress_message,
                progress_args=("💠 Upload Started... ⚡", sts, c_time, new_name, username, "Upload")
            )
        except Exception as e:
            await safe_edit_message(sts, f"Error: {e}")
            await db.update_task_status(task_id, "failed")
            return

    os.remove(downloaded)
    os.remove(output_file)
    if file_thumb and os.path.exists(file_thumb):
        os.remove(file_thumb)
    await sts.delete()
    await db.update_task_status(task_id, "completed")


@Client.on_message(filters.command("merge") & filters.chat(GROUP))
async def start_merge_command(bot, msg: Message):
    global MERGE_ENABLED
    if not MERGE_ENABLED:
        return await msg.reply_text("The merge feature is currently disabled.")

    user_id = msg.from_user.id
    username = msg.from_user.username or msg.from_user.first_name

    # Add a new task to the user tasks schema
    task_id = await db.add_task(user_id, username, "Start Merge", "Queued")
    await bot.send_message(GROUP, f"Merge Task is initiated by {username} ({user_id})")

    merge_state[user_id] = {"files": [], "output_filename": None, "is_merging": False, "task_id": task_id}

    await msg.reply_text("Send up to 10 video/document files one by one. Once done, send `/videomerge filename`.")

@Client.on_message(filters.command("videomerge") & filters.chat(GROUP))
async def start_video_merge_command(bot, msg: Message):
    user_id = msg.from_user.id
    if user_id not in merge_state or not merge_state[user_id]["files"]:
        return await msg.reply_text("No files received for merging. Please send files using /merge command first.")

    task_id = merge_state[user_id]["task_id"]
    output_filename = msg.text.split(' ', 1)[1].strip()  # Extract output filename from command
    merge_state[user_id]["output_filename"] = output_filename
    merge_state[user_id]["is_merging"] = True  # Set the flag to indicate that merging has started

    await db.update_task_status(task_id, "Merging")
    await merge_and_upload(bot, msg)

@Client.on_message(filters.document | filters.video & filters.chat(GROUP))
async def handle_media_files(bot, msg: Message):
    user_id = msg.from_user.id
    if user_id in merge_state:
        if merge_state[user_id].get("is_merging"):
            await msg.reply_text("Merging process has started. No more files can be added.")
            return

        if len(merge_state[user_id]["files"]) < 10:
            merge_state[user_id]["files"].append(msg)
            await msg.reply_text("File received. Send another file or use `/videomerge filename` to start merging.")
        else:
            await msg.reply_text("You have already sent 10 files. Use `/videomerge filename` to start merging.")
            
async def merge_and_upload(bot, msg: Message):
    user_id = msg.from_user.id
    if user_id not in merge_state:
        return await msg.reply_text("No merge state found for this user. Please start the merge process again.")

    files_to_merge = merge_state[user_id]["files"]
    output_filename = merge_state[user_id].get("output_filename", "merged_output.mp4")  # Default output filename
    output_path = f"{output_filename}"

    sts = await msg.reply_text("🚀 Starting merge process...")

    input_file = "input.txt"
    file_paths = []
    task_id = f"merge_{user_id}_{int(time.time())}"  # Generate a task ID for tracking

    try:
        for file_msg in files_to_merge:
            file_path = await download_media(file_msg, sts, task_id)
            file_paths.append(file_path)

        with open(input_file, "w") as f:
            for file_path in file_paths:
                f.write(f"file '{file_path}'\n")

        await sts.edit("💠 Merging videos... ⚡")
        await merge_videos(input_file, output_path)

        filesize = os.path.getsize(output_path)
        filesize_human = humanbytes(filesize)
        cap = f"{output_filename}\n\n🌟 Size: {filesize_human}"

        await sts.edit("💠 Uploading... ⚡")

        # Thumbnail handling
        thumbnail_file_id = await db.get_thumbnail(user_id)
        file_thumb = None
        if thumbnail_file_id:
            try:
                file_thumb = await bot.download_media(thumbnail_file_id)
            except Exception as e:
                print(f"Error downloading thumbnail: {e}")

        # Uploading the merged file
        c_time = time.time()
        if filesize > FILE_SIZE_LIMIT:
            file_link = await upload_to_google_drive(output_path, output_filename, sts)
            button = [[InlineKeyboardButton("☁️ CloudUrl ☁️", url=f"{file_link}")]]
            await msg.reply_text(
                f"File successfully merged and uploaded to Google Drive!\n\n"
                f"Google Drive Link: [View File]({file_link})\n\n"
                f"Uploaded File: {output_filename}\n"
                f"Request User: {msg.from_user.mention}\n\n"
                f"Size: {filesize_human}",
                reply_markup=InlineKeyboardMarkup(button)
            )
        else:
            await bot.send_document(
                user_id,
                document=output_path,
                thumb=file_thumb,
                caption=cap,
                progress=progress_message,
                progress_args=("💠 Upload Started... ⚡", sts, c_time)
            )

            await msg.reply_text(
                f"┏📥 **File Name:** {output_filename}\n"
                f"┠💾 **Size:** {filesize_human}\n"
                f"┠♻️ **Mode:** Merge : Video + Video\n"
                f"┗🚹 **Request User:** {msg.from_user.mention}\n\n"
                f"❄ **File has been sent in Bot PM!**"
            )

    except Exception as e:
        await sts.edit(f"❌ Error: {e}")

    finally:
        # Clean up temporary files
        for file_path in file_paths:
            if os.path.exists(file_path):
                os.remove(file_path)
        if os.path.exists(input_file):
            os.remove(input_file)
        if os.path.exists(output_path):
            os.remove(output_path)
        if file_thumb and os.path.exists(file_thumb):
            os.remove(file_thumb)

        # Clear merge state for the user
        if user_id in merge_state:
            del merge_state[user_id]

        await sts.delete()

@Client.on_message(filters.command("leech") & filters.chat(GROUP))
async def linktofile(bot, msg: Message):
    if len(msg.command) < 2 or not msg.reply_to_message:
        return await msg.reply_text("Please reply to a file, video, audio, or link with the desired filename and extension (e.g., `.mkv`, `.mp4`, `.zip`).")

    reply = msg.reply_to_message
    new_name = msg.text.split(" ", 1)[1]
    
    if not new_name.endswith((".mkv", ".mp4", ".zip")):
        return await msg.reply_text("Please specify a filename ending with .mkv, .mp4, or .zip.")

    media = reply.document or reply.audio or reply.video or reply.text

    sts = await msg.reply_text("🚀 Downloading... ⚡")
    c_time = time.time()

    user_id = msg.from_user.id
    username = msg.from_user.username or msg.from_user.first_name

    task_id = await db.add_task(user_id, username, "Leech Command", "Queued")
    await bot.send_message(GROUP, f"Leech Task is added by {username} ({user_id})")

    if reply.text and ("seedr" in reply.text or "workers" in reply.text):
        await handle_link_download(bot, msg, reply.text, new_name, media, sts, c_time, task_id)
    else:
        if not media:
            return await msg.reply_text("Please reply to a valid file, video, audio, or link with the desired filename and extension (e.g., `.mkv`, `.mp4`, `.zip`).")

        try:
            downloaded = await reply.download(file_name=new_name, progress=progress_message, progress_args=("🚀 Download Started... ⚡️", sts, c_time))
        except RPCError as e:
            await db.update_task_status(task_id, "Failed")
            return await sts.edit(f"Download failed: {e}")

        filesize = humanbytes(os.path.getsize(downloaded))

        if CAPTION:
            try:
                cap = CAPTION.format(file_name=new_name, file_size=filesize)
            except KeyError as e:
                await db.update_task_status(task_id, "Failed")
                return await sts.edit(text=f"Caption error: unexpected keyword ({e})")
        else:
            cap = f"{new_name}\n\n🌟 Size: {filesize}"

        # Thumbnail handling
        thumbnail_file_id = await db.get_thumbnail(msg.from_user.id)
        og_thumbnail = None
        if thumbnail_file_id:
            try:
                og_thumbnail = await bot.download_media(thumbnail_file_id)
            except Exception:
                pass
        else:
            if hasattr(media, 'thumbs') and media.thumbs:
                try:
                    og_thumbnail = await bot.download_media(media.thumbs[0].file_id)
                except Exception:
                    pass

        await sts.edit("💠 Uploading... ⚡")
        c_time = time.time()

        try:
            if os.path.getsize(downloaded) > FILE_SIZE_LIMIT:
                file_link = await upload_to_google_drive(downloaded, new_name, sts)
                await msg.reply_text(f"File uploaded to Google Drive!\n\n📁 **File Name:** {new_name}\n💾 **Size:** {filesize}\n🔗 **Link:** {file_link}")
            else:
                await bot.send_document(
                    msg.chat.id,
                    document=downloaded,
                    thumb=og_thumbnail,
                    caption=cap,
                    progress=progress_message,
                    progress_args=("💠 Upload Started... ⚡", sts, c_time)
                )
            await db.update_task_status(task_id, "Completed")
        except Exception as e:
            await db.update_task_status(task_id, "Failed")
            return await sts.edit(f"Upload failed: {e}")

        try:
            if og_thumbnail:
                os.remove(og_thumbnail)
            os.remove(downloaded)
        except Exception as e:
            print(f"Error deleting files: {e}")

        await sts.delete()

async def handle_link_download(bot, msg: Message, link: str, new_name: str, media, sts, c_time, task_id: int):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as resp:
                if resp.status == 200:
                    with open(new_name, 'wb') as f:
                        f.write(await resp.read())
                else:
                    await db.update_task_status(task_id, "Failed")
                    return await sts.edit(f"Failed to download file from link. Status code: {resp.status}")
    except Exception as e:
        await db.update_task_status(task_id, "Failed")
        return await sts.edit(f"Error during download: {e}")

    if not os.path.exists(new_name):
        await db.update_task_status(task_id, "Failed")
        return await sts.edit("File not found after download. Please check the link and try again.")

    filesize = humanbytes(os.path.getsize(new_name))

    # Thumbnail handling
    thumbnail_file_id = await db.get_thumbnail(msg.from_user.id)
    og_thumbnail = None
    if thumbnail_file_id:
        try:
            og_thumbnail = await bot.download_media(thumbnail_file_id)
        except Exception:
            pass
    else:
        if hasattr(media, 'thumbs') and media.thumbs:
            try:
                og_thumbnail = await bot.download_media(media.thumbs[0].file_id)
            except Exception:
                pass

    await sts.edit("💠 Uploading... ⚡")
    c_time = time.time()

    try:
        if os.path.getsize(new_name) > FILE_SIZE_LIMIT:
            file_link = await upload_to_google_drive(new_name, new_name, sts)
            await msg.reply_text(f"File uploaded to Google Drive!\n\n📁 **File Name:** {new_name}\n💾 **Size:** {filesize}\n🔗 **Link:** {file_link}")
        else:
            await bot.send_document(
                msg.chat.id,
                document=new_name,
                thumb=og_thumbnail,
                caption=f"{new_name}\n\n🌟 Size: {filesize}",
                progress=progress_message,
                progress_args=("💠 Upload Started... ⚡", sts, c_time)
            )
        await db.update_task_status(task_id, "Completed")
    except Exception as e:
        await db.update_task_status(task_id, "Failed")
        return await sts.edit(f"Upload failed: {e}")

    try:
        if og_thumbnail:
            os.remove(og_thumbnail)
        os.remove(new_name)
    except Exception as e:
        print(f"Error deleting files: {e}")

    await sts.delete()      
        

async def safe_edit_message(message, new_text):
    try:
        if message.text != new_text:
            await message.edit(new_text)
    except Exception as e:
        print(f"Failed to edit message: {e}")

@Client.on_message(filters.command("removetags") & filters.chat(GROUP))
async def remove_tags(bot, msg):
    global REMOVETAGS_ENABLED
    if not REMOVETAGS_ENABLED:
        return await msg.reply_text("The removetags feature is currently disabled.")

    reply = msg.reply_to_message
    if not reply:
        return await msg.reply_text("Please reply to a media file with the removetags command.")

    media = reply.document or reply.audio or reply.video
    if not media:
        return await msg.reply_text("Please reply to a valid media file (audio, video, or document) with the removetags command.")

    command_text = " ".join(msg.command[1:]).strip()
    new_name = None

    if "-n" in command_text:
        try:
            new_name = command_text.split('-n')[1].strip()
        except IndexError:
            return await msg.reply_text("Please provide a valid filename with the -n option (e.g., `-n new_filename.mkv`).")

        valid_extensions = ('.mkv', '.mp4', '.avi')
        if not any(new_name.lower().endswith(ext) for ext in valid_extensions):
            return await msg.reply_text("The new filename must include a valid extension (e.g., `.mkv`, `.mp4`, `.avi`).")

    sts = await msg.reply_text("🚀 Downloading media... ⚡")
    c_time = time.time()
    
    user_id = msg.from_user.id
    username = msg.from_user.username or msg.from_user.first_name

    task_id = await db.add_task(user_id, username, "Remove Tags", "Queued")
    await bot.send_message(GROUP, f"Remove Tags Task is added by {username} ({user_id})")
    
    try:
        downloaded = await reply.download(progress=progress_message, progress_args=("🚀 Download Started... ⚡️", sts, c_time))
    except Exception as e:
        await safe_edit_message(sts, f"Error downloading media: {e}")
        await db.update_task_status(task_id, "Failed")
        return

    cleaned_file = new_name if new_name else "cleaned_" + os.path.basename(downloaded)

    await safe_edit_message(sts, "💠 Removing all tags... ⚡")
    try:
        remove_all_tags(downloaded, cleaned_file)
    except Exception as e:
        await safe_edit_message(sts, f"Error removing all tags: {e}")
        os.remove(downloaded)
        await db.update_task_status(task_id, "Failed")
        return

    file_thumb = None
    thumbnail_id = await db.get_thumbnail(msg.from_user.id)
    if thumbnail_id:
        try:
            file_thumb = await bot.download_media(thumbnail_id, file_name=f"thumbnail_{msg.from_user.id}.jpg")
        except Exception as e:
            print(f"Error downloading thumbnail: {e}")

    await safe_edit_message(sts, "🔼 Uploading cleaned file... ⚡")
    try:
        filesize = os.path.getsize(cleaned_file)
        if filesize > FILE_SIZE_LIMIT:
            file_link = await upload_to_google_drive(cleaned_file, new_name or os.path.basename(cleaned_file), sts)
            button = [[InlineKeyboardButton("☁️ CloudUrl ☁️", url=f"{file_link}")]]
            await msg.reply_text(
                f"File successfully removed tags and uploaded to Google Drive!\n\n"
                f"Google Drive Link: [View File]({file_link})\n\n"
                f"Uploaded File: {new_name or os.path.basename(cleaned_file)}\n"
                f"Request User: {msg.from_user.mention}\n\n"
                f"Size: {humanbytes(filesize)}",
                reply_markup=InlineKeyboardMarkup(button)
            )
        else:
            await bot.send_document(
                msg.from_user.id,
                cleaned_file,
                thumb=file_thumb,
                caption="Here is your file with all tags removed.",
                progress=progress_message,
                progress_args=("🔼 Upload Started... ⚡️", sts, c_time)
            )

            await msg.reply_text(
                f"┏📥 **File Name:** {new_name or os.path.basename(cleaned_file)}\n"
                f"┠💾 **Size:** {humanbytes(filesize)}\n"
                f"┠♻️ **Mode:** Remove Tags\n"
                f"┗🚹 **Request User:** {msg.from_user.mention}\n\n"
                f"❄ **File has been sent to your PM in the bot!**"
            )

        await sts.delete()
        await db.update_task_status(task_id, "Completed")
    except Exception as e:
        await safe_edit_message(sts, f"Error uploading cleaned file: {e}")
        await db.update_task_status(task_id, "Failed")
    finally:
        os.remove(downloaded)
        os.remove(cleaned_file)
        if file_thumb and os.path.exists(file_thumb):
            os.remove(file_thumb)

    if new_name:
        await db.save_new_name(msg.from_user.id, new_name)


#Screenshots Command
@Client.on_message(filters.command("screenshots") & filters.chat(GROUP))
async def screenshots_command(client, message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name

    # Fetch user settings for screenshots count
    num_screenshots = await db.get_screenshots_count(user_id)
    if not num_screenshots:
        num_screenshots = 5  # Default to 5 if not set

    if not message.reply_to_message:
        return await message.reply_text("Please reply to a valid video file or document.")

    media = message.reply_to_message.video or message.reply_to_message.document
    if not media:
        return await message.reply_text("Please reply to a valid video file.")

    sts = await message.reply_text("🚀 Downloading media... ⚡")
    
    # Add task to the database
    task_id = await db.add_task(user_id, username, "Generate Screenshots", "Queued")
    await client.send_message(GROUP, f"Generate Screenshots Task is added by {username} ({user_id})")

    try:
        input_path = await client.download_media(media)
    except Exception as e:
        await sts.edit(f"Error downloading media: {e}")
        await db.update_task_status(task_id, "Failed")
        return

    if not os.path.exists(input_path):
        await sts.edit("Error: The downloaded file does not exist.")
        await db.update_task_status(task_id, "Failed")
        return

    try:
        await sts.edit("🚀 Reading video duration... ⚡")
        command = ['ffprobe', '-i', input_path, '-show_entries', 'format=duration', '-v', 'quiet', '-of', 'csv=p=0']
        duration_output = subprocess.check_output(command, stderr=subprocess.STDOUT)
        duration = float(duration_output.decode('utf-8').strip())
    except subprocess.CalledProcessError as e:
        await sts.edit(f"Error reading video duration: {e.output.decode('utf-8')}")
        os.remove(input_path)
        await db.update_task_status(task_id, "Failed")
        return
    except ValueError:
        await sts.edit("Error reading video duration: Unable to convert duration to float.")
        os.remove(input_path)
        await db.update_task_status(task_id, "Failed")
        return

    interval = duration / num_screenshots

    await sts.edit(f"🚀 Generating {num_screenshots} screenshots... ⚡")
    screenshot_paths = []
    for i in range(num_screenshots):
        time_position = interval * i
        screenshot_path = f"screenshot_{user_id}_{i}.jpg"

        command = ['ffmpeg', '-ss', str(time_position), '-i', input_path, '-vframes', '1', '-y', screenshot_path]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            await sts.edit(f"Error generating screenshot {i+1}: {stderr.decode('utf-8')}")
            for path in screenshot_paths:
                os.remove(path)
            os.remove(input_path)
            await db.update_task_status(task_id, "Failed")
            return

        screenshot_paths.append(screenshot_path)

        try:
            await client.send_photo(chat_id=user_id, photo=screenshot_path)
        except Exception as e:
            await sts.edit(f"Error uploading screenshot {i+1}: {e}")
            os.remove(screenshot_path)

        os.remove(screenshot_path)

    await db.save_screenshot_paths(user_id, screenshot_paths)

    os.remove(input_path)

    try:
        await message.reply_text("📸 Screenshots have been sent to your PM.")
    except Exception as e:
        print(f"Failed to send notification: {e}")

    await db.delete_screenshot_paths(user_id)
    await db.update_task_status(task_id, "Completed")
    await sts.delete()

@Client.on_message(filters.command("samplevideo") & filters.chat(GROUP))
async def sample_video(bot, msg):
    user_id = msg.from_user.id
    username = msg.from_user.username or msg.from_user.first_name

    # Fetch user settings
    sample_video_duration = await db.get_sample_video_duration(user_id)

    if sample_video_duration is None:
        return await msg.reply_text("Please set a valid sample video duration using /usersettings.")

    if not msg.reply_to_message:
        return await msg.reply_text("Please reply to a valid video file or document.")

    media = msg.reply_to_message.video or msg.reply_to_message.document
    if not media:
        return await msg.reply_text("Please reply to a valid video file or document.")

    sts = await msg.reply_text("🚀 Downloading media... ⚡")

    # Add task to the database
    task_id = await db.add_task(user_id, username, "Generate Sample Video", "Queued")
    await bot.send_message(GROUP, f"Generate Sample Video Task is added by {username} ({user_id})")

    c_time = time.time()
    try:
        input_path = await bot.download_media(media, progress=progress_message, progress_args=("🚀 Downloading media... ⚡️", sts, c_time))
    except Exception as e:
        await sts.edit(f"Error downloading media: {e}")
        await db.update_task_status(task_id, "Failed")
        return

    output_file = f"sample_video_{sample_video_duration}s.mp4"

    await sts.edit("🚀 Processing sample video... ⚡")
    try:
        generate_sample_video(input_path, sample_video_duration, output_file)
    except Exception as e:
        await sts.edit(f"Error generating sample video: {e}")
        os.remove(input_path)
        await db.update_task_status(task_id, "Failed")
        return

    filesize = os.path.getsize(output_file)
    filesize_human = humanbytes(filesize)
    cap = f"{os.path.basename(output_file)}\n\n🌟 Size: {filesize_human}"

    await sts.edit("💠 Uploading sample video to your PM... ⚡")
    c_time = time.time()
    try:
        await bot.send_document(
            user_id, 
            document=output_file, 
            caption=cap, 
            progress=progress_message, 
            progress_args=("💠 Upload Started... ⚡️", sts, c_time)
        )
        # Save sample video settings to database
        await db.save_sample_video_settings(user_id, sample_video_duration, "Not set")

        # Send notification about the file upload
        await msg.reply_text(f"File Sample Video has been uploaded to your PM. Check your PM of the bot ✅ .")
        await db.update_task_status(task_id, "Completed")

    except Exception as e:
        await sts.edit(f"Error uploading sample video: {e}")
        await db.update_task_status(task_id, "Failed")
        return

    os.remove(input_path)
    os.remove(output_file)
    await sts.delete()

 # Define restart_app command
@Client.on_message(filters.command("restart") & filters.chat(AUTH_USERS))
async def restart_app(bot, msg):
    if not f'{msg.from_user.id}' == f'{int(AUTH_USERS)}':
        return await msg.reply_text("Only authorized user can restart!")

    result = await heroku_restart()
    if result is None:
        return await msg.reply_text("You have not filled `HEROKU_API` and `HEROKU_APP_NAME` vars.")
    elif result is False:
        return await msg.reply_text("An error occurred!")
    elif result is True:
        return await msg.reply_text("Restarting app, wait for a minute.")
        

# Command to unzip a zip file
@Client.on_message(filters.command("unzip") & filters.chat(GROUP))
async def unzip(bot, msg):
    user_id = msg.from_user.id
    username = msg.from_user.username or msg.from_user.first_name

    if not msg.reply_to_message:
        return await msg.reply_text("Please reply to a zip file to unzip.")

    media = msg.reply_to_message.document
    if not media or not media.file_name.endswith('.zip'):
        return await msg.reply_text("Please reply to a valid zip file.")

    # Add task to the database
    task_id = await db.add_task(user_id, username, "Unzip File", "Queued")
    await bot.send_message(GROUP, f"Unzip File Task is added by {username} ({user_id})")

    sts = await msg.reply_text("🚀 Downloading file... ⚡")
    c_time = time.time()
    input_path = await bot.download_media(media, progress=progress_message, progress_args=("🚀 Downloading file... ⚡️", sts, c_time))

    if not os.path.exists(input_path):
        await sts.edit(f"Error: The downloaded file does not exist.")
        await db.update_task_status(task_id, "Failed")
        return

    extract_path = os.path.join("extracted")
    os.makedirs(extract_path, exist_ok=True)

    await sts.edit("🚀 Unzipping file... ⚡")
    try:
        extracted_files = unzip_file(input_path, extract_path)
    except Exception as e:
        await sts.edit(f"Error unzipping file: {e}")
        await db.update_task_status(task_id, "Failed")
        os.remove(input_path)
        shutil.rmtree(extract_path)
        return

    if extracted_files:
        await sts.edit(f"✅ File unzipped successfully. Uploading extracted files... ⚡")
        try:
            await upload_files(bot, msg.chat.id, extract_path)
            await sts.edit(f"✅ All extracted files uploaded successfully.")
            # Save extracted files to database
            await db.save_extracted_files(user_id, extracted_files)
            await db.update_task_status(task_id, "Completed")
        except Exception as e:
            await sts.edit(f"Error uploading extracted files: {e}")
            await db.update_task_status(task_id, "Failed")
    else:
        await sts.edit(f"❌ Failed to unzip file.")
        await db.update_task_status(task_id, "Failed")

    os.remove(input_path)
    shutil.rmtree(extract_path)


@Client.on_message(filters.command("gofile") & filters.chat(GROUP))
async def gofile_upload(bot, msg: Message):
    user_id = msg.from_user.id
    
    # Retrieve the user's Gofile API key from the database
    gofile_api_key = await db.get_gofile_api_key(user_id)

    if not gofile_api_key:
        return await msg.reply_text("Gofile API key is not set. Use /gofilesetup {your_api_key} to set it.")

    reply = msg.reply_to_message
    if not reply or not reply.document and not reply.video:
        return await msg.reply_text("Please reply to a file or video to upload to Gofile.")

    media = reply.document or reply.video
    new_name = None

    # Check if a new name is provided
    args = msg.text.split(" ", 1)
    if len(args) == 2:
        new_name = args[1]
        await db.save_new_name(user_id, new_name)  # Save new name to database

    # Use new name if available, otherwise use the file name
    file_name = new_name or media.file_name

    # Add task to the database
    username = msg.from_user.username or msg.from_user.first_name
    task_id = await db.add_task(user_id, username, "Upload to Gofile", "Queued")
    await bot.send_message(GROUP, f"Upload to Gofile task added by {username} ({user_id})")

    sts = await msg.reply_text("🚀 Uploading to Gofile...")
    c_time = time.time()
    
    downloaded_file = None

    try:
        async with aiohttp.ClientSession() as session:
            # Get available servers
            async with session.get("https://api.gofile.io/servers") as resp:
                if resp.status != 200:
                    await sts.edit(f"Failed to get servers. Status code: {resp.status}")
                    await db.update_task_status(task_id, "Failed")
                    return

                data = await resp.json()
                servers = data.get("data", {}).get("servers", [])
                if not servers:
                    await sts.edit("No servers available.")
                    await db.update_task_status(task_id, "Failed")
                    return
                
                server_name = servers[0].get("name")  # Use the server name
                if not server_name:
                    await sts.edit("Server name is missing.")
                    await db.update_task_status(task_id, "Failed")
                    return
                
                upload_url = f"https://{server_name}.gofile.io/contents/uploadfile"

            # Download the media file
            downloaded_file = await bot.download_media(
                media,
                file_name=file_name,  # Use new or original filename directly
                progress=progress_message,
                progress_args=("🚀 Download Started...", sts, c_time)
            )

            # Upload the file to Gofile
            with open(downloaded_file, "rb") as file:
                form_data = aiohttp.FormData()
                form_data.add_field("file", file, filename=file_name)
                headers = {"Authorization": f"Bearer {gofile_api_key}"} if gofile_api_key else {}

                async with session.post(
                    upload_url,
                    headers=headers,
                    data=form_data
                ) as resp:
                    if resp.status != 200:
                        await sts.edit(f"Upload failed: Status code {resp.status}")
                        await db.update_task_status(task_id, "Failed")
                        return

                    response = await resp.json()
                    if response["status"] == "ok":
                        download_url = response["data"]["downloadPage"]
                        await sts.edit(f"Upload successful!\nDownload link: {download_url}")
                        await db.update_task_status(task_id, "Completed")
                    else:
                        await sts.edit(f"Upload failed: {response['message']}")
                        await db.update_task_status(task_id, "Failed")

    except Exception as e:
        await sts.edit(f"Error during upload: {e}")
        await db.update_task_status(task_id, "Failed")

    finally:
        try:
            if downloaded_file and os.path.exists(downloaded_file):
                os.remove(downloaded_file)
        except Exception as e:
            print(f"Error deleting file: {e}")



@Client.on_message(filters.command("clone") & filters.chat(GROUP))
async def clone_file(bot, msg: Message):
    user_id = msg.from_user.id

    # Retrieve the user's Google Drive folder ID from database
    gdrive_folder_id = await db.get_gdrive_folder_id(user_id)

    if not gdrive_folder_id:
        return await msg.reply_text("Google Drive folder ID is not set. Please use the /gdriveid command to set it.")

    if len(msg.command) < 2:
        return await msg.reply_text("Please specify the Google Drive file URL.")

    src_url = msg.text.split(" ", 1)[1]
    src_id = extract_id_from_url(src_url)

    if not src_id:
        return await msg.reply_text("Invalid Google Drive URL. Please provide a valid file URL.")

    sts = await msg.reply_text("Starting cloning process...")

    try:
        copied_file_info = await copy_file(src_id, gdrive_folder_id)
        if copied_file_info:
            file_link = f"https://drive.google.com/file/d/{copied_file_info['id']}/view"
            button = [
                [InlineKeyboardButton("☁️ View File ☁️", url=file_link)]
            ]
            if copied_file_info['status'] == 'existing':
                await sts.edit(
                    f"File Already Exists 📂 : {copied_file_info['name']}\n[View File]({file_link})",
                    reply_markup=InlineKeyboardMarkup(button)
                )
            else:
                await sts.edit(
                    f"File Cloned Successfully ✅: {copied_file_info['name']}\n[View File]({file_link})",
                    reply_markup=InlineKeyboardMarkup(button)
                )
        else:
            await sts.edit("Failed to clone the file.")
    except Exception as e:
        await sts.edit(f"Error: {e}")

@Client.on_message(filters.command("extractaudios") & filters.chat(GROUP))
async def extract_audios(bot, msg):
    global EXTRACT_ENABLED
    
    if not EXTRACT_ENABLED:
        return await msg.reply_text("The Extract Audio feature is currently disabled.")

    reply = msg.reply_to_message
    if not reply:
        return await msg.reply_text("Please reply to a media file with the extractaudios command.")

    media = reply.document or reply.audio or reply.video
    if not media:
        return await msg.reply_text("Please reply to a valid media file (audio, video, or document) with the extractaudios command.")

    user_id = msg.from_user.id
    username = msg.from_user.username or msg.from_user.first_name
    
    # Add task to the database
    task_id = await db.add_task(user_id, username, "Extracting", "Queued")
    await bot.send_message(GROUP, f"Extracting audio streams task added by {username} ({user_id})")    

    sts = await msg.reply_text("🚀 Downloading media... ⚡")
    c_time = time.time()
    try:
        downloaded = await reply.download(progress=progress_message, progress_args=("🚀 Download Started... ⚡️", sts, c_time))
    except Exception as e:
        await safe_edit_message(sts, f"Error downloading media: {e}")
        await db.update_task_status(task_id, status="Failed", error_message=str(e))
        return

    await safe_edit_message(sts, "🎵 Extracting audio streams... ⚡")
    try:
        extracted_files = extract_audios_from_file(downloaded)
        if not extracted_files:
            raise Exception("No audio streams found or extraction failed.")
    except Exception as e:
        await safe_edit_message(sts, f"Error extracting audio streams: {e}")
        os.remove(downloaded)
        await db.update_task_status(task_id, status="Failed", error_message=str(e))
        return

    await safe_edit_message(sts, "🔼 Uploading extracted audio files... ⚡")
    try:
        for file, metadata in extracted_files:
            new_name = metadata.get('tags', {}).get('title', os.path.basename(file))  # Use title if available, otherwise use file name
            language = metadata.get('tags', {}).get('language', 'Unknown')
            caption = f"[{language}] Extracted audio file."
            await bot.send_document(
                msg.from_user.id,
                file,
                caption=caption[:1024],  # Ensure caption does not exceed 1024 characters
                progress=progress_message,
                progress_args=("🔼 Upload Started... ⚡️", sts, c_time)
            )
                
        await msg.reply_text("Audio streams extracted and sent to your PM in the bot!")

        # Update task to completed
        await db.update_task_status(task_id, status="Completed")
        await sts.delete()
    except Exception as e:
        await safe_edit_message(sts, f"Error uploading extracted audio files: {e}")
        await db.update_task_status(task_id, status="Failed", error_message=str(e))
    finally:
        os.remove(downloaded)
        for file, _ in extracted_files:
            os.remove(file)




# Extract subtitles command
@Client.on_message(filters.command("extractsubtitles") & filters.chat(GROUP))
async def extract_subtitles(bot, msg):
    global EXTRACT_ENABLED
    
    if not EXTRACT_ENABLED:
        return await msg.reply_text("The Extract Subtitles feature is currently disabled.")

    reply = msg.reply_to_message
    if not reply:
        return await msg.reply_text("Please reply to a media file with the extractsubtitles command.")

    media = reply.document or reply.audio or reply.video
    if not media:
        return await msg.reply_text("Please reply to a valid media file (audio, video, or document) with the extractsubtitles command.")

    user_id = msg.from_user.id
    username = msg.from_user.username or msg.from_user.first_name
   
    # Add task to the database
    task_id = await db.add_task(user_id, username, "Extracting", "Queued")
    await bot.send_message(GROUP, "Extracting subtitles task added by {username} ({user_id})")    
    
    sts = await msg.reply_text("🚀 Downloading media... ⚡")
    c_time = time.time()
    try:
        downloaded = await reply.download(progress=progress_message, progress_args=("🚀 Download Started... ⚡️", sts, c_time))
    except Exception as e:
        await safe_edit_message(sts, f"Error downloading media: {e}")
        await db.update_task_status(task_id, status="Failed", error_message=str(e))
        return

    await safe_edit_message(sts, "🎥 Extracting subtitle streams... ⚡")
    try:
        extracted_files = extract_subtitles_from_file(downloaded)
        if not extracted_files:
            raise Exception("No subtitle streams found or extraction failed.")
    except Exception as e:
        await safe_edit_message(sts, f"Error extracting subtitle streams: {e}")
        os.remove(downloaded)
        await db.update_task_status(task_id, status="Failed", error_message=str(e))
        return

    await safe_edit_message(sts, "🔼 Uploading extracted subtitle files... ⚡")
    try:
        for file, metadata in extracted_files:
            language = metadata.get('tags', {}).get('language', 'Unknown')
            caption = f"[{language}] Here is an extracted subtitle file."
            await bot.send_document(
                msg.from_user.id,
                file,
                caption=caption[:1024],  # Ensure caption does not exceed 1024 characters
                progress=progress_message,
                progress_args=("🔼 Upload Started... ⚡️", sts, c_time)
            )

        await msg.reply_text(
            "Subtitle streams extracted and sent to your PM in the bot!"
        )

        # Update task to completed
        await db.update_task_status(task_id, status="Completed")
        await sts.delete()
    except Exception as e:
        await safe_edit_message(sts, f"Error uploading extracted subtitle files: {e}")
        await db.update_task_status(task_id, status="Failed", error_message=str(e))
    finally:
        os.remove(downloaded)
        for file, _ in extracted_files:
            os.remove(file)



##extract video command
@Client.on_message(filters.command("extractvideo") & filters.chat(GROUP))
async def extract_video(bot, msg: Message):
    global EXTRACT_ENABLED
    
    if not EXTRACT_ENABLED:
        return await msg.reply_text("The extract feature is currently disabled.")

    reply = msg.reply_to_message
    if not reply:
        return await msg.reply_text("Please reply to a media file (video or document) with the extractvideo command.")

    media = reply.video or reply.document
    if not media:
        return await msg.reply_text("Please reply to a valid video or document file with the extractvideo command.")

    user_id = msg.from_user.id
    username = msg.from_user.username or msg.from_user.first_name
    
    # Add task to the database
    task_id = await db.add_task(user_id, username, "Extracting", "Queued")
    await bot.send_message(GROUP, f"Extracting video task added by {username} ({user_id})")    
        
    sts = await msg.reply_text("🚀 Downloading media... ⚡")
    c_time = time.time()
    try:
        downloaded = await reply.download(progress=progress_message, progress_args=("🚀 Download Started... ⚡️", sts, c_time))
    except Exception as e:
        await safe_edit_message(sts, f"Error downloading media: {e}")
        await db.update_task_status(task_id, status="Failed", error_message=str(e))
        return

    await safe_edit_message(sts, "🎥 Extracting video stream... ⚡")
    try:
        extracted_file = extract_video_from_file(downloaded)
        if not extracted_file:
            raise Exception("No video stream found or extraction failed.")
    except Exception as e:
        await safe_edit_message(sts, f"Error extracting video stream: {e}")
        os.remove(downloaded)
        await db.update_task_status(task_id, status="Failed", error_message=str(e))
        return

    await safe_edit_message(sts, "🔼 Uploading extracted video... ⚡")
    try:
        output_extension = os.path.splitext(extracted_file)[1]
        output_file = os.path.join(os.path.dirname(downloaded), f"Extracted_By_Sunrises_24_Video{output_extension}")
        os.rename(extracted_file, output_file)

        await bot.send_document(
            msg.from_user.id,
            output_file,
            progress=progress_message,
            progress_args=("🔼 Upload Started... ⚡️", sts, c_time)
        )
        await msg.reply_text(
            "Video stream extracted and sent to your PM in the bot!"
        )

        # Update task to completed
        await db.update_task_status(task_id, status="Completed")
        await sts.delete()
    except Exception as e:
        await safe_edit_message(sts, f"Error uploading extracted video: {e}")
        await db.update_task_status(task_id, status="Failed", error_message=str(e))
    finally:
        os.remove(downloaded)
        if os.path.exists(output_file):
            os.remove(output_file)


# Command handler for /list
@Client.on_message(filters.command("list") & filters.chat(GROUP))
async def list_files(bot, msg: Message):
    user_id = msg.from_user.id

    # Retrieve the user's Google Drive folder ID from database
    gdrive_folder_id = await db.get_gdrive_folder_id(user_id)

    if not gdrive_folder_id:
        return await msg.reply_text("Google Drive folder ID is not set. Please use the /gdriveid command to set it.")

    sts = await msg.reply_text("Fetching File List...🔎")

    try:
        files = get_files_in_folder(gdrive_folder_id)
        if not files:
            return await sts.edit("No files found in the specified folder.")

        # Categorize files
        file_types = {'Images': [], 'Movies': [], 'Audios': [], 'Archives': [], 'Others': []}
        for file in files:
            mime_type = file['mimeType']
            file_name = file['name'].lower()
            if mime_type.startswith('image/'):
                file_types['Images'].append(file)
            elif mime_type.startswith('video/') or file_name.endswith(('.mkv', '.mp4')):
                file_types['Movies'].append(file)
            elif mime_type.startswith('audio/') or file_name.endswith(('.aac', '.eac3', '.mp3', '.opus', '.eac')):
                file_types['Audios'].append(file)
            elif file_name.endswith(('.zip', '.rar')):
                file_types['Archives'].append(file)
            else:
                file_types['Others'].append(file)

        # Create inline buttons for each category with emojis
        buttons = []
        for category, items in file_types.items():
            if items:
                if category == 'Images':
                    emoji = '🖼️'
                elif category == 'Movies':
                    emoji = '🎞️'
                elif category == 'Audios':
                    emoji = '🔊'
                elif category == 'Archives':
                    emoji = '📦'
                else:
                    emoji = '📁'

                buttons.append([InlineKeyboardButton(f"{emoji} {category}", callback_data=f"{category}")])
                for file in sorted(items, key=lambda x: x['name']):
                    file_link = f"https://drive.google.com/file/d/{file['id']}/view"
                    buttons.append([InlineKeyboardButton(file['name'], url=file_link)])

        await sts.edit(
            "Files In The Specified Folder 📁:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except HttpError as error:
        await sts.edit(f"An error occurred: {error}")
    except Exception as e:
        await sts.edit(f"Error: {e}")

#cleam command
@Client.on_message(filters.command("clean") & filters.chat(GROUP))
async def clean_files(bot, msg: Message):
    user_id = msg.from_user.id

    # Retrieve the user's Google Drive folder ID from database
    gdrive_folder_id = await db.get_gdrive_folder_id(user_id)

    if not gdrive_folder_id:
        return await msg.reply_text("Google Drive folder ID is not set. Please use the /gdriveid command to set it.")

    try:
        # Check if the command is followed by a file name or a direct link
        command_parts = msg.text.split(maxsplit=1)
        if len(command_parts) < 2:
            return await msg.reply_text("Please provide a file name or direct link to delete.")

        query_or_link = command_parts[1].strip()

        # If the query_or_link starts with 'http', treat it as a direct link
        if query_or_link.startswith("http"):
            # Extract file ID from the direct link
            file_id = extract_id_from_url(query_or_link)
            if not file_id:
                return await msg.reply_text("Invalid Google Drive file link. Please provide a valid direct link.")

            # Delete the file by its ID
            drive_service.files().delete(fileId=file_id).execute()
            await msg.reply_text(f"Deleted File with ID '{file_id}' Successfully ✅.")

        else:
            # Treat it as a file name and delete files by name in the specified folder
            file_name = query_or_link

            # Define query to find files by name in the specified folder
            query = f"'{gdrive_folder_id}' in parents and trashed=false and name='{file_name}'"

            # Execute the query to find matching files
            response = drive_service.files().list(q=query, fields='files(id, name)').execute()
            files = response.get('files', [])

            if not files:
                return await msg.reply_text(f"No files found with the name '{file_name}' in the specified folder.")

            # Delete each found file
            for file in files:
                drive_service.files().delete(fileId=file['id']).execute()
                await msg.reply_text(f"Deleted File '{file['name']}' Successfully ✅.")

    except HttpError as error:
        await msg.reply_text(f"An error occurred: {error}")
    except Exception as e:
        await msg.reply_text(f"An unexpected error occurred: {e}")



# Downloading Progress Hook for YouTube in logs work process
async def progress_hook(status_message):
    async def hook(d):
        if d['status'] == 'downloading':
            current_progress = d.get('_percent_str', '0%')
            current_size = humanbytes(d.get('total_bytes', 0))
            await safe_edit_message(status_message, f"🚀 Downloading... ⚡\nProgress: {current_progress}\nSize: {current_size}")
        elif d['status'] == 'finished':
            await safe_edit_message(status_message, "Download finished. 🚀")
    return hook
    
@Client.on_message(filters.command("ytdlleech") & filters.chat(GROUP))
async def ytdlleech_handler(client: Client, msg: Message):
    if len(msg.command) < 2:
        return await msg.reply_text("Please provide a YouTube link.")

    command_text = msg.text.split(" ", 1)[1]
    url = command_text.strip()

    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'force_generic_extractor': True,
        'noplaylist': True,
        'merge_output_format': 'mkv'
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            formats = info_dict.get('formats', [])

            buttons = [
                InlineKeyboardButton(
                    f"{f.get('format_note', 'Unknown')} - {humanbytes(f.get('filesize'))}",
                    callback_data=f"{f['format_id']}"
                )
                for f in formats if f.get('filesize') is not None
            ]
            buttons = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
            await msg.reply_text("Choose quality:", reply_markup=InlineKeyboardMarkup(buttons))

            file_data = {
                'title': info_dict['title'],
                'thumbnail': info_dict.get('thumbnail')  # No default thumbnail path
            }
            await db.save_file_data(msg.from_user.id, file_data)

            user_quality_selection = {
                'url': url,
                'title': info_dict['title'],
                'thumbnail': info_dict.get('thumbnail'),
                'formats': formats
            }
            await db.save_user_quality_selection(msg.from_user.id, user_quality_selection)

    except Exception as e:
        await msg.reply_text(f"Error: {e}")

@Client.on_callback_query(filters.regex(r"^\d+$"))
async def callback_query_handler(client: Client, query):
    user_id = query.from_user.id
    format_id = query.data
    username = query.from_user.username or msg.from_user.first_name    

    selection = await db.get_user_quality_selection(user_id)
    if not selection:
        return await query.answer("No download in progress.")

    url = selection['url']
    video_title = selection['title']
    formats = selection['formats']

    selected_format = next((f for f in formats if f['format_id'] == format_id), None)
    if not selected_format:
        return await query.answer("Invalid format selection.")

    quality = selected_format.get('format_note', 'Unknown')
    file_size = selected_format.get('filesize', 0)
    new_name = f"{video_title} - {quality}.mkv"  # Updated variable name

    # Add task to the database
    task_id = await db.add_task(user_id, username, f"Downloading video in {quality}", "Queued")
    await bot.send_message(GROUP, f"Downloading video in {quality} task added by {username} ({user_id})")             

    sts = await query.message.reply_text(f"🚀 Downloading {quality} - {humanbytes(file_size)}... ⚡")

    ydl_opts = {
        'format': f'{format_id}+bestaudio/best',
        'outtmpl': new_name,  # Updated variable name
        'quiet': True,
        'noplaylist': True,
        'progress_hooks': [await progress_hook(status_message=sts)],
        'merge_output_format': 'mkv'
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if not os.path.exists(new_name):  # Updated variable name
            return await safe_edit_message(sts, "Error: Download failed. File not found.")
        
        # No thumbnail downloading
        file_thumb = None
        
        if file_size >= FILE_SIZE_LIMIT:
            await safe_edit_message(sts, "💠 Uploading to Google Drive... ⚡")
            file_link = await upload_to_google_drive(new_name, new_name, sts)  # Updated variable name
            button = [[InlineKeyboardButton("☁️ CloudUrl ☁️", url=f"{file_link}")]]
            await query.message.reply_text(
                f"**File successfully uploaded to Google Drive!**\n\n"
                f"**Google Drive Link**: [View File]({file_link})\n\n"
                f"**Uploaded File**: {new_name}\n"  # Updated variable name
                f"**Size**: {humanbytes(file_size)}",
                reply_markup=InlineKeyboardMarkup(button)
            )
        else:
            await safe_edit_message(sts, "💠 Uploading to Telegram... ⚡")
            caption = f"**Uploaded Document 📄**: {new_name}\n\n🌟 Size: {humanbytes(file_size)}"  # Updated variable name
            
            try:
                with open(new_name, 'rb') as file:  # Updated variable name
                    await query.message.reply_document(
                        document=file,
                        caption=caption,
                        thumb=file_thumb,  # No thumbnail
                        progress=progress_message,
                        progress_args=("💠 Upload Started... ⚡", sts, time.time())
                    )
            except Exception as e:
                await safe_edit_message(sts, f"Error uploading file: {e}")
                return

        # Update task to completed
        await db.update_task(task_id, status="Completed")

    except Exception as e:
        await safe_edit_message(sts, f"Error: {e}")
        await db.update_task(task_id, status="Failed", error_message=str(e))

    finally:
        if os.path.exists(new_name):  # Updated variable name
            os.remove(new_name)  # Updated variable name
        await sts.delete()
        await query.message.delete()



@Client.on_message(filters.command("mediainfo") & filters.chat(GROUP))
async def mediainfo_handler(client: Client, message: Message):
    if not message.reply_to_message or (not message.reply_to_message.document and not message.reply_to_message.video):
        await message.reply_text("Please reply to a document or video to get media info.")
        return

    reply = message.reply_to_message
    media = reply.document or reply.video

    # Send an acknowledgment message immediately
    processing_message = await message.reply_text("Getting MediaInfo...")

    try:
        # Download the media file to a local location
        if media:
            file_path = await client.download_media(media)
        else:
            raise ValueError("No valid media found in the replied message.")

        # Get media info
        media_info_html = get_mediainfo(file_path)

        # Remove date from the media info
        media_info_html = (
            f"<strong>SUNRISES 24 BOT UPDATES</strong><br>"
            f"<strong>MediaInfo X</strong><br>"
            f"{media_info_html}"
            f"<p>Rights Designed By Sᴜɴʀɪsᴇs Hᴀʀsʜᴀ 𝟸𝟺 🇮🇳 ᵀᴱᴸ</p>"
        )

        # Save the media info to an HTML file
        html_file_path = f"media_info_{media.file_id}.html"
        with open(html_file_path, "w") as file:
            file.write(media_info_html)

        # Store media info in MongoDB
        media_info_data = {
            'media_info': media_info_html,
            'media_id': media.file_id
        }
        media_info_id = await db.store_media_info_in_db(media_info_data)

        # Upload the media info to Telegraph
        response = telegraph.post(
            title="MediaInfo",
            author="SUNRISES 24 BOT UPDATES",
            author_url="https://t.me/Sunrises24BotUpdates",
            text=media_info_html
        )
        link = f"https://graph.org/{response['path']}"

        # Prepare the final message with the Telegraph link
        message_text = (
            f"SUNRISES 24 BOT UPDATES\n"
            f"MediaInfo X\n\n"
            f"[View Info on Telegraph]({link})\n"
            f"Rights designed by Sᴜɴʀɪsᴇs Hᴀʀsʜᴀ 𝟸𝟺 🇮🇳 ᵀᴱᴸ"
        )

        # Send HTML file and Telegraph link
        await message.reply_document(document=html_file_path, caption=message_text)

    except Exception as e:
        await message.reply_text(f"Error: {e}")
    finally:
        # Clean up the acknowledgment message
        await processing_message.delete()

        # Clean up downloaded files and HTML file
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        if 'html_file_path' in locals() and os.path.exists(html_file_path):
            os.remove(html_file_path)
        

# Function to handle "/getmodapk" command
@Client.on_message(filters.command("getmodapk") & filters.chat(GROUP))
async def get_mod_apk(bot, msg: Message):
    if len(msg.command) < 2:
        return await msg.reply_text("Please provide a URL from getmodsapk.com or gamedva.com.")
    
    # Extract URL from command arguments
    apk_url = msg.command[1]
    user_id = msg.from_user.id
    username = msg.from_user.username or msg.from_user.first_name
    
    # Validate URL
    if not (apk_url.startswith("https://files.getmodsapk.com/") or apk_url.startswith("https://file.gamedva.com/")):
        return await msg.reply_text("Please provide a valid URL from getmodsapk.com or gamedva.com.")
    
    # Add task to the database
    task_id = await db.add_task(user_id, username, "Downloading Getmodsapk", "Queued")
    await bot.send_message(GROUP, f"Getmodsapk task added by {username} ({user_id})")
    
    # Downloading and sending the file
    sts = await msg.reply_text("🚀 Downloading APK... ⚡️")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(apk_url) as response:
                if response.status == 200:
                    # Extract filename from URL
                    new_name = apk_url.split("/")[-1]

                    # Write the downloaded content to a temporary file
                    with open(new_name, 'wb') as f:
                        f.write(await response.read())

                    # Send the APK file as a document
                    await bot.send_document(msg.chat.id, document=new_name, caption=f"Downloaded from {apk_url}")

                    # Clean up: delete the downloaded file
                    os.remove(new_name)

                    await sts.edit("✅ APK sent successfully!")
                    # Update task to completed
                    await db.update_task(task_id, status="Completed")
                else:
                    await sts.edit("❌ Failed to download APK.")
                    # Update task to failed
                    await db.update_task(task_id, status="Failed", error_message="Failed to download APK.")
    except Exception as e:
        await sts.edit(f"❌ Error: {str(e)}")
        # Update task to failed
        await db.update_task(task_id, status="Failed", error_message=str(e))

    await sts.delete()


@Client.on_message(filters.command("ban") & filters.user(ADMIN))
async def ban_user(bot, msg: Message):
    try:
        user_id = int(msg.text.split()[1])
        # Ban user in the database
        await db.ban_user(user_id)
        # Ban user from the chat
        await bot.ban_chat_member(chat_id=msg.chat.id, user_id=user_id)
        await msg.reply_text(f"User {user_id} has been banned.")
    except PyMongoError as e:
        await msg.reply_text(f"Database error occurred: {e}")
    except FloodWait as e:
        await asyncio.sleep(e.x)
        await msg.reply_text(f"Flood wait error: Please try again later.")
    except Exception as e:
        await msg.reply_text(f"An error occurred: {e}")

@Client.on_message(filters.command("unban") & filters.user(ADMIN))
async def unban_user(bot, msg: Message):
    try:
        user_id = int(msg.text.split()[1])
        # Unban user in the database
        await db.unban_user(user_id)
        # Unban user from the chat
        await bot.unban_chat_member(chat_id=msg.chat.id, user_id=user_id)
        await msg.reply_text(f"User {user_id} has been unbanned.")
    except PyMongoError as e:
        await msg.reply_text(f"Database error occurred: {e}")
    except FloodWait as e:
        await asyncio.sleep(e.x)
        await msg.reply_text(f"Flood wait error: Please try again later.")
    except Exception as e:
        await msg.reply_text(f"An error occurred: {e}")

@Client.on_message(filters.command("users") & filters.user(ADMIN))
async def count_users(bot, msg):
    try:
        total_users = await db.count_users()
        banned_users = await db.count_banned_users()

        response = (
            f"**User Statistics:**\n"
            f"Total Active Users: {total_users}\n"
            f"Banned Users: {banned_users}"
        )
        await msg.reply_text(response)
    except PyMongoError as e:
        await msg.reply_text(f"Database error occurred while counting users: {e}")
    except Exception as e:
        await msg.reply_text(f"An error occurred: {e}")

@Client.on_message(filters.command("stats") & filters.chat(GROUP))        
async def stats_command(_, msg):
    uptime = datetime.datetime.now() - START_TIME
    uptime_str = str(timedelta(seconds=int(uptime.total_seconds())))

    total_space = psutil.disk_usage('/').total / (1024 ** 3)
    used_space = psutil.disk_usage('/').used / (1024 ** 3)
    free_space = psutil.disk_usage('/').free / (1024 ** 3)

    cpu_usage = psutil.cpu_percent()
    ram_usage = psutil.virtual_memory().percent

    stats_message = (
        f"📊 **Server Stats** 📊\n\n"
        f"⏳ **Uptime:** `{uptime_str}`\n"
        f"💾 **Total Space:** `{total_space:.2f} GB`\n"
        f"📂 **Used Space:** `{used_space:.2f} GB` ({used_space / total_space * 100:.1f}%)\n"
        f"📁 **Free Space:** `{free_space:.2f} GB`\n"
        f"⚙️ **CPU Usage:** `{cpu_usage:.1f}%`\n"
        f"💻 **RAM Usage:** `{ram_usage:.1f}%`\n"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton("🔄 Refresh", callback_data="refresh_stats")]
        ]
    )

    await msg.reply_text(stats_message, reply_markup=keyboard)

@Client.on_callback_query(filters.regex("^refresh_stats$"))
async def refresh_stats_callback(_, callback_query):
    # Refresh stats
    uptime = datetime.datetime.now() - START_TIME
    uptime_str = str(timedelta(seconds=int(uptime.total_seconds())))

    total_space = psutil.disk_usage('/').total / (1024 ** 3)
    used_space = psutil.disk_usage('/').used / (1024 ** 3)
    free_space = psutil.disk_usage('/').free / (1024 ** 3)

    cpu_usage = psutil.cpu_percent()
    ram_usage = psutil.virtual_memory().percent

    stats_message = (
        f"📊 **Server Stats** 📊\n\n"
        f"⏳ **Uptime:** `{uptime_str}`\n"
        f"💾 **Total Space:** `{total_space:.2f} GB`\n"
        f"📂 **Used Space:** `{used_space:.2f} GB` ({used_space / total_space * 100:.1f}%)\n"
        f"📁 **Free Space:** `{free_space:.2f} GB`\n"
        f"⚙️ **CPU Usage:** `{cpu_usage:.1f}%`\n"
        f"💻 **RAM Usage:** `{ram_usage:.1f}%`\n"
    )

    await callback_query.message.edit_text(stats_message, reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton("🔄 Refresh", callback_data="refresh_stats")]
        ]
    ))


@Client.on_message(filters.command("clear") & filters.user(ADMIN))
async def clear_database_handler(client: Client, msg: Message):
    try:
        await db.clear_database()
        await msg.reply_text("Database has been cleared✅.")
    except Exception as e:
        await msg.reply_text(f"An error occurred: {e}")

@Client.on_message(filters.command("broadcast") & filters.user(ADMIN))
async def broadcast(bot, msg: Message):
    if not msg.reply_to_message:
        await msg.reply_text("Please reply to a message to broadcast it.")
        return

    broadcast_message = msg.reply_to_message

    # Fetch all user IDs
    user_ids = await db.get_all_user_ids()

    sent_count = 0
    failed_count = 0
    log_entries = []

    for user_id in user_ids:
        try:
            await broadcast_message.copy(chat_id=user_id)
            sent_count += 1
            log_entries.append(f"Sent to {user_id}")
        except Exception as e:
            failed_count += 1
            log_entries.append(f"Failed to send to {user_id}: {e}")

        await asyncio.sleep(0.5)  # To avoid hitting rate limits

    # Write log entries to a text file
    log_content = "\n".join(log_entries)
    with open("broadcast_log.txt", "w") as log_file:
        log_file.write(log_content)

    # Send summary to admin
    await msg.reply_text(f"Broadcast completed: {sent_count} sent, {failed_count} failed.")
    await msg.reply_document('broadcast_log.txt')


#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
#FUNCTION ABOUT HANDLER
@Client.on_message(filters.command("about"))
async def about_command(bot, msg):
    about_text = """
<b>✯ Mʏ Nᴀᴍᴇ : <a href=https://t.me/MetaMorpher24Bot>𝐌𝐞𝐭𝐚𝐌𝐨𝐫𝐩𝐡𝐞𝐫 🌟</a></b>
<b>✯ Dᴇᴠᴇʟᴏᴘᴇʀ 🧑🏻‍💻 : <a href=https://t.me/Sunrises_24>𝐒𝐔𝐍𝐑𝐈𝐒𝐄𝐒™ ⚡</a></b>
<b>✯ Uᴘᴅᴀᴛᴇs 📢 : <a href=https://t.me/Sunrises24BotUpdates>𝐔𝐏𝐃𝐀𝐓𝐄𝐒 📢</a></b>
<b>✯ Sᴜᴘᴘᴏʀᴛ ✨ : <a href=https://t.me/Sunrises24BotUpdates>𝐒𝐔𝐏𝐏𝐎𝐑𝐓 ✨</a></b>
<b>✯ Bᴜɪʟᴅ Sᴛᴀᴛᴜs 📊 : ᴠ2.5 [Sᴛᴀʙʟᴇ]</b>
    """
    await msg.reply_text(about_text)

# Function to handle /help command
@Client.on_message(filters.command("help"))
async def help_command(bot, msg):
    help_text = """
    <b>Hᴇʟʟᴏ Mᴀᴡᴀ ❤️
Hᴇʀᴇ Is Tʜᴇ Hᴇʟᴘ Fᴏʀ Mʏ Cᴏᴍᴍᴀɴᴅs.

🦋 ʜᴏᴡ ᴛᴏ ᴜꜱᴇ
◉ Reply To Any Video/File 🖼️

/start - 𝐵𝑜𝑡 𝑎𝑙𝑖𝑣𝑒 𝑜𝑟 𝑁𝑜𝑡 🚶🏻
/usersettings - 𝑂𝑝𝑒𝑛 𝑡ℎ𝑒 𝑈𝑠𝑒𝑟𝑠𝑒𝑡𝑡𝑖𝑛𝑔𝑠 𝐹𝑜𝑟 𝐵𝑜𝑡 𝐼𝑛𝑓𝑜
/bsettings - 𝐵𝑜𝑡 𝑆𝑒𝑡𝑡𝑖𝑛𝑔𝑠 𝐸𝑛𝑎𝑏𝑙𝑒𝑑 𝑜𝑟 𝐷𝑖𝑠𝑎𝑏𝑙𝑒𝑑 [𝐴𝐷𝑀𝐼𝑁]
/setmetadata - 𝑆𝑒𝑡 𝑀𝑒𝑡𝑎𝑑𝑎𝑡𝑎 𝐼𝑛𝑑𝑖𝑣𝑖𝑑𝑢𝑎𝑙 𝑇𝑖𝑡𝑙𝑒𝑠
/clear - 𝑐𝑙𝑒𝑎𝑟 𝑡ℎ𝑒 𝑑𝑎𝑡𝑎𝑏𝑎𝑠𝑒
/gofilesetup - 𝑆𝑒𝑡𝑢𝑝 𝑇ℎ𝑒 𝐺𝑜𝑓𝑖𝑙𝑒 𝐴𝑃𝐼 𝐾𝐸𝑌 𝑓𝑟𝑜𝑚 𝐺𝑜𝑓𝑖𝑙𝑒.𝑖𝑜 ⚙️[𝑃𝑟𝑖𝑣𝑎𝑡𝑒]
/gdriveid - 𝑇ℎ𝑒 𝐺𝑜𝑜𝑔𝑙𝑒 𝐷𝑟𝑖𝑣𝑒 𝐹𝑜𝑙𝑑𝑒𝑟 𝐼𝐷 𝑆𝑒𝑡𝑢𝑝 📁[𝑃𝑟𝑖𝑣𝑎𝑡𝑒]
/mirror - 𝑀𝑖𝑟𝑟𝑜𝑟 𝑓𝑖𝑙𝑒𝑠 𝑡𝑜 𝑎 𝐺𝑜𝑜𝑔𝑙𝑒 𝐷𝑟𝑖𝑣𝑒 𝑙𝑖𝑛𝑘.
/clone -  𝐶𝑙𝑜𝑛𝑒 𝑎 𝐺𝑜𝑜𝑔𝑙𝑒 𝐷𝑟𝑖𝑣𝑒 𝑙𝑖𝑛𝑘.
/list - 𝐶ℎ𝑒𝑐𝑘 𝑡ℎ𝑒 𝑓𝑖𝑙𝑒𝑠 𝑖𝑛 𝐺𝑜𝑜𝑔𝑙𝑒 𝐷𝑟𝑖𝑣𝑒 𝑣𝑖𝑎 𝑡ℎ𝑒 𝑏𝑜𝑡.
/clean - 𝐷𝑒𝑙𝑒𝑡𝑒 𝑓𝑖𝑙𝑒𝑠 𝑖𝑛 𝐺𝑜𝑜𝑔𝑙𝑒 𝐷𝑟𝑖𝑣𝑒 𝑏𝑦 𝑓𝑖𝑙𝑒 𝑛𝑎𝑚𝑒.
/leech - 𝑙𝑒𝑒𝑐ℎ 𝑡ℎ𝑒 𝑆𝑒𝑒𝑑𝑟 & 𝑊𝑜𝑟𝑘𝑒𝑟𝑠 𝐿𝑖𝑛𝑘𝑠 𝑡𝑜 𝐹𝑖𝑙𝑒 𝑜𝑟 𝐺𝑑𝑟𝑖𝑣𝑒 [𝐴𝑈𝑇𝐻_𝑈𝑆𝐸𝑅𝑆].
/extractaudios - 𝐸𝑥𝑡𝑟𝑎𝑐𝑡 𝑎𝑢𝑑𝑖𝑜 𝑓𝑟𝑜𝑚 𝑓𝑖𝑙𝑒𝑠.
/extractsubtitles - 𝐸𝑥𝑡𝑟𝑎𝑐𝑡 𝑠𝑢𝑏𝑡𝑖𝑡𝑙𝑒𝑠 𝑓𝑟𝑜𝑚 𝑓𝑖𝑙𝑒𝑠.
/extractvideo - 𝐸𝑥𝑡𝑟𝑎𝑐𝑡 𝑣𝑖𝑑𝑒𝑜 𝑓𝑟𝑜𝑚 𝑓𝑖𝑙𝑒𝑠.
/rename - 𝑟𝑒𝑝𝑙𝑎𝑦 𝑤𝑖𝑡ℎ 𝑓𝑖𝑙𝑒 𝑡𝑜 𝑅𝑒𝑛𝑎𝑚𝑒📝
/gofile - 𝑇ℎ𝑒 𝐹𝑖𝑙𝑒𝑠 𝑈𝑝𝑙𝑜𝑎𝑑 𝑇𝑜 𝐺𝑜𝑓𝑖𝑙𝑒 𝐿𝑖𝑛𝑘 🔗
/mediainfo - 𝑀𝑒𝑑𝑖𝑎 & 𝑉𝑖𝑑𝑒𝑜 𝐼𝑛𝑓𝑜𝑟𝑚𝑎𝑡𝑖𝑜𝑛 ℹ️ 
/ytdlleech - 𝐿𝑒𝑒𝑐ℎ 𝑡ℎ𝑒 𝑌𝑜𝑢𝑡𝑢𝑏𝑒 𝐿𝑖𝑛𝑘𝑠
/changeindexaudio - 𝑅𝑒𝑜𝑟𝑑𝑒𝑟 𝑡ℎ𝑒 𝑠𝑒𝑞𝑢𝑒𝑛𝑐𝑒 [a-1  𝑓𝑜𝑟 𝑟𝑒𝑚𝑜𝑣𝑒 𝑎𝑢𝑑𝑖𝑜 , a-2-1-3-4  𝑓𝑜𝑟 𝑠𝑤𝑎𝑝 𝑎𝑢𝑑𝑖𝑜]
/changeindexsub - 𝑅𝑒𝑜𝑟𝑑𝑒𝑟 𝑡ℎ𝑒 𝑠𝑒𝑞𝑢𝑒𝑛𝑐𝑒 [s-1  𝑓𝑜𝑟 𝑟𝑒𝑚𝑜𝑣𝑒 𝑠𝑢𝑏𝑡𝑖𝑡𝑙𝑒 , s-2-1-3-4  𝑓𝑜𝑟 𝑠𝑤𝑎𝑝 𝑠𝑢𝑏𝑡𝑖𝑡𝑙𝑒]
/changemetadata - 𝑇𝑟𝑎𝑛𝑠𝑓𝑜𝑟𝑚 𝑡ℎ𝑒 𝑚𝑒𝑡𝑎𝑑𝑎𝑡𝑎
/removetags - 𝑇𝑜 𝑅𝑒𝑚𝑜𝑣𝑒 𝐴𝑙𝑙 𝑀𝑒𝑡𝑎𝑑𝑎𝑡𝑎 𝑇𝑎𝑔𝑠
/merge - 𝑆𝑒𝑛𝑑 𝑢𝑝 𝑡𝑜 10 𝑣𝑖𝑑𝑒𝑜/𝑑𝑜𝑐𝑢𝑚𝑒𝑛𝑡 𝑓𝑖𝑙𝑒𝑠 𝑜𝑛𝑒 𝑏𝑦 𝑜𝑛𝑒.
/videomerge - 𝑉𝑖𝑑𝑒𝑜𝑚𝑒𝑟𝑔𝑒 𝑤𝑖𝑡ℎ 𝑓𝑖𝑙𝑒𝑛𝑎𝑚𝑒.𝑚𝑘𝑣 𝑡𝑜 𝑠𝑡𝑎𝑟𝑡 𝑚𝑒𝑟𝑔𝑖𝑛𝑔
/samplevideo - 𝐶𝑟𝑒𝑎𝑡𝑒 𝐴 𝑆𝑎𝑚𝑝𝑙𝑒 𝑉𝑖𝑑𝑒𝑜 🎞️
/screenshots - 𝐶𝑎𝑝𝑡𝑢𝑟𝑒 𝑠𝑜𝑚𝑒 𝑚𝑒𝑚𝑜𝑟𝑎𝑏𝑙𝑒 𝑠ℎ𝑜𝑡𝑠 📸
/unzip - 𝐸𝑥𝑡𝑟𝑎𝑐𝑡 𝑓𝑖𝑙𝑒𝑠 (𝑍𝐼𝑃 𝑓𝑜𝑟𝑚𝑎𝑡 𝑜𝑛𝑙𝑦)
/setphoto  -  𝑇𝑜 𝑎𝑑𝑑 𝑎 𝑝ℎ𝑜𝑡𝑜 𝑡𝑜 𝑎 𝑓𝑖𝑙𝑒  𝑎𝑡𝑡𝑎𝑐ℎ𝑚𝑒𝑛𝑡.𝑗𝑝𝑔 𝑓𝑜𝑟 𝑠𝑒𝑛𝑑𝑖𝑛𝑔 𝑡ℎ𝑒 𝑝ℎ𝑜𝑡𝑜 𝑎𝑠 𝑎𝑛 𝑎𝑡𝑡𝑎𝑐ℎ𝑚𝑒𝑛𝑡.
/attachphoto - 𝑇ℎ𝑖𝑠 𝑐𝑜𝑚𝑚𝑎𝑛𝑑 𝑖𝑠 𝑢𝑠𝑒𝑑 𝑡𝑜 𝑎𝑑𝑑 𝑎 𝑝ℎ𝑜𝑡𝑜 𝑎𝑡𝑡𝑎𝑐ℎ𝑚𝑒𝑛𝑡.𝑗𝑝𝑔 𝑡𝑜 𝑎 𝑓𝑖𝑙𝑒
/stats - 𝑠𝑡𝑎𝑡𝑠 𝑜𝑓 𝑡ℎ𝑒 𝑏𝑜𝑡 📊
/users - 𝐴𝑐𝑡𝑖𝑣𝑒 𝑢𝑠𝑒𝑟𝑠 𝑜𝑓 𝑏𝑜𝑡[𝐴𝑑𝑚𝑖𝑛]
/ban - 𝐵𝑎𝑛 𝑡ℎ𝑒 𝑢𝑠𝑒𝑟 𝑓𝑟𝑜𝑚  𝐵𝑜𝑡[𝐴𝑑𝑚𝑖𝑛]
/unban - 𝑈𝑛𝑏𝑎𝑛 𝑡ℎ𝑒 𝑢𝑠𝑒𝑟 𝑓𝑟𝑜𝑚  𝐵𝑜𝑡[𝐴𝑑𝑚𝑖𝑛]
/broadcast  -  𝑀𝑒𝑠𝑠𝑎𝑔𝑒𝑠 𝑡𝑜 𝐸𝑣𝑒𝑟𝑦 𝑈𝑠𝑒𝑟𝑠 𝑖𝑛 𝑏𝑜𝑡 [𝐴𝑑𝑚𝑖𝑛]
/help - 𝐺𝑒𝑡 𝑑𝑒𝑡𝑎𝑖𝑙𝑒𝑑 𝑜𝑓 𝑏𝑜𝑡 𝑐𝑜𝑚𝑚𝑎𝑛𝑑𝑠 📝
/about - 𝐿𝑒𝑎𝑟𝑛 𝑚𝑜𝑟𝑒 𝑎𝑏𝑜𝑢𝑡 𝑡ℎ𝑖𝑠 𝑏𝑜𝑡 🧑🏻‍💻
/ping - 𝑇𝑜 𝐶ℎ𝑒𝑐𝑘 𝑇ℎ𝑒 𝑃𝑖𝑛𝑔 𝑂𝑓 𝑇ℎ𝑒 𝐵𝑜𝑡 📍

 💭• Tʜɪs Bᴏᴛ Is Fᴏʟʟᴏᴡs ᴛʜᴇ 𝟸GB Bᴇʟᴏᴡ Fɪʟᴇs Tᴏ Tᴇʟᴇɢʀᴀᴍ.\n• 𝟸GB Aʙᴏᴠᴇ Fɪʟᴇs Tᴏ Gᴏᴏɢʟᴇ Dʀɪᴠᴇ.
 
🔱 𝐌𝐚𝐢𝐧𝐭𝐚𝐢𝐧𝐞𝐝 𝐁𝐲 : <a href='https://t.me/Sunrises_24'>𝐒𝐔𝐍𝐑𝐈𝐒𝐄𝐒™</a></b>
    
   """
    await msg.reply_text(help_text)
    

#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
#Ping
@Client.on_message(filters.command("ping"))
async def ping(bot, msg):
    start_t = time.time()
    rm = await msg.reply_text("Checking")
    end_t = time.time()
    time_taken_s = (end_t - start_t) * 1000
    await rm.edit(f"Pong!📍\n{time_taken_s:.3f} ms")


@Client.on_message(filters.command("compress") & filters.chat(GROUP))
async def compress_media(bot, msg: Message):
    user_id = msg.from_user.id

    reply = msg.reply_to_message
    if not reply:
        return await msg.reply_text("Please reply to a media file with the compress command\nFormat: `compress -n output_filename`")

    if len(msg.command) < 3 or msg.command[1] != "-n":
        return await msg.reply_text("Please provide the output filename with the `-n` flag\nFormat: `compress -n output_filename`")

    output_filename = " ".join(msg.command[2:]).strip()

    if not output_filename.lower().endswith(('.mkv', '.mp4', '.avi')):
        return await msg.reply_text("Invalid file extension. Please use a valid video file extension (e.g., .mkv, .mp4, .avi).")

    media = reply.document or reply.audio or reply.video
    if not media:
        return await msg.reply_text("Please reply to a valid media file (audio, video, or document) with the compress command.")

    sts = await msg.reply_text("🚀 Downloading media... ⚡")
    c_time = time.time()
    try:
        downloaded = await reply.download(progress=progress_message, progress_args=("🚀 Download Started... ⚡️", sts, c_time))
    except Exception as e:
        await safe_edit_message(sts, f"Error downloading media: {e}")
        return

    output_file = output_filename

    await safe_edit_message(sts, "💠 Compressing media... ⚡")
    try:
        compress_video(downloaded, output_file)
    except Exception as e:
        await safe_edit_message(sts, f"Error compressing media: {e}")
        os.remove(downloaded)
        return

    # Retrieve thumbnail from the database
    thumbnail_file_id = await db.get_thumbnail(user_id)
    file_thumb = None
    if thumbnail_file_id:
        try:
            file_thumb = await bot.download_media(thumbnail_file_id)
        except Exception:
            pass
    else:
        if hasattr(media, 'thumbs') and media.thumbs:
            try:
                file_thumb = await bot.download_media(media.thumbs[0].file_id)
            except Exception as e:
                file_thumb = None

    filesize = os.path.getsize(output_file)
    filesize_human = humanbytes(filesize)
    cap = f"{output_filename}\n\n🌟 Size: {filesize_human}"

    await safe_edit_message(sts, "💠 Uploading... ⚡")
    c_time = time.time()

    if filesize > FILE_SIZE_LIMIT:
        file_link = await upload_to_google_drive(output_file, output_filename, sts)
        button = [[InlineKeyboardButton("☁️ CloudUrl ☁️", url=f"{file_link}")]]
        await msg.reply_text(
            f"**File successfully compressed and uploaded to Google Drive!**\n\n"
            f"**Google Drive Link**: [View File]({file_link})\n\n"
            f"**Uploaded File**: {output_filename}\n"
            f"**Request User:** {msg.from_user.mention}\n\n"
            f"**Size**: {filesize_human}",
            reply_markup=InlineKeyboardMarkup(button)
        )
    else:
        try:
            await bot.send_document(msg.chat.id, document=output_file, thumb=file_thumb, caption=cap, progress=progress_message, progress_args=("💠 Upload Started... ⚡", sts, c_time))
        except Exception as e:
            return await safe_edit_message(sts, f"Error: {e}")

    os.remove(downloaded)
    os.remove(output_file)
    if file_thumb and os.path.exists(file_thumb):
        os.remove(file_thumb)
    await sts.delete()


def compress_video(input_path, output_path):
    command = [
        'ffmpeg',
        '-i', input_path,
        '-preset', 'ultrafast',
        '-c:v', 'libx265',
        '-crf', '27',
        '-map', '0:v',
        '-c:a', 'aac',
        '-map', '0:a',
        '-c:s', 'copy',
        '-map', '0:s?',
        output_path,
        '-y'
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise Exception(f"FFmpeg error: {stderr.decode('utf-8')}")



@Client.on_message(filters.command("change") & filters.chat(GROUP))
async def change(bot, msg: Message):
    global METADATA_ENABLED, CHANGE_INDEX_ENABLED

    if not (METADATA_ENABLED and CHANGE_INDEX_ENABLED):
        return await msg.reply_text("One or more required features are currently disabled.")

    user_id = msg.from_user.id

    # Fetch metadata titles from the database
    metadata_titles = await db.get_metadata_titles(user_id)
    video_title = metadata_titles.get('video_title', '')
    audio_title = metadata_titles.get('audio_title', '')
    subtitle_title = metadata_titles.get('subtitle_title', '')

    if not any([video_title, audio_title, subtitle_title]):
        return await msg.reply_text("Metadata titles are not set. Please set metadata titles using `/setmetadata video_title audio_title subtitle_title`.")

    reply = msg.reply_to_message
    if not reply:
        return await msg.reply_text("Please reply to a media file with the change command\nFormat: `/change a-2 -m -n filename.mkv`")

    if len(msg.command) < 5 or '-m' not in msg.command or '-n' not in msg.command:
        return await msg.reply_text("Please provide the correct format\nFormat: `/change a-2 -m -n filename.mkv`")

    index_cmd = msg.command[1]
    metadata_flag_index = msg.command.index('-m')
    output_flag_index = msg.command.index('-n')
    output_filename = " ".join(msg.command[output_flag_index + 1:]).strip()

    if not output_filename.lower().endswith(('.mkv', '.mp4', '.avi')):
        return await msg.reply_text("Invalid file extension. Please use a valid video file extension (e.g., .mkv, .mp4, .avi).")

    media = reply.document or reply.audio or reply.video
    if not media:
        return await msg.reply_text("Please reply to a valid media file (audio, video, or document) with the change command.")

    sts = await msg.reply_text("🚀 Downloading media... ⚡")
    c_time = time.time()
    try:
        downloaded = await reply.download(progress=progress_message, progress_args=("🚀 Download Started... ⚡️", sts, c_time))
    except Exception as e:
        await safe_edit_message(sts, f"Error downloading media: {e}")
        return

    # Output file path (temporary file)
    intermediate_file = os.path.splitext(downloaded)[0] + "_indexed" + os.path.splitext(downloaded)[1]

    index_params = index_cmd.split('-')
    stream_type = index_params[0]
    indexes = [int(i) - 1 for i in index_params[1:]]

    # Construct the FFmpeg command to modify indexes
    ffmpeg_cmd = ['ffmpeg', '-i', downloaded, '-map', '0:v']  # Always map video stream

    for idx in indexes:
        ffmpeg_cmd.extend(['-map', f'0:{stream_type}:{idx}'])

    # Copy all subtitle streams if they exist
    ffmpeg_cmd.extend(['-map', '0:s?'])

    ffmpeg_cmd.extend(['-c', 'copy', intermediate_file, '-y'])

    await safe_edit_message(sts, "💠 Changing audio indexing... ⚡")
    process = await asyncio.create_subprocess_exec(*ffmpeg_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        await safe_edit_message(sts, f"❗ FFmpeg error: {stderr.decode('utf-8')}")
        os.remove(downloaded)
        if os.path.exists(intermediate_file):
            os.remove(intermediate_file)
        return

    output_file = output_filename

    await safe_edit_message(sts, "💠 Changing metadata... ⚡")
    try:
        change_video_metadata(intermediate_file, video_title, audio_title, subtitle_title, output_file)
    except Exception as e:
        await safe_edit_message(sts, f"Error changing metadata: {e}")
        os.remove(downloaded)
        os.remove(intermediate_file)
        return

    # Retrieve thumbnail from the database
    thumbnail_file_id = await db.get_thumbnail(user_id)
    file_thumb = None
    if thumbnail_file_id:
        try:
            file_thumb = await bot.download_media(thumbnail_file_id)
        except Exception:
            pass
    else:
        if hasattr(media, 'thumbs') and media.thumbs:
            try:
                file_thumb = await bot.download_media(media.thumbs[0].file_id)
            except Exception as e:
                file_thumb = None

    filesize = os.path.getsize(output_file)
    filesize_human = humanbytes(filesize)
    cap = f"{output_filename}\n\n🌟 Size: {filesize_human}"

    await safe_edit_message(sts, "💠 Uploading... ⚡")
    c_time = time.time()

    if filesize > FILE_SIZE_LIMIT:
        file_link = await upload_to_google_drive(output_file, output_filename, sts)
        button = [[InlineKeyboardButton("☁️ CloudUrl ☁️", url=f"{file_link}")]]
        await msg.reply_text(
            f"**File successfully changed audio index and metadata, then uploaded to Google Drive!**\n\n"
            f"**Google Drive Link**: [View File]({file_link})\n\n"
            f"**Uploaded File**: {output_filename}\n"
            f"**Request User:** {msg.from_user.mention}\n\n"
            f"**Size**: {filesize_human}",
            reply_markup=InlineKeyboardMarkup(button)
        )
    else:
        try:
            await bot.send_document(
                msg.chat.id,
                document=output_file,
                file_name=output_filename,
                thumb=file_thumb,
                caption=cap,
                progress=progress_message,
                progress_args=("💠 Upload Started... ⚡", sts, c_time)
            )
        except Exception as e:
            return await safe_edit_message(sts, f"Error: {e}")

    os.remove(downloaded)
    os.remove(intermediate_file)
    os.remove(output_file)
    if file_thumb and os.path.exists(file_thumb):
        os.remove(file_thumb)
    await sts.delete()

"""
 
@Client.on_message(filters.command("changeleech") & filters.chat(GROUP))
async def changeleech(bot, msg: Message):
    if len(msg.command) < 2 or not msg.reply_to_message:
        return await msg.reply_text("Please reply to a file, video, audio, or link with the desired filename and extension (e.g., `.mkv`, `.mp4`, `.zip`).")

    reply = msg.reply_to_message
    new_name = msg.text.split(" ", 1)[1]

    if not new_name.endswith((".mkv", ".mp4", ".zip")):
        return await msg.reply_text("Please specify a filename ending with .mkv, .mp4, or .zip.")

    media = reply.document or reply.audio or reply.video or reply.text

    sts = await msg.reply_text("🚀 Downloading... ⚡")
    c_time = time.time()

    if reply.text and ("seedr" in reply.text or "workers" in reply.text):
        await handle_link_download(bot, msg, reply.text, new_name, media, sts, c_time)
    else:
        if not media:
            return await msg.reply_text("Please reply to a valid file, video, audio, or link with the desired filename and extension (e.g., `.mkv`, `.mp4`, `.zip`).")

        try:
            downloaded = await reply.download(file_name=new_name, progress=progress_message, progress_args=("🚀 Download Started... ⚡️", sts, c_time))
        except RPCError as e:
            return await sts.edit(f"Download failed: {e}")

        filesize = humanbytes(os.path.getsize(downloaded))

        # Change indexing and metadata if required
        if len(msg.command) > 2:
            await change_metadata_and_index(bot, msg, downloaded, new_name, media, sts, c_time)

        # Thumbnail handling
        thumbnail_file_id = await db.get_thumbnail(msg.from_user.id)
        og_thumbnail = None
        if thumbnail_file_id:
            try:
                og_thumbnail = await bot.download_media(thumbnail_file_id)
            except Exception:
                pass
        else:
            if hasattr(media, 'thumbs') and media.thumbs:
                try:
                    og_thumbnail = await bot.download_media(media.thumbs[0].file_id)
                except Exception:
                    pass

        await sts.edit("💠 Uploading... ⚡")
        c_time = time.time()

        if os.path.getsize(downloaded) > FILE_SIZE_LIMIT:
            file_link = await upload_to_google_drive(downloaded, new_name, sts)
            await msg.reply_text(f"File uploaded to Google Drive!\n\n📁 **File Name:** {new_name}\n💾 **Size:** {filesize}\n🔗 **Link:** {file_link}")
        else:
            try:
                await bot.send_document(msg.chat.id, document=downloaded, thumb=og_thumbnail, caption=cap, progress=progress_message, progress_args=("💠 Upload Started... ⚡", sts, c_time))
            except ValueError as e:
                return await sts.edit(f"Upload failed: {e}")
            except TimeoutError as e:
                return await sts.edit(f"Upload timed out: {e}")

        try:
            if og_thumbnail:
                os.remove(og_thumbnail)
            os.remove(downloaded)
        except Exception as e:
            print(f"Error deleting files: {e}")

        await sts.delete()

async def handle_link_download(bot, msg: Message, link: str, new_name: str, media, sts, c_time):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as resp:
                if resp.status == 200:
                    with open(new_name, 'wb') as f:
                        f.write(await resp.read())
                else:
                    await sts.edit(f"Failed to download file from link. Status code: {resp.status}")
                    return
    except Exception as e:
        await sts.edit(f"Error during download: {e}")
        return

    if not os.path.exists(new_name):
        await sts.edit("File not found after download. Please check the link and try again.")
        return

    filesize = humanbytes(os.path.getsize(new_name))

    # Change indexing and metadata if required
    if len(msg.command) > 2:
        await change_metadata_and_index(bot, msg, new_name, new_name, media, sts, c_time)

    # Thumbnail handling
    thumbnail_file_id = await db.get_thumbnail(msg.from_user.id)
    og_thumbnail = None
    if thumbnail_file_id:
        try:
            og_thumbnail = await bot.download_media(thumbnail_file_id)
        except Exception:
            pass
    else:
        if hasattr(media, 'thumbs') and media.thumbs:
            try:
                og_thumbnail = await bot.download_media(media.thumbs[0].file_id)
            except Exception:
                pass

    await sts.edit("💠 Uploading... ⚡")
    c_time = time.time()

    if os.path.getsize(new_name) > FILE_SIZE_LIMIT:
        file_link = await upload_to_google_drive(new_name, new_name, sts)
        await msg.reply_text(f"File uploaded to Google Drive!\n\n📁 **File Name:** {new_name}\n💾 **Size:** {filesize}\n🔗 **Link:** {file_link}")
    else:
        try:
            await bot.send_document(msg.chat.id, document=new_name, thumb=og_thumbnail, caption=f"{new_name}\n\n🌟 Size: {filesize}", progress=progress_message, progress_args=("💠 Upload Started... ⚡", sts, c_time))
        except ValueError as e:
            return await sts.edit(f"Upload failed: {e}")
        except TimeoutError as e:
            return await sts.edit(f"Upload timed out: {e}")

    try:
        if og_thumbnail:
            os.remove(og_thumbnail)
        os.remove(new_name)
    except Exception as e:
        print(f"Error deleting files: {e}")

    await sts.delete()"""

#below code safe edit changeleech
"""
from pyrogram.errors import RPCError

async def safe_edit_message(sts, text):
    try:
        await sts.edit(text)
    except RPCError as e:
        if e.code == 400 and "MESSAGE_ID_INVALID" in str(e):
            # Handle the specific case of invalid message ID
            print("Failed to edit message: Invalid message ID.")
        else:
            # Handle other potential RPC errors
            print(f"Failed to edit message: {e}")

"""

@Client.on_message(filters.command("changeleech") & filters.chat(GROUP))
async def changeleech(bot, msg: Message):
    if len(msg.command) < 2 or not msg.reply_to_message:
        return await msg.reply_text("Please reply to a file, video, audio, or link with the desired filename and extension (e.g., `.mkv`, `.mp4`, `.zip`).")

    reply = msg.reply_to_message
    new_name = msg.text.split(" ", 1)[1]

    if not new_name.endswith((".mkv", ".mp4", ".zip")):
        return await msg.reply_text("Please specify a filename ending with .mkv, .mp4, or .zip.")

    media = reply.document or reply.audio or reply.video or reply.text

    sts = await msg.reply_text("🚀 Downloading... ⚡")
    c_time = time.time()

    if reply.text and ("seedr" in reply.text or "workers" in reply.text):
        await handle_link_download(bot, msg, reply.text, new_name, media, sts, c_time)
    else:
        if not media:
            return await msg.reply_text("Please reply to a valid file, video, audio, or link with the desired filename and extension (e.g., `.mkv`, `.mp4`, `.zip`).")

        try:
            downloaded = await reply.download(file_name=new_name, progress=progress_message, progress_args=("🚀 Download Started... ⚡️", sts, c_time))
        except RPCError as e:
            return await sts.edit(f"Download failed: {e}")

        if not os.path.exists(downloaded):
            return await sts.edit("File not found after download. Please check the reply and try again.")

        filesize = humanbytes(os.path.getsize(downloaded))

        # Change indexing and metadata if required
        if len(msg.command) > 2:
            await change_metadata_and_index(bot, msg, downloaded, new_name, media, sts, c_time)

        # Thumbnail handling
        thumbnail_file_id = await db.get_thumbnail(msg.from_user.id)
        og_thumbnail = None
        if thumbnail_file_id:
            try:
                og_thumbnail = await bot.download_media(thumbnail_file_id)
            except Exception:
                pass
        else:
            if hasattr(media, 'thumbs') and media.thumbs:
                try:
                    og_thumbnail = await bot.download_media(media.thumbs[0].file_id)
                except Exception:
                    pass

        await sts.edit("💠 Uploading... ⚡")
        c_time = time.time()

        if os.path.getsize(downloaded) > FILE_SIZE_LIMIT:
            file_link = await upload_to_google_drive(downloaded, new_name, sts)
            await msg.reply_text(f"File uploaded to Google Drive!\n\n📁 **File Name:** {new_name}\n💾 **Size:** {filesize}\n🔗 **Link:** {file_link}")
        else:
            try:
                await bot.send_document(msg.chat.id, document=downloaded, thumb=og_thumbnail, caption=new_name, progress=progress_message, progress_args=("💠 Upload Started... ⚡", sts, c_time))
            except ValueError as e:
                return await sts.edit(f"Upload failed: {e}")
            except TimeoutError as e:
                return await sts.edit(f"Upload timed out: {e}")

        try:
            if og_thumbnail and os.path.exists(og_thumbnail):
                os.remove(og_thumbnail)
            if os.path.exists(downloaded):
                os.remove(downloaded)
        except Exception as e:
            print(f"Error deleting files: {e}")

        await sts.delete()

async def handle_link_download(bot, msg: Message, link: str, new_name: str, media, sts, c_time):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as resp:
                if resp.status == 200:
                    with open(new_name, 'wb') as f:
                        f.write(await resp.read())
                else:
                    await sts.edit(f"Failed to download file from link. Status code: {resp.status}")
                    return
    except Exception as e:
        await sts.edit(f"Error during download: {e}")
        return

    if not os.path.exists(new_name):
        await sts.edit("File not found after download. Please check the link and try again.")
        return

    filesize = humanbytes(os.path.getsize(new_name))

    # Change indexing and metadata if required
    if len(msg.command) > 2:
        await change_metadata_and_index(bot, msg, new_name, new_name, media, sts, c_time)

    # Thumbnail handling
    thumbnail_file_id = await db.get_thumbnail(msg.from_user.id)
    og_thumbnail = None
    if thumbnail_file_id:
        try:
            og_thumbnail = await bot.download_media(thumbnail_file_id)
        except Exception:
            pass
    else:
        if hasattr(media, 'thumbs') and media.thumbs:
            try:
                og_thumbnail = await bot.download_media(media.thumbs[0].file_id)
            except Exception:
                pass

    await sts.edit("💠 Uploading... ⚡")
    c_time = time.time()

    if os.path.getsize(new_name) > FILE_SIZE_LIMIT:
        file_link = await upload_to_google_drive(new_name, new_name, sts)
        await msg.reply_text(f"File uploaded to Google Drive!\n\n📁 **File Name:** {new_name}\n💾 **Size:** {filesize}\n🔗 **Link:** {file_link}")
    else:
        try:
            await bot.send_document(msg.chat.id, document=new_name, thumb=og_thumbnail, caption=f"{new_name}\n\n🌟 Size: {filesize}", progress=progress_message, progress_args=("💠 Upload Started... ⚡", sts, c_time))
        except ValueError as e:
            return await sts.edit(f"Upload failed: {e}")
        except TimeoutError as e:
            return await sts.edit(f"Upload timed out: {e}")

    try:
        if og_thumbnail and os.path.exists(og_thumbnail):
            os.remove(og_thumbnail)
        if os.path.exists(new_name):
            os.remove(new_name)
    except Exception as e:
        print(f"Error deleting files: {e}")

    await sts.delete()



async def change_metadata_and_index(bot, msg, downloaded, new_name, media, sts, c_time):
    global METADATA_ENABLED, CHANGE_INDEX_ENABLED

    if not (METADATA_ENABLED and CHANGE_INDEX_ENABLED):
        await msg.reply_text("One or more required features are currently disabled.")
        return

    user_id = msg.from_user.id

    # Fetch metadata titles from the database
    metadata_titles = await db.get_metadata_titles(user_id)
    video_title = metadata_titles.get('video_title', '')
    audio_title = metadata_titles.get('audio_title', '')
    subtitle_title = metadata_titles.get('subtitle_title', '')

    if not any([video_title, audio_title, subtitle_title]):
        await msg.reply_text("Metadata titles are not set. Please set metadata titles using `/setmetadata video_title audio_title subtitle_title`.")
        return

    if len(msg.command) < 5 or '-m' not in msg.command or '-n' not in msg.command:
        await msg.reply_text("Please provide the correct format\nFormat: `/change a-2 -m -n filename.mkv`")
        return

    index_cmd = msg.command[1]
    metadata_flag_index = msg.command.index('-m')
    output_flag_index = msg.command.index('-n')
    output_filename = " ".join(msg.command[output_flag_index + 1:]).strip()

    if not output_filename.lower().endswith(('.mkv', '.mp4', '.avi')):
        await msg.reply_text("Invalid file extension. Please use a valid video file extension (e.g., .mkv, .mp4, .avi).")
        return

    # Output file path (temporary file)
    intermediate_file = os.path.splitext(downloaded)[0] + "_indexed" + os.path.splitext(downloaded)[1]

    index_params = index_cmd.split('-')
    stream_type = index_params[0]
    indexes = [int(i) - 1 for i in index_params[1:]]

    # Construct the FFmpeg command to modify indexes
    ffmpeg_cmd = ['ffmpeg', '-i', downloaded, '-map', '0:v']  # Always map video stream

    for idx in indexes:
        ffmpeg_cmd.extend(['-map', f'0:{stream_type}:{idx}'])

    # Copy all subtitle streams if they exist
    ffmpeg_cmd.extend(['-map', '0:s?'])

    ffmpeg_cmd.extend(['-c', 'copy', intermediate_file, '-y'])

    await safe_edit_message(sts, "💠 Changing audio indexing... ⚡")
    process = await asyncio.create_subprocess_exec(*ffmpeg_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        await safe_edit_message(sts, f"❗ FFmpeg error: {stderr.decode('utf-8')}")
        os.remove(downloaded)
        if os.path.exists(intermediate_file):
            os.remove(intermediate_file)
        return

    output_file = output_filename

    await safe_edit_message(sts, "💠 Changing metadata... ⚡")
    try:
        change_video_metadata(intermediate_file, video_title, audio_title, subtitle_title, output_file)
    except Exception as e:
        await safe_edit_message(sts, f"Error changing metadata: {e}")
        os.remove(downloaded)
        os.remove(intermediate_file)
        return

    # Retrieve thumbnail from the database
    thumbnail_file_id = await db.get_thumbnail(user_id)
    file_thumb = None
    if thumbnail_file_id:
        try:
            file_thumb = await bot.download_media(thumbnail_file_id)
        except Exception:
            pass
    else:
        if hasattr(media, 'thumbs') and media.thumbs:
            try:
                file_thumb = await bot.download_media(media.thumbs[0].file_id)
            except Exception as e:
                file_thumb = None

    filesize = os.path.getsize(output_file)
    filesize_human = humanbytes(filesize)
    cap = f"{output_filename}\n\n🌟 Size: {filesize_human}"

    await safe_edit_message(sts, "💠 Uploading... ⚡")
    c_time = time.time()

    if filesize > FILE_SIZE_LIMIT:
        file_link = await upload_to_google_drive(output_file, output_filename, sts)
        button = [[InlineKeyboardButton("☁️ CloudUrl ☁️", url=f"{file_link}")]]
        await msg.reply_text(
            f"**File successfully changed audio index and metadata, then uploaded to Google Drive!**\n\n"
            f"**Google Drive Link**: [View File]({file_link})\n\n"
            f"**Uploaded File**: {output_filename}\n"
            f"**Request User:** {msg.from_user.mention}\n\n"
            f"**Size**: {filesize_human}",
            reply_markup=InlineKeyboardMarkup(button)
        )
    else:
        try:
            await bot.send_document(
                msg.chat.id,
                document=output_file,
                file_name=output_filename,
                thumb=file_thumb,
                caption=cap,
                progress=progress_message,
                progress_args=("💠 Upload Started... ⚡", sts, c_time)
            )
        except Exception as e:
            return await safe_edit_message(sts, f"Error: {e}")

    os.remove(downloaded)
    os.remove(intermediate_file)
    os.remove(output_file)
    if file_thumb and os.path.exists(file_thumb):
        os.remove(file_thumb)
    await sts.delete()



import aiohttp
import os
import time
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery


CHANNEL_ID = -1002038048493

# Define GROUP filter as per your requirements


@Client.on_message(filters.command("gofilepost") & filters.chat(GROUP))
async def gofile_upload(bot: Client, msg: Message):
    user_id = msg.from_user.id

    # Retrieve the user's Gofile API key from the database
    gofile_api_key = await db.get_gofile_api_key(user_id)

    if not gofile_api_key:
        return await msg.reply_text("Gofile API key is not set. Use /gofilesetup {your_api_key} to set it.")

    reply = msg.reply_to_message
    if not reply or not (reply.document or reply.video or reply.audio):
        return await msg.reply_text("Please reply to a file, video, or audio to upload to Gofile.")

    media = reply.document or reply.video or reply.audio
    original_file_name = media.file_name

    # Replace underscores with dashes for display purposes
    display_file_name = original_file_name.replace("_", " - ")

    sts = await msg.reply_text("🚀 Uploading to Gofile...")
    c_time = time.time()
    
    downloaded_file = None

    try:
        async with aiohttp.ClientSession() as session:
            # Get available servers
            async with session.get("https://api.gofile.io/servers") as resp:
                if resp.status != 200:
                    return await sts.edit(f"Failed to get servers. Status code: {resp.status}")

                data = await resp.json()
                servers = data.get("data", {}).get("servers", [])
                if not servers:
                    return await sts.edit("No servers available.")
                
                server_name = servers[0].get("name")  # Use the server name
                if not server_name:
                    return await sts.edit("Server name is missing.")
                
                upload_url = f"https://{server_name}.gofile.io/contents/uploadfile"

            # Download the media file
            downloaded_file = await bot.download_media(
                media,
                file_name=original_file_name,  # Use the original filename for download
                progress=progress_message,
                progress_args=("🚀 Download Started...", sts, c_time)
            )

            # Get the file size
            file_size = os.path.getsize(downloaded_file)
            filesize_human = humanbytes(file_size)

            # Upload the file to Gofile
            with open(downloaded_file, "rb") as file:
                form_data = aiohttp.FormData()
                form_data.add_field("file", file, filename=original_file_name)
                headers = {"Authorization": f"Bearer {gofile_api_key}"} if gofile_api_key else {}

                async with session.post(
                    upload_url,
                    headers=headers,
                    data=form_data
                ) as resp:
                    if resp.status != 200:
                        return await sts.edit(f"Upload failed: Status code {resp.status}")

                    response = await resp.json()
                    if response["status"] == "ok":
                        download_url = response["data"]["downloadPage"]

                        # Calculate upload time
                        upload_time = time.time() - c_time
                        readable_upload_time = str(datetime.timedelta(seconds=int(upload_time)))

                        # Prepare the caption
                        caption = (
                            f"📂 Filename: {display_file_name}\n\n"
                            f"📏 Size: {filesize_human}\n\n"                         
                            f"⏳ Upload Time: {readable_upload_time}\n\n"
                            f"🖇️ Download link: {download_url}"
                        )

                        # Retrieve the saved photo from the database
                        saved_photo = await db.get_saved_photo(user_id)
                        if saved_photo:
                            await bot.send_photo(CHANNEL_ID, saved_photo, caption=caption)
                        else:
                            await bot.send_message(CHANNEL_ID, caption)

                        await sts.edit(f"Upload successful!\nDownload link: {download_url}")
                    else:
                        await sts.edit(f"Upload failed: {response['message']}")

    except Exception as e:
        await sts.edit(f"Error during upload: {e}")

    finally:
        try:
            if downloaded_file and os.path.exists(downloaded_file):
                os.remove(downloaded_file)
        except Exception as e:
            print(f"Error deleting file: {e}")


            
if __name__ == '__main__':
    app = Client("my_bot", bot_token=BOT_TOKEN)
    app.run()
