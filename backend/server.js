// server.js — FHIR Proxy 後端
// 作為前端和 hapi.fhir.org/baseR4 之間的中介層，解決 CORS 問題

const express = require('express');
const axios = require('axios');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());

const FHIR_BASE = 'https://hapi.fhir.org/baseR4';
const FHIR_HEADERS = {
  'Content-Type': 'application/fhir+json',
  'Accept': 'application/fhir+json',
};

// 從 HTTP Response 取得資源 ID（優先從 body，備用從 Location header）
function extractId(resp) {
  if (resp.data && resp.data.id) return String(resp.data.id);
  const loc = resp.headers['location'] || '';
  const m = loc.match(/\/([^/]+)\/_history/);
  return m ? m[1] : null;
}

// ─── POST Organization ───────────────────────────────────────
app.post('/api/organization', async (req, res) => {
  const { name, identifier } = req.body;
  if (!name) return res.status(400).json({ error: '機構名稱為必填' });

  const payload = {
    resourceType: 'Organization',
    active: true,
    name,
    ...(identifier && {
      identifier: [{
        system: 'https://www.nhi.gov.tw',
        value: identifier,
      }],
    }),
  };

  try {
    const resp = await axios.post(`${FHIR_BASE}/Organization`, payload, {
      headers: FHIR_HEADERS,
    });
    res.json({ id: extractId(resp), httpStatus: resp.status, resource: resp.data });
  } catch (err) {
    res.status(err.response?.status || 500).json({
      error: err.response?.data?.issue?.[0]?.diagnostics || err.message,
      httpStatus: err.response?.status,
    });
  }
});

// ─── POST Location ────────────────────────────────────────────
app.post('/api/location', async (req, res) => {
  const { name, type, orgId } = req.body;
  if (!name || !orgId) return res.status(400).json({ error: '地點名稱與 Organization ID 為必填' });

  const payload = {
    resourceType: 'Location',
    status: 'active',
    name,
    managingOrganization: { reference: `Organization/${orgId}` },
    ...(type && {
      type: [{
        coding: [{
          system: 'http://terminology.hl7.org/CodeSystem/v3-RoleCode',
          code: type,
        }],
      }],
    }),
  };

  try {
    const resp = await axios.post(`${FHIR_BASE}/Location`, payload, {
      headers: FHIR_HEADERS,
    });
    res.json({ id: extractId(resp), httpStatus: resp.status, resource: resp.data });
  } catch (err) {
    res.status(err.response?.status || 500).json({
      error: err.response?.data?.issue?.[0]?.diagnostics || err.message,
      httpStatus: err.response?.status,
    });
  }
});

// ─── POST Patient ─────────────────────────────────────────────
app.post('/api/patient', async (req, res) => {
  const { familyName, givenName, identifier, gender, birthDate, orgId } = req.body;
  if (!familyName || !givenName || !orgId) {
    return res.status(400).json({ error: '姓名與 Organization ID 為必填' });
  }

  const payload = {
    resourceType: 'Patient',
    active: true,
    name: [{ use: 'official', family: familyName, given: [givenName] }],
    gender: gender || 'unknown',
    managingOrganization: { reference: `Organization/${orgId}` },
    ...(identifier && {
      identifier: [{
        system: 'http://www.moi.gov.tw',
        value: identifier,
      }],
    }),
    ...(birthDate && { birthDate }),
  };

  try {
    const resp = await axios.post(`${FHIR_BASE}/Patient`, payload, {
      headers: FHIR_HEADERS,
    });
    res.json({ id: extractId(resp), httpStatus: resp.status, resource: resp.data });
  } catch (err) {
    res.status(err.response?.status || 500).json({
      error: err.response?.data?.issue?.[0]?.diagnostics || err.message,
      httpStatus: err.response?.status,
    });
  }
});

// ─── GET Patients by Organization ────────────────────────────
app.get('/api/organization/:id/patients', async (req, res) => {
  try {
    const resp = await axios.get(`${FHIR_BASE}/Patient`, {
      params: { organization: `Organization/${req.params.id}` },
      headers: FHIR_HEADERS,
    });
    res.json(resp.data);
  } catch (err) {
    res.status(err.response?.status || 500).json({
      error: err.response?.data?.issue?.[0]?.diagnostics || err.message,
    });
  }
});

