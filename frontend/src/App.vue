<template>
  <div id="app">
    <!-- ── Header ── -->
    <header class="app-header">
      <div class="header-inner">
        <h1>🏥 FHIR 資源交換測試系統</h1>
        <p>
          Track 1: Organization → Location → Patient &nbsp;│&nbsp;
          <a href="https://hapi.fhir.org/baseR4" target="_blank" rel="noopener">hapi.fhir.org/baseR4</a>
        </p>
      </div>
    </header>

    <!-- ── Main Layout ── -->
    <div class="layout">

      <!-- ════════════════════════════════════
           左側：依序建立資源
           ════════════════════════════════════ -->
      <section class="panel">
        <h2 class="panel-title">① 依序建立資源</h2>

        <!-- Step 1: Organization -->
        <div class="card" :class="{ 'card--done': org.id, 'card--error': org.error }">
          <div class="card-header">
            <span class="step-badge">Step 1</span>
            <div class="card-title">
              <h3>Organization</h3>
              <small>醫療機構</small>
            </div>
            <span v-if="org.id" class="tag tag--ok">✅ 完成</span>
          </div>
          <div class="card-body">
            <div class="field">
              <label>機構名稱 <span class="req">*</span></label>
              <input v-model="org.form.name" placeholder="花蓮好健康醫院" :disabled="!!org.id" />
            </div>
            <div class="field">
              <label>健保機構代碼</label>
              <input v-model="org.form.identifier" placeholder="1145060001" :disabled="!!org.id" />
            </div>
            <button class="btn btn--primary" @click="createOrg"
              :disabled="!org.form.name.trim() || !!org.id || org.loading">
              <span v-if="org.loading" class="loading-dot">建立中</span>
              <span v-else-if="org.id">✅ 已建立</span>
              <span v-else>建立 Organization</span>
            </button>
            <transition name="fade">
              <div v-if="org.id" class="result result--ok">
                <div class="result-row">
                  <span class="result-label">Resource ID</span>
                  <code class="result-id">{{ org.id }}</code>
                  <button class="copy-btn" @click="copyText(org.id)" title="複製 ID">📋</button>
                </div>
                <div class="result-row">
                  <span class="result-label">HTTP 狀態</span>
                  <span class="http-badge">{{ org.httpStatus }} Created</span>
                </div>
              </div>
            </transition>
            <div v-if="org.error" class="result result--err">❌ {{ org.error }}</div>
          </div>
        </div>

        <!-- Step 2: Location -->
        <div class="card" :class="{ 'card--locked': !org.id, 'card--done': loc.id }">
          <div class="card-header">
            <span class="step-badge">Step 2</span>
            <div class="card-title">
              <h3>Location</h3>
              <small>診間 / 地點</small>
            </div>
            <span v-if="loc.id" class="tag tag--ok">✅ 完成</span>
            <span v-else-if="!org.id" class="tag tag--lock">🔒 需先建立機構</span>
          </div>
          <div class="card-body">
            <div v-if="org.id" class="ref-badge">
              🔗 managingOrganization →
              <code>Organization/{{ org.id }}</code>
            </div>
            <div class="field">
              <label>地點名稱 <span class="req">*</span></label>
              <input v-model="loc.form.name" placeholder="第一心臟內科診間"
                :disabled="!org.id || !!loc.id" />
            </div>
            <div class="field">
              <label>地點類型（選填）</label>
              <select v-model="loc.form.type" :disabled="!org.id || !!loc.id">
                <option value="">— 不指定 —</option>
                <option value="OF">OF · 門診</option>
                <option value="HU">HU · 病房</option>
                <option value="ER">ER · 急診</option>
                <option value="CVDX">CVDX · 心血管診療</option>
              </select>
            </div>
            <button class="btn btn--primary" @click="createLoc"
              :disabled="!org.id || !loc.form.name.trim() || !!loc.id || loc.loading">
              <span v-if="loc.loading" class="loading-dot">建立中</span>
              <span v-else-if="loc.id">✅ 已建立</span>
              <span v-else>建立 Location</span>
            </button>
            <transition name="fade">
              <div v-if="loc.id" class="result result--ok">
                <div class="result-row">
                  <span class="result-label">Resource ID</span>
                  <code class="result-id">{{ loc.id }}</code>
                  <button class="copy-btn" @click="copyText(loc.id)" title="複製 ID">📋</button>
                </div>
                <div class="result-row">
                  <span class="result-label">HTTP 狀態</span>
                  <span class="http-badge">{{ loc.httpStatus }} Created</span>
                </div>
              </div>
            </transition>
            <div v-if="loc.error" class="result result--err">❌ {{ loc.error }}</div>
          </div>
        </div>

        <!-- Step 3: Patient -->
        <div class="card" :class="{ 'card--locked': !org.id, 'card--done': pat.id }">
          <div class="card-header">
            <span class="step-badge">Step 3</span>
            <div class="card-title">
              <h3>Patient</h3>
              <small>病患</small>
            </div>
            <span v-if="pat.id" class="tag tag--ok">✅ 完成</span>
            <span v-else-if="!org.id" class="tag tag--lock">🔒 需先建立機構</span>
          </div>
          <div class="card-body">
            <div v-if="org.id" class="ref-badge">
              🔗 managingOrganization →
              <code>Organization/{{ org.id }}</code>
            </div>
            <div class="form-row">
              <div class="field">
                <label>姓 <span class="req">*</span></label>
                <input v-model="pat.form.familyName" placeholder="王"
                  :disabled="!org.id || !!pat.id" />
              </div>
              <div class="field">
                <label>名 <span class="req">*</span></label>
                <input v-model="pat.form.givenName" placeholder="小明"
                  :disabled="!org.id || !!pat.id" />
              </div>
            </div>
            <div class="field">
              <label>身分證字號</label>
              <input v-model="pat.form.identifier" placeholder="A123456789"
                :disabled="!org.id || !!pat.id" />
            </div>
            <div class="form-row">
              <div class="field">
                <label>性別</label>
                <select v-model="pat.form.gender" :disabled="!org.id || !!pat.id">
                  <option value="male">男 (male)</option>
                  <option value="female">女 (female)</option>
                  <option value="other">其他 (other)</option>
                  <option value="unknown">未知</option>
                </select>
              </div>
              <div class="field">
                <label>出生日期</label>
                <input type="date" v-model="pat.form.birthDate"
                  :disabled="!org.id || !!pat.id" />
              </div>
            </div>
            <button class="btn btn--primary" @click="createPat"
              :disabled="!org.id || !pat.form.familyName.trim() || !pat.form.givenName.trim() || !!pat.id || pat.loading">
              <span v-if="pat.loading" class="loading-dot">建立中</span>
              <span v-else-if="pat.id">✅ 已建立</span>
              <span v-else>建立 Patient</span>
            </button>
            <transition name="fade">
              <div v-if="pat.id" class="result result--ok">
                <div class="result-row">
                  <span class="result-label">Resource ID</span>
                  <code class="result-id">{{ pat.id }}</code>
                  <button class="copy-btn" @click="copyText(pat.id)" title="複製 ID">📋</button>
                </div>
                <div class="result-row">
                  <span class="result-label">HTTP 狀態</span>
                  <span class="http-badge">{{ pat.httpStatus }} Created</span>
                </div>
              </div>
            </transition>
            <div v-if="pat.error" class="result result--err">❌ {{ pat.error }}</div>
          </div>
        </div>

        <button class="btn btn--ghost reset-btn" @click="resetAll">↺ 重置，重新開始</button>
      </section>

      <!-- ════════════════════════════════════
           右側：查詢資源
           ════════════════════════════════════ -->
      <section class="panel">
        <h2 class="panel-title">② 查詢資源</h2>

        <!-- 查詢機構下所有病患 -->
        <div class="card">
          <div class="card-header">
            <div class="card-title"><h3>機構下所有病患</h3></div>
          </div>
          <div class="card-body">
            <div class="field">
              <label>Organization ID</label>
              <div class="input-group">
                <input v-model="qOrg.inputId" placeholder="輸入 Organization ID"
                  @keyup.enter="queryByOrg" />
                <button class="btn btn--secondary" @click="queryByOrg"
                  :disabled="!qOrg.inputId.trim() || qOrg.loading">
                  {{ qOrg.loading ? '查詢中...' : '查詢' }}
                </button>
              </div>
            </div>

            <transition name="fade">
              <div v-if="qOrg.result">
                <p class="query-summary">
                  共找到 <strong>{{ qOrg.result.total ?? 0 }}</strong> 位病患
                </p>
                <div v-if="qOrg.result.entry?.length" class="patient-list">
                  <div
                    v-for="e in qOrg.result.entry"
                    :key="e.resource.id"
                    class="patient-row"
                    @click="openPatient(e.resource.id)"
                    title="點擊查看詳情"
                  >
                    <div class="pr-id">{{ e.resource.id }}</div>
                    <div class="pr-name">
                      {{ e.resource.name?.[0]?.family }}{{ e.resource.name?.[0]?.given?.join('') }}
                      <span class="pr-gender">{{ GENDER_MAP[e.resource.gender] ?? '' }}</span>
                    </div>
                    <div v-if="e.resource.birthDate" class="pr-birth">
                      🎂 {{ e.resource.birthDate }}
                    </div>
                  </div>
                </div>
                <p v-else class="no-data">此機構尚無病患資料</p>
              </div>
            </transition>
            <div v-if="qOrg.error" class="result result--err">❌ {{ qOrg.error }}</div>
          </div>
        </div>

        <!-- 查詢指定病患 -->
        <div class="card">
          <div class="card-header">
            <div class="card-title"><h3>指定病患詳情</h3></div>
          </div>
          <div class="card-body">
            <div class="field">
              <label>Patient ID</label>
              <div class="input-group">
                <input v-model="qPat.inputId" placeholder="輸入 Patient ID"
                  @keyup.enter="queryByPatId" />
                <button class="btn btn--secondary" @click="queryByPatId"
                  :disabled="!qPat.inputId.trim() || qPat.loading">
                  {{ qPat.loading ? '查詢中...' : '查詢' }}
                </button>
              </div>
            </div>

            <transition name="fade">
              <div v-if="qPat.result" class="patient-detail">
                <div class="detail-status">
                  <span class="http-badge">HTTP 200 OK</span>
                  <span class="tag tag--ok">資源存在</span>
                </div>
                <table class="detail-table">
                  <tbody>
                    <tr>
                      <th>Resource ID</th>
                      <td><code>{{ qPat.result.id }}</code></td>
                    </tr>
                    <tr>
                      <th>姓名</th>
                      <td>
                        {{ qPat.result.name?.[0]?.family }}{{ qPat.result.name?.[0]?.given?.join('') }}
                      </td>
                    </tr>
                    <tr>
                      <th>性別</th>
                      <td>{{ GENDER_MAP[qPat.result.gender] ?? qPat.result.gender }}</td>
                    </tr>
                    <tr>
                      <th>出生日期</th>
                      <td>{{ qPat.result.birthDate || '—' }}</td>
                    </tr>
                    <tr>
                      <th>身分識別碼</th>
                      <td>{{ qPat.result.identifier?.[0]?.value || '—' }}</td>
                    </tr>
                    <tr>
                      <th>管理機構</th>
                      <td>{{ qPat.result.managingOrganization?.reference || '—' }}</td>
                    </tr>
                    <tr>
                      <th>狀態</th>
                      <td>
                        <span :class="qPat.result.active ? 'tag tag--ok' : 'tag tag--warn'">
                          {{ qPat.result.active ? '啟用中' : '停用' }}
                        </span>
                      </td>
                    </tr>
                  </tbody>
                </table>
                <details class="json-viewer">
                  <summary>查看完整 FHIR JSON</summary>
                  <pre>{{ JSON.stringify(qPat.result, null, 2) }}</pre>
                </details>
              </div>
            </transition>
            <div v-if="qPat.error" class="result result--err">❌ {{ qPat.error }}</div>
          </div>
        </div>
      </section>
    </div>

    <!-- ── Toast 通知 ── -->
    <transition name="toast">
      <div v-if="toast.show" class="toast">{{ toast.msg }}</div>
    </transition>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import axios from 'axios'

