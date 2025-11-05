import asyncio
import threading
import time
from asyncio import Lock

data: int = 0
lock: Lock = threading.Lock()


def odd(lock: Lock):
    global data
    print("Running in odd Thread:", threading.get_ident())

    while data < 10:
        if data % 2 == 0:
            with lock:
                data += 1
                print(threading.get_ident(), data)
        else:
            time.sleep(0)


def even(lock: Lock):
    global data
    print("Running in even Thread:", threading.get_ident())

    while data < 10:
        if data % 2 == 1:
            with lock:
                data += 1
                print(threading.get_ident(), data)
        else:
            time.sleep(0)


async def main():
    print("Running in main Thread:", threading.get_ident())
    loop = asyncio.get_running_loop()
    odd_task = loop.run_in_executor(None, odd, lock)
    even_task = loop.run_in_executor(None, even, lock)

    await asyncio.gather(odd_task, even_task)  # runs both at the same time


asyncio.run(main())
