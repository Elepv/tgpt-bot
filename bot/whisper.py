from telegram import Update
from telegram.ext import CallbackContext
from telegram.constants import ParseMode

from pathlib import Path
import tempfile
import pydub

import openai_utils
import poe_utils

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


async def voice_to_speech(voice_file_id: str, context) -> str:
    # 临时文件存储录音文件
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_dir = Path(tmp_dir)
        voice_ogg_path = tmp_dir / "group_voice.ogg"

        # download 下载语音文件
        voice_file = await context.bot.get_file(voice_file_id)
        await voice_file.download_to_drive(voice_ogg_path)

        # convert to mp3
        voice_mp3_path = tmp_dir / "gourp_voice.mp3"
        pydub.AudioSegment.from_file(voice_ogg_path).export(voice_mp3_path, format="mp3")

        # transcribe
        with open(voice_mp3_path, "rb") as f:
            transcribed_text = await openai_utils.transcribe_audio(f)

            if transcribed_text is None:
                 transcribed_text = "" 

        return transcribed_text

# 处理语音信息
async def handle_voice_message_to_short_summary(update: Update, context: CallbackContext):

    try:
        chat_id = update.effective_chat.id
        bot = context.bot

        # send placeholder message to user
        placeholder_message = await bot.send_message(chat_id=chat_id, text="...")

        # send typing action
        await bot.send_chat_action(chat_id=chat_id, action="typing")

        voice = update.message.voice

        transcribed_text = await voice_to_speech(voice.file_id, context)

        # await message_handle(update, context, message=transcribed_text)
        short_summary = await poe_utils.get_short_summary(transcribed_text)
        text = f"🎤 摘要: <i>{short_summary}</i>"
        
        # await update.message.reply_text(text, parse_mode=ParseMode.HTML)
        parse_mode = ParseMode.HTML
        await context.bot.edit_message_text(text, chat_id=placeholder_message.chat_id, message_id=placeholder_message.message_id, parse_mode=parse_mode)


    except Exception as e:
        error_text = f"Something went wrong during completion. Reason: {e}"
        logger.error(error_text)
        await bot.send_message(chat_id=chat_id, text=error_text)


# 语音信息总结
async def voice_summary_handle(update: Update, context: CallbackContext):

    logging.info("voice_summary_handle runs")

    message = update.message
    voice = None

    if message.reply_to_message and message.reply_to_message.voice:
        file_id = message.reply_to_message.voice.file_id
    elif message.voice:
        file_id = message.voice.file_id
    elif message.audio:
        file_id = message.audio.file_id 
        logging.info("handle a mp3 file...")
    else:
        raise ValueError("No voice message found.")
    

    try:
        bot = context.bot
        chat_id = update.effective_chat.id

        placeholder_message = await bot.send_message(chat_id=chat_id, text="...")
        # send typing action
        await bot.send_chat_action(chat_id=chat_id, action="typing")
   
        transcribed_text = await voice_to_speech(file_id, context)
        text = f"🎤 语音信息内容:\n <i>{transcribed_text}</i>"
        await bot.edit_message_text(text, chat_id=placeholder_message.chat_id, message_id=placeholder_message.message_id, parse_mode=ParseMode.HTML)

        placeholder_message = await bot.send_message(chat_id=chat_id, text="In summary, please wait...")
        # send typing action
        await bot.send_chat_action(chat_id=chat_id, action="typing")


        summary = await poe_utils.get_summary(transcribed_text)
        await bot.edit_message_text(summary, chat_id=placeholder_message.chat_id, message_id=placeholder_message.message_id, parse_mode=ParseMode.HTML)
    
    except Exception as e:
        error_text = f"Something went wrong during completion. Reason: {e}"
        logger.error(error_text)
        await context.bot.send_message(chat_id=chat_id, text=error_text)

# await context.bot.edit_message_text(answer, chat_id=placeholder_message.chat_id, message_id=placeholder_message.message_id, parse_mode=parse_mode)