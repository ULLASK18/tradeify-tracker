import urllib.request
import re
import json
import os
import sys

STATE_FILE = 'tracked_state.json'
CODES_OUTPUT_FILE = 'tradeify_1296_codes.txt'
CHARSET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
NTFY_TOPIC = "tradeify-lucid-alert"

def send_mobile_alert(title, message, priority="default", tags="bell"):
    url = f"https://ntfy.sh/{NTFY_TOPIC}"
    headers = {
        "Title": title,
        "Priority": priority,
        "Tags": tags
    }
    try:
        req = urllib.request.Request(url, data=message.encode('utf-8'), headers=headers)
        with urllib.request.urlopen(req, timeout=10) as r:
            print(f"[Mobile Alert Sent]: {title}")
    except Exception as e:
        print(f"[Mobile Alert Error]: {e}")

def send_mobile_file(filepath, title="Tradeify Codes File"):
    url = f"https://ntfy.sh/{NTFY_TOPIC}"
    filename = os.path.basename(filepath)
    headers = {
        "Title": title,
        "Filename": filename,
        "Priority": "urgent",
        "Tags": "fire,package"
    }
    try:
        with open(filepath, 'rb') as f:
            data = f.read()
        req = urllib.request.Request(url, data=data, headers=headers, method="PUT")
        with urllib.request.urlopen(req, timeout=20) as r:
            print(f"[Mobile File Sent]: {filename}")
    except Exception as e:
        print(f"[Mobile File Error]: {e}")

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "tweet_id": "2121181285473218802",
        "known_replies": [],
        "confirmed_slots": {},
        "admin_posts": [],
        "last_checked": "",
        "abc_cracked": False
    }

def save_state(state):
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2)

def generate_1296_combinations(a, b, c):
    import random
    combinations = []
    for d in CHARSET:
        for e in CHARSET:
            code = f"TDFY-6{a}SU-{b}3{c}D-Z{d}{e}6"
            combinations.append((d, e, code))
    random.shuffle(combinations)
    
    with open(CODES_OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(f"# TRADEIFY BULL PACK - 1,296 CODE COMBINATIONS\n")
        f.write(f"# Confirmed ABC: A={a}, B={b}, C={c}\n")
        f.write(f"# Total: {len(combinations)} combinations for (D, E)\n\n")
        for d, e, code in combinations:
            f.write(f"{code}  (Slot D: {d}, Slot E: {e})\n")
    return combinations

def check_updates():
    state = load_state()
    url = f"https://x.com/propfirmtrend/status/2121181285473218802"
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Cache-Control': 'no-cache'
    })
    
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error fetching tweet page: {e}")
        return False, f"Fetch error: {e}"

    tid_matches = list(re.finditer(r'edit_tweet_ids\\*":\[\\*"([0-9]+)\\*"\]', html))
    
    new_replies = []
    new_admin_posts = []
    existing_ids = {r.get('id') for r in state.get('known_replies', [])}

    for m in tid_matches:
        tid = m.group(1)
        if tid == "2121181285473218802":
            continue

        pos = m.start()
        window = html[max(0, pos-1200):min(len(html), pos+1200)]
        
        ft_match = re.search(r'full_text\\*":\\*"(.*?)\\*"', window)
        text_content = ""
        if ft_match:
            try:
                text_content = ft_match.group(1).encode('utf-8').decode('unicode_escape')
            except Exception:
                text_content = ft_match.group(1)

        author = "unknown"
        author_match = re.search(r'href=[\"\']/@?([A-Za-z0-9_]+)/status/' + tid, html)
        if author_match:
            author = author_match.group(1)
        else:
            hrefs = re.findall(r'href=[\"\']/@?([A-Za-z0-9_]+)[\"\']', window)
            valid = [h for h in hrefs if h.lower() not in ['i', 'search', 'hashtag', 'home', 'explore', 'notifications']]
            if valid:
                author = valid[0]

        reply_obj = {
            "id": tid,
            "author": author,
            "text": text_content
        }

        if tid not in existing_ids:
            new_replies.append(reply_obj)
            state['known_replies'].append(reply_obj)
            existing_ids.add(tid)

            if author.lower() in ['propfirmtrend', 'iamjminx']:
                new_admin_posts.append(reply_obj)
                state['admin_posts'].append(reply_obj)
                send_mobile_alert(
                    "Admin Reply on Tradeify Hunt!",
                    f"@{author}: {text_content}",
                    priority="high",
                    tags="loudspeaker,rotating_light"
                )

            slot_patterns = [
                r'slot\s+([A-E])\s+is\s+([A-Za-z0-9])',
                r'slot\s+([A-E])[:=]\s*([A-Za-z0-9])',
                r'([A-E])\s*=\s*([A-Za-z0-9])',
                r'correct[^\.\n]*?([A-E])[^\.\n]*?([A-Za-z0-9])'
            ]
            if author.lower() in ['propfirmtrend', 'iamjminx']:
                for pat in slot_patterns:
                    sm = re.search(pat, text_content, re.IGNORECASE)
                    if sm:
                        s_letter = sm.group(1).upper()
                        s_val = sm.group(2).upper()
                        state['confirmed_slots'][s_letter] = s_val
                        send_mobile_alert(
                            f"Slot {s_letter} Confirmed = {s_val}!",
                            f"Verified by @{author}. Current slots: {state['confirmed_slots']}",
                            priority="high",
                            tags="white_check_mark,party_popper"
                        )

    # Check if A, B, and C are all confirmed
    confirmed = state['confirmed_slots']
    if 'A' in confirmed and 'B' in confirmed and 'C' in confirmed and not state.get('abc_cracked'):
        state['abc_cracked'] = True
        combos = generate_1296_combinations(confirmed['A'], confirmed['B'], confirmed['C'])
        print(f"!!! CRACKED ABC: A={confirmed['A']}, B={confirmed['B']}, C={confirmed['C']} !!!")
        
        send_mobile_alert(
            "ABC CRACKED! 1296 Codes Ready!",
            f"Slots confirmed: A={confirmed['A']}, B={confirmed['B']}, C={confirmed['C']}. Delivering codes file now...",
            priority="urgent",
            tags="fire,rotating_light"
        )
        send_mobile_file(CODES_OUTPUT_FILE, f"Tradeify 1296 Codes (A={confirmed['A']}, B={confirmed['B']}, C={confirmed['C']})")

    import datetime
    state['last_checked'] = datetime.datetime.now().isoformat()
    save_state(state)

    print(f"Total replies tracked: {len(state['known_replies'])}")
    print(f"Confirmed slots: {state['confirmed_slots']}")
    return True, state

if __name__ == '__main__':
    # When run directly in GitHub Actions loop or single run
    check_updates()
