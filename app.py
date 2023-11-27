import asyncio
from flask import Flask, request, Response
from botbuilder.schema import Activity
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings

from pchatbot import PizzaChatBot

app = Flask(__name__)
loop = asyncio.get_event_loop()

pizza_bot = PizzaChatBot()

botadaptersettings = BotFrameworkAdapterSettings("", "")
botadapter = BotFrameworkAdapter(botadaptersettings)

@app.route("/api/messages", methods=["POST"])
def messages():
    if "application/json" in request.headers['content-type']:
        json_message = request.json
    else:
        return Response(status=415)
    
    activity = Activity().deserialize(json_message)
    
    async def turn_call(turn_context):
        await pizza_bot.on_turn(turn_context)
        
    task = loop.create_task(botadapter.process_activity(activity,"",turn_call))
    loop.run_until_complete(task)

    return "", 201

if __name__ == "__main__":
    app.run('localhost', 3978)
    