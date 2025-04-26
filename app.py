from flask import Flask, request
import telegram
import os

app = Flask(__name__)

# 读取环境变量
BOT_TOKEN = os.environ.get("BOT_TOKEN")
SHEET_ID = os.environ.get("SHEET_ID")
SHEET_TAB = os.environ.get("SHEET_TAB", "Sheet1")  # 默认Sheet页名为Sheet1
bot = telegram.Bot(token=BOT_TOKEN)

# 简单内存数据库（正式版应接Google Sheet）
tasks = {}
next_task_id = 1

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    global next_task_id
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    if update.message:
        chat_id = update.message.chat.id
        text = update.message.text.strip()

        if text == "/start" or text == "/help":
            bot.send_message(chat_id=chat_id, text="\u4f60\u597d\uff0c\u6211\u662f\u4efb\u52a1\u7ba1\u7406Bot\u3002\n\u547d\u4ee4\uff1a\n/\u65b0\u589e\u4efb\u52a1 \u521b\u5efa\u4efb\u52a1\n/\u4efb\u52a1\u5217\u8868 \u67e5\u770b\u4efb\u52a1\n/\u5b8c\u6210\u4efb\u52a1 [\u4efb\u52a1ID] \u6807\u8bb0\u5b8c\u6210")

        elif text == "/\u65b0\u589e\u4efb\u52a1":  # /新增任务
            bot.send_message(chat_id=chat_id, text="\u8bf7\u53d1\u9001\u4efb\u52a1\u5185\u5bb9\uff08\u76f4\u63a5\u56de\u590d\uff09")
            tasks[chat_id] = {"status": "waiting_content"}

        elif text == "/\u4efb\u52a1\u5217\u8868":  # /任务列表
            message = "\u5f53\u524d\u4efb\u52a1\uff1a\n"
            for tid, task in tasks.items():
                if isinstance(tid, int):
                    message += f"#{tid}: {task['content']} [{task['state']}]\n"
            bot.send_message(chat_id=chat_id, text=message if message != "\u5f53\u524d\u4efb\u52a1\uff1a\n" else "\u6682\u65e0\u4efb\u52a1")

        elif text.startswith("/\u5b8c\u6210\u4efb\u52a1"):
            try:
                _, task_id = text.split()
                task_id = int(task_id)
                if task_id in tasks:
                    tasks[task_id]["state"] = "\u5df2\u5b8c\u6210"
                    bot.send_message(chat_id=chat_id, text=f"\u4efb\u52a1 #{task_id} \u5df2\u6807\u8bb0\u4e3a\u5b8c\u6210\u3002")
                else:
                    bot.send_message(chat_id=chat_id, text="\u672a\u627e\u5230\u8be5\u4efb\u52a1ID")
            except Exception as e:
                bot.send_message(chat_id=chat_id, text="\u8bf7\u6839\u636e\u683c\u5f0f\uff1a/\u5b8c\u6210\u4efb\u52a1 [ID]\u64cd\u4f5c")

        elif chat_id in tasks and tasks[chat_id].get("status") == "waiting_content":
            tasks[next_task_id] = {"content": text, "state": "\u5f85\u529e"}
            bot.send_message(chat_id=chat_id, text=f"\u4efb\u52a1 #{next_task_id} \u5df2\u521b\u5efa\uff01")
            next_task_id += 1
            del tasks[chat_id]

    return "ok"

@app.route("/")
def index():
    return "Task Bot is running."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
