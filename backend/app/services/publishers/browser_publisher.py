import asyncio
import os
from playwright.async_api import async_playwright

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
USER_DATA_DIR = r"d:\linkedin_Project\backend\browser_profile"

async def publish_linkedin_zero_click(content: str, image_path: str = None) -> dict:
    """
    Automates zero-click publishing to LinkedIn using local Google Chrome profile.
    1. Opens Chrome with persistent user data so you stay logged in.
    2. Navigates to LinkedIn feed.
    3. Clicks 'Start a post' or opens the post modal.
    4. Pastes the post content and attaches image if provided.
    5. Clicks the 'Post' button automatically.
    """
    os.makedirs(USER_DATA_DIR, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            executable_path=CHROME_PATH,
            headless=False, # Show browser window so user can log in on first run
            args=["--start-maximized", "--no-sandbox", "--disable-blink-features=AutomationControlled"]
        )
        
        page = await browser.new_page()
        await page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded")
        await asyncio.sleep(3)
        
        # Check if user needs to log in
        if "login" in page.url or "checkpoint" in page.url or await page.locator("input#username").count() > 0:
            return {
                "success": False,
                "needs_login": True,
                "message": "LinkedIn is opened. Please log in to your account once in the browser window so your session is saved permanently."
            }
            
        try:
            # Click 'Start a post' button
            start_post_btn = page.locator("button:has-text('Start a post')")
            if await start_post_btn.count() == 0:
                start_post_btn = page.locator(".share-box-feed-entry__trigger")
                
            await start_post_btn.first.click()
            await asyncio.sleep(2)
            
            # Type / paste post content into the editor
            editor = page.locator("div.editor-content, div[role='textbox'], div[aria-label*='post']")
            await editor.first.click()
            await editor.first.fill(content)
            await asyncio.sleep(1)
            
            # Attach image if provided
            if image_path and os.path.exists(image_path):
                file_input = page.locator("input[type='file'][name='file'], input[type='file'][accept*='image']")
                if await file_input.count() > 0:
                    await file_input.first.set_input_files(image_path)
                    await asyncio.sleep(3)
                    
                    # If LinkedIn shows a 'Next' button inside image modal
                    next_btn = page.locator("button:has-text('Next')")
                    if await next_btn.count() > 0:
                        await next_btn.first.click()
                        await asyncio.sleep(2)

            # Click the final 'Post' button automatically
            post_btn = page.locator("button.share-actions__primary-action, button:has-text('Post')")
            await post_btn.last.click()
            await asyncio.sleep(5)
            
            await browser.close()
            return {"success": True, "message": "Post published to LinkedIn automatically with zero clicks!"}
        except Exception as e:
            await browser.close()
            return {"success": False, "error": str(e)}

if __name__ == "__main__":
    test_content = "Testing 100% Zero-Click Autonomous Posting from local engine!"
    res = asyncio.run(publish_linkedin_zero_click(test_content))
    print("Result:", res)
