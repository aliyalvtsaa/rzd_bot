import asyncio
import logging
import sys
from dotenv import load_dotenv
import os
from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from config import TOKEN
from handlers import router
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
 
 
from rzd_monitoring import periodic_check

async def main():  
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    check_task = asyncio.create_task(periodic_check())
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Все!')