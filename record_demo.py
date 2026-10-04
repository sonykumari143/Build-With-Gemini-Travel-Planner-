import os
import time
from playwright.sync_api import sync_playwright

ARTIFACT_DIR = "/config/.gemini/antigravity/brain/dfddc32b-c4cf-4fc4-813f-c2c29fa094ab"
APP_URL = "https://travel-planner-frontend-888284866598.us-east1.run.app"

def record_demo():
    os.makedirs(ARTIFACT_DIR, exist_ok=True)
    video_dir = os.path.join(ARTIFACT_DIR, "video_temp")
    os.makedirs(video_dir, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            record_video_dir=video_dir,
            record_video_size={"width": 1280, "height": 800}
        )

        page = context.new_page()
        print("Navigating to App URL...")
        page.goto(APP_URL, wait_until="networkidle")
        time.sleep(3)  # Let UI settle and display header/chips

        # Scenario 1: First Prompt - Plan a 3-day itinerary for Tokyo
        print("Starting Scenario 1: Itinerary planning via chip or typing...")
        chip = page.locator(".prompt-chip").first
        if chip.is_visible():
            print("Clicking first prompt chip...")
            chip.click()
        else:
            prompt_input = page.locator("#input")
            prompt_input.click()
            first_prompt = "Plan a 3-day itinerary for Tokyo with top sights, food, and culture"
            page.keyboard.type(first_prompt, delay=40)
            time.sleep(1)
            send_button = page.locator(".send-btn")
            send_button.click()

        print("Submitted first prompt, waiting for response...")

        # Wait for agent response to complete
        time.sleep(18)
        page.evaluate("window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'})")
        time.sleep(3)

        # Scenario 2: Second Prompt - Richer prompt with tool call & image/video gen
        print("Starting Scenario 2: Richer prompt with tool calls...")
        prompt_input = page.locator("#input")
        prompt_input.click()
        second_prompt = "Find nearby places around Tokyo Tower and generate a custom video of Tokyo Tower at night"
        page.keyboard.type(second_prompt, delay=40)
        time.sleep(1)
        
        send_button = page.locator(".send-btn")
        send_button.click()
        print("Submitted second prompt, waiting for tool responses...")

        # Wait for tool calls, map, and generated video
        time.sleep(30)
        page.evaluate("window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'})")
        time.sleep(5)

        # Save video path
        recorded_path = page.video.path()
        print("Raw video path:", recorded_path)

        context.close()
        browser.close()

        # Move recorded video to artifact directory
        target_video_path = os.path.join(ARTIFACT_DIR, "agent_demo.webm")
        if os.path.exists(recorded_path):
            os.rename(recorded_path, target_video_path)
            print("Successfully saved demo video to:", target_video_path)
            return target_video_path
        else:
            print("Error: Recorded video file not found at", recorded_path)
            return None

if __name__ == "__main__":
    record_demo()
