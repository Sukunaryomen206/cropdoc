const API = 'http://localhost:5000/api';

// ── NAV ──
document.getElementById('hamburger').addEventListener('click', () => {
  document.getElementById('navLinks').classList.toggle('open');
});
document.querySelectorAll('.nav-links a').forEach(a => {
  a.addEventListener('click', () => document.getElementById('navLinks').classList.remove('open'));
});

// ── STAT COUNTERS ──
const counterObserver = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (!entry.isIntersecting) return;
    const el = entry.target, target = +el.dataset.target;
    let count = 0;
    const timer = setInterval(() => {
      count = Math.min(count + Math.ceil(target / 50), target);
      el.textContent = count;
      if (count >= target) clearInterval(timer);
    }, 30);
    counterObserver.unobserve(el);
  });
}, { threshold: 0.5 });
document.querySelectorAll('.stat-num').forEach(c => counterObserver.observe(c));

// ── LANGUAGE SWITCHER ──
const translations = {
  en: { heroTitle: 'Diagnose Crop Diseases<br/><span class="highlight">Instantly, Anywhere</span>', heroSub: 'Detect crop diseases without internet. Identify problems at the earliest stage. Get a full organic treatment plan — right on your phone.' },
  hi: { heroTitle: 'फसल की बीमारी पहचानो<br/><span class="highlight">तुरंत, कहीं भी</span>',       heroSub: 'बिना इंटरनेट के बीमारी पहचानो। शुरुआती चरण में ही identify करो। पूरा organic treatment plan पाओ।' },
  gu: { heroTitle: 'પાકની બીમારી ઓળખો<br/><span class="highlight">તરત, ગમે ત્યાં</span>',         heroSub: 'ઇન્ટરનેટ વગર બીમારી ઓળખો. શરૂઆતના તબક્કે identify કરો. સંપૂર્ણ organic treatment plan મેળવો.' }
};
document.querySelectorAll('.lang-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.lang-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    const t = translations[btn.dataset.lang];
    document.getElementById('heroTitle').innerHTML = t.heroTitle;
    document.getElementById('heroSub').textContent = t.heroSub;
  });
});

// ── UPLOAD & DIAGNOSE ──
const photoInput     = document.getElementById('photoInput');
const uploadArea     = document.getElementById('uploadArea');
const uploadPreview  = document.getElementById('uploadPreview');
const previewImg     = document.getElementById('previewImg');
const previewName    = document.getElementById('previewName');
const analyzing      = document.getElementById('analyzing');
const diagnosisResult = document.getElementById('diagnosisResult');
const resultImg      = document.getElementById('resultImg');
const uploadBox      = document.getElementById('uploadBox');

document.getElementById('browseBtn').addEventListener('click', () => photoInput.click());
photoInput.addEventListener('change', () => { if (photoInput.files[0]) showPreview(photoInput.files[0]); });

uploadBox.addEventListener('dragover', e => { e.preventDefault(); uploadBox.classList.add('dragover'); });
uploadBox.addEventListener('dragleave', () => uploadBox.classList.remove('dragover'));
uploadBox.addEventListener('drop', e => {
  e.preventDefault(); uploadBox.classList.remove('dragover');
  const f = e.dataTransfer.files[0];
  if (f && f.type.startsWith('image/')) showPreview(f);
});

function showPreview(file) {
  previewImg.src = URL.createObjectURL(file);
  previewName.textContent = file.name;
  uploadArea.style.display = 'none';
  uploadPreview.style.display = 'flex';
}

document.getElementById('retakeBtn').addEventListener('click', resetUpload);
document.getElementById('resetBtn').addEventListener('click', resetUpload);

document.getElementById('diagnoseBtn').addEventListener('click', async () => {
  const file = photoInput.files[0];
  if (!file) return;

  uploadPreview.style.display = 'none';
  analyzing.style.display = 'block';
  runAnalysisSteps();

  const formData = new FormData();
  formData.append('photo', file);
  formData.append('crop', 'Tomato');

  try {
    const res = await fetch(`${API}/diagnose`, { method: 'POST', body: formData });
    const data = await res.json();

    if (!res.ok) throw new Error(data.error || 'Diagnosis failed');

    // Wait for animation to finish
    await new Promise(r => setTimeout(r, 2500));
    analyzing.style.display = 'none';
    showResults(data);

  } catch (err) {
    analyzing.style.display = 'none';
    uploadArea.style.display = 'flex';
    alert('Error: ' + err.message + '\n\nMake sure the backend server is running.');
  }
});

