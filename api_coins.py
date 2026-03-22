import requests
import time

# --- DATA FROM YOUR LATEST LOGS ---
TOKEN = "Bearer eyJhbGciOiJodHRwOi8vd3d3LnczLm9yZy8yMDAxLzA0L3htbGRzaWctbW9yZSNobWFjLXNoYTI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJPU00uQXV0aGVudGljYXRpb24iLCJleHAiOjE3NzQwNzYxMzUsIm5iZiI6MTc3NDA3NDkzNSwiaHR0cDovL3NjaGVtYXMueG1sc29hcC5vcmcvd3MvMjAwNS8wNS9pZGVudGl0eS9jbGFpbXMvbmFtZWlkZW50aWZpZXIiOiI5NDM5MjY3NDAiLCJzdWIiOjk0MzkyNjc0MCwid29ybGQiOjEsInRlYW0iOiIxNzkzMTEwMDYsMTgiLCJpYXQiOjE3NzQwNzQ5MzV9.vOwnJU2zkvd07xjRJ4pcFBWXdLwo7XdrizRJ2p6DeyE"

HEADERS = {
    "authorization": TOKEN,
    "platformid": "31",
    "appversion": "4.0.95.01",
    "user-agent": "okhttp/5.3.2",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "accept-encoding": "gzip"
}

def run_reward_cycle():
    # STEP 1: START THE VIDEO
    print("Step 1: Starting video...")
    start_url = "https://android.onlinesoccermanager.com/api/v1.1/user/videos/start"
    # For Business Club coins, use 'BusinessClub' or 'Header' as seen in your logs
    requests.post(start_url, headers=HEADERS, data="actionId=BusinessClub&capVariation=0")

    # STEP 2: SIMULATE AD DURATION
    print("Step 2: Simulating ad (35 seconds)...")
    time.sleep(3)

    # STEP 3: MARK AS WATCHED AND GET REWARD ID
    print("Step 3: Marking ad as watched...")
    watched_url = "https://android.onlinesoccermanager.com/api/v1.1/user/videos/watched"
    r1 = requests.post(watched_url, headers=HEADERS, data="actionId=BusinessClub&capVariation=0&rewardVariation=0")
    
    if r1.status_code == 200:
        reward_id = r1.json()[0]['id']
        print(f"       Generated Reward ID: {reward_id}")
        
        # STEP 4: CONSUME THE REWARD (CLAIM COINS)
        print("Step 4: Claiming coins...")
        consume_url = "https://android.onlinesoccermanager.com/api/v1/user/bosscoinwallet/consumereward"
        r2 = requests.post(consume_url, headers=HEADERS, data=f"RewardId={reward_id}")
        
        if r2.status_code == 200:
            print("✅ SUCCESS: Coins added to your account!")
            print(f"       New Balance Info: {r2.text}")
        else:
            print(f"❌ FAILED at Step 4: {r2.status_code} - {r2.text}")
    else:
        print(f"❌ FAILED at Step 3: {r1.status_code} - {r1.text}")

if __name__ == "__main__":
    run_reward_cycle()