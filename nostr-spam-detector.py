#!/usr/bin/env python3
#
# Project:      nostr relay spam detection
# Members:      ronaldstoner
#
# NOTE: This script is a work in progress. Pubkeys identified should NOT be banned at this time until more accuracy and scoring as well as testing occurs.

version = "0.1.3.2"

import asyncio
import json
import re
import websockets
from itertools import islice

relay_timeout = 5     # Timeout to close relay websocket
ping_keepalive = 30       # Ping keep alive time
min_spam_score = 300  # Arbitrary minimum overall spam score to filter final results

# Different relays may give different results. Some timeout, some loop, some keep alive.
#relay = "wss://brb.io"
#relay = "wss://nostr.rocks"
#relay = "wss://nostr.bitcoiner.social"
#relay = "wss://relayer.fiatjaf.com"
#relay = "wss://nostr.onsats.org"
#relay = "wss://nostr-relay.wlvs.space"
relay = "wss://nostr-pub.wellorder.net"
#relay = "wss://relay.stoner.com"
#relay = "wss://nostr.fmt.wiz.biz"
#relay = "wss://relay.nostr.bg"
#relay = "wss://relay.damus.io"
#relay = "wss://relay.snort.social"

# Load spam rules
with open('spam.rules', 'r') as f:
    spam_rules = json.load(f)

# Dictionary to store pubkeys and their duplicate event count
pubkey_duplicates = {}
# Dictionary to store pubkeys and their event count within a given time window
pubkey_burst = {}
# Dictionary to store the pubkeys and their spamming scores
pubkey_tally = {}
# Dictionary to store the rules violated and the count of each
violated_rules = {}

# Iterate over the keys in the spam_rules
for key in spam_rules:
    if key.startswith("00"):
        violated_rules[key] = {"description": spam_rules[key]["description"], "count": 0}

async def connect_to_relay():
    print("Connecting to websocket...")
    async with websockets.connect(relay, ping_interval=ping_keepalive) as relay_conn:
        print(f"Connected to {relay}")

        # Send a REQ message to subscribe to note events
        print("Subscribing to event types = 1")
        await relay_conn.send(json.dumps(["REQ", "subscription_id", {"kinds": [1]}]))

        print(f"Gathering data from {relay}...")
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
    event_timestamp = content["created_at"]
    event_score = 0
    event_rules = []
    event_examples = []

    # Check if the event content has only emojis (old manual reactions)
    if all(ord(c) > 127 for c in event_content):
        #drop the event
        return

    # 001 - Check if the pubkey has already posted this event content
    if pubkey in pubkey_duplicates and event_content in pubkey_duplicates[pubkey]:
        pubkey_duplicates[pubkey][event_content] += 1
        event_score = spam_rules["001"]["weight"]
        event_rules.append("001")
        event_examples.append(event_content)
    else:
        if pubkey not in pubkey_duplicates:
            pubkey_duplicates[pubkey] = {}
        pubkey_duplicates[pubkey][event_content] = 1

    # 002 - Check if the pubkey is sending a large burst of messages
    if pubkey in pubkey_burst:
        time_since_last_event = event_timestamp - pubkey_burst[pubkey]["last_event_timestamp"]
        if time_since_last_event <= spam_rules["002"]["window"]:
            pubkey_burst[pubkey]["event_count"] += 1
            if pubkey_burst[pubkey]["event_count"] > spam_rules["002"]["value"]:
                event_score += spam_rules["002"]["weight"]
                event_rules.append("002")
                violated_rules["002"]["count"] += 1
        else:
            # reset event_count if the time_since_last_event is greater than the window time
            pubkey_burst[pubkey]["event_count"] = 1
    else:
        pubkey_burst[pubkey] = {"event_count": 1, "last_event_timestamp": event_timestamp}

    #003 - Check if the event content has excessive use of capital letters
    if re.search(spam_rules["003"]["regex"], event_content):
        event_score += spam_rules["003"]["weight"]
        event_rules.append("003")
        violated_rules["003"]["count"] += 1
        event_examples.append(event_content)
    if pubkey not in pubkey_tally:
        pubkey_tally[pubkey] = {"score": event_score, "rules": event_rules, "examples": event_examples}
    else:
        pubkey_tally[pubkey]["score"] += event_score
        pubkey_tally[pubkey]["rules"].extend(event_rules)
        pubkey_tally[pubkey]["examples"].extend(event_examples)

if __name__ == "__main__":
    try:
        asyncio.run(connect_to_relay())
        print("\nSpammy pubkeys and their total score:\n")
        for pubkey, values in sorted(pubkey_tally.items(), key=lambda x: x[1]['score'], reverse=True):
            if values['rules'] != []:
                event_count = sum(values['rules'].count(r) for r in set(values["rules"]))
                if values['score'] >= min_spam_score:
                    print(f"Pubkey: {pubkey}\nTotal Score: {values['score']}")
                    print("Rules violated:")
                    for rule in set(values["rules"]):
                        print(f" - {rule} ({spam_rules[rule]['description']}) - {values['rules'].count(rule)} times")
                    print("Examples of spam messages:")
                    for example in islice(set(values["examples"]),5):
                        print(f" - {example}")
                    print("\n")
        print("The script has finished.")
    except Exception as e:
        print(f"Exception: {e}\nThe script has finished.")
