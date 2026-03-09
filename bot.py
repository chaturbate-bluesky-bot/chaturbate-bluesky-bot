import requests

# Your existing code...

# Function to send a post
def send_post(message):
    chaturbate_link = 'https://chaturbate.com'
    # Wrapping the Chaturbate link in Bluesky facet formatting
    clickable_link = f'@{chaturbate_link}'
    # Update the message to include the clickable link
    updated_message = f'{message} {clickable_link}'
    # Code to send the post
    # requests.post(...) # Sending logic

# Your existing logic...
