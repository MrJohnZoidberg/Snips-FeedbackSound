#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import paho.mqtt.client as mqtt
import json

# MQTT client to connect to the bus
mqtt_client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    client.subscribe("hermes/intent/domi:toggleFeedbackSound")

def toggle_sound(client, userdata, msg):
    slots = parse_slots(msg)
    session_id = json.loads(msg.payload.decode("utf-8"))['sessionId']
    if slots['toggle_state'] == "on":
        mqtt_client.publish('hermes/feedback/sound/toggleOn', json.dumps({"siteId": "default"}))
        text = "Der Signalton wurde aktiviert."
    else:
        mqtt_client.publish('hermes/feedback/sound/toggleOff', json.dumps({"siteId": "default"}))
        text = "Der Signalton wurde deaktiviert."
    mqtt_client.publish('hermes/dialogueManager/endSession',
                        json.dumps({'text': text, "sessionId": session_id}))

def parse_slots(msg):
    # We extract the slots as a dict
    data = json.loads(msg.payload.decode("utf-8"))
    return {slot['slotName']: slot['value']['value'] for slot in data['slots']}  # Slotvalue

if __name__ == "__main__":
    mqtt_client.on_connect = on_connect
    mqtt_client.message_callback_add("hermes/intent/domi:toggleFeedbackSound", toggle_sound)
    mqtt_client.connect("localhost", 1883)
    mqtt_client.loop_forever()
