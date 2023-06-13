import config
import asyncio

from notion_client import AsyncClient

import utils

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# database_id = "f05180116fa54b009643148abc23ed97"
# notion_token = config.notion_token
# notion_page_id = ""

class NotionClient:

    # def __init__(self, notion_token, database_id) -> None:
    def __init__(self) -> None:
        notion_token = config.notion_token
        database_id = "f05180116fa54b009643148abc23ed97"

        self.database_id = database_id
        self.client = AsyncClient(auth=notion_token)
    
    # 新建数据库条目
    async def write_row(self, speak_time, abstract=None, topic=None, user_id=None):
        
        # response_data = await self.client.pages.create(
        #     **{
        #         "parent": {
        #             "database_id": database_id
        #         },
        #         "properties": {
        #             "Abstract": {"title": [{"text": {"content": abstract}}]},
        #             "Topic": {"rich_text": [{"text": {"content": topic}}]},
        #             "Speaker": {"people": [{"id": user_id}]},
        #             "Speak_Time": {"date": {"start": speak_time}}
        #         }
        #     }
        # )

        properties = {
            "Speak_Time": {"date": {"start": speak_time}},
            "Abstract": {"title": [{"text": {"content": abstract}}]} if abstract else {},
            "Topic": {"rich_text": [{"text": {"content": topic}}]} if topic else {},
            "Speaker": {"people": [{"id": user_id}]} if user_id else {},
        }

        response_data = await self.client.pages.create(
            **{
                "parent": {
                    "database_id": self.database_id
                },
                "properties": {k:v for k,v in properties.items() if v}
            }
        )

        return response_data

    # 加入文本块
    async def write_text_block(self, page_id, text_block):
        await self.client.blocks.children.append(
            block_id = page_id,
            children = [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": text_block
                                }
                            }
                        ]
                    }
                }
            ]
        )

async def test():
    client = NotionClient()

    abstract = "abstract test3"
    topic = "topic test 3"
    speak_time = utils.get_time_now()
    user_id = "28236a9a-da36-4486-8a7f-535350791102"  # Crie Elep

    response_data = await client.write_row(speak_time=speak_time, abstract=abstract, user_id=user_id)

    added_db_id = response_data['id']

    await client.write_text_block(page_id=added_db_id, text_block="hellow world!")

if __name__ == '__main__':
    # 测试用例
    asyncio.run(test())