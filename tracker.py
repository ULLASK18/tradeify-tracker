import urllib.request
import re
import json
import os
import sys

STATE_FILE = 'tracked_state.json'
TRADEIFY_CODES_FILE = 'tradeify_1296_codes.txt'
LUCID_CODES_FILE = 'lucid_combinations.txt'
ALPHANUMERIC = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ALPHABET_ONLY = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
NTFY_TOPIC = "tradeify-lucid-alert"

BASELINE_SEEN_IDS = {
    "2121181285473218802",
    "2121182360049995809",
    "2121181543573934326",
    "2121183838370189494",
    "2121112034985312415",
    "2120910694841524316",
    "2120778618758644143",
    "2121119848382226548",
    "2121113284476866582",
    "2121487762767724738"
}

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

def send_mobile_file(filepath, title="Codes File"):
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
    state = {
        "tradeify": {
            "seen_ids": list(BASELINE_SEEN_IDS),
            "confirmed_slots": {},
            "abc_cracked": False
        },
        "lucid": {
            "seen_ids": list(BASELINE_SEEN_IDS),
            "revealed_pattern": "XC______"
        },
        "last_checked": ""
    }
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                saved = json.load(f)
                if isinstance(saved, dict):
                    for k in ["tradeify", "lucid"]:
                        if k in saved and isinstance(saved[k], dict):
                            state[k].update(saved[k])
                            existing = set(state[k].get("seen_ids", []))
                            state[k]["seen_ids"] = list(existing.union(BASELINE_SEEN_IDS))
                    state["last_checked"] = saved.get("last_checked", "")
        except Exception:
            pass
    return state

def save_state(state):
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2)

def generate_tradeify_1296(a, b, c):
    import random
    combinations = []
    for d in ALPHANUMERIC:
        for e in ALPHANUMERIC:
            code = f"TDFY-6{a}SU-{b}3{c}D-Z{d}{e}6"
            combinations.append((d, e, code))
    random.shuffle(combinations)
    
    with open(TRADEIFY_CODES_FILE, 'w', encoding='utf-8') as f:
        f.write(f"# TRADEIFY BULL PACK - 1,296 CODE COMBINATIONS\n")
        f.write(f"# Confirmed ABC: A={a}, B={b}, C={c}\n")
        f.write(f"# Total: {len(combinations)} combinations for (D, E)\n\n")
        for d, e, code in combinations:
            f.write(f"{code}  (Slot D: {d}, Slot E: {e})\n")
    return combinations

def generate_lucid_combinations(known_prefix, remaining_count=2):
    """
    When 4 more characters are revealed (e.g. XCxxxx), 2 characters remain.
    Generates all 1,296 alphanumeric combinations (36x36), prioritizing the 676
    pure alphabet (A-Z) combinations first since Venom mentioned 'alphabet drops'.
    """
    import random
    letter_combos = []
    other_combos = []
    
    if remaining_count == 2:
        # 1. Pure letters first (26 x 26 = 676)
        for c1 in ALPHABET_ONLY:
            for c2 in ALPHABET_ONLY:
                letter_combos.append(f"LUCIDFLEX25K-{known_prefix}{c1}{c2}")
        random.shuffle(letter_combos)
        
        # 2. Mixed alphanumeric remaining (1296 - 676 = 620)
        for c1 in ALPHANUMERIC:
            for c2 in ALPHANUMERIC:
                code = f"LUCIDFLEX25K-{known_prefix}{c1}{c2}"
                if code not in letter_combos:
                    other_combos.append(code)
        random.shuffle(other_combos)
        
        all_combos = letter_combos + other_combos
        
    elif remaining_count == 1:
        for c in ALPHABET_ONLY:
            letter_combos.append(f"LUCIDFLEX25K-{known_prefix}{c}")
        for c in "0123456789":
            other_combos.append(f"LUCIDFLEX25K-{known_prefix}{c}")
        all_combos = letter_combos + other_combos

    with open(LUCID_CODES_FILE, 'w', encoding='utf-8') as f:
        f.write(f"# LUCID FLEX 25K - {len(all_combos)} COMBINATIONS\n")
        f.write(f"# Known prefix: LUCIDFLEX25K-{known_prefix}\n")
        f.write(f"# Top {len(letter_combos)} are pure alphabets (A-Z)\n\n")
        for c in all_combos:
            f.write(f"{c}\n")
            
    return all_combos

