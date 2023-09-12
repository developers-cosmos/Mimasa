import asyncio
import json

import websockets


async def onsuccess(music_filename, speech_filename):
    print("Music Filename: ", music_filename)
    print("Speech Filename: ", speech_filename)


async def onfailure(exc_type, exc_message):
    print("Error Type: ", exc_type)
    print("Error Message: ", exc_message)


async def get_realtime_status(task_id, onsuccess, onfailure):
    async with websockets.connect("ws://localhost:8000/ws/audio_separation/{}/".format(task_id)) as websocket:
        response = await websocket.recv()
        response_json = json.loads(response)
        if response_json["type"] == "success":
            await onsuccess(response_json["music_filename"], response_json["speech_filename"])
        else:
            await onfailure(response_json["exc_type"], response_json["exc_message"])


task_id = "65a9c1eb-451c-4c3d-b970-d7410016e1ad"
asyncio.run(get_realtime_status(task_id, onsuccess, onfailure))


"""
Example 2

import asyncio
import websockets
import json

async def get_realtime_status(task_id):
    async with websockets.connect("ws://localhost:8000/ws/audio_separation/{}/".format(task_id)) as websocket:
        response = await websocket.recv()
        response_json = json.loads(response)
        if response_json["type"] == "success":
            print("Music Filename: ", response_json["music_filename"])
            print("Speech Filename: ", response_json["speech_filename"])
        else:
            print("Error Type: ", response_json["exc_type"])
            print("Error Message: ", response_json["exc_message"])


task_id = "65a9c1eb-451c-4c3d-b970-d7410016e1ad"
asyncio.run(get_realtime_status(task_id))

"""
