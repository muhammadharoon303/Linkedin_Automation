import time
import undetected_chromedriver as uc

options = uc.ChromeOptions()
options.add_argument(r"--user-data-dir=d:\linkedin_Project\backend\chrome_automation_profile")
options.add_argument("--start-maximized")

print("\n" + "="*60)
print(">>> OPENING GOOGLE CHROME FOR ONE-TIME LOGIN...")
print(">>> PLEASE ENTER YOUR LINKEDIN EMAIL & PASSWORD IN THE WINDOW.")
print(">>> WAITING UNTIL YOU ARE ON THE FEED...")
print("="*60 + "\n")

driver = uc.Chrome(options=options)
driver.get("https://www.linkedin.com/login")

for i in range(180): # Wait up to 3 minutes
    time.sleep(2)
    current = driver.current_url.lower()
    if "feed" in current or "mynetwork" in current or "messaging" in current:
        print("\n[SUCCESS] Login detected! Profile session saved permanently!")
        time.sleep(3)
        driver.quit()
        exit(0)

print("[TIMEOUT] Login was not completed within 3 minutes.")
driver.quit()
