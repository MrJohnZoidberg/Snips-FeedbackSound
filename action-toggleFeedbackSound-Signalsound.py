#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import paho.mqtt.client as mqtt
import toml
import json

USERNAME_INTENTS = "domi"
MQTT_BROKER_ADDRESS = "localhost:1883"
MQTT_USERNAME = None
MQTT_PASSWORD = None


def add_prefix(intent_name):
    return USERNAME_INTENTS + ":" + intent_name


# MQTT client to connect to the bus
mqtt_client = mqtt.Client()


def on_connect(client, userdata, flags, rc):
    client.subscribe("hermes/intent/#")


def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode('utf8'))
    intentname = data['intent']['intentName']
    if intentname == add_prefix("toggleFeedbackSound"):
        slots = parse_slots(data)
        text = ""
        if slots['toggle_state'] == "on":
            mqtt_client.publish('hermes/feedback/sound/toggleOn', json.dumps({"siteId": data['siteId']}))
            text = "Der Signalton wurde angeschaltet."
        elif slots['toggle_state'] == "off":
            mqtt_client.publish('hermes/feedback/sound/toggleOff', json.dumps({"siteId": data['siteId']}))
            text = "Der Signalton wurde ausgeschaltet."
        session_id = data['sessionId']
        mqtt_client.publish('hermes/dialogueManager/endSession', json.dumps({'text': text, "sessionId": session_id}))


def parse_slots(data):
    # We extract the slots as a dict
    return {slot['slotName']: slot['value']['value'] for slot in data['slots']}


if __name__ == "__main__":
    snips_config = toml.load('/etc/snips.toml')
    if 'mqtt' in snips_config['snips-common'].keys():
        MQTT_BROKER_ADDRESS = snips_config['snips-common']['mqtt']
    if 'mqtt_username' in snips_config['snips-common'].keys():
        MQTT_USERNAME = snips_config['snips-common']['mqtt_username']
    if 'mqtt_password' in snips_config['snips-common'].keys():
        MQTT_PASSWORD = snips_config['snips-common']['mqtt_password']

    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect(MQTT_BROKER_ADDRESS.split(":")[0], int(MQTT_BROKER_ADDRESS.split(":")[1]))
    mqtt_client.loop_forever()
