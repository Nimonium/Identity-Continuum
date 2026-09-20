import os
import time
import json
import requests
from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "http://127.0.0.1:8000"
STATIC_SCREENSHOTS_DIR = os.path.abspath(r"backend/static/screenshots")
ARTIFACTS_DIR = os.path.abspath(r"C:\Users\kpaha\.gemini\antigravity-ide\brain\2185d235-8d8b-4af8-bea0-d971b4ab0cd9")
os.makedirs(STATIC_SCREENSHOTS_DIR, exist_ok=True)
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

def save_dual_screenshot(driver, filename):
    p1 = os.path.join(STATIC_SCREENSHOTS_DIR, filename)
    p2 = os.path.join(ARTIFACTS_DIR, filename)
    driver.save_screenshot(p1)
    driver.save_screenshot(p2)
    print(f"  [SCREENSHOT CAPTURED] -> {filename}")
    return p1

def get_driver():
    options = EdgeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1600,1050")
    options.add_argument("--no-sandbox")
    options.set_capability("goog:loggingPrefs", {"browser": "ALL"})
    try:
        return webdriver.Edge(options=options)
    except Exception:
        c_options = ChromeOptions()
        c_options.add_argument("--headless=new")
        c_options.add_argument("--disable-gpu")
        c_options.add_argument("--window-size=1600,1050")
        c_options.add_argument("--no-sandbox")
        c_options.set_capability("goog:loggingPrefs", {"browser": "ALL"})
        return webdriver.Chrome(options=c_options)

