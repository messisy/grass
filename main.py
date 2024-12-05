import os
import uuid
import aiohttp
import argparse
from datetime import datetime, timezone
from fake_useragent import UserAgent
from colorama import *

green = Fore.LIGHTGREEN_EX
red = Fore.LIGHTRED_EX
magenta = Fore.LIGHTMAGENTA_EX
white = Fore.LIGHTWHITE_EX
black = Fore.LIGHTBLACK_EX
reset = Style.RESET_ALL
yellow = Fore.LIGHTYELLOW_EX


class Grass:
    def __init__(self, userid):
        self.userid = userid
        self.ses = aiohttp.ClientSession()

    def log(self, msg):
        now = datetime.now(tz=timezone.utc).isoformat(" ").split(".")[0]
        print(f"{black}[{now}] {reset}{msg}{reset}")

    async def start(self):
        max_retry = 9999999999
        retry = 1
        useragent = UserAgent().random
        headers = {
            "Host": "proxy2.wynd.network:4600",
            "Connection": "Upgrade",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "User-Agent": useragent,
            "Upgrade": "websocket",
            "Origin": "chrome-extension://lkbnfiajjmbhnfledhphioinpickokdi",
            "Sec-WebSocket-Version": "13",
            "Accept-Language": "zh-CN,zh;q=0.9",
        }

        # WebSocket URL
        websocket_url = "ws://proxy2.wynd.network:80/"  # 使用 ws:// 协议
        # websocket_url = "wss://proxy2.wynd.network:443/"  # 如果需要加密，切换到 wss://

        while True:
            try:
                if retry >= max_retry:
                    self.log(f"{yellow}重试次数已达最大限制，跳过连接！")
                    await self.ses.close()
                    return
                async with self.ses.ws_connect(
                    websocket_url,
                    headers=headers,
                    timeout=1000,
                    autoclose=False,
                    # ssl=False  # 如果需要忽略 SSL 错误，可以取消注释此行
                ) as wss:
                    res = await wss.receive_json()
                    auth_id = res.get("id")
                    if auth_id is None:
                        self.log(f"{red}认证ID为空，连接失败！")
                        return None
                    auth_data = {
                        "id": auth_id,
                        "origin_action": "AUTH",
                        "result": {
                            "browser_id": uuid.uuid5(uuid.NAMESPACE_URL, useragent).__str__(),
                            "user_id": self.userid,
                            "user_agent": useragent,
                            "timestamp": int(datetime.now().timestamp()),
                            "device_type": "desktop",
                            "version": "4.26.2",
                            "desktop_id": "lkbnfiajjmbhnfledhphioinpickokdi",
                        },
                    }
                    await wss.send_json(auth_data)
                    self.log(f"{green}成功连接到服务器！{reset}")
                    retry = 1
                    while True:
                        ping_data = {
                            "id": uuid.uuid4().__str__(),
                            "version": "1.0.0",
                            "action": "PING",
                            "data": {},
                        }
                        await wss.send_json(ping_data)
                        self.log(f"{white}发送 {green}PING {white}到服务器!")
                        pong_data = {"id": "F3X", "origin_action": "PONG"}
                        await wss.send_json(pong_data)
                        self.log(f"{white}发送 {magenta}PONG {white}到服务器!")
                        await countdown(120)
            except KeyboardInterrupt:
                await self.ses.close()
                exit()
            except Exception as e:
                self.log(f"{red}错误: {white}{e}")
                retry += 1
                continue


async def countdown(t):
    for i in range(t, 0, -1):
        minute, seconds = divmod(i, 60)
        hour, minute = divmod(minute, 60)
        seconds = str(seconds).zfill(2)
        minute = str(minute).zfill(2)
        hour = str(hour).zfill(2)
        print(f"等待时间：{hour}:{minute}:{seconds} ", flush=True, end="\r")
        await asyncio.sleep(1)


async def main():
    os.system("cls" if os.name == "nt" else "clear")
    print(
        f"""
    {green}  Gass 2.0
    {green}  本脚本由 L先生 提供，无任何收费！！！ 
    {green}  请勿倒卖，请遵守开源精神！
    {green}  QQ：214376358
    {green}  开始种草!go go go
          """
    )
    userid = open("userid.txt", "r").read().strip()
    if len(userid) <= 0:
        print(f"{red}错误: {white}请先输入您的用户ID！")
        exit()
    tasks = [Grass(userid).start()]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    try:
        import asyncio

        if os.name == "nt":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
    except KeyboardInterrupt:
        exit()
