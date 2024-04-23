import asyncio
import time

from aiogram import Bot, Dispatcher, types
import ssl
from aiohttp import TCPConnector, ClientSession

API_TOKEN = "6800317608:AAGJN9DuVMM5CWCGcCN5Rz5p2WTJCN0CjzI"
CHAT_ID = -1002099577880


async def queue_process(process_id, config_id, machine_id):
    """

    :param process_id:
    :param config_id:
    :param machine_id:
    """
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    connector = TCPConnector(ssl=ssl_context)
    async with ClientSession(connector=connector) as session:
        async with session.post(
            url="https://rpa.magnum.kz:8443/enqueue",
            json={"process": process_id, "config": config_id, "machines": [machine_id]},
        ) as response:
            if response.status == 200:
                return 200
            else:
                print()
                return response.status


async def send_message(chat_id, text, token):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": text}

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    connector = TCPConnector(ssl=ssl_context)
    async with ClientSession(connector=connector) as session:
        async with session.post(url, json=data) as response:
            return await response.json()


async def check_for_commands(token, try_num):

    print("Checking")

    if try_num == 0:
        await send_message(CHAT_ID, "Пришлите код из СМС в виде: \n/XXXXXX\nГде ХХХХХХ - 6-значный код. Обязательно напишите слэш(/) в начале", token)
    else:
        await send_message(CHAT_ID, "Неверный код!\n\nПришлите код из СМС в виде: \n/XXXXXX\nГде ХХХХХХ - 6-значный код. Обязательно напишите слэш(/) в начале", token)

    url = f"https://api.telegram.org/bot{token}/getUpdates"
    offset = None  # Идентификатор первого обновления, которое будет получено

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    connector = TCPConnector(ssl=ssl_context)

    found = False
    code = None

    async with ClientSession(connector=connector) as session:
        while True:
            params = {"timeout": 30}
            if offset is not None:
                params["offset"] = offset

            current_time = int(time.time())
            thirty_seconds_ago = current_time - 30

            async with session.get(url, params=params) as response:
                updates = await response.json()

            if updates["ok"] and updates["result"]:
                for update in updates["result"]:
                    message = update.get("message", {})
                    message_time = message.get("date", 0)

                    if message_time < thirty_seconds_ago:
                        # Обновление offset для получения следующего обновления
                        offset = update["update_id"] + 1
                        continue  # Пропускаем сообщения, старше 30 секунд
                    chat_id = message.get("chat", {}).get("id")
                    text = str(message.get("text", "")).replace('/', '').replace(' ', '')

                    print(chat_id)
                    print(text)
                    is_6_digit_num = False
                    try:
                        formatted_text = int(text)
                        print('#', text, formatted_text)
                        if isinstance(formatted_text, int) and len(text) == 6:
                            is_6_digit_num = True
                    except:
                        is_6_digit_num = False

                    # Обработка команды /start для SELEKTIV_CHAT_ID
                    if is_6_digit_num and chat_id == CHAT_ID:
                        print("6 digit num!")
                        await send_message(chat_id, "Достоверный код", token)
                        found = True
                        code = text
                        break

                    else:
                        print("NOT a 6 digit num!")
                        await send_message(chat_id, "Мне нужен 6 значный код в виде /XXXXXX", token)

                    offset = update["update_id"] + 1
            if found:
                break
            await asyncio.sleep(30)  # Пауза перед следующей проверкой

    if found:
        return code
        # raise asyncio.CancelledError


async def main_tg_bot(var):
    code = await check_for_commands(API_TOKEN, var)
    return code


def a():

    asyncio.run(main_tg_bot(var))


if __name__ == "__main__":
    var = 'LOL'
    # asyncio.run(main_tg_bot(var))
    a()
