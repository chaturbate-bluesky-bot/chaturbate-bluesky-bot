import os
import requests
import time
from atproto import Client, client_utils
from datetime import datetime

# === CONFIG ===
BLUESKY_HANDLE = os.getenv('BLUESKY_HANDLE')
BLUESKY_PASS = os.getenv('BLUESKY_PASSWORD')
API_URL = "https://chaturbate.com/affiliates/api/onlinerooms/?format=json&wm=T2CSW"
MAX_POSTS_PER_RUN = 4

def main():
    print(f"[{datetime.now()}] 🚀 Starting bot run...")

    try:
        client = Client()
        client.login(BLUESKY_HANDLE, BLUESKY_PASS)
        print("✅ Logged into Bluesky")
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return

    try:
        data = requests.get(API_URL, timeout=15).json()
        print(f"✅ Fetched {len(data)} total online rooms")
    except Exception as e:
        print(f"❌ API fetch failed: {e}")
        return

    # Reliable filter - female public shows only
    filtered = [
        room for room in data
        if room.get('gender') == 'f' and room.get('current_show') == 'public'
    ]
    print(f"✅ {len(filtered)} female public rooms available")

    filtered.sort(key=lambda x: int(x.get('num_users', 0)), reverse=True)

    posted = 0
    for i, room in enumerate(filtered[:MAX_POSTS_PER_RUN]):
        try:
            img_resp = requests.get(room['image_url_360x270'], timeout=10)
            img_bytes = img_resp.content

            subject = (room.get('room_subject', '')[:80] + '...') if len(room.get('room_subject', '')) > 80 else room.get('room_subject', '')

            # === CLICKABLE LINK + WORKING HASHTAGS ===
            watch_link = room['chat_room_url_revshare']
            tb = client_utils.TextBuilder()
            tb.text(f"🔥 LIVE NOW ({room['num_users']} watching)\n\n")
            tb.text(f"{room['username']} • {room['age']} • {room['country'] or '??'}\n")
            tb.text(f"{subject}\n\n👉 ")
            tb.link("Watch free", watch_link)                                   # ← official clickable affiliate link
            tb.text("\n\n#Chaturbate #CamGirls #LiveCams #Adult #nsfw #realnsfw #bskynsfw #nsfwsky")

            client.send_image(
                text=tb,
                image=img_bytes,
                image_alt=f"Live HD cam of {room['username']}"
            )

            print(f"✅ Posted #{i+1}: {room['username']} ({room['num_users']} viewers) — LINK + HASHTAGS WORKING")
            posted += 1
            time.sleep(12)

        except Exception as e:
            print(f"⚠️  Failed to post {room.get('username')}: {e}")

    print(f"[{datetime.now()}] ✅ Run complete — {posted} posts sent\n")

if __name__ == "__main__":
    main()
