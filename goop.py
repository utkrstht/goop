import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
from random import randint
from copy import deepcopy
from pathlib import Path
import schedule
import time
import threading
import json

# load .env
load_dotenv()
print("loaded env vars")

PRIMARY_USER = os.environ.get("PRIMARY_USER")
TODO_CANVAS_ID = os.environ.get("TODO_CANVAS_ID")
TODO_SECTION_ID = os.environ.get("TODO_SECTION_ID")
PROJECT_CANVAS_ID = os.environ.get("PROJECT_CANVAS_ID")
PROJECT_SECTION_ID = os.environ.get("PROJECT_SECTION_ID")

# easter egg on/off
easter_egg_enabled = False

goals = []
# goals_secondary exists as a temporary copy of goals so we can access and manipulate goals without touching the primary list
goals_secondary = []
goalAsk_threads = set()
goalDone_threads = set()
goals_ask_dialog = ["wowie! you sure have some work! :woa:", "oooo that sounds interesting", "that is goopy yes", "ooooooo"]
goals_done_dialog = ["great job!", "you did alot of work :o", "so... goopy...", "wowie"]

projectAdd_threads = set()

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# import easter egg if user installed the file
file_path = Path("easter_groq.py")
if file_path.is_file():
    SECONDARY_USER = os.environ.get("SECONDARY_USER")
    from easter_groq import generate_message
    easter_egg_enabled = True
else: 
    print("Easter egg unavailable")


##### util helpers
def say_thread(text, channel, client):
    response = client.chat_postMessage(
        channel=channel,
        text=text,
    )
    return response

def say_in_thread(text, say, channel, client, thread_ts):
    if thread_ts:
        response = client.chat_postMessage(
            channel=channel,
            text=text,
            thread_ts=thread_ts,
        )
        return response
    else: 
        # edge cases where thread_ts MAY exist
        say(text)

