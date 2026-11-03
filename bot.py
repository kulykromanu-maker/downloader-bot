import os
import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
import yt_dlp

# 1. Сюда ты вставляешь токен, который получил от BotFather
BOT_TOKEN = "9021283769:AAEu0CDn3IfWpTMp9Unz8Dz8z_BBsn2qEWo"

# 2. Создаем объект бота
bot = Bot(token=BOT_TOKEN)

# 3. Создаем диспетчер
dp = Dispatcher()

# Обработчик команды /start
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        "Hi! I'm Downloader bot by hachiiiroku.\n"
        "Send me a link and I'll help you to download a video or a track!"
    )

def download_tiktok_video(url: str) -> str:
    ydl_opts = {
        'outtmpl': 'downloads/%(id)s.%(ext)s', # Папка и шаблон для сохранения
        'format': 'mp4',                       # Желаемый формат
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        },
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename

# Обработчик текстовых сообщений (ловим ссылки)
@dp.message()
async def handle_text(message: types.Message):
    user_text = message.text

    # Проверяем, есть ли ссылка на TikTok
    if "tiktok.com" in user_text:
        processing_msg = await message.answer("⏳ Downloading video, wait a few seconds...")

        file_path = None
        try:
            # Запускаем скачивание
            file_path = download_tiktok_video(user_text)

            # Отправляем видео пользователю
            video_file = types.FSInputFile(file_path)
            await message.answer_video(video_file)

            # Удаляем сообщение о загрузке
            await processing_msg.delete()

        except Exception as e:
            await message.answer(f"❌ Error of dowloading a video: {e}")
            # ВСЕГДА удаляем временный файл с диска после отправки (или ошибки)
        finally:
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as ex:
                    logging.error(f"Failed to delete file {file_path}: {ex}")
    else:
        await message.answer("I wait for the TikTok link! Send me it.")

# Запуск процесса поллинга
async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    await dp.start_polling(bot)

# Точка входа в программу
if __name__ == "__main__":
    asyncio.run(main())

