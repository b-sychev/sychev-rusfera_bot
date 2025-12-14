import asyncio
from data_manager import get_all_requests, update_request_status
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_pending_requests():
    """Проверяет заявки и меняет статус (имитация работы с внешним сервисом)."""
    requests = get_all_requests()
    for req in requests:
        if req['status'] == 'Принята в обработку':
            await asyncio.sleep(2)
            new_status = 'На диагностике'
            update_request_status(req['number'], new_status)
            logger.info(f"Заявка {req['number']} переведена в статус: {new_status}")
        elif req['status'] == 'На диагностике':
            await asyncio.sleep(3)
            new_status = 'Ожидает запчастей'
            update_request_status(req['number'], new_status)
            logger.info(f"Заявка {req['number']} переведена в статус: {new_status}")

async def start_reminder_service():
    """Фоновая задача для проверки заявок каждые 10 секунд."""
    while True:
        await check_pending_requests()
        await asyncio.sleep(10)