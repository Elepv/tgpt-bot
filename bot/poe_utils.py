import config
import poe
import logging

#send a message and immediately delete it

token = config.poe_api_token
poe.logger.setLevel(logging.INFO)
client = poe.Client(token)

# for chunk in client.send_message("voicesummary", message, with_chat_break=True,timeout = 180):
#   pass # 不逐句打印
#   print(chunk["text_new"], end="", flush=True)  # 逐句打印
# print(chunk["text"])  # 不逐句打印


async def get_short_summary(text):
    message = text

    for chunk in client.send_message("shortsummary", message, with_chat_break=True,timeout = 180):
      pass # 不逐句打印
      # print(chunk["text_new"], end="", flush=True)  # 逐句打印
    summary = chunk["text"]  # 不逐句打印
    
    return summary

async def get_summary(text):
    message = text

    for chunk in client.send_message("voicesummary", message, with_chat_break=True,timeout = 180):
      pass # 不逐句打印
      # print(chunk["text_new"], end="", flush=True)  # 逐句打印
    summary = chunk["text"]  # 不逐句打印
    
    return summary