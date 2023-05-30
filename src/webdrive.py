from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from PIL import Image
import time
import io
from PIL import ImageChops
from selenium.webdriver.common.by import By


def stitch_images(screenshots, height_deltas, output_filename):
    # Get total width from the first screenshot
    total_width = screenshots[0].size[0]
    total_height = sum(screenshot.size[1] for screenshot in screenshots)
    # Create a new image object with the total height and width of all screenshots
    stitched_image = Image.new('RGB', (total_width, total_height))
    # Paste screenshots into new image object
    current_height = 0
    height_deltas.pop(0)
    height_deltas.append(0)
    for (screenshot, height) in list(zip(screenshots,height_deltas)):
        stitched_image.paste(screenshot, (0, current_height))
        current_height += height#screenshot.size[1]
    # Save stitched image
    print(output_filename)
    stitched_image.save(output_filename)
    return output_filename


def screenshot_of_zerion_page(address, _type, filename=''):
    if filename == '':
        filename=f'{address}_{_type}.png'
    valid_types = ['tokens', 'nfts', 'history'] #tokens= /overview in url

    #default
    if _type not in valid_types: _type = 'overview'

    if _type == 'tokens':
        _type == 'overview'
    if 'nft' in _type:
        _type = 'nfts'
     #if type includes 'history'
    if 'history' in _type or 'transactions' in _type:
    #or 'transactions' in type
        _type = 'history'
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--start-maximized")
    # chrome_options.add_argument("--window-size=375x812")  # iPhone X dimensions   

    # Set the webdriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    # Navigate to url
    url = f'https://app.zerion.io/{address}/{_type}'
    driver.get(url)

    # Let the page load
    time.sleep(2)

    try:
        # Wait for up to 10 seconds before throwing a TimeoutException
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Accept']"))
        )
        button.click()
        print("Button clicked!")
    except Exception as e:
        print(f"Button not found or not clickable. Exception: {str(e)}")

    temp_filenames = []
    # Calculate total height of the page
    total_height = driver.execute_script("return document.body.scrollHeight")
    try:
        menubar = driver.find_element(By.CLASS_NAME, "MobileVersionTopBar-m4hzw4-0.igRbyj")
        menubar2 = driver.find_element(By.CLASS_NAME, "MobileVersionSpaceBetween-m4hzw4-1.hIGhpK")
        element = driver.find_element(By.CLASS_NAME, "PageContentColumn-uudlam-0.gfHdoP")
        element2 = driver.find_element(By.CLASS_NAME, "sharedHStack-sc-1qg837v-1.iiBdOd")
        element3 = driver.find_element(By.CLASS_NAME, "SpacerSpacerElement-sc-6ie5tt-0.eiiqPJ")
        driver.execute_script("arguments[0].style.setProperty('display', 'none', 'important');", menubar)
        driver.execute_script("arguments[0].style.setProperty('display', 'none', 'important');", menubar2)
        driver.execute_script("arguments[0].style.setProperty('display', 'none', 'important');", element)
        driver.execute_script("arguments[0].style.setProperty('display', 'none', 'important');", element2)
        driver.execute_script("arguments[0].style.setProperty('display', 'none', 'important');", element3)
    except NoSuchElementException as e:
        print(e)
    #driver.execute_script("arguments[0].style.display = 'none';", element)
    # Initial viewport height (by JavaScript)
    #viewport_height = driver.execute_script("return window.innerHeight")
    viewport_height = 600
    driver.set_window_size(1024, 600)
    
    # Store all screenshots in a list
    screenshots = []
    height_deltas = []
    prev = 0
    # Scroll and capture screenshots
    for offset in range(0, total_height, viewport_height):
        driver.execute_script(f"window.scrollTo(0, {offset});")
        # Wait to load page
        time.sleep(2)
        # Hide scrollbar
        driver.execute_script("document.body.style.overflow = 'hidden';")
        screenshot_as_png = driver.get_screenshot_as_png()
        driver.execute_script("document.body.style.overflow = 'auto';")
        screenshot = Image.open(io.BytesIO(screenshot_as_png))
        screenshots.append(screenshot)
        height = driver.execute_script("return window.scrollY;")
        height_deltas.append(height-prev)
        prev = height
    stitch_images(screenshots, height_deltas, filename)
    print("Saved screenshot as ", filename)
    return 0#stitch_images(temp_filenames, "0x5a68c82e4355968db53177033ad3edcfd62accca_overview.png")
    # Screenshot and save
    screenshot_full_page(driver, )
    # Navigate to url
    driver.delete_all_cookies()  # Clear cookies
    driver.close()
    driver.quit()