##### goals management
def load_goals():
    try:
        with open("goals.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    
def save_goals(goals):
    with open("goals.json", "w", encoding="utf-8") as f:
        json.dump(goals, f, indent=4)

def lookup_goal(goal):
    words = goal.split()

    # get biggest (unique?) word to prevent duplicates
    search_term = max(words, key=len)

    response = app.client.canvases_sections_lookup(
    canvas_id=TODO_CANVAS_ID,
    criteria={
        "contains_text": search_term
        }
    )

    return response["sections"][0]["id"]

def add_goal(goal):
    goals = load_goals()
    # since we do not want to touch the primary object, we make an independent copy
    goals_secondary = deepcopy(goals)

    goals_secondary.append({"goal": goal, "done": False, "synced": False})
    # update canvas using secondary object
    update_todo_canvas(goals_secondary)
    section_id = lookup_goal(goal)

    # add goal
    goals.append({"goal": goal, "done": False, "synced": True, "section_id": section_id})
    save_goals(goals)

# this is for removing the unchecked goal as when we update the canvas, it creates a new checkbox
def delete_goal_section(goal):
    goals = load_goals()

    for goal_new in goals:
        if goal_new["goal"] == goal:
            app.client.canvases_edit(canvas_id=TODO_CANVAS_ID, changes=[{"operation": "delete", "section_id": goal_new["section_id"]}])

def mark_goal(goal):
    goals = load_goals()
    
    for goal_new in goals:
        if goal_new["goal"] == goal:
            delete_goal_section(goal)
            goal_new["done"] = True
            # set synced to false so on next update cycle it updates
            goal_new["synced"] = False
            break

    save_goals(goals)
    update_todo_canvas(goals)

def goals_to_markdown(goals_secondary):
    lines = []

    for goal in goals_secondary:
        # only pass goals that aren't synced to prevent the entire goal list from being appended
        if goal.get("synced"):
            continue

        checkbox = "x" if goal["done"] else " "
        lines.append(f"- [{checkbox}] {goal['goal']}")

    return "\n".join(lines)

##### project management
# we don't need anything other than this for now since project ideas don't really need much 
def add_project(project_idea):
    project_idea = f"- [ ] {project_idea}"

    app.client.canvases_edit(canvas_id=PROJECT_CANVAS_ID, changes=[{"operation": "insert_after", "section_id": PROJECT_SECTION_ID, "document_content": {"type": "markdown", "markdown": f"\n{project_idea}"}}])

##### goop activities
@app.message("hi goop")
def message_goop(client, message, say):
    # if invoked in thread, it will reply in thread
    thread_ts = message.get("thread_ts") 
    say_in_thread("hi i'm goop", say, message["channel"], client, thread_ts)
    print("goop was hi'ed")

@app.message("goop say hi")
def message_goop(client, message, say):
    # if invoked in thread, it will reply in thread
    thread_ts = message.get("thread_ts") 
    say_in_thread("hi i'm goop", say, message["channel"], client, thread_ts)
    print("goop was hi'ed")

@app.message("i love goop")
def message_goop(client, message, say):
    # if invoked in thread, it will reply in thread
    thread_ts = message.get("thread_ts") 
    say_in_thread("awww i love you too", say, message["channel"], client, thread_ts)
    print("goop was love'ed")

@app.message("goopy goop")
def message_goop(client, message, say):
    # if invoked in thread, it will reply in thread
    thread_ts = message.get("thread_ts") 
    say_in_thread("goopy", say, message["channel"], client, thread_ts)
    print("goop was gooped")

@app.message("goop tell vro to shut up")
def message_shutup(client, message, say):
    # if invoked in thread, it will reply in thread
    thread_ts = message.get("thread_ts") 
    say_in_thread("vro shut up", say, message["channel"], client, thread_ts)
    print("goop shut someone up")

##### project ideas
@app.message("goop i have a idea")
def project_add(message, client):
    response = say_thread(channel=message["channel"], text=f"what's your project idea? <@{PRIMARY_USER}>", client=client)
    print("goop asked for project idea")
    projectAdd_threads.add(response["ts"])


##### todo stuff
#@app.message("goop ask me my goals")
def todo_update(channel, client):
    # switch to using custom function
    response = say_thread(channel=channel, text=f"what are your goals for today? <@{PRIMARY_USER}>", client=client)
    print("goop asked for goals")
    goalAsk_threads.add(response["ts"])

#@app.message("goop i did alot of work")
def todo_check(channel, client):
    response = say_thread(channel=channel, text=f"what goals did you get done? <@{PRIMARY_USER}>", client=client)
    print("goop asked what goals are done")
    goalDone_threads.add(response["ts"])

# update canvas
def update_todo_canvas(goals_secondary):
    # create checklist in form: - [ ] (goal)
    checklist = goals_to_markdown(goals_secondary)

    # edit canvas
    app.client.canvases_edit(canvas_id=TODO_CANVAS_ID, changes=[{"operation": "insert_after", "section_id": TODO_SECTION_ID, "document_content": {"type": "markdown", "markdown": f"\n{checklist}"}}])

##### event listener functions
def handle_todo_update(event, client, say):
    if event.get("subtype"):
        return
    
    thread_ts = event.get("thread_ts")

    # is it a thread reply?
    if not thread_ts:
        return

    # is it our thread?
    if not thread_ts in goalAsk_threads:
        return

    # is it me?
    if event.get("user") != PRIMARY_USER:
        return
    
    # goals done!
    # wow am i dumb :3
    if event.get("text").lower() in ("that's it", "that's it!", "that's all!", "that's all"):
        goalAsk_threads.remove(thread_ts)
        # say random cool thing lol
        # add custom helper for thread reply
        say_in_thread(goals_ask_dialog[randint(0, len(goals_ask_dialog)-1)], say, event.get("channel"), client=client, thread_ts=thread_ts)
        print("updated todo canvas")
        return
    
    print("goop saw a thread reply from kabom")
    goal = event.get("text")
    add_goal(goal)
    print(f"goop added a goal to goals: {goal}")

def handle_todo_check(event, client, say):
    if event.get("subtype"):
        return
    
    thread_ts = event.get("thread_ts")

    # is it a thread reply?
    if not thread_ts:
        return

    # is it our thread?
    if not thread_ts in goalDone_threads:
        return

    # is it me?
    if event.get("user") != PRIMARY_USER:
        return
    
    if event.get("text").lower() in ("that's it", "that's it!", "that's all!", "that's all"):
        goalDone_threads.remove(thread_ts)
        # say random cool thing lol
        say_in_thread(goals_done_dialog[randint(0, len(goals_done_dialog)-1)], say, event.get("channel"), client=client, thread_ts=thread_ts)
        print("todo check done")
        return
    
    print("goop saw a thread reply from kabom (goals done thread)")
    goal = event.get("text")
    mark_goal(goal)
    print(f"goop updated a goal: {goal}")

def handle_project_add(event, client, say):
    if event.get("subtype"):
        return
    
    thread_ts = event.get("thread_ts")

    # is it a thread reply?
    if not thread_ts:
        return

    # is it our thread?
    if not thread_ts in projectAdd_threads:
        return

    # is it me?
    if event.get("user") != PRIMARY_USER:
        return
    
    print("goop saw a thread reply from kabom (project add thread)")
    project_idea = event.get("text")
    add_project(project_idea)
    say_in_thread("wowie that sounds super cool!", say=say, channel=event.get("channel"), client=client, thread_ts=thread_ts)
    print(f"goop added a project idea: {project_idea}")
    projectAdd_threads.remove(thread_ts)

def easter_egg(event, client, say):
    if not easter_egg_enabled:
        return

    if event.get("subtype"):
        return

    if event.get("user") != SECONDARY_USER:
        return

    # generate awesome reply :3
    awesome_reply = generate_message(event.get("text"))

    thread_ts = event.get("ts") or event.get("thread_ts")

    # send awesome reply!!
    say_in_thread(awesome_reply, say, event.get("channel"), client, thread_ts)

# global message event listener
@app.event("message")
def global_message_event_listener(event, client, say):
    # call todo update handler
    handle_todo_update(event=event, client=client, say=say)

    # call todo check handler
    handle_todo_check(event=event, client=client, say=say)

    # call project add handler
    handle_project_add(event=event, client=client, say=say)
    
    # call easter egg
    easter_egg(event=event, client=client, say=say)

##### scheduler functions
def scheduler_loop():
    print("scheduler start")

    # call todo update handler
    schedule.every().day.at("12:45").do(
        todo_update,
        channel="C0AJTDS75HN",
        client=app.client,
    )
    # call todo check handler
    schedule.every().day.at("21:00").do(
        todo_check,
        channel="C0AJTDS75HN",
        client=app.client,
    )

    while True:
        schedule.run_pending()

        # optimization :3        
        idle_seconds = schedule.idle_seconds()
        print("sleeping for ", idle_seconds)
        time.sleep(idle_seconds)


if __name__ == "__main__":
    threading.Thread(target=scheduler_loop, daemon=True).start()


    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()



    