def check_lucid(state):
    l_state = state.setdefault("lucid", {
        "seen_ids": list(BASELINE_SEEN_IDS),
        "revealed_pattern": "XC______"
    })
    
    seen_ids = set(l_state.get("seen_ids", []))
    current_pattern = l_state.get("revealed_pattern", "XC______")
    
    urls = [
        "https://x.com/venom_NeverDies",
        "https://x.com/venom_NeverDies/status/2121487762767724738"
    ]
    
    for url in urls:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Cache-Control': 'no-cache'
        })
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                html = resp.read().decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            continue

        patterns = re.findall(r'LUCIDFLEX25K-([A-Za-z0-9_]{3,12})', html)
        for pat in patterns:
            clean_pat = pat.upper()
            known_chars = clean_pat.replace('_', '')
            curr_known_chars = current_pattern.replace('_', '')
            
            # Trigger whenever a new letter is revealed
            if len(known_chars) > len(curr_known_chars):
                print(f"*** NEW LUCID PATTERN REVEALED: {clean_pat} ***")
                l_state["revealed_pattern"] = clean_pat
                current_pattern = clean_pat
                
                send_mobile_alert(
                    "Lucid Flex 25K: New Letter Revealed!",
                    f"Updated Code: LUCIDFLEX25K-{clean_pat}\nKnown letters ({len(known_chars)}/8): {known_chars}",
                    priority="urgent",
                    tags="key,party_popper"
                )
                
                # When 4 more letters are revealed, 2 remain -> Auto-generate 1,296 codes!
                underscores_left = clean_pat.count('_')
                if 0 < underscores_left <= 2:
                    combos = generate_lucid_combinations(known_chars, remaining_count=underscores_left)
                    send_mobile_alert(
                        f"Lucid Code Ready! {len(combos)} Combos Generated!",
                        f"Only {underscores_left} characters left! Complete codes file attached.",
                        priority="urgent",
                        tags="fire,rotating_light"
                    )
                    send_mobile_file(LUCID_CODES_FILE, f"LucidFlex25K {len(combos)} Codes ({clean_pat})")

        tid_matches = re.findall(r'edit_tweet_ids\\*":\[\\*"([0-9]+)\\*"\]', html)
        for tid in tid_matches:
            seen_ids.add(tid)
            
    l_state["seen_ids"] = list(seen_ids)

def check_tradeify(state):
    t_state = state.setdefault("tradeify", {
        "seen_ids": list(BASELINE_SEEN_IDS),
        "confirmed_slots": {},
        "abc_cracked": False
    })
    
    seen_ids = set(t_state.get("seen_ids", []))
    url = "https://x.com/propfirmtrend/status/2121181285473218802"
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Cache-Control': 'no-cache'
    })
    
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error fetching Tradeify tweet: {e}")
        return

    tid_matches = list(re.finditer(r'edit_tweet_ids\\*":\[\\*"([0-9]+)\\*"\]', html))
    for m in tid_matches:
        tid = m.group(1)
        if tid in seen_ids or tid == "2121181285473218802":
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

        seen_ids.add(tid)

        if author.lower() in ['propfirmtrend', 'iamjminx']:
            slot_patterns = [
                r'slot\s+([A-E])\s+is\s+([A-Za-z0-9])',
                r'slot\s+([A-E])[:=]\s*([A-Za-z0-9])',
                r'correct[^\.\n]*?([A-E])[^\.\n]*?([A-Za-z0-9])'
            ]
            for pat in slot_patterns:
                sm = re.search(pat, text_content, re.IGNORECASE)
                if sm:
                    s_letter = sm.group(1).upper()
                    s_val = sm.group(2).upper()
                    t_state['confirmed_slots'][s_letter] = s_val
                    send_mobile_alert(
                        f"Tradeify: Slot {s_letter} Confirmed = {s_val}!",
                        f"Verified by @{author}. Slots: {t_state['confirmed_slots']}",
                        priority="high",
                        tags="white_check_mark,party_popper"
                    )

    t_state["seen_ids"] = list(seen_ids)

def check_all():
    state = load_state()
    check_tradeify(state)
    check_lucid(state)
    
    import datetime
    state['last_checked'] = datetime.datetime.now().isoformat()
    save_state(state)
    
    print(f"Checked both Tradeify & Lucid at {state['last_checked']}")
    print(f"Lucid pattern: {state.get('lucid', {}).get('revealed_pattern')}")
    print(f"Tradeify slots: {state.get('tradeify', {}).get('confirmed_slots')}")
    return True, state

if __name__ == '__main__':
    check_all()
