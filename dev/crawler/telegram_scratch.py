from telethon import TelegramClient, events, sync
from telethon.tl import types

# 用你的API ID和Hash替换下面的值
api_id = '25859012'
api_hash = '8f6db4c750781a91767f81c84ea0cff7'

# 创建Telegram客户端
client = TelegramClient('session_name', api_id, api_hash)

async def main():
    # 目标频道的用户名或ID
    channel = 'https://t.me/meiriyiwen'
    
    with open('meiriyiwen.txt', 'w', encoding='utf-8') as file:
        # 连接到客户端
        async with client:
            # 访问频道并爬取消息
            async for message in client.iter_messages(channel):
                # 检查消息是否包含链接
                if message.entities:
                    for entity in message.entities:
                        # 如果实体是URL，提取并打印链接
                        if isinstance(entity, types.MessageEntityUrl):
                            url = message.message[entity.offset:entity.offset+entity.length]
                            # 检查链接是否包含telegra.ph
                            if "telegra.ph" in url:
                                file.write(url + '\n')

# 运行客户端
with client:
    client.loop.run_until_complete(main())