function runAnalysisSteps() {
  const steps = ['aStep1','aStep2','aStep3','aStep4'];
  steps.forEach(id => document.getElementById(id).classList.remove('active','done'));
  let i = 0;
  const interval = setInterval(() => {
    if (i > 0) document.getElementById(steps[i-1]).classList.add('done');
    if (i < steps.length) { document.getElementById(steps[i]).classList.add('active'); i++; }
    else clearInterval(interval);
  }, 600);
}

function showResults(data) {
  // Set image
  resultImg.src = `${API}/image/${data.scan_id}.jpg`;
  resultImg.onerror = () => { resultImg.src = previewImg.src; };

  // Health score ring
  const health = data.health_score;
  document.getElementById('healthScore').textContent = Math.round(health);
  const circumference = 2 * Math.PI * 34;
  const offset = circumference * (1 - health / 100);
  const arc = document.getElementById('healthArc');
  arc.setAttribute('stroke-dashoffset', offset.toFixed(1));
  arc.setAttribute('stroke', health > 70 ? '#00ff88' : health > 40 ? '#ffd600' : '#ff4444');

  // Severity
  document.getElementById('sevFill').style.width = data.severity_pct + '%';
  document.getElementById('sevPct').textContent = data.severity_pct + '%';
  ['sevMild','sevMod','sevSev'].forEach(id => document.getElementById(id).classList.remove('active-sev'));
  const map = { mild:'sevMild', moderate:'sevMod', severe:'sevSev' };
  if (map[data.severity]) document.getElementById(map[data.severity]).classList.add('active-sev');

  // Top predictions
  const predContainer = document.getElementById('predictionsContainer');
  predContainer.innerHTML = data.predictions.map(p => `
    <div class="result-item">
      <span class="result-disease">${p.disease} ${p.disease === data.disease ? `<em>(${data.scientific_name})</em>` : ''}</span>
      <div class="confidence-bar"><div class="confidence-fill" style="width:${p.confidence}%"></div></div>
      <span class="confidence-pct">${p.confidence}%</span>
    </div>`).join('');

  // Treatment plan
  const treatContainer = document.getElementById('treatmentContainer');
  if (data.treatment && data.treatment.length > 0) {
    treatContainer.innerHTML = data.treatment.map(t => `
      <div class="treat-card">
        <span class="treat-day">${t.day}</span>
        <strong>${t.name}</strong>
        <p>${t.instruction}</p>
        <span class="treat-dose">Dose: ${t.dose}</span>
      </div>`).join('');
  } else {
    treatContainer.innerHTML = '<p style="color:var(--green)">✅ Plant is healthy — no treatment needed.</p>';
  }

  // Preventive
  document.getElementById('preventiveText').textContent = data.preventive;

  // Store scan_id for progress logging
  diagnosisResult.dataset.scanId = data.scan_id;

  diagnosisResult.style.display = 'block';
  diagnosisResult.scrollIntoView({ behavior: 'smooth', block: 'start' });

  // Refresh dashboard
  loadDashboard();
}

// ── HEATMAP TOGGLE ──
document.getElementById('heatmapToggle').addEventListener('click', () => {
  const overlay = document.getElementById('heatmapOverlay');
  const btn = document.getElementById('heatmapToggle');
  overlay.classList.toggle('show');
  const active = overlay.classList.contains('show');
  btn.style.background   = active ? 'rgba(255,68,68,0.3)' : 'rgba(0,0,0,0.7)';
  btn.style.color        = active ? '#ff4444' : 'var(--green)';
  btn.style.borderColor  = active ? '#ff4444' : 'var(--green)';
});

function resetUpload() {
  photoInput.value = '';
  previewImg.src = '';
  uploadArea.style.display = 'flex';
  uploadPreview.style.display = 'none';
  analyzing.style.display = 'none';
  diagnosisResult.style.display = 'none';
  document.getElementById('heatmapOverlay').classList.remove('show');
}