// Vite proxy 將 /api 轉發至 http://localhost:3001
const API = '/api'

const GENDER_MAP = { male: '男', female: '女', other: '其他', unknown: '未知' }

// ── 建立資源狀態 ──────────────────────────────────────────────
const org = reactive({
  form: { name: '花蓮好健康醫院', identifier: '1145060001' },
  id: null, httpStatus: null, error: null, loading: false,
})
const loc = reactive({
  form: { name: '第一心臟內科診間', type: 'CVDX' },
  id: null, httpStatus: null, error: null, loading: false,
})
const pat = reactive({
  form: { familyName: '王', givenName: '小明', identifier: '', gender: 'male', birthDate: '1985-05-20' },
  id: null, httpStatus: null, error: null, loading: false,
})

// ── 查詢資源狀態 ──────────────────────────────────────────────
const qOrg = reactive({ inputId: '', result: null, error: null, loading: false })
const qPat = reactive({ inputId: '', result: null, error: null, loading: false })

// ── Toast 通知 ────────────────────────────────────────────────
const toast = reactive({ show: false, msg: '' })
function showToast(msg) {
  toast.msg = msg
  toast.show = true
  setTimeout(() => { toast.show = false }, 2500)
}

// ── 複製到剪貼簿 ──────────────────────────────────────────────
async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text)
    showToast(`✅ 已複製: ${text}`)
  } catch {
    showToast('複製失敗，請手動複製')
  }
}

