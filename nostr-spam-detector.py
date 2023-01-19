#!/usr/bin/env python3
#
# Project:      nostr relay spam detection
# Members:      ronaldstoner
#
# Changelog
# 0.1 - Initial PoC
# 0.1.1 - Websocket timeouts

# NOTE: This script is a work in progress. Pubkeys identified should NOT be banned at this time until more accuracy and scoring as well as testing occurs. 

version = "0.1.1"

import json
import asyncio
import websockets
import datetime

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

    # Check if the pubkey has already posted this event content
    if pubkey in pubkey_duplicates and event_content in pubkey_duplicates[pubkey]:
        pubkey_duplicates[pubkey][event_content] += 1
        print(f"Pubkey {pubkey} has posted duplicate content '{event_content}' {pubkey_duplicates[pubkey][event_content]} times")
    else:
        if pubkey not in pubkey_duplicates:
            pubkey_duplicates[pubkey] = {}
        pubkey_duplicates[pubkey][event_content] = 1

if __name__ == "__main__":
    try:
        asyncio.run(connect_to_relay())
        print("The script has finished.")
    except Exception as e:
        print(f"Exception: {e}\nThe script has finished.")
