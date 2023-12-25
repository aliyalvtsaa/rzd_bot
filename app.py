import asyncio
import logging
from aiogram import Bot, Dispatcher
from handlers import router
from aiogram.fsm.storage.memory import MemoryStorage

from rzd_monitoring import periodic_check
from config import TOKEN
logging.getLogger('WDM').setLevel(logging.WARNING)

async def main():  
    bot = Bot(token=TOKEN)
    dp = Dispatcher(storage = MemoryStorage())
    dp.include_router(router)
    asyncio.create_task(periodic_check())
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, filename='rzd_bot.log', filemode='w')
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Все!')