// ── 建立 Organization ─────────────────────────────────────────
async function createOrg() {
  org.loading = true
  org.error = null
  try {
    const { data } = await axios.post(`${API}/organization`, org.form)
    org.id = data.id
    org.httpStatus = data.httpStatus
    qOrg.inputId = data.id   // 自動填入查詢框
    showToast(`✅ Organization 建立成功！ID: ${data.id}`)
  } catch (e) {
    org.error = e.response?.data?.error ?? e.message
  } finally {
    org.loading = false
  }
}

// ── 建立 Location ─────────────────────────────────────────────
async function createLoc() {
  loc.loading = true
  loc.error = null
  try {
    const { data } = await axios.post(`${API}/location`, { ...loc.form, orgId: org.id })
    loc.id = data.id
    loc.httpStatus = data.httpStatus
    showToast(`✅ Location 建立成功！ID: ${data.id}`)
  } catch (e) {
    loc.error = e.response?.data?.error ?? e.message
  } finally {
    loc.loading = false
  }
}

// ── 建立 Patient ──────────────────────────────────────────────
async function createPat() {
  pat.loading = true
  pat.error = null
  try {
    const { data } = await axios.post(`${API}/patient`, { ...pat.form, orgId: org.id })
    pat.id = data.id
    pat.httpStatus = data.httpStatus
    qPat.inputId = data.id   // 自動填入查詢框
    showToast(`✅ Patient 建立成功！ID: ${data.id}`)
  } catch (e) {
    pat.error = e.response?.data?.error ?? e.message
  } finally {
    pat.loading = false
  }
}

