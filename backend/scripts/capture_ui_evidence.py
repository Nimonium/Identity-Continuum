import os
import time
from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

ARTIFACTS_DIR = os.path.abspath(r"C:\Users\kpaha\.gemini\antigravity-ide\brain\2185d235-8d8b-4af8-bea0-d971b4ab0cd9")
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

def get_driver():
    try:
        options = EdgeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1600,1050")
        options.add_argument("--no-sandbox")
        return webdriver.Edge(options=options)
    except Exception:
        options = ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1600,1050")
        options.add_argument("--no-sandbox")
        return webdriver.Chrome(options=options)

def main():
    print("[*] Launching headless browser to capture real UI evidence...")
    driver = get_driver()
    wait = WebDriverWait(driver, 10)

    try:
        driver.get("http://127.0.0.1:8000/")
        time.sleep(2)

        # 1. Enter Console
        btn_enter = wait.until(EC.element_to_be_clickable((By.ID, "btn-enter-console")))
        btn_enter.click()
        time.sleep(1)

        # 2. Intake Screen Screenshot
        nav_intake = driver.find_element(By.CSS_SELECTOR, '[data-nav="screen-intake"]')
        nav_intake.click()
        time.sleep(0.5)

        # Trigger doc selection & photo capture UI
        btn_capture = driver.find_element(By.ID, "btn-capture-photo")
        btn_capture.click()
        time.sleep(0.8)

        intake_path = os.path.join(ARTIFACTS_DIR, "screenshot_intake.png")
        driver.save_screenshot(intake_path)
        print(f"[OK] Saved Intake Screen: {intake_path}")

        # 3. Scenario 1: Clean Identity (Arthur Pendelton)
        nav_dash = driver.find_element(By.CSS_SELECTOR, '[data-nav="screen-dashboard"]')
        nav_dash.click()
        time.sleep(0.5)

        card_clean = driver.find_element(By.CSS_SELECTOR, '[data-state="clean"]')
        card_clean.click()
        time.sleep(2.0) # Wait for animation and gauge to settle

        clean_path = os.path.join(ARTIFACTS_DIR, "screenshot_results_clean.png")
        driver.save_screenshot(clean_path)
        print(f"[OK] Saved Clean Identity Results: {clean_path}")

        # 4. Scenario 2: Tampered Document (Marcus Vance)
        nav_dash = driver.find_element(By.CSS_SELECTOR, '[data-nav="screen-dashboard"]')
        nav_dash.click()
        time.sleep(0.5)

        card_tampered = driver.find_element(By.CSS_SELECTOR, '[data-state="tampered"]')
        card_tampered.click()
        time.sleep(2.0)

        tampered_path = os.path.join(ARTIFACTS_DIR, "screenshot_results_tampered.png")
        driver.save_screenshot(tampered_path)
        print(f"[OK] Saved Tampered Document Results: {tampered_path}")

        # 5. Scenario 3: Identity Fracture (Elena Vance / Elena Rostova)
        nav_dash = driver.find_element(By.CSS_SELECTOR, '[data-nav="screen-dashboard"]')
        nav_dash.click()
        time.sleep(0.5)

        card_fracture = driver.find_element(By.CSS_SELECTOR, '[data-state="fracture"]')
        card_fracture.click()
        time.sleep(2.0)

        fracture_path = os.path.join(ARTIFACTS_DIR, "screenshot_results_fracture.png")
        driver.save_screenshot(fracture_path)
        print(f"[OK] Saved Identity Fracture Results: {fracture_path}")

        # 6. Graph Screen on Scenario 3
        nav_graph = driver.find_element(By.CSS_SELECTOR, '[data-nav="screen-graph"]')
        nav_graph.click()
        time.sleep(2.0)

        graph_path = os.path.join(ARTIFACTS_DIR, "screenshot_graph_fracture.png")
        driver.save_screenshot(graph_path)
        print(f"[OK] Saved Graph Screen: {graph_path}")

        # 7. Ledger Screen & Verification
        nav_ledger = driver.find_element(By.CSS_SELECTOR, '[data-nav="screen-ledger"]')
        nav_ledger.click()
        time.sleep(1.0)

        btn_verify_ledger = driver.find_element(By.ID, "btn-verify-ledger")
        btn_verify_ledger.click()
        time.sleep(3.0) # Wait for cryptographic verification banner

        ledger_path = os.path.join(ARTIFACTS_DIR, "screenshot_ledger_verified.png")
        driver.save_screenshot(ledger_path)
        print(f"[OK] Saved Ledger Screen: {ledger_path}")

        print("[SUCCESS] All 6 UI evidence screenshots successfully captured!")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
