
import time
import logging
from contextlib import contextmanager

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger(__name__)

BASE_URL = "https://crex.com"
DEFAULT_TIMEOUT = 20  # seconds


def _chrome_options() -> Options:
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument(
       
    )
    # Suppress images / CSS to speed things up
    prefs = {
       
    }
    opts.add_experimental_option("prefs", prefs)
    return opts


@contextmanager
def get_driver():
    
    driver = webdriver.Chrome(options=_chrome_options())
    driver.set_page_load_timeout(60)
    try:
        yield driver
    finally:
        driver.quit()


def wait_for(driver, css_selector: str, timeout: int = DEFAULT_TIMEOUT):
    
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
    )


def safe_text(element, css: str, default: str = "") -> str:
    """Return stripped text of the first child matching `css`, or default."""
    try:
        return element.find_element(By.CSS_SELECTOR, css).text.strip()
    except NoSuchElementException:
        return default


def safe_texts(element, css: str) -> list[str]:
    
    try:
        return [el.text.strip() for el in element.find_elements(By.CSS_SELECTOR, css)]
    except Exception:
        return []


def click_tab(driver, tab_name: str, timeout: int = DEFAULT_TIMEOUT) -> bool:
 
  
    try:
        tabs = WebDriverWait(driver, timeout).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul.tab-list li, .tab-item, nav a"))
        )
        for tab in tabs:
            if tab_name.lower() in tab.text.lower():
                driver.execute_script("arguments[0].click();", tab)
                time.sleep(1.5)
                return True
    except TimeoutException:
        pass
    logger.warning("Tab '%s' not found", tab_name)
    return False


def scroll_to_bottom(driver, pause: float = 1.0) -> None:
    """Scroll down until no new content loads."""
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
