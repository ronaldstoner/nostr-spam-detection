#!/usr/bin/env python3
#
# Project:      nostr relay spam detection
# Members:      ronaldstoner
#
# NOTE: This script is a work in progress. Pubkeys identified should NOT be banned at this time until more accuracy and scoring as well as testing occurs. 

version = "0.1.2"

import json
import asyncio
import websockets
import datetime
import re

# Timeout to close relay websocket
relay_timeout=5

# Different relays may give different results. Some timeout, some loop, some keep alive.
#relay = "wss://brb.io"
#relay = "wss://nostr.rocks"
#relay = "wss://nostr.bitcoiner.social"
#relay = "wss://relayer.fiatjaf.com"
#relay = "wss://nostr.onsats.org"
#relay = "wss://nostr-relay.wlvs.space"
#relay = "wss://nostr-pub.wellorder.net"
relay = "wss://relay.stoner.com"
#relay = "wss://nostr.fmt.wiz.biz"
#relay = "wss://relay.nostr.bg"
#relay = "wss://relay.damus.io"
#relay = "wss://relay.snort.social"

# Dictionary to store pubkeys and their duplicate event count
pubkey_duplicates = {}
# Dictionary to store pubkeys and their event count within a given time window
pubkey_burst = {}

# Load spam rules
with open('spam.rules', 'r') as f:
    spam_rules = json.load(f)

async def connect_to_relay():
    print("Connecting to websocket...")
    async with websockets.connect(relay, ping_interval=30) as relay_conn:
        print(f"Connected to {relay}")

        # Send a REQ message to subscribe to note events
        print("Subscribing to event types = 1")
        await relay_conn.send(json.dumps(["REQ", "subscription_id", {"kinds": [1]}]))

        while True:
            try:
                event = await asyncio.wait_for(relay_conn.recv(), timeout=relay_timeout)
                event = json.loads(event)
                if event[0] == "EVENT" and event[2]["kind"] == 1:
                    await handle_event(event)
            except asyncio.TimeoutError:
                print("Timeout occurred, closing websocket.")
                await relay_conn.close()
                break
            except Exception as e:
                print(f"Error occurred: {e}")
                await relay_conn.close()
                break

async def handle_event(event):
    content = event[2]
    pubkey = content["pubkey"]
    event_content = content["content"]
    event_score = 0

    # Check if the pubkey has already posted this event content
    if pubkey in pubkey_duplicates and event_content in pubkey_duplicates[pubkey]:
        pubkey_duplicates[pubkey][event_content] += 1
        event_score = spam_rules["001"]["weight"]
        print(f"Pubkey {pubkey} has posted duplicate content '{event_content}' {pubkey_duplicates[pubkey][event_content]} times. Event score: {event_score}")
    else:
        if pubkey not in pubkey_duplicates:
            pubkey_duplicates[pubkey] = {}
        pubkey_duplicates[pubkey][event_content] = 1

    # Check if the pubkey is sending a large burst of messages
    now = datetime.datetime.now()
    if pubkey in pubkey_burst:
        if (now - pubkey_burst[pubkey]["last_message_time"]).seconds <= spam_rules["002"]["window"]:
            pubkey_burst[pubkey]["message_count"] += 1
            if pubkey_burst[pubkey]["message_count"] > spam_rules["002"]["value"]:
                event_score += spam_rules["002"]["weight"]
                print(f"Pubkey {pubkey} has sent a large burst of messages. Event score: {event_score}")
        else:
            pubkey_burst[pubkey]["message_count"] = 1
    else:
        pubkey_burst[pubkey] = {"message_count": 1, "last_message_time": now}

    #Check if the event content has excessive use of capital letters
    if re.search(spam_rules["003"]["regex"], event_content):
        event_score += spam_rules["003"]["weight"]
        print(f"Pubkey {pubkey} has used excessive capital letters in the event content. Event score: {event_score}")

if __name__ == "__main__":
    try:
        asyncio.run(connect_to_relay())
        print("The script has finished.")
    except Exception as e:
        print(f"Exception: {e}\nThe script has finished.")

