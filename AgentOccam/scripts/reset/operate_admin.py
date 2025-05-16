from playwright.sync_api import sync_playwright
from time import sleep


def automate_magento():
    max_retries = 5  # Maximum number of retries
    retry_count = 0

    while retry_count < max_retries:
        try:
            print(f"🌐 Starting Magento operation... (Attempt {retry_count + 1})")
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)  # Launch the browser in headless mode
                page = browser.new_page()

                # Open Magento admin dashboard
                page.goto("http://<your_base_url>:7780/admin/admin/dashboard/")
                print("✅ Accessed the login page")

                # Enter login credentials
                page.fill("#username", "admin")
                page.fill("#login", "admin1234")

                # Click the login button
                page.click("button.action-login")
                print("✅ Submitted login information")

                # Wait for the dashboard to load
                page.wait_for_selector(".page-header", timeout=20000)
                print("✅ Logged into the dashboard")

                # Navigate to the products page
                page.goto("http://<your_base_url>:7780/admin/catalog/product/")
                page.wait_for_load_state("networkidle")

                # **Retrieve all `<button>` elements**
                buttons = page.locator("button").all()
                print(f"Number of `<button>` elements on the page: {len(buttons)}")

                # **Click button 19**
                if len(buttons) > 19:
                    print("✅ Attempting to click button 19...")
                    buttons[18].click(force=True)  # Select button
                    buttons[19].click(force=True)  # 20 items display button
                    print("✅ Successfully clicked button 19")
                    sleep(5)
                    browser.close()
                    return 1
                else:
                    print("❌ Button 19 was not found")
                    sleep(5)
                    browser.close()
                    return 0

        except Exception as e:
            retry_count += 1
            print(f"❌ An error occurred: {e}")
            if retry_count < max_retries:
                print(f"🔄 Retrying in 10 seconds... (Attempt {retry_count}/{max_retries})")
                sleep(10)
            else:
                print("⚠️ Maximum number of retries reached. Stopping the process.")
                return 0

# Run the function
if __name__ == "__main__":
    success = 0
    while success == 0:
        print("Starting Magento operation...")
        success = automate_magento()
