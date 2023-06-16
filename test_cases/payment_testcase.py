import pytest
import time
from selenium import webdriver
from selenium.common import WebDriverException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


@pytest.fixture(scope="module")
def browser():
    # Creating a WebDriver
    chr_options = Options()
    chr_options.add_experimental_option("detach", True)
    global driver, wait
    driver = webdriver.Chrome()
    driver.implicitly_wait(10)
    wait = WebDriverWait(driver, 15)
    driver.maximize_window()

    yield driver

    # After the test is completed, quitting the WebDriver
    driver.quit()


def test_payment(browser):
    # Navigate to the payment page
    driver.get("https://app-staging.qlub.cloud/qr/ae/dummy-checkout/86/_/_/808b16b149")

    # Click on 'Pay now' button
    driver.find_element(By.XPATH, "//span[normalize-space()='Pay now']").click()

    # Click on 'Split bill' button
    driver.find_element(By.XPATH, "//span[normalize-space()='Split bill']").click()

    # Click on 'Pay a custom amount', set any amount, and click on the 'Confirm' button
    driver.find_element(By.CSS_SELECTOR, "button[id='select-custom'] span[class='wrapper']").click()
    driver.find_element(By.ID, "fullWidth").send_keys("1")
    driver.find_element(By.XPATH, "//span[normalize-space()='Confirm']").click()

    # Choose one of the tip options
    driver.find_element(By.ID, "tip_11").click()

    # Enter card information
    # Switch to the 'cardNumber' iframe and enter the card number
    driver.switch_to.frame("cardNumber")
    driver.find_element(By.ID, "checkout-frames-card-number").send_keys("4242424242424242")
    driver.switch_to.default_content()

    # Switch to the 'expiryDate' iframe and enter the expiry date
    driver.switch_to.frame("expiryDate")
    driver.find_element(By.ID, "checkout-frames-expiry-date").send_keys("02/26")
    driver.switch_to.default_content()

    # Switch to the 'cvv' iframe and enter the CVV
    driver.switch_to.frame("cvv")
    driver.find_element(By.ID, "checkout-frames-cvv").send_keys("100")
    driver.switch_to.default_content()

    # Click on the 'Pay' button
    driver.find_element(By.XPATH, "//button[@id='checkout-action-btn']").click()

    # 3D secure page
    time.sleep(5)
    driver.switch_to.frame("cko-3ds2-iframe")
    driver.find_element(By.ID, "password").send_keys("Checkout1!")

    # Click on the 'Continue' button (if available)
    continue_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@id='txtButton']")))
    action = ActionChains(driver)
    try:
        action.click(continue_button).perform()
    except WebDriverException:
        # Ignore the exception and continue execution
        pass

    # Verify whether 'Payment was successful!' message appears or not
    wait.until(EC.visibility_of_element_located((By.XPATH, "//p[contains(text(),'Payment was successful!')]")))
    actual_text = browser.find_element(By.XPATH, "//p[contains(text(),'Payment was successful!')]").text
    assert actual_text == "Payment was successful!"
