import telegram
from telegram import (
    Update,
    # User
    # InlineKeyboardButton,
    # InlineKeyboardMarkup,
    # BotCommand
)
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackContext,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    AIORateLimiter,
    filters
)
from telegram.constants import ParseMode

from pathlib import Path
import tempfile

import pydub
import config
import openai_utils

# 处理语音信息
async def voice_message_handle(update: Update, context: CallbackContext):
    voice = update.message.voice

    # 临时文件存储录音文件
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_dir = Path(tmp_dir)
        voice_ogg_path = tmp_dir / "group_voice.ogg"

        # download 下载语音文件
        voice_file = await context.bot.get_file(voice.file_id)
        await voice_file.download_to_drive(voice_ogg_path)

        # convert to mp3
        voice_mp3_path = tmp_dir / "gourp_voice.mp3"
        pydub.AudioSegment.from_file(voice_ogg_path).export(voice_mp3_path, format="mp3")

        # transcribe
        with open(voice_mp3_path, "rb") as f:
            transcribed_text = await openai_utils.transcribe_audio(f)

            if transcribed_text is None:
                 transcribed_text = ""

        # 发送到群组
        if len(transcribed_text) <= 15:
            text = f"🎤: <i>{transcribed_text}</i>"
        else:
            # 如果消息长度大于15，则使用ChatGPT获取一个12个字以内的总结
            # await message_handle(update, context, message=transcribed_text)
            short_summary = await openai_utils.get_short_summary(transcribed_text)
            text = f"🎤 摘要: <i>{short_summary}</i>"
        
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)