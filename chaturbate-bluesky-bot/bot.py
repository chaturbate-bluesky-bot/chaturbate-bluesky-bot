import os
import requests
import time
from atproto import Client, models
from datetime import datetime

# === CONFIG ===
BLUESKY_HANDLE = os.getenv('BLUESKY_HANDLE')
BLUESKY_PASS = os.getenv('BLUESKY_PASSWORD')
API_URL = "https://chaturbate.com/affiliates/api/onlinerooms/?format=json&wm=T2CSW"
MAX_POSTS_PER_RUN = 4
POST_EVERY_HOURS = 1

def main():
    client = Client()
    client.login(BLUESKY_HANDLE, BLUESKY_PASS)

    # Fetch live rooms
    data = requests.get(API_URL).json()

    # Smart filter (high-converting rooms only)
    filtered = [
        room for room in data
        if room['gender'] == 'f' 
        and room['current_show'] == 'public'
        and room['is_hd']
        and int(room['num_users']) >= 50
    ]

    # Sort by viewers (most popular first)
    filtered.sort(key=lambda x: int(x['num_users']), reverse=True)

    for i, room in enumerate(filtered[:MAX_POSTS_PER_RUN]):
        try:
            # Download thumbnail (360x270 is perfect size & fast)
            img_resp = requests.get(room['image_url_360x270'])
            img_bytes = img_resp.content

            # Compelling post text (under 300 chars)
            subject = room['room_subject'][:80] + '...' if len(room['room_subject']) > 80 else room['room_subject']
            
            # Build post text with clickable link using Bluesky facets
            watch_link = room['chat_room_url_revshare']
            link_text = "Watch free"
            
            text = f"🔥 LIVE NOW ({room['num_users']} watching)\n\n" \
                   f"{room['username']} • {room['age']} • {room['country'] or '??'}\n" \
                   f"{subject}\n\n" \
                   f"👉 {link_text}: {watch_link}\n\n" \
                   f"#nsfw #realnsfw #bskynsfw #nsfwsky"

            # Create facet to make the link clickable
            link_start = text.find(link_text)
            link_end = link_start + len(link_text)
            
            facets = [
                models.Facet(
                    index=models.indices.ByteSlice(
                        byte_start=len(text[:link_start].encode('utf-8')),
                        byte_end=len(text[:link_end].encode('utf-8'))
                    ),
                    features=[
                        models.UriFeature(uri=watch_link)
                    ]
                )
            ]

            # Post with image + alt text and facets for clickable link
            client.send_image(
                text=text,
                image=img_bytes,
                image_alt=f"Live HD cam thumbnail of {room['username']} - {room['room_subject'][:50]}",
                facets=facets
            )

            print(f"Posted: {room['username']}")
            time.sleep(15)

        except Exception as e:
            print(f"Error posting {room['username']}: {e}")

    print(f"Run finished at {datetime.now()}")

if __name__ == "__main__":
    main()
