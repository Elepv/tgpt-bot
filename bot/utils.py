from datetime import datetime, timezone, timedelta

# 获取当前时间
def get_time_now():
  # 获取东八区当前时间
  shanghai_tz = timezone(offset=timezone(timedelta(hours=8)).utcoffset(None), name='Asia/Shanghai')
  now = datetime.now().astimezone(shanghai_tz).isoformat()
  # return date_string
  return now