// ─── GET Patient by ID ────────────────────────────────────────
app.get('/api/patient/:id', async (req, res) => {
  try {
    const resp = await axios.get(`${FHIR_BASE}/Patient/${req.params.id}`, {
      headers: FHIR_HEADERS,
    });
    res.json(resp.data);
  } catch (err) {
    res.status(err.response?.status || 500).json({
      error: err.response?.data?.issue?.[0]?.diagnostics || err.message,
    });
  }
});

// ─── GET 通用搜尋（支援 identifier、name、organization、organization.name 等）──
app.get('/api/search/:resourceType', async (req, res) => {
  const { resourceType } = req.params;
  try {
    const resp = await axios.get(`${FHIR_BASE}/${resourceType}`, {
      params: req.query,
      headers: FHIR_HEADERS,
    });
    res.json(resp.data);
  } catch (err) {
    res.status(err.response?.status || 500).json({
      error: err.response?.data?.issue?.[0]?.diagnostics || err.message,
    });
  }
});

// ─── POST $validate ───────────────────────────────────────────
// 先 GET 現存資源，再 POST 至 {ResourceType}/$validate 端點
app.post('/api/validate/:resourceType/:id', async (req, res) => {
  const { resourceType, id } = req.params;
  try {
    const getResp = await axios.get(`${FHIR_BASE}/${resourceType}/${id}`, {
      headers: FHIR_HEADERS,
    });
    const valResp = await axios.post(
      `${FHIR_BASE}/${resourceType}/$validate`,
      getResp.data,
      { headers: FHIR_HEADERS }
    );
    res.json({ httpStatus: valResp.status, outcome: valResp.data });
  } catch (err) {
    // $validate 失敗時回傳的 OperationOutcome 也視為合法回應
    if (err.response?.data?.resourceType === 'OperationOutcome') {
      return res.json({ httpStatus: err.response.status, outcome: err.response.data });
    }
    res.status(err.response?.status || 500).json({
      error: err.response?.data?.issue?.[0]?.diagnostics || err.message,
    });
  }
});

// ─── PUT Update Patient ───────────────────────────────────────
app.put('/api/patient/:id', async (req, res) => {
  const { id } = req.params;
  const { familyName, givenName, identifier, gender, birthDate, orgId, active } = req.body;
  if (!familyName || !givenName || !orgId) {
    return res.status(400).json({ error: '姓名與 Organization ID 為必填' });
  }

  const payload = {
    resourceType: 'Patient',
    id,
    active: active !== undefined ? active : true,
    name: [{ use: 'official', family: familyName, given: [givenName] }],
    gender: gender || 'unknown',
    managingOrganization: { reference: `Organization/${orgId}` },
    ...(identifier && {
      identifier: [{
        system: 'http://www.moi.gov.tw',
        value: identifier,
      }],
    }),
    ...(birthDate && { birthDate }),
  };

  try {
    const resp = await axios.put(`${FHIR_BASE}/Patient/${id}`, payload, {
      headers: FHIR_HEADERS,
    });
    res.json({ id: extractId(resp) || id, httpStatus: resp.status, resource: resp.data });
  } catch (err) {
    res.status(err.response?.status || 500).json({
      error: err.response?.data?.issue?.[0]?.diagnostics || err.message,
      httpStatus: err.response?.status,
    });
  }
});

// ─── DELETE resource ──────────────────────────────────────────
app.delete('/api/:resourceType/:id', async (req, res) => {
  const { resourceType, id } = req.params;
  try {
    const resp = await axios.delete(`${FHIR_BASE}/${resourceType}/${id}`, {
      headers: FHIR_HEADERS,
    });
    res.json({ httpStatus: resp.status });
  } catch (err) {
    res.status(err.response?.status || 500).json({ error: err.message });
  }
});

const PORT = 3001;
app.listen(PORT, () => {
  console.log(`✅ FHIR Proxy 後端啟動 → http://localhost:${PORT}`);
  console.log(`   代理目標: ${FHIR_BASE}`);
});
