import asyncio
from app.services.publishers.browser_publisher import USER_DATA_DIR, CHROME_PATH
from playwright.async_api import async_playwright

async def login_setup():
    print("Launching Google Chrome...")
    print("Please log into your LinkedIn account in the Chrome window that appears.")
    print("Once you see your LinkedIn Feed, you can close the Chrome window or press Enter here.")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            executable_path=CHROME_PATH,
            headless=False,
            args=["--start-maximized"]
        )
        page = await browser.new_page()
        await page.goto("https://www.linkedin.com/login")
        print("\n--> Chrome is open. Log into LinkedIn now. Waiting for login to complete...")
        
        # Wait up to 120 seconds for user to log in and reach the feed
        for _ in range(120):
            await asyncio.sleep(2)
            if "feed" in page.url:
                print("\n[SUCCESS] Login detected! You are now on your LinkedIn Feed.")
                print("Session cookies have been saved permanently in your local backend.")
                await asyncio.sleep(2)
                await browser.close()
                return True
                
        await browser.close()
        return False

if __name__ == "__main__":
    asyncio.run(login_setup())
