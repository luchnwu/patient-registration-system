# FHIR Track 1: 機構與病患基本資料

## 環境說明

- **FHIR Server**: https://hapi.fhir.org/baseR4
- **資源建立順序**: Organization → Location → Patient
- **後端**: Express.js (Node.js), Port 3001
- **前端**: Vue 3 + Vite, Port 5173

## 快速開始

### 1. 安裝依賴

```bash
# 後端
cd backend
npm install

# 前端（另開終端）
cd frontend
npm install
```

### 2. 啟動應用

```bash
# 終端 1：啟動後端 (Port 3001)
cd backend
npm start

# 終端 2：啟動前端 (Port 5173)
cd frontend
npm run dev
```

### 3. 開啟瀏覽器
```
http://localhost:5173
```

---

## 測試腳本執行

```bash
pip install requests
python test_track1.py
```

---

## 測試四階段架構

| 階段 | 動作 | 預期結果 |
|------|------|----------|
| **Setup** | POST Organization / Location / Patient | HTTP 201 Created |
| **Action** | GET（ID 查詢、identifier 搜尋、關聯查詢、Chaining） | HTTP 200 OK |
| **Assert** | `$validate` 驗證各資源 | OperationOutcome 無 Error |
| **Teardown** | DELETE 所有測試資料 | HTTP 200 / 204 |

---

## 查詢語法對照表

### 基礎查詢

```
# 用健保代碼找醫院
GET https://hapi.fhir.org/baseR4/Organization?identifier=1145060001

# 用身分證字號找病患
GET https://hapi.fhir.org/baseR4/Patient?identifier=U123456789

# 精確指定 identifier system
GET https://hapi.fhir.org/baseR4/Patient?identifier=http://www.moi.gov.tw|U123456789
```

### 關聯查詢（Reference Search）

```
# 找出醫院底下所有空間
GET https://hapi.fhir.org/baseR4/Location?organization=Organization/{id}

# 找出醫院管理的所有病患
GET https://hapi.fhir.org/baseR4/Patient?organization=Organization/{id}
```

### 連鎖查詢（Chaining）

```
# 只知道醫院名稱，直接找病患
GET https://hapi.fhir.org/baseR4/Patient?organization.name=花蓮好健康醫院
```

---

## 資源欄位速查

### Organization

| 欄位 | 說明 | 範例值 |
|------|------|--------|
| `resourceType` | 固定為 "Organization" | `"Organization"` |
| `identifier` | 機構外部編號（健保代碼等） | `"1145060001"` |
| `active` | 是否營運中 | `true` |
| `type` | 機構類型（HL7 code） | `prov` |
| `name` | 官方名稱 | `"花蓮好健康醫院"` |
| `alias` | 別名 / 英文名 | `["HGHH"]` |
| `telecom` | 電話 / Email | `"03-8123456"` |
| `address` | 地址 | `"花蓮縣吉安鄉..."` |

### Location

| 欄位 | 說明 | 範例值 |
|------|------|--------|
| `status` | `active` / `inactive` | `"active"` |
| `mode` | `instance`（實體空間） | `"instance"` |
| `physicalType` | 空間層級（ro = Room） | `"ro"` |
| `managingOrganization` | 所屬機構（**關聯關鍵**） | `"Organization/{id}"` |

### Patient

| 欄位 | 說明 | 範例值 |
|------|------|--------|
| `identifier` | 身分證字號 / 病歷號 | `"U123456789"` |
| `name.family` / `name.given` | 姓 / 名 | `"王"` / `"小明"` |
| `gender` | `male` / `female` / `other` | `"male"` |
| `birthDate` | 出生日期 YYYY-MM-DD | `"1985-05-20"` |
| `managingOrganization` | 管理機構（**關聯關鍵**） | `"Organization/{id}"` |
