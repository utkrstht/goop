import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

# load .env
load_dotenv()
print("loaded env vars")

kaboom = "U092KBRD5SB"
goal_threads = set()

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# goop activities
@app.message("hi goop")
def message_goop(say):
    say("hi i'm goop")
    print("goop was hi'ed")

@app.message("goop say hi")
def message_goop(say):
    say("hi i'm goop")
    print("goop was hi'ed")

# todo stuff
@app.message("goop ask me my goals for today please")
def todo_create(message, client):
    # use this weird ass thing to get thread_ts
    response = client.chat_postMessage(
        channel=message["channel"],
        text=f"what are your goals for today? <@{kaboom}>"
    )
    print("goop asked for goals")
    goal_threads.add(response["ts"])

# handle goals thread reply
@app.event("message")
def handle_todo_update(event, say):
    if event.get("subtype"):
        return
    
    thread_ts = event.get("thread_ts")

    # is it a thread reply?
    if not thread_ts:
        return

    # is it our thread?
    if not thread_ts in goal_threads:
        return

    # is it me?
    if event.get("user") != kaboom:
        return
    
    print("goop saw a thread reply from kabom")
    goals = event.get("text")
    say(text=f"```{goals}```", thread_ts=thread_ts)

if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()