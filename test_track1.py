"""
FHIR Track 1: 機構與病患基本資料 (Administration - Basics)
測試腳本 - 遵循 Setup → Action → Assert → Teardown 四階段架構

使用 HAPI FHIR Public Test Server: https://hapi.fhir.org/baseR4
"""

import json
import sys
import os
import time
import uuid
import requests

FHIR_BASE = "https://hapi.fhir.org/baseR4"
HEADERS = {
    "Content-Type": "application/fhir+json",
    "Accept": "application/fhir+json",
}

RESOURCES_DIR = os.path.join(os.path.dirname(__file__), "resources")

# 每次測試使用唯一 suffix 避免公開伺服器上的重複資源衝突
_RUN_ID = str(int(time.time()))[-6:]   # 取 Unix timestamp 後 6 碼

# 儲存伺服器自動產生的 ID（PUT 時 id 由 client 給定，POST 時由 server 產生）
created_ids = {
    "organization": None,
    "location": None,
    "patient": None,
}


def load_resource(filename: str) -> dict:
    path = os.path.join(RESOURCES_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def assert_status(response: requests.Response, expected: int, label: str):
    if response.status_code == expected:
        print(f"  ✔ {label}: HTTP {response.status_code}")
    else:
        print(f"  ✘ {label}: 期望 HTTP {expected}，實際 HTTP {response.status_code}")
        print(f"    回應內容: {response.text[:300]}")
        sys.exit(1)


def get_id_from_response(response: requests.Response) -> str:
    """從回應取得資源 ID（Location header 或 body 中的 id）"""
    location = response.headers.get("Location", "")
    if location:
        # Location: https://hapi.fhir.org/baseR4/Patient/12345/_history/1
        parts = location.rstrip("/").split("/")
        hist_idx = parts.index("_history") if "_history" in parts else -1
        if hist_idx > 0:
            return parts[hist_idx - 1]
    body = response.json()
    return body.get("id", "")


# ─────────────────────────────────────────────
# Phase 1: SETUP — 建立測試資料
# ─────────────────────────────────────────────
def phase_setup():
    print("\n" + "=" * 60)
    print("【Phase 1: Setup】建立測試資料至 FHIR Server")
    print("=" * 60)

    # 1-A: POST Organization（讓伺服器產生 ID，但 identifier 加入 run-id 確保唯一）
    print("\n[1-A] POST Organization...")
    org = load_resource("organization.json")
    org.pop("id", None)
    # 在 identifier value 後加 run-id 確保測試不衝突
    org["identifier"][0]["value"] = f"1145060001-{_RUN_ID}"
    org["name"] = f"花蓮好健康醫院 [{_RUN_ID}]"
    resp = requests.post(f"{FHIR_BASE}/Organization", json=org, headers=HEADERS, timeout=30)
    assert_status(resp, 201, "POST Organization")
    created_ids["organization"] = get_id_from_response(resp)
    print(f"       伺服器產生 Organization ID: {created_ids['organization']}")

    # 1-B: POST Location（參照剛建立的 Organization）
    print("\n[1-B] POST Location...")
    loc = load_resource("location.json")
    loc.pop("id", None)
    loc["managingOrganization"]["reference"] = f"Organization/{created_ids['organization']}"
    resp = requests.post(f"{FHIR_BASE}/Location", json=loc, headers=HEADERS, timeout=30)
    assert_status(resp, 201, "POST Location")
    created_ids["location"] = get_id_from_response(resp)
    print(f"       伺服器產生 Location ID: {created_ids['location']}")

    # 1-C: POST Patient（參照剛建立的 Organization）
    print("\n[1-C] POST Patient...")
    pat = load_resource("patient.json")
    pat.pop("id", None)
    pat["managingOrganization"]["reference"] = f"Organization/{created_ids['organization']}"
    # identifier 加 run-id 確保唯一
    for ident in pat.get("identifier", []):
        ident["value"] = f"{ident['value']}-{_RUN_ID}"
    resp = requests.post(f"{FHIR_BASE}/Patient", json=pat, headers=HEADERS, timeout=30)
    assert_status(resp, 201, "POST Patient")
    created_ids["patient"] = get_id_from_response(resp)
    print(f"       伺服器產生 Patient ID: {created_ids['patient']}")


# ─────────────────────────────────────────────
# Phase 2: ACTION — 執行查詢操作
# ─────────────────────────────────────────────
def phase_action():
    print("\n" + "=" * 60)
    print("【Phase 2: Action】執行 GET 查詢")
    print("=" * 60)

    # 2-A: 用 _id 取得 Organization
    print(f"\n[2-A] GET Organization by _id: {created_ids['organization']}")
    resp = requests.get(
        f"{FHIR_BASE}/Organization/{created_ids['organization']}",
        headers=HEADERS, timeout=30
    )
    assert_status(resp, 200, "GET Organization by ID")

    # 2-B: 用 identifier 搜尋 Organization（健保代碼）
    print(f"\n[2-B] GET Organization by identifier=1145060001-{_RUN_ID}")
    resp = requests.get(
        f"{FHIR_BASE}/Organization",
        params={"identifier": f"1145060001-{_RUN_ID}"},
        headers=HEADERS, timeout=30
    )
    assert_status(resp, 200, "GET Organization by identifier")
    bundle = resp.json()
    total = bundle.get("total", 0)
    print(f"       找到 {total} 筆 Organization")

    # 2-C: 用 identifier 搜尋 Patient（身分證字號）
    print(f"\n[2-C] GET Patient by identifier=U123456789-{_RUN_ID}")
    resp = requests.get(
        f"{FHIR_BASE}/Patient",
        params={"identifier": f"U123456789-{_RUN_ID}"},
        headers=HEADERS, timeout=30
    )
    assert_status(resp, 200, "GET Patient by identifier")
    bundle = resp.json()
    total = bundle.get("total", 0)
    print(f"       找到 {total} 筆 Patient")

    # 2-D: 關聯查詢 — 找出隸屬該機構的 Location
    print(f"\n[2-D] GET Location?organization=Organization/{created_ids['organization']}")
    resp = requests.get(
        f"{FHIR_BASE}/Location",
        params={"organization": f"Organization/{created_ids['organization']}"},
        headers=HEADERS, timeout=30
    )
    assert_status(resp, 200, "GET Location by organization")
    bundle = resp.json()
    total = bundle.get("total", 0)
    print(f"       找到 {total} 筆 Location")

    # 2-E: 關聯查詢 — 找出隸屬該機構的 Patient
    print(f"\n[2-E] GET Patient?organization=Organization/{created_ids['organization']}")
    resp = requests.get(
        f"{FHIR_BASE}/Patient",
        params={"organization": f"Organization/{created_ids['organization']}"},
        headers=HEADERS, timeout=30
    )
    assert_status(resp, 200, "GET Patient by organization")
    bundle = resp.json()
    total = bundle.get("total", 0)
    print(f"       找到 {total} 筆 Patient")

    # 2-F: 連鎖查詢 (Chaining) — 用機構名稱找病患
    org_name_query = f"花蓮好健康醫院 [{_RUN_ID}]"
    print(f"\n[2-F] GET Patient?organization.name={org_name_query}")
    resp = requests.get(
        f"{FHIR_BASE}/Patient",
        params={"organization.name": org_name_query},
        headers=HEADERS, timeout=30
    )
    assert_status(resp, 200, "GET Patient by organization.name (Chaining)")
    bundle = resp.json()
    total = bundle.get("total", 0)
    print(f"       找到 {total} 筆 Patient")


# ─────────────────────────────────────────────
# Phase 3: ASSERT — 呼叫 $validate 驗證資料
# ─────────────────────────────────────────────
def phase_assert():
    print("\n" + "=" * 60)
    print("【Phase 3: Assert】$validate 驗證 FHIR 規範合規性")
    print("=" * 60)

    for resource_type, res_id in [
        ("Organization", created_ids["organization"]),
        ("Location", created_ids["location"]),
        ("Patient", created_ids["patient"]),
    ]:
        print(f"\n[Assert] {resource_type}/{res_id} $validate")
        # 先 GET 資源，再 POST 至 $validate endpoint
        get_resp = requests.get(
            f"{FHIR_BASE}/{resource_type}/{res_id}",
            headers=HEADERS, timeout=30
        )
        if get_resp.status_code != 200:
            print(f"  ⚠ 無法取得 {resource_type}/{res_id}，略過驗證")
            continue
        resp = requests.post(
            f"{FHIR_BASE}/{resource_type}/$validate",
            json=get_resp.json(),
            headers=HEADERS, timeout=30
        )
        # $validate 回傳 200 含 OperationOutcome
        if resp.status_code == 200:
            outcome = resp.json()
            issues = outcome.get("issue", [])
            errors = [i for i in issues if i.get("severity") in ("error", "fatal")]
            if errors:
                print(f"  ✘ {resource_type} 驗證有 Error:")
                for e in errors:
                    print(f"    - [{e.get('severity')}] {e.get('diagnostics', e.get('details', {}).get('text', ''))}")
            else:
                print(f"  ✔ {resource_type} 驗證通過（無 Error / Fatal）")
        else:
            print(f"  ⚠ {resource_type} $validate 回傳 HTTP {resp.status_code}（部分伺服器不支援，略過）")


# ─────────────────────────────────────────────
# Phase 4: TEARDOWN — 清理測試資料
# ─────────────────────────────────────────────
def phase_teardown():
    print("\n" + "=" * 60)
    print("【Phase 4: Teardown】清理測試資料")
    print("=" * 60)

    # 先刪 Patient / Location，再刪 Organization（避免參照衝突）
    for resource_type, res_id in [
        ("Patient", created_ids["patient"]),
        ("Location", created_ids["location"]),
        ("Organization", created_ids["organization"]),
    ]:
        if not res_id:
            continue
        print(f"\n[DELETE] {resource_type}/{res_id}")
        resp = requests.delete(
            f"{FHIR_BASE}/{resource_type}/{res_id}",
            headers=HEADERS, timeout=30
        )
        # HAPI FHIR 刪除成功回 200 或 204
        if resp.status_code in (200, 204):
            print(f"  ✔ DELETE {resource_type}/{res_id}: HTTP {resp.status_code}")
        else:
            print(f"  ⚠ DELETE {resource_type}/{res_id}: HTTP {resp.status_code}")


# ─────────────────────────────────────────────
# 主流程
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("FHIR Track 1: 機構與病患基本資料 測試腳本")
    print(f"FHIR Server: {FHIR_BASE}")

    try:
        phase_setup()
        phase_action()
        phase_assert()
    finally:
        phase_teardown()

    print("\n" + "=" * 60)
    print("測試完成")
    print("=" * 60)
