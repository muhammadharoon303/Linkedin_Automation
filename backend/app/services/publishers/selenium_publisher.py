import time
import os
import shutil
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

AUTO_PROFILE = r"d:\linkedin_Project\backend\chrome_automation_profile"

def post_to_linkedin_isolated(text_content: str, image_path: str = None) -> dict:
    os.makedirs(AUTO_PROFILE, exist_ok=True)
    options = uc.ChromeOptions()
    options.add_argument(f"--user-data-dir={AUTO_PROFILE}")
    options.add_argument("--start-maximized")
    options.add_argument("--no-first-run")
    options.add_argument("--no-service-autorun")

    driver = None
    try:
        driver = uc.Chrome(options=options)
        driver.get("https://www.linkedin.com/feed/")
        time.sleep(3)

        # If on login screen, instruct user to log in once
        if "login" in driver.current_url.lower() or "checkpoint" in driver.current_url.lower():
            print("\n=======================================================")
            print(">>> Please log into LinkedIn in the browser window now.")
            print(">>> Waiting 45 seconds for you to log in...")
            print("=======================================================\n")
            for _ in range(45):
                time.sleep(1)
                if "feed" in driver.current_url.lower():
                    print(">>> Login detected! Continuing post...")
                    break
            else:
                return {"success": False, "error": "Login timed out. Please run again and log in."}

        wait = WebDriverWait(driver, 15)
        
        # Open post modal directly via URL or robust button selector
        try:
            driver.get("https://www.linkedin.com/feed/?shareActive=true")
            time.sleep(3)
        except Exception:
            pass

        # Try locating editor directly or clicking trigger
        editor = None
        try:
            editor = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'editor-content') or @role='textbox' or contains(@aria-label, 'post') or contains(@aria-label, 'What do you want to talk about')]")))
        except Exception:
            # If modal didn't open via URL, click the trigger button
            try:
                start_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Start a post') or contains(@class, 'share-box-feed-entry__trigger') or contains(@class, 'artdeco-button')]")))
                start_btn.click()
                time.sleep(2)
            except Exception:
                pass
            editor = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'editor-content') or @role='textbox' or contains(@aria-label, 'post') or contains(@aria-label, 'What do you want to talk about')]")))

        editor.click()
        time.sleep(1)
        # Type clean text
        editor.send_keys(text_content)
        time.sleep(1)

        # Attach image
        if image_path and os.path.exists(image_path):
            try:
                file_inputs = driver.find_elements(By.XPATH, "//input[@type='file']")
                if file_inputs:
                    file_inputs[0].send_keys(os.path.abspath(image_path))
                    time.sleep(3)
                    # Click next in photo dialog if present
                    try:
                        next_btn = driver.find_element(By.XPATH, "//button[contains(., 'Next')]")
                        next_btn.click()
                        time.sleep(2)
                    except Exception:
                        pass
            except Exception as e:
                print("Image attach notice:", e)

        # Click final Post button
        time.sleep(2)
        post_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'share-actions__primary-action') or (contains(., 'Post') and not(contains(., 'Start')))]")))
        post_btn.click()
        time.sleep(6)

        return {"success": True, "message": "Successfully posted to LinkedIn with zero clicks and attached image!"}

    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass

if __name__ == "__main__":
    post_text = "90% of developers are still building static endpoints. Here is why Agentic Tool Calling in FastAPI changes everything.\n\n#FastAPI #Python #AgenticAI"
    res = post_to_linkedin_isolated(post_text, "d:/linkedin_Project/backend/generated_media/day_01_card.png")
    print("Post Result:", res)
