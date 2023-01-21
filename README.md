# nostr-spam-detection
Scripts to detect spammy nostr content

# Screenshot
<img src="https://github.com/ronaldstoner/nostr-spam-detection/blob/main/images/poc.png?raw=true" alt="A text console showing spammy pubkeys and their content" width="600">

# Spam sucks
This script is used to detect note spam on the nostr decentralized event-based system, using a specific relay and set of rules to detect spam. It connects to a websocket endpoint on a relay, subscribes to events of a specific type, and receives events. It then checks each event against a set of predefined spam rules, which include checking for duplicate events and high burst of events from a specific public key, and assigns a score to the event based on the number of rules it violates. The script keeps track of the total score for each public key, and flags those that exceed a certain threshold as potential spammers. This is a work in progress and should not be used to ban any public keys until further testing and scoring is done.

# NOTE
This is a very early proof of concept. Just because your pubkey shows up in the list does NOT mean you are a spammer. The script will iterate and introduce more accuracy over time. 

# Donations
If you find this script useful or decide to use any of it's methods feel free to donate any spare sats you may have. This goes a long way to fueling the caffiene needed for late night development. 

⚡Alby: stoner@getalby.com 

# TODO
- DMs
- Class everything
- Save pubkey list to DB
- Save event content to DB record with associated data
- Output final pubkey list to csv based on min score
- ~~Introduce timing component (what is the time between pubkey posts?)~~ (FALSE POSITIVE: bots)
- ~~Detection of messages bursts based on timestamp~~
- ~~Scoring and confidence rates~~
- ~~Don't track emojis~~ and reactions
- Whitelist pubkeys to be removed from results
- Adjust scoring rates
- Let user set all variables for scoring, display, event counts
- Front end client all the things
- Stretch: Publish list for relay consumption