def main():
    report_data = {
        "scenarios": {},
        "edge_cases": {},
        "latencies": {},
        "ledger": {},
        "console_logs": []
    }

    print("================================================================================")
    print("      IDENTITY CONTINUUM — COMPREHENSIVE UI REGRESSION TEST SUITE              ")
    print("================================================================================")

    driver = get_driver()
    wait = WebDriverWait(driver, 10)

    try:
        driver.get(BASE_URL)
        time.sleep(2)

        # Enter console
        btn_enter = wait.until(EC.element_to_be_clickable((By.ID, "btn-enter-console")))
        btn_enter.click()
        time.sleep(1)

        # --------------------------------------------------------------------------
        # 1. SCENARIO 1: CLEAN IDENTITY (Arthur Pendelton)
        # --------------------------------------------------------------------------
        print("\n[*] Executing Scenario 1: Clean Identity (Arthur Pendelton)...")
        nav_dash = driver.find_element(By.CSS_SELECTOR, '[data-nav="screen-dashboard"]')
        nav_dash.click()
        time.sleep(0.5)

        card_clean = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-state="clean"]')))
        
        t_start = time.perf_counter()
        card_clean.click()
        wait.until(EC.visibility_of_element_located((By.ID, "screen-results")))
        wait.until(lambda d: d.find_element(By.ID, "res-gauge-txt").text.strip() != "")
        time.sleep(1.2)
        t_ui_clean = time.perf_counter() - t_start
        report_data["latencies"]["scenario_clean"] = round(t_ui_clean, 3)

        save_dual_screenshot(driver, "regression_clean_results.png")

        score_clean = driver.find_element(By.ID, "res-gauge-txt").text.strip()
        name_clean = driver.find_element(By.ID, "res-name").text.strip()
        fracture_banner = driver.find_element(By.ID, "fracture-banner")
        is_fracture_visible = "hidden" not in fracture_banner.get_attribute("class")

        # Fetch Raw JSON
        res_api_clean = requests.post(f"{BASE_URL}/api/verify", json={"scenario": "clean"}).json()
        report_data["scenarios"]["clean"] = {
            "ui_score": score_clean,
            "ui_name": name_clean,
            "fracture_banner_visible": is_fracture_visible,
            "ui_latency_sec": round(t_ui_clean, 3),
            "raw_json": res_api_clean
        }
        print(f"  -> UI Score: {score_clean} | Name: {name_clean} | Fracture Banner Visible: {is_fracture_visible} | UI Latency: {t_ui_clean:.3f}s")

        # --------------------------------------------------------------------------
        # 2. SCENARIO 2: TAMPERED DOCUMENT (Marcus Vance)
        # --------------------------------------------------------------------------
        print("\n[*] Executing Scenario 2: Tampered Document (Marcus Vance)...")
        nav_dash.click()
        time.sleep(0.5)

        card_tampered = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-state="tampered"]')))
        
        t_start = time.perf_counter()
        card_tampered.click()
        wait.until(EC.visibility_of_element_located((By.ID, "screen-results")))
        wait.until(lambda d: d.find_element(By.ID, "res-gauge-txt").text.strip() != "")
        time.sleep(1.2)
        t_ui_tampered = time.perf_counter() - t_start
        report_data["latencies"]["scenario_tampered"] = round(t_ui_tampered, 3)

        save_dual_screenshot(driver, "regression_tampered_results.png")

        score_tampered = driver.find_element(By.ID, "res-gauge-txt").text.strip()
        name_tampered = driver.find_element(By.ID, "res-name").text.strip()
        is_fracture_visible = "hidden" not in driver.find_element(By.ID, "fracture-banner").get_attribute("class")

        res_api_tampered = requests.post(f"{BASE_URL}/api/verify", json={"scenario": "tampered"}).json()
        report_data["scenarios"]["tampered"] = {
            "ui_score": score_tampered,
            "ui_name": name_tampered,
            "fracture_banner_visible": is_fracture_visible,
            "ui_latency_sec": round(t_ui_tampered, 3),
            "raw_json": res_api_tampered
        }
        print(f"  -> UI Score: {score_tampered} | Name: {name_tampered} | Fracture Banner Visible: {is_fracture_visible} | UI Latency: {t_ui_tampered:.3f}s")

        # --------------------------------------------------------------------------
        # 3. SCENARIO 3: IDENTITY FRACTURE (Elena Rostova / Vance) & Cross-Screen Consistency
        # --------------------------------------------------------------------------
        print("\n[*] Executing Scenario 3: Identity Fracture (Elena Rostova / Vance)...")
        nav_dash.click()
        time.sleep(0.5)

        card_fracture = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-state="fracture"]')))
        
        t_start = time.perf_counter()
        card_fracture.click()
        wait.until(EC.visibility_of_element_located((By.ID, "screen-results")))
        wait.until(lambda d: d.find_element(By.ID, "res-gauge-txt").text.strip() != "")
        time.sleep(1.2)
        t_ui_fracture = time.perf_counter() - t_start
        report_data["latencies"]["scenario_fracture"] = round(t_ui_fracture, 3)

        save_dual_screenshot(driver, "regression_fracture_results.png")

        score_fracture = driver.find_element(By.ID, "res-gauge-txt").text.strip()
        name_fracture = driver.find_element(By.ID, "res-name").text.strip()
        is_fracture_visible = "hidden" not in driver.find_element(By.ID, "fracture-banner").get_attribute("class")
        fracture_text = driver.find_element(By.ID, "fracture-banner-desc").text.strip()

        # Capture Fracture Time Machine
        nav_tm = driver.find_element(By.CSS_SELECTOR, '[data-nav="screen-time-machine"]')
        nav_tm.click()
        time.sleep(1.5)
        save_dual_screenshot(driver, "regression_fracture_timemachine.png")

        # Capture Fracture Graph
        nav_graph = driver.find_element(By.CSS_SELECTOR, '[data-nav="screen-graph"]')
        nav_graph.click()
        time.sleep(1.5)
        save_dual_screenshot(driver, "regression_fracture_graph.png")

        res_api_fracture = requests.post(f"{BASE_URL}/api/verify", json={"scenario": "fracture"}).json()
        report_data["scenarios"]["fracture"] = {
            "ui_score": score_fracture,
            "ui_name": name_fracture,
            "fracture_banner_visible": is_fracture_visible,
            "fracture_text": fracture_text,
            "ui_latency_sec": round(t_ui_fracture, 3),
            "raw_json": res_api_fracture
        }
        print(f"  -> UI Score: {score_fracture} | Name: {name_fracture} | Fracture Banner Visible: {is_fracture_visible} | UI Latency: {t_ui_fracture:.3f}s")
        print(f"  -> Fracture Text: {fracture_text}")

        # --------------------------------------------------------------------------
        # 4. EDGE CASE A: NON-DOCUMENT IMAGE UPLOAD FLOW
        # --------------------------------------------------------------------------
        print("\n[*] Executing Edge Case A: Non-Document Image Upload Flow...")
        nav_intake = driver.find_element(By.CSS_SELECTOR, '[data-nav="screen-intake"]')
        nav_intake.click()
        time.sleep(0.5)

        driver.execute_script("""
            const vc = document.getElementById('bio-capture-view');
            const vs = document.getElementById('bio-success-view');
            if (vc) vc.classList.remove('hidden');
            if (vs) vs.classList.add('hidden');
            const docInput = document.getElementById('upload-doc');
            const photoInput = document.getElementById('upload-photo');
            if (docInput) docInput.value = '';
            if (photoInput) photoInput.value = '';
        """)

        non_doc_path = os.path.abspath("backend/static/documents/random_scenery.jpg")
        live_photo_path = os.path.abspath("backend/static/faces/live_arthur.jpg")

        doc_input = driver.find_element(By.ID, "upload-doc")
        photo_input = driver.find_element(By.ID, "upload-photo")
        doc_input.send_keys(non_doc_path)
        driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", doc_input)
        time.sleep(0.3)
        photo_input.send_keys(live_photo_path)
        driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", photo_input)
        time.sleep(0.5)

        btn_run = driver.find_element(By.ID, "btn-run-verify")
        t_start = time.perf_counter()
        btn_run.click()
        wait.until(EC.visibility_of_element_located((By.ID, "screen-results")))
        wait.until(lambda d: d.find_element(By.ID, "res-gauge-txt").text.strip() != "")
        time.sleep(1.2)
        t_ui_nondoc = time.perf_counter() - t_start
        report_data["latencies"]["edge_case_nondoc"] = round(t_ui_nondoc, 3)

        save_dual_screenshot(driver, "edge_case_nondoc.png")
        score_nondoc = driver.find_element(By.ID, "res-gauge-txt").text.strip()
        name_nondoc = driver.find_element(By.ID, "res-name").text.strip()

        with open(non_doc_path, "rb") as f_doc, open(live_photo_path, "rb") as f_live:
            res_api_nondoc = requests.post(
                f"{BASE_URL}/api/verify-upload",
                files={"doc_file": ("random_scenery.jpg", f_doc, "image/jpeg"), "live_file": ("live_arthur.jpg", f_live, "image/jpeg")}
            ).json()

        report_data["edge_cases"]["non_document"] = {
            "ui_score": score_nondoc,
            "ui_name": name_nondoc,
            "ui_latency_sec": round(t_ui_nondoc, 3),
            "raw_json": res_api_nondoc
        }
        print(f"  -> UI Score: {score_nondoc} | Name: {name_nondoc} | UI Latency: {t_ui_nondoc:.3f}s")

        # --------------------------------------------------------------------------
        # 5. EDGE CASE B: BIOMETRIC FACE MISMATCH FLOW
        # --------------------------------------------------------------------------
        print("\n[*] Executing Edge Case B: Biometric Face Mismatch Flow...")
        nav_intake.click()
        time.sleep(0.5)

        driver.execute_script("""
            const vc = document.getElementById('bio-capture-view');
            const vs = document.getElementById('bio-success-view');
            if (vc) vc.classList.remove('hidden');
            if (vs) vs.classList.add('hidden');
            const docInput = document.getElementById('upload-doc');
            const photoInput = document.getElementById('upload-photo');
            if (docInput) docInput.value = '';
            if (photoInput) photoInput.value = '';
        """)

        arthur_doc_path = os.path.abspath("backend/static/documents/passport_arthur_clean.jpg")
        marcus_live_path = os.path.abspath("backend/static/faces/live_marcus.jpg")

        doc_input = driver.find_element(By.ID, "upload-doc")
        photo_input = driver.find_element(By.ID, "upload-photo")
        doc_input.send_keys(arthur_doc_path)
        driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", doc_input)
        time.sleep(0.3)
        photo_input.send_keys(marcus_live_path)
        driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", photo_input)
        time.sleep(0.5)

        btn_run = driver.find_element(By.ID, "btn-run-verify")
        t_start = time.perf_counter()
        btn_run.click()
        wait.until(EC.visibility_of_element_located((By.ID, "screen-results")))
        wait.until(lambda d: d.find_element(By.ID, "res-gauge-txt").text.strip() != "")
        time.sleep(1.2)
        t_ui_mismatch = time.perf_counter() - t_start
        report_data["latencies"]["edge_case_biomismatch"] = round(t_ui_mismatch, 3)

        save_dual_screenshot(driver, "edge_case_biomismatch.png")
        score_mismatch = driver.find_element(By.ID, "res-gauge-txt").text.strip()
        name_mismatch = driver.find_element(By.ID, "res-name").text.strip()

        with open(arthur_doc_path, "rb") as f_doc, open(marcus_live_path, "rb") as f_live:
            res_api_mismatch = requests.post(
                f"{BASE_URL}/api/verify-upload",
                files={"doc_file": ("passport_arthur_clean.jpg", f_doc, "image/jpeg"), "live_file": ("live_marcus.jpg", f_live, "image/jpeg")}
            ).json()

        report_data["edge_cases"]["biometric_mismatch"] = {
            "ui_score": score_mismatch,
            "ui_name": name_mismatch,
            "ui_latency_sec": round(t_ui_mismatch, 3),
            "raw_json": res_api_mismatch
        }
        print(f"  -> UI Score: {score_mismatch} | Name: {name_mismatch} | UI Latency: {t_ui_mismatch:.3f}s")

        # --------------------------------------------------------------------------
        # 6. EDGE CASE C: CORRUPTED / BLANK FILE UPLOAD FLOW
        # --------------------------------------------------------------------------
        print("\n[*] Executing Edge Case C: Corrupted File Upload Flow...")
        nav_intake.click()
        time.sleep(0.5)

        driver.execute_script("""
            const vc = document.getElementById('bio-capture-view');
            const vs = document.getElementById('bio-success-view');
            if (vc) vc.classList.remove('hidden');
            if (vs) vs.classList.add('hidden');
            const docInput = document.getElementById('upload-doc');
            const photoInput = document.getElementById('upload-photo');
            if (docInput) docInput.value = '';
            if (photoInput) photoInput.value = '';
        """)

        corrupted_path = os.path.abspath("backend/static/documents/corrupted_file.bin")
        doc_input = driver.find_element(By.ID, "upload-doc")
        photo_input = driver.find_element(By.ID, "upload-photo")
        doc_input.send_keys(corrupted_path)
        driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", doc_input)
        time.sleep(0.3)
        photo_input.send_keys(live_photo_path)
        driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", photo_input)
        time.sleep(0.5)

        btn_run = driver.find_element(By.ID, "btn-run-verify")
        btn_run.click()
        time.sleep(1.0)
        
        alert_handled_msg = None
        try:
            alert = driver.switch_to.alert
            alert_handled_msg = alert.text
            alert.accept()
            print(f"  [UI MODAL ALERT HANDLED] Clean structured modal: '{alert_handled_msg}'")
        except Exception:
            pass

        time.sleep(0.5)
        save_dual_screenshot(driver, "edge_case_corrupted.png")

        # API check
        with open(corrupted_path, "rb") as f_doc:
            res_corrupted = requests.post(f"{BASE_URL}/api/verify-upload", files={"doc_file": ("corrupted.bin", f_doc, "application/octet-stream")})
            report_data["edge_cases"]["corrupted"] = {
                "http_status": res_corrupted.status_code,
                "ui_alert": alert_handled_msg,
                "raw_json": res_corrupted.json() if res_corrupted.headers.get("content-type", "").startswith("application/json") else res_corrupted.text
            }
        print(f"  -> HTTP Status for Corrupted File: {res_corrupted.status_code}")

        # --------------------------------------------------------------------------
        # 7. AUDIT LEDGER INTEGRITY TEST
        # --------------------------------------------------------------------------
        print("\n[*] Executing Audit Ledger Integrity Verification...")
        nav_ledger = driver.find_element(By.CSS_SELECTOR, '[data-nav="screen-ledger"]')
        nav_ledger.click()
        time.sleep(1.0)

        btn_verify_ledger = driver.find_element(By.ID, "btn-verify-ledger")
        btn_verify_ledger.click()
        time.sleep(3.5)

        save_dual_screenshot(driver, "regression_ledger_verified.png")

        res_ledger_api = requests.post(f"{BASE_URL}/api/audit/verify").json()
        report_data["ledger"] = res_ledger_api
        print(f"  -> Total Blocks Verified: {res_ledger_api.get('blocks_checked')} | Tamper Detected: {res_ledger_api.get('tamper_detected')} | Latest Hash: {res_ledger_api.get('latest_block_hash')}")

        # --------------------------------------------------------------------------
        # 8. AUDIT BROWSER CONSOLE LOGS
        # --------------------------------------------------------------------------
        print("\n[*] Auditing Browser Console Logs...")
        logs = driver.get_log("browser")
        filtered_logs = []
        for l in logs:
            if "favicon.ico" not in l["message"]:
                filtered_logs.append(l)
        report_data["console_logs"] = filtered_logs
        print(f"  -> Total Non-Favicon Console Entries: {len(filtered_logs)}")
        for l in filtered_logs:
            print(f"     [{l.get('level')}] {l.get('message')}")

    finally:
        driver.quit()

    # Save full regression JSON report
    report_path = os.path.join(ARTIFACTS_DIR, "regression_report.json")
    with open(report_path, "w") as f:
        json.dump(report_data, f, indent=2)
    print(f"\n[SUCCESS] Full regression report saved to: {report_path}")

if __name__ == "__main__":
    main()