// ── 查詢機構下所有病患 ────────────────────────────────────────
async function queryByOrg() {
  if (!qOrg.inputId.trim()) return
  qOrg.loading = true
  qOrg.result = null
  qOrg.error = null
  try {
    const { data } = await axios.get(`${API}/organization/${qOrg.inputId.trim()}/patients`)
    qOrg.result = data
  } catch (e) {
    qOrg.error = e.response?.data?.error ?? e.message
  } finally {
    qOrg.loading = false
  }
}

// ── 查詢指定病患 ──────────────────────────────────────────────
async function queryByPatId() {
  if (!qPat.inputId.trim()) return
  qPat.loading = true
  qPat.result = null
  qPat.error = null
  try {
    const { data } = await axios.get(`${API}/patient/${qPat.inputId.trim()}`)
    qPat.result = data
  } catch (e) {
    qPat.error = e.response?.data?.error ?? e.message
  } finally {
    qPat.loading = false
  }
}

// ── 從病患列表點擊開啟詳情 ───────────────────────────────────
function openPatient(id) {
  qPat.inputId = id
  queryByPatId()
}

// ── 重置全部 ──────────────────────────────────────────────────
function resetAll() {
  Object.assign(org, { id: null, httpStatus: null, error: null, loading: false })
  Object.assign(loc, { id: null, httpStatus: null, error: null, loading: false })
  Object.assign(pat, { id: null, httpStatus: null, error: null, loading: false })
  qOrg.result = null
  qOrg.error = null
  qPat.result = null
  qPat.error = null
  showToast('已重置')
}
</script>

