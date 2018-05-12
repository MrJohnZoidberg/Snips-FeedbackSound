#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import paho.mqtt.client as mqtt
import json

# MQTT client to connect to the bus
mqtt_client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    client.subscribe("hermes/intent/domi:toggleFeedbackSound")

def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())
    slots = parse_slots(data)
    session_id = data['sessionId']
    user,intentname = data['intent']['intentName'].split(':')
    if intentname == "toggleFeedbackSound":
        if slots['toggle_state'] == "on":
            mqtt_client.publish('hermes/feedback/sound/toggleOn', json.dumps({"siteId": "default"}))
            text = "Der Signalton wurde angeschaltet."
        elif if slots['toggle_state'] == "off":
            mqtt_client.publish('hermes/feedback/sound/toggleOff', json.dumps({"siteId": "default"}))
            text = "Der Signalton wurde ausgeschaltet."
        mqtt_client.publish('hermes/dialogueManager/endSession',
                            json.dumps({'text': text, "sessionId": session_id}))

def parse_slots(data):
    # We extract the slots as a dict
    return {slot['slotName']: slot['value']['value'] for slot in data['slots']}  # Slotvalue

if __name__ == "__main__":
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect("localhost", 1883)
    mqtt_client.loop_forever()