// ── VOICE GUIDANCE ──
const voiceTexts = {
  en: (d) => `Diagnosis complete. ${d.disease} detected with ${d.confidence} percent confidence. Severity is ${d.severity} at ${d.severity_pct} percent. Health score is ${Math.round(d.health_score)} out of 100.`,
  hi: (d) => `निदान पूरा हुआ। ${d.disease} ${d.confidence} प्रतिशत विश्वास के साथ पाया गया। गंभीरता ${d.severity} है, ${d.severity_pct} प्रतिशत। स्वास्थ्य स्कोर 100 में से ${Math.round(d.health_score)} है।`,
  gu: (d) => `નિદાન પૂર્ણ થયું. ${d.disease} ${d.confidence} ટકા વિશ્વાસ સાથે મળ્યો. ગંભીરતા ${d.severity} છે, ${d.severity_pct} ટકા. આરોગ્ય સ્કોર 100 માંથી ${Math.round(d.health_score)} છે.`
};

function speakResult(lang) {
  if (!window.speechSynthesis) { alert('Voice not supported in this browser.'); return; }
  window.speechSynthesis.cancel();
  const scanId = diagnosisResult.dataset.scanId;
  if (!scanId) { alert('Please run a diagnosis first.'); return; }

  fetch(`${API}/scan/${scanId}`)
    .then(r => r.json())
    .then(data => {
      const text = voiceTexts[lang](data);
      const utter = new SpeechSynthesisUtterance(text);
      utter.lang = lang === 'hi' ? 'hi-IN' : lang === 'gu' ? 'gu-IN' : 'en-US';
      utter.rate = 0.9;
      window.speechSynthesis.speak(utter);
    });
}

// ── DASHBOARD ──
async function loadDashboard() {
  try {
    const [dashRes, scansRes] = await Promise.all([
      fetch(`${API}/dashboard`),
      fetch(`${API}/scans`)
    ]);
    const dash  = await dashRes.json();
    const scans = await scansRes.json();

    document.getElementById('totalScanned').textContent = dash.total_scanned;
    document.getElementById('healthyCount').textContent = dash.healthy;
    document.getElementById('diseasedCount').textContent = dash.diseased;
    document.getElementById('farmHealthScore').textContent = dash.farm_health_score + '%';

    // Recent scans table
    const tbody = document.getElementById('scanTableBody');
    if (scans.length === 0) {
      tbody.innerHTML = '<div class="scan-row"><span colspan="5" style="color:var(--muted);text-align:center">No scans yet. Upload a photo to get started.</span></div>';
    } else {
      tbody.innerHTML = scans.slice(0, 6).map(s => `
        <div class="scan-row">
          <span>${s.crop}</span>
          <span>${s.disease}</span>
          <span class="sev-tag ${s.severity}">${s.severity} ${s.severity_pct}%</span>
          <span>${s.created_at}</span>
          <span class="status-tag ${s.status}">${s.status}</span>
        </div>`).join('');
    }
  } catch {
    // Backend not running — keep static demo data
  }
}

// ── WEATHER RISK ──
async function loadWeatherRisk() {
  try {
    const res = await fetch(`${API}/weather-risk`);
    const data = await res.json();
    if (data.alert) {
      document.getElementById('weatherAlert').innerHTML =
        `<i class="fas fa-exclamation-triangle"></i><div><strong>Alert:</strong> ${data.alert}</div>`;
    }
  } catch {
    // Keep static demo data
  }
}

// ── CONTACT FORM ──
document.getElementById('contactForm').addEventListener('submit', e => {
  e.preventDefault();
  e.target.style.display = 'none';
  document.getElementById('formSuccess').style.display = 'block';
});

// ── SCROLL NAV HIGHLIGHT ──
const sections = document.querySelectorAll('section[id]');
window.addEventListener('scroll', () => {
  const scrollY = window.scrollY + 100;
  sections.forEach(sec => {
    const link = document.querySelector(`.nav-links a[href="#${sec.id}"]`);
    if (!link) return;
    if (scrollY >= sec.offsetTop && scrollY < sec.offsetTop + sec.offsetHeight) {
      document.querySelectorAll('.nav-links a').forEach(a => a.style.color = '');
      link.style.color = '#00ff88';
    }
  });
});

// ── INIT ──
loadDashboard();
loadWeatherRisk();