<style>
/* ── Global Reset ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans TC', sans-serif;
  background: #f0f9ff;
  color: #0f172a;
  line-height: 1.6;
  font-size: 14px;
}
</style>

<style scoped>
/* ── App Header ── */
.app-header {
  background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
  color: white;
  padding: 20px 32px;
  box-shadow: 0 2px 8px rgba(2, 132, 199, 0.3);
}
.header-inner h1 {
  font-size: 22px;
  font-weight: 700;
  letter-spacing: -0.3px;
}
.header-inner p {
  font-size: 13px;
  opacity: 0.85;
  margin-top: 4px;
}
.header-inner a {
  color: #bae6fd;
  text-decoration: none;
}
.header-inner a:hover { text-decoration: underline; }

/* ── Layout ── */
.layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  max-width: 1280px;
  margin: 0 auto;
  padding: 24px 24px 40px;
}
@media (max-width: 900px) {
  .layout { grid-template-columns: 1fr; }
}

/* ── Panel ── */
.panel-title {
  font-size: 16px;
  font-weight: 700;
  color: #0369a1;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 2px solid #bae6fd;
}

/* ── Card ── */
.card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  margin-bottom: 16px;
  overflow: hidden;
  transition: box-shadow 0.2s, opacity 0.2s;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
.card--done {
  border-color: #86efac;
  box-shadow: 0 1px 4px rgba(34,197,94,0.15);
}
.card--locked { opacity: 0.6; pointer-events: none; }
.card--error { border-color: #fca5a5; }

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 18px;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}
.card-title h3 {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
}
.card-title small {
  font-size: 12px;
  color: #64748b;
  margin-left: 4px;
}
.card-body { padding: 18px; }

/* ── Step Badge ── */
.step-badge {
  background: #0284c7;
  color: white;
  font-size: 11px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 20px;
  white-space: nowrap;
}

/* ── Tags ── */
.tag {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 20px;
  margin-left: auto;
  white-space: nowrap;
  background: #e2e8f0;
  color: #475569;
}
.tag--ok { background: #dcfce7; color: #16a34a; }
.tag--lock { background: #fef9c3; color: #a16207; }
.tag--warn { background: #fef3c7; color: #b45309; }

/* ── Form Fields ── */
.field {
  margin-bottom: 12px;
}
.field label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: #475569;
  margin-bottom: 5px;
}
.req { color: #ef4444; }
input, select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #cbd5e1;
  border-radius: 7px;
  font-size: 14px;
  color: #1e293b;
  background: #fff;
  transition: border-color 0.15s, box-shadow 0.15s;
  outline: none;
}
input:focus, select:focus {
  border-color: #0284c7;
  box-shadow: 0 0 0 3px rgba(2,132,199,0.12);
}
input:disabled, select:disabled {
  background: #f1f5f9;
  color: #94a3b8;
  cursor: not-allowed;
}
.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.input-group {
  display: flex;
  gap: 8px;
}
.input-group input { flex: 1; }

/* ── Buttons ── */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 9px 18px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: all 0.15s;
  white-space: nowrap;
}
.btn:disabled { opacity: 0.5; cursor: not-allowed; }

.btn--primary {
  width: 100%;
  background: #0284c7;
  color: white;
  margin-top: 4px;
}
.btn--primary:hover:not(:disabled) { background: #0369a1; }

.btn--secondary {
  background: #e0f2fe;
  color: #0369a1;
  flex-shrink: 0;
}
.btn--secondary:hover:not(:disabled) { background: #bae6fd; }

.btn--ghost {
  background: transparent;
  color: #64748b;
  border: 1px solid #e2e8f0;
  padding: 7px 16px;
  font-size: 13px;
}
.btn--ghost:hover { background: #f1f5f9; }

.reset-btn {
  display: block;
  width: 100%;
  text-align: center;
}

/* ── Ref Badge (Resource Link) ── */
.ref-badge {
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  border-radius: 7px;
  padding: 8px 12px;
  font-size: 12px;
  color: #0369a1;
  margin-bottom: 14px;
}
.ref-badge code {
  font-family: 'Roboto Mono', 'Courier New', monospace;
  background: #e0f2fe;
  padding: 1px 5px;
  border-radius: 4px;
}

/* ── Result Boxes ── */
.result {
  margin-top: 12px;
  padding: 12px 14px;
  border-radius: 8px;
  font-size: 13px;
}
.result--ok {
  background: #f0fdf4;
  border: 1px solid #86efac;
}
.result--err {
  background: #fef2f2;
  border: 1px solid #fca5a5;
  color: #b91c1c;
}
.result-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}
.result-row:last-child { margin-bottom: 0; }
.result-label {
  font-size: 11px;
  font-weight: 600;
  color: #64748b;
  min-width: 70px;
}
.result-id {
  font-family: 'Roboto Mono', 'Courier New', monospace;
  background: #dcfce7;
  color: #15803d;
  padding: 1px 7px;
  border-radius: 5px;
  font-size: 13px;
  word-break: break-all;
}
.http-badge {
  background: #dbeafe;
  color: #1d4ed8;
  font-size: 11px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 5px;
}
.copy-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 14px;
  padding: 0 2px;
  opacity: 0.6;
  transition: opacity 0.15s;
}
.copy-btn:hover { opacity: 1; }

/* ── Query Results ── */
.query-summary {
  font-size: 13px;
  color: #475569;
  margin-bottom: 10px;
  padding: 8px 12px;
  background: #f8fafc;
  border-radius: 6px;
}
.query-summary strong { color: #0284c7; font-size: 16px; }

.patient-list { display: flex; flex-direction: column; gap: 6px; }
.patient-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s;
}
.patient-row:hover {
  background: #e0f2fe;
  border-color: #7dd3fc;
  transform: translateX(2px);
}
.pr-id {
  font-family: 'Roboto Mono', 'Courier New', monospace;
  font-size: 11px;
  color: #64748b;
  background: #e2e8f0;
  padding: 1px 6px;
  border-radius: 4px;
}
.pr-name { font-weight: 600; font-size: 14px; }
.pr-gender {
  font-size: 11px;
  color: #64748b;
  background: #e2e8f0;
  padding: 1px 6px;
  border-radius: 10px;
  margin-left: 4px;
}
.pr-birth { font-size: 12px; color: #64748b; }
.no-data { color: #94a3b8; font-size: 13px; text-align: center; padding: 16px; }

/* ── Patient Detail Table ── */
.patient-detail { margin-top: 0; }
.detail-status {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 12px;
}
.detail-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}
.detail-table th, .detail-table td {
  padding: 9px 12px;
  border-bottom: 1px solid #f1f5f9;
  text-align: left;
  vertical-align: top;
}
.detail-table th {
  width: 100px;
  color: #64748b;
  font-weight: 600;
  white-space: nowrap;
}
.detail-table td { color: #1e293b; }
.detail-table code {
  font-family: 'Roboto Mono', 'Courier New', monospace;
  background: #f1f5f9;
  padding: 1px 5px;
  border-radius: 4px;
  font-size: 12px;
  word-break: break-all;
}

/* ── JSON Viewer ── */
.json-viewer {
  margin-top: 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
}
.json-viewer summary {
  padding: 8px 14px;
  font-size: 12px;
  font-weight: 600;
  color: #475569;
  cursor: pointer;
  background: #f8fafc;
  user-select: none;
}
.json-viewer summary:hover { background: #f1f5f9; }
.json-viewer pre {
  padding: 14px;
  font-family: 'Roboto Mono', 'Courier New', monospace;
  font-size: 11px;
  background: #1e293b;
  color: #94a3b8;
  overflow-x: auto;
  max-height: 360px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-word;
}

/* ── Loading Dots ── */
.loading-dot::after {
  content: '...';
  animation: dots 1.2s steps(4, end) infinite;
}
@keyframes dots {
  0%, 20% { content: ''; }
  40% { content: '.'; }
  60% { content: '..'; }
  80%, 100% { content: '...'; }
}

/* ── Toast ── */
.toast {
  position: fixed;
  bottom: 28px;
  left: 50%;
  transform: translateX(-50%);
  background: #1e293b;
  color: white;
  padding: 10px 22px;
  border-radius: 24px;
  font-size: 13px;
  font-weight: 500;
  box-shadow: 0 4px 20px rgba(0,0,0,0.25);
  z-index: 1000;
}

/* ── Transitions ── */
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.toast-enter-active, .toast-leave-active { transition: all 0.3s ease; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateX(-50%) translateY(10px); }
</style>
