import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
from random import randint

# load .env
load_dotenv()
print("loaded env vars")

PRIMARY_USER = os.environ.get("PRIMARY_USER")
SECONDARY_USER = os.environ.get("SECONDARY_USER")
CANVAS_ID = os.environ.get("TODO_CANVAS_ID")
SECTION_ID = os.environ.get("TODO_SECTION_ID")

goals = []
goal_threads = set()
goals_done_dialog = ["wowie! you sure have some work! :woa:", "oooo that sounds interesting", "that is goopy yes", "ooooooo"]

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

##### goop activities
@app.message("hi goop")
def message_goop(say):
    say("hi i'm goop")
    print("goop was hi'ed")

@app.message("goop say hi")
def message_goop(say):
    say("hi i'm goop")
    print("goop was hi'ed")

##### todo stuff
@app.message("goop ask me my goals for today please")
def todo_create(message, client):
    # make sure no one abuses 
    if message["user"] != PRIMARY_USER:
        return
    
    # use this weird ass thing to get thread_ts    
    response = client.chat_postMessage(
        channel=message["channel"],
        text=f"what are your goals for today? <@{PRIMARY_USER}>"
    )
    print("goop asked for goals")
    goal_threads.add(response["ts"])

# updating canvas
def update_todo_canvas():
    # create checklist in form: - [ ] (goal)
    checklist = "\n".join(f"- [ ] {goal}" for goal in goals)

    # edit canvas
    app.client.canvases_edit(canvas_id=CANVAS_ID, changes=[{"operation": "insert_after", "section_id": SECTION_ID, "document_content": {"type": "markdown", "markdown": f"\n{checklist}"}}])

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
    if event.get("user") != PRIMARY_USER:
        return
    
    # goals done!
    # wow am i dumb :3
    if event.get("text").lower() == "that's it!" or event.get("text").lower() == "that's it":
        goal_threads.remove(thread_ts)
        # say random cool thing lol
        say(goals_done_dialog[randint(0, len(goals_done_dialog)-1)])
        update_todo_canvas()
        print("updated todo canvas")
        return
    
    print("goop saw a thread reply from kabom")
    goal = event.get("text")
    goals.append(goal)
    print(f"goop added a goal to goals: {goal}")


if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()