(function () {
  const D = JSON.parse(document.getElementById('rg-data').textContent);
  const NOTES = D.notes;
  const GUN = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar'];
  const AY = ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık'];
  const SRC = ['Resmî günlük sayfa', 'Künye (OCR)', 'Künye (görsel okuma)', 'Asıl sayıyla aynı gün', 'Mükerrer künyesinden', 'Komşu sayılardan kesin', 'Tahmin', 'TBMM kaydı', 'Resmî Gazete atfı', 'Künye düzeltmesi'];
  const fmt = n => n.toLocaleString('tr-TR');
  // rows: [yyyymmdd, n, muk, src, noteIdx?, url?]
  const rows = D.rows.map(r => {
    const d = r[0], y = Math.floor(d / 10000), m = Math.floor(d / 100) % 100, day = d % 100;
    return { y, m, d: day, n: r[1], k: r[2], s: r[3], note: r.length > 4 && r[4] >= 0 ? NOTES[r[4]] : '', url: r[5] || '', key: d };
  });
  const iso = r => `${r.y}-${String(r.m).padStart(2, '0')}-${String(r.d).padStart(2, '0')}`;
  const wd = r => GUN[(new Date(Date.UTC(r.y, r.m - 1, r.d)).getUTCDay() + 6) % 7];
  const name = n => n <= 21 ? 'Ceride-i Resmiye' : n <= 762 ? 'Resmî Ceride' : 'T.C. Resmî Gazete';
  function url(r) {
    if (r.url) return 'https://www.resmigazete.gov.tr/' + r.url;
    if (r.key >= 20000627) { const p = `${r.y}/${String(r.m).padStart(2, '0')}/${r.key}`; return `https://www.resmigazete.gov.tr/eskiler/${p}${r.k ? 'M' + r.k : ''}.htm`; }
    return `https://www.resmigazete.gov.tr/arsiv/${r.n}${r.k ? '_' + r.k : ''}${r.n <= 1053 && !r.k ? 'T' : ''}.pdf`;
  }
  // per-year
  const years = new Map();
  for (const r of rows) {
    let e = years.get(r.y); if (!e) years.set(r.y, e = { y: r.y, a: 0, m: 0, est: 0, lo: Infinity, hi: -Infinity, rows: [] });
    e.rows.push(r); if (r.k) e.m++; else { e.a++; e.lo = Math.min(e.lo, r.n); e.hi = Math.max(e.hi, r.n); }
    if (r.s === 6) e.est++;
  }
  const Y0 = rows[0].y, Y1 = rows[rows.length - 1].y;
  const allYears = []; for (let y = Y0; y <= Y1; y++) allYears.push(y);
  const mains = rows.filter(r => !r.k).length, muks = rows.length - mains, est = rows.filter(r => r.s === 6).length;
  const first = rows[0], last = rows[rows.length - 1];
  document.getElementById('facts').innerHTML =
    `<span><b>${fmt(rows.length)}</b> yayın</span><span><b>${fmt(mains)}</b> asıl sayı</span><span><b>${fmt(muks)}</b> mükerrer</span>` +
    `<span>ilk: <b>${first.d} ${AY[first.m - 1]} ${first.y}</b> · Sayı 1</span><span>son: <b>${last.d} ${AY[last.m - 1]} ${last.y}</b> · Sayı ${last.n}</span>`;

  // ---------- chart
  const box = document.getElementById('chart');
  const tip = document.createElement('div'); tip.className = 'tip'; tip.hidden = true; box.appendChild(tip);
  const NS = 'http://www.w3.org/2000/svg';
  const el = (t, a) => { const e = document.createElementNS(NS, t); for (const k in a) e.setAttribute(k, a[k]); return e; };
  let svg;
  function drawChart() {
    if (svg) svg.remove();
    const W = Math.max(320, box.clientWidth), H = W < 560 ? 220 : 280;
    const m = { l: 36, r: 6, t: 26, b: 24 };
    const iw = W - m.l - m.r, ih = H - m.t - m.b;
    const maxV = 500, band = iw / allYears.length, bw = Math.max(1.5, band * (band > 6 ? 0.72 : 0.86));
    const yv = v => m.t + ih - ih * v / maxV;
    svg = el('svg', { viewBox: `0 0 ${W} ${H}`, role: 'img', 'aria-label': 'Yıllara göre Resmî Gazete asıl ve mükerrer sayı adetleri, 1921–' + Y1 });
    const g = el('g', {});
    for (let v = 0; v <= maxV; v += 100) {
      g.appendChild(el('line', { x1: m.l, x2: W - m.r, y1: yv(v), y2: yv(v), stroke: 'var(--rule-2)', 'stroke-width': v ? 1 : 1.2, ...(v ? {} : { stroke: 'var(--rule)' }) }));
      const t = el('text', { x: m.l - 6, y: yv(v) + 4, 'text-anchor': 'end' }); t.textContent = v; g.appendChild(t);
    }
    const step = W < 560 ? 20 : 10;
    allYears.forEach((y, i) => {
      if (y % step === 0) { const t = el('text', { x: m.l + band * i + band / 2, y: H - 6, 'text-anchor': 'middle' }); t.textContent = y; g.appendChild(t); }
    });
    // annotations: name changes
    const ann = el('g', { class: 'ann' });
    [[1923, 'Resmî Ceride'], [1927, 'T.C. Resmî Gazete']].forEach(([y, label], j) => {
      const x = m.l + band * (y - Y0) + band / 2;
      ann.appendChild(el('line', { x1: x, x2: x, y1: m.t - 14 + j * 0, y2: yv(0), stroke: 'var(--muted)', 'stroke-dasharray': '2 3', 'stroke-width': 1 }));
      const t = el('text', { x: x + 4, y: m.t - 16 + j * 12, 'text-anchor': 'start' }); t.textContent = label; ann.appendChild(t);
    });
    g.appendChild(ann);
    allYears.forEach((y, i) => {
      const e = years.get(y); if (!e) return;
      const x = m.l + band * i + (band - bw) / 2, r = Math.min(3, bw / 2);
      const ya = yv(e.a), ym = yv(e.a + e.m);
      const gap = e.m && bw > 3 ? 1.5 : 0;
      g.appendChild(el('path', { d: barPath(x, ya, bw, yv(0) - ya, e.m ? 0 : r), fill: 'var(--s1)' }));
      if (e.m) g.appendChild(el('path', { d: barPath(x, ym, bw, Math.max(0.8, ya - ym - gap), r), fill: 'var(--s2)' }));
    });
    // hit areas
    const hit = el('g', {});
    allYears.forEach((y, i) => {
      const rct = el('rect', { x: m.l + band * i, y: m.t, width: band, height: ih, fill: 'transparent', style: 'cursor:pointer' });
      rct.addEventListener('pointerenter', ev => showTip(y, m.l + band * i + band / 2, ev));
      rct.addEventListener('pointermove', ev => showTip(y, m.l + band * i + band / 2, ev));
      rct.addEventListener('pointerleave', () => { tip.hidden = true; hl.setAttribute('opacity', 0); });
      rct.addEventListener('click', () => { if (years.has(y)) { setYear(y); document.getElementById('h-list').scrollIntoView({ behavior: 'smooth', block: 'start' }); } });
      hit.appendChild(rct);
    });
    const hl = el('rect', { x: 0, y: m.t, width: band, height: ih, fill: 'var(--ink)', opacity: 0, 'pointer-events': 'none' });
    g.insertBefore(hl, g.firstChild);
    svg.appendChild(g); svg.appendChild(hit);
    box.insertBefore(svg, tip);
    function showTip(y, cx, ev) {
      const e = years.get(y);
      hl.setAttribute('x', cx - band / 2); hl.setAttribute('opacity', 0.06);
      tip.innerHTML = e ? `<div class="t">${y}</div><div class="r"><span><i style="background:var(--s1)"></i>Asıl sayı</span><b>${fmt(e.a)}</b></div><div class="r"><span><i style="background:var(--s2)"></i>Mükerrer</span><b>${fmt(e.m)}</b></div><div class="h">Sayı ${e.lo}–${e.hi}${e.est ? ` · ${e.est} tahmini tarih` : ''}</div><div class="h">Listeyi açmak için tıklayın</div>`
        : `<div class="t">${y}</div><div class="h">Bu yıl yayımlanmış sayı yok</div>`;
      tip.hidden = false;
      const bx = box.getBoundingClientRect(), sx = bx.width / W;
      let left = cx * sx + 12; if (left + 190 > bx.width) left = cx * sx - 200;
      tip.style.left = Math.max(0, left) + 'px'; tip.style.top = '8px';
    }
  }
  function barPath(x, y, w, h, r) {
    if (h <= 0) return '';
    r = Math.min(r, h, w / 2);
    return `M${x},${y + h}V${y + r}Q${x},${y} ${x + r},${y}H${x + w - r}Q${x + w},${y} ${x + w},${y + r}V${y + h}Z`;
  }
  drawChart();
  let rt; window.addEventListener('resize', () => { clearTimeout(rt); rt = setTimeout(drawChart, 120); });

  // yearly table (accessible view of the chart)
  const yt = document.getElementById('ytable');
  yt.innerHTML = '<thead><tr><th>Yıl</th><th>Asıl</th><th>Mükerrer</th><th>Sayı aralığı</th></tr></thead><tbody>' +
    [...years.values()].map(e => `<tr><td class="num">${e.y}</td><td class="num">${fmt(e.a)}</td><td class="num">${fmt(e.m)}</td><td class="date">${e.lo}–${e.hi}</td></tr>`).join('') + '</tbody>';

  // ---------- list
  const sel = document.getElementById('year');
  sel.innerHTML = [...years.values()].map(e => `<option value="${e.y}">${e.y} · ${fmt(e.a + e.m)}</option>`).join('');
  const tbody = document.querySelector('#list tbody');
  const status = document.getElementById('status');
  let curYear = Y0, filter = 'all', hitKey = null;
  const ICON = '<svg viewBox="0 0 16 16" aria-hidden="true"><path fill="currentColor" d="M8 1.5 15 14H1L8 1.5Zm-.75 4.25v4h1.5v-4h-1.5Zm0 5.25v1.5h1.5V11h-1.5Z"/></svg>';
  const esc = s => s.replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  function render() {
    const e = years.get(curYear);
    document.getElementById('ylabel').textContent = curYear;
    document.getElementById('ymeta').textContent = `${fmt(e.a)} asıl · ${fmt(e.m)} mükerrer · Sayı ${e.lo}–${e.hi}`;
    let list = e.rows;
    if (filter === 'muk') list = list.filter(r => r.k);
    else if (filter === 'note') list = list.filter(r => r.note);
    else if (filter === 'est') list = list.filter(r => r.s === 6);
    tbody.innerHTML = list.map(r => {
      const kind = r.k ? `<span class="kind m"><i class="dot" style="background:var(--s2)"></i>${r.k}. Mükerrer</span>` : `<span class="kind"><i class="dot" style="background:var(--s1)"></i>Asıl</span>`;
      const badge = r.s === 6 ? `<span class="badge est">${ICON}Tahmin</span>` : `<span class="badge">${SRC[r.s]}</span>`;
      const k = `${r.n}-${r.k}`;
      return `<tr class="${r.k ? 'muk' : ''}${hitKey === k ? ' hit' : ''}" id="r-${k}"><td class="date">${String(r.d).padStart(2, '0')}.${String(r.m).padStart(2, '0')}.${r.y}</td><td>${wd(r)}</td><td class="num"><a href="${url(r)}" target="_blank" rel="noopener" title="Kaynağı resmigazete.gov.tr'de aç">${r.n}</a></td><td>${kind}</td><td>${name(r.n)}</td><td>${badge}</td><td class="note">${esc(r.note)}</td></tr>`;
    }).join('') || `<tr><td colspan="7" style="color:var(--muted)">${curYear} yılında bu filtreye uyan kayıt yok.</td></tr>`;
    if (!status.dataset.keep) status.textContent = `${fmt(list.length)} kayıt gösteriliyor`;
    delete status.dataset.keep;
  }
  function setYear(y) { curYear = y; sel.value = y; render(); }
  sel.addEventListener('change', () => { hitKey = null; setYear(+sel.value); });
  const ylist = [...years.keys()];
  document.getElementById('prev').addEventListener('click', () => { const i = ylist.indexOf(curYear); if (i > 0) { hitKey = null; setYear(ylist[i - 1]); } });
  document.getElementById('next').addEventListener('click', () => { const i = ylist.indexOf(curYear); if (i < ylist.length - 1) { hitKey = null; setYear(ylist[i + 1]); } });
  document.querySelectorAll('.chips button').forEach(b => b.addEventListener('click', () => {
    document.querySelectorAll('.chips button').forEach(x => x.setAttribute('aria-pressed', x === b));
    filter = b.dataset.f; render();
  }));
  // search
  const q = document.getElementById('q');
  let qt; q.addEventListener('input', () => { clearTimeout(qt); qt = setTimeout(search, 250); });
  q.addEventListener('keydown', ev => { if (ev.key === 'Enter') { clearTimeout(qt); search(); } });
  function search() {
    const v = q.value.trim(); if (!v) { hitKey = null; render(); return; }
    let m, found = null, msg = '';
    if ((m = v.match(/^(\d{1,2})[.\/](\d{1,2})[.\/](\d{4})$/)) || (m = v.match(/^(\d{4})-(\d{1,2})-(\d{1,2})$/))) {
      const [y, mo, d] = v.includes('-') ? [+m[1], +m[2], +m[3]] : [+m[3], +m[2], +m[1]];
      const key = y * 10000 + mo * 100 + d;
      const same = rows.filter(r => r.key === key);
      if (same.length) { found = same[0]; msg = `${d}.${mo}.${y}: ${same.map(r => r.k ? r.n + ' (' + r.k + '. mükerrer)' : r.n).join(', ')}`; }
      else {
        const after = rows.find(r => r.key > key);
        msg = `${d}.${mo}.${y} tarihinde yayımlanmış sayı yok.` + (after ? ` Sonraki sayı: ${after.n} (${after.d}.${after.m}.${after.y}).` : '');
        found = after || null;
      }
    } else if ((m = v.match(/^\d{1,5}$/))) {
      const n = +v; const r = rows.find(x => x.n === n && !x.k);
      if (r) { found = r; const mk = rows.filter(x => x.n === n && x.k).length; msg = `Sayı ${n}: ${r.d} ${AY[r.m - 1]} ${r.y}, ${wd(r)}${mk ? ` · ${mk} mükerrer` : ''}${r.s === 6 ? ' · tarih tahminidir' : ''}`; }
      else msg = `Sayı ${n} bulunamadı (son sayı ${last.n}).`;
    } else msg = 'Bir sayı numarası (ör. 17863) ya da tarih (ör. 09.11.1982) yazın.';
    hitKey = found ? `${found.n}-${found.k}` : null;
    filter = 'all'; document.querySelectorAll('.chips button').forEach(x => x.setAttribute('aria-pressed', x.dataset.f === 'all'));
    status.textContent = msg; status.dataset.keep = '1';
    if (found) { setYear(found.y); const tr = document.getElementById('r-' + hitKey); if (tr) tr.scrollIntoView({ block: 'center' }); }
    else render();
  }
  setYear(Y0);
})();
