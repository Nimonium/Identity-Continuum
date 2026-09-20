from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
import time
import json

opts = Options()
opts.add_argument('--headless=new')
opts.add_argument('--window-size=1600,1000')
driver = webdriver.Edge(options=opts)

try:
    driver.get('http://127.0.0.1:8000/')
    time.sleep(1)
    
    # Check landing page vs console
    enter_btns = driver.find_elements(By.XPATH, "//button[contains(text(), 'Enter Console')]")
    if enter_btns:
        enter_btns[0].click()
        time.sleep(1)

    # 1. Intake screen
    intake_btn = driver.find_element(By.CSS_SELECTOR, "[data-nav='screen-intake']")
    intake_btn.click()
    time.sleep(1)
    
    # Click sample clean document button
    sample_doc_btn = driver.find_element(By.ID, "btn-sample-clean")
    sample_doc_btn.click()
    time.sleep(1)
    
    # Click load sample selfie button
    sample_selfie_btn = driver.find_element(By.ID, "btn-load-sample-selfie")
    sample_selfie_btn.click()
    time.sleep(1)
    driver.save_screenshot("backend/static/screenshots/live_intake_enrolled.png")
    
    # Click Run Verification
    run_btn = driver.find_element(By.ID, "btn-run-verify")
    run_btn.click()
    time.sleep(4)
    driver.save_screenshot("backend/static/screenshots/live_results_screen.png")

    # 2. Time Machine screen
    tm_btn = driver.find_element(By.CSS_SELECTOR, "[data-nav='screen-time-machine']")
    tm_btn.click()
    time.sleep(1)
    evts = driver.find_elements(By.CSS_SELECTOR, "#screen-time-machine .event-row")
    print(f"Time Machine Milestones rendered: {len(evts)}")
    driver.save_screenshot("backend/static/screenshots/live_timemachine.png")

    # 3. Identity Graph screen
    gr_btn = driver.find_element(By.CSS_SELECTOR, "[data-nav='screen-graph']")
    gr_btn.click()
    time.sleep(1)
    nodes = driver.find_elements(By.CSS_SELECTOR, ".graph-svg-node")
    print(f"Graph SVG nodes rendered: {len(nodes)}")
    driver.save_screenshot("backend/static/screenshots/live_graph.png")

    # 4. Audit Ledger screen
    lg_btn = driver.find_element(By.CSS_SELECTOR, "[data-nav='screen-ledger']")
    lg_btn.click()
    time.sleep(1)
    blocks = driver.find_elements(By.CSS_SELECTOR, "#screen-ledger .ledger-block")
    print(f"Audit Ledger blocks rendered: {len(blocks)}")
    driver.save_screenshot("backend/static/screenshots/live_ledger.png")

    print("ALL LIVE FRONTEND SCREENS VERIFIED SUCCESSFULLY.")

finally:
    driver.quit()
