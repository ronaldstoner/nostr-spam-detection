# nostr-spam-detection
Scripts to detect spammy nostr content

# Screenshot
<img src="https://github.com/ronaldstoner/nostr-spam-detection/blob/main/images/poc.png?raw=true" alt="A text console showing spammy pubkeys and their content" width="600">

# Spam sucks
This script connects to a remote nostr relay and queries for event type 1. If the script detects the rules in spam.rules it will track the pubkey, event, content, and assign a score. The script will print potentially spammy pubkeys and content once it is completed and has pulled enough info from the remote relay. 

# NOTE
This is a very early proof of concept. Just because your pubkey shows up in the list does NOT mean you are a spammer. The script will iterate and introduce more accuracy over time. 

# TODO
- Class everything
- Save pubkey list to DB
- Save event content to DB record
- Whitelist pubkeys to be removed from results
- Fix scoring rates
- Let user set all variables for scoring, display, event counts
- Stretch: Publish list for relay consumption
