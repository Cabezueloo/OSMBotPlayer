import requests

# --- DATA FROM YOUR LATEST HAR FILE ---
URL = "https://android.onlinesoccermanager.com/api/v1.1/user/videos/watched"

# This token was extracted from your capture at 07:42 AM
TOKEN = "Bearer eyJhbGciOiJodHRwOi8vd3d3LnczLm9yZy8yMDAxLzA0L3htbGRzaWctbW9yZSNobWFjLXNoYTI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJPU00uQXV0aGVudGljYXRpb24iLCJleHAiOjE3NzQwNzYxMzUsIm5iZiI6MTc3NDA3NDkzNSwiaHR0cDovL3NjaGVtYXMueG1sc29hcC5vcmcvd3MvMjAwNS8wNS9pZGVudGl0eS9jbGFpbXMvbmFtZWlkZW50aWZpZXIiOiI5NDM5MjY3NDAiLCJzdWIiOjk0MzkyNjc0MCwid29ybGQiOjEsInRlYW0iOiIxNzkzMTEwMDYsMTgiLCJpYXQiOjE3NzQwNzQ5MzV9.vOwnJU2zkvd07xjRJ4pcFBWXdLwo7XdrizRJ2p6DeyE"

HEADERS = {
    "authorization": TOKEN,
    "platformid": "31",
    "appversion": "4.0.95.01",
    "user-agent": "okhttp/5.3.2",
    "Content-Type": "application/x-www-form-urlencoded",
    "accept-encoding": "gzip"
}

# The parameters for the Stadium Timer reward
DATA = {
    "actionId": "StadiumTimer",
    "capVariation": "0",
    "rewardVariation": "0"
}

def do_post():
    print(f"Sending POST to {URL}...")
    response = requests.post(URL, headers=HEADERS, data=DATA)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")

if __name__ == "__main__":
    do_post()