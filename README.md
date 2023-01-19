# nostr-spam-detection
Scripts to detect spammy nostr content

# Screenshot
<img src="https://github.com/ronaldstoner/nostr-spam-detection/blob/main/images/poc.png?raw=true" alt="A text console showing spammy pubkeys and their content" width="600">

# Spam sucks
This script connects to a remote nostr relay and queries for event type 1. If the script detects multiple posts containing the same content, it flags the pubkey and counts the amount of spammy posts. 

# NOTE
This is a very early proof of concept. Just because your pubkey shows up in the list does NOT mean you are a spammer. The script will iterate and introduce more accuracy over time. 

# TODO
- Class everything
- Save pubkey list to DB
- Save event content to DB record
- Introduce timing component (what is the time between pubkey posts?) (FALSE POSITIVE: bots)
- Publish list for relay consumption
- Detection of messages bursts based on timestamp
- Scoring and confidence rates
