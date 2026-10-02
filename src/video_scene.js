/* Keystone Fence & Deck Co. — "site walk" hero video scene.
   An elevation drawing in the site's style: a homeowner and a Keystone
   estimator talk at the back fence line while the old leaning fence comes
   out and the new one draws itself in. build() lays the scene out once
   (after fonts load, so labels can be measured); render(t) poses it at
   time t, so every frame is deterministic. */
'use strict';
const NS = 'http://www.w3.org/2000/svg';
const W = 1280, H = 720, GY = 560, FT = 45, TOP = GY - 6 * FT, DUR = 16;
const C = {
  sheet: '#FAFAF7', vellum: '#F1F1EC', steel: '#16191B', steel3: '#3A4145', graphite: '#575E62', pencil: '#80878A',
  rule: '#D6D7D0', rule2: '#BEC0B8', cedar: '#A0552A', cedarDeep: '#7C401E', cedarTint: '#EFDCCD',
  wood: '#D9AE86', wood2: '#C19068', wood3: '#E8C9A8', stamp: '#2F5B4C', alert: '#A33A2B',
  canopy: '#D2E0D7', scrub: '#BFD1C5', skin: '#D8C8B8', conc: '#DCDAD3', old: '#DCCFC1', mulch: '#CDB397',
};
const POSTS = [90, 450, 810, 990];
const svg = document.getElementById('s');
const R = {};                                   // named nodes render() animates

function el(tag, a, parent) {
  const e = document.createElementNS(NS, tag);
  for (const k in a) e.setAttribute(k, a[k]);
  (parent || svg).appendChild(e);
  return e;
}
const grp = (parent, a) => el('g', a || {}, parent);
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const seg = (t, a, b) => clamp((t - a) / (b - a));
const easeOut = x => 1 - Math.pow(1 - x, 3);
const ease = x => (x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);
const win = (t, a, b, fi = .3, fo = .3) => Math.min(easeOut(seg(t, a, a + fi)), 1 - ease(seg(t, b - fo, b)));
let seed = 7;
const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);

// ── labels with a knockout box, like the site's drawing callouts ──────────
function label(parent, x, y, text, cls, anchor = 'start', pad = 6) {
  const g = grp(parent);
  const bg = el('rect', { fill: C.sheet }, g);
  const tx = el('text', { x, y, class: cls, 'text-anchor': anchor }, g);
  tx.textContent = text;
  const b = tx.getBBox();
  Object.entries({ x: b.x - pad, y: b.y - pad + 1, width: b.width + pad * 2, height: b.height + pad * 2 - 2 })
    .forEach(([k, v]) => bg.setAttribute(k, v));
  return g;
}
function leader(parent, pts, color = C.steel) {
  el('polyline', { points: pts.map(p => p.join(',')).join(' '), fill: 'none', stroke: color, 'stroke-width': 1.6 }, parent);
  const [x, y] = pts[pts.length - 1];
  el('circle', { cx: x, cy: y, r: 3.6, fill: color }, parent);
}
function dimH(parent, x1, x2, y, text) {
  el('line', { x1, y1: y, x2, y2: y, stroke: C.cedarDeep, 'stroke-width': 1.6 }, parent);
  for (const x of [x1, x2]) {
    el('line', { x1: x, y1: y - 9, x2: x, y2: y + 9, stroke: C.cedarDeep, 'stroke-width': 1.6 }, parent);
    el('line', { x1: x - 6, y1: y + 6, x2: x + 6, y2: y - 6, stroke: C.cedarDeep, 'stroke-width': 2.2 }, parent);
  }
  label(parent, (x1 + x2) / 2, y + 6, text, 'dimt', 'middle', 5);
}
function dimV(parent, x, y1, y2, text) {
  el('line', { x1: x, y1, x2: x, y2, stroke: C.cedarDeep, 'stroke-width': 1.6 }, parent);
  for (const y of [y1, y2]) {
    el('line', { x1: x - 9, y1: y, x2: x + 9, y2: y, stroke: C.cedarDeep, 'stroke-width': 1.6 }, parent);
    el('line', { x1: x - 6, y1: y + 6, x2: x + 6, y2: y - 6, stroke: C.cedarDeep, 'stroke-width': 2.2 }, parent);
  }
  const g = label(parent, x, (y1 + y2) / 2 + 6, text, 'dimt', 'middle', 5);
  g.setAttribute('transform', `rotate(-90 ${x} ${(y1 + y2) / 2})`);
}
function cloud(parent, pts, fill) {                 // union-of-circles canopy
  for (const [x, y, r] of pts) el('circle', { cx: x, cy: y, r: r + 1.6, fill: C.steel }, parent);
  for (const [x, y, r] of pts) el('circle', { cx: x, cy: y, r, fill }, parent);
}

// ── scale figures ─────────────────────────────────────────────────────────
// Local coordinates: origin between the feet, facing +x, y up is negative.
function limb(parent, color, w) {
  const o = el('polyline', { fill: 'none', stroke: C.steel, 'stroke-width': w + 3.4, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, parent);
  const i = el('polyline', { fill: 'none', stroke: color, 'stroke-width': w, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, parent);
  return [o, i];
}
function arm(parent, shirt, sx, sy) {
  const g = grp(parent);
  const up = limb(g, shirt, 15), fore = limb(g, C.skin, 11);
  const hand = el('circle', { r: 6.6, fill: C.skin, stroke: C.steel, 'stroke-width': 1.7 }, g);
  const extra = grp(g);
  return { g, up, fore, hand, extra, sx, sy };
}
function poseArm(a, a1, a2) {                       // angles in degrees from straight down, + is forward
  const r = d => d * Math.PI / 180;
  const ex = a.sx + Math.sin(r(a1)) * 46, ey = a.sy + Math.cos(r(a1)) * 46;
  const hx = ex + Math.sin(r(a2)) * 42, hy = ey + Math.cos(r(a2)) * 42;
  const sleeve = [a.sx + Math.sin(r(a1)) * 30, a.sy + Math.cos(r(a1)) * 30];
  a.up.forEach(p => p.setAttribute('points', `${a.sx},${a.sy} ${sleeve[0]},${sleeve[1]}`));
  a.fore.forEach(p => p.setAttribute('points', `${sleeve[0]},${sleeve[1]} ${ex},${ey} ${hx},${hy}`));
  a.hand.setAttribute('cx', hx); a.hand.setAttribute('cy', hy);
  a.extra.setAttribute('transform', `translate(${hx} ${hy}) rotate(${-a2 * .15})`);
}
function figure(id, x, scale, flip, shirt, pants, kind) {
  const root = grp(svg, { transform: `translate(${x} ${GY}) scale(${flip ? -scale : scale} ${scale})` });
  const back = arm(root, shirt, -15, -194);
  // legs + shoes
  el('path', { d: 'M -20 -131 L 1 -131 L -2 -9 L -17 -9 Z', fill: pants, stroke: C.steel, 'stroke-width': 1.7, 'stroke-linejoin': 'round' }, root);
  el('path', { d: 'M -1 -131 L 22 -131 L 19 -9 L 4 -9 Z', fill: pants, stroke: C.steel, 'stroke-width': 1.7, 'stroke-linejoin': 'round' }, root);
  el('rect', { x: -21, y: -11, width: 22, height: 10, rx: 4.5, fill: C.steel }, root);
  el('rect', { x: 2, y: -11, width: 26, height: 10, rx: 4.5, fill: C.steel }, root);
  // torso
  el('path', { d: 'M -22 -128 L -25 -172 Q -27 -197 -13 -201 L 17 -201 Q 30 -197 28 -172 L 25 -128 Z', fill: shirt, stroke: C.steel, 'stroke-width': 1.8, 'stroke-linejoin': 'round' }, root);
  el('line', { x1: -22.5, y1: -131, x2: 25, y2: -131, stroke: C.steel, 'stroke-width': 2.4 }, root);
  if (kind === 'est') {
    el('rect', { x: -27, y: -138, width: 13, height: 20, rx: 2, fill: C.wood2, stroke: C.steel, 'stroke-width': 1.5 }, root);
    el('circle', { cx: -20.5, cy: -126, r: 3.4, fill: C.steel3 }, root);
  } else {
    el('path', { d: 'M -5 -201 L 3 -191 L 10 -201', fill: 'none', stroke: C.steel, 'stroke-width': 1.6 }, root);
  }
  // neck + head (head group rotates about the neck for nods and talk)
  el('rect', { x: -5, y: -213, width: 11, height: 15, fill: C.skin, stroke: C.steel, 'stroke-width': 1.6 }, root);
  const head = grp(root);
  const hx = 3, hy = -228;
  const clip = el('clipPath', { id: id + '-hc' }, el('defs', {}, root));
  el('circle', { cx: hx, cy: hy, r: 17.5 }, clip);
  el('circle', { cx: hx, cy: hy, r: 17.5, fill: C.skin }, head);
  const hair = grp(head, { 'clip-path': `url(#${id}-hc)` });
  if (kind === 'est') {
    el('rect', { x: hx - 20, y: hy - 22, width: 40, height: 14, fill: C.cedarDeep }, hair);
    el('path', { d: `M ${hx + 6} ${hy - 9.5} L ${hx + 30} ${hy - 9.5} Q ${hx + 31} ${hy - 4} ${hx + 26} ${hy - 4} L ${hx + 6} ${hy - 4.5} Z`, fill: C.cedarDeep, stroke: C.steel, 'stroke-width': 1.5 }, head);
  } else {
    el('path', { d: `M ${hx - 20} ${hy - 22} L ${hx + 20} ${hy - 22} L ${hx + 20} ${hy - 9} Q ${hx + 4} ${hy - 13} ${hx - 6} ${hy - 6} L ${hx - 9} ${hy + 10} L ${hx - 20} ${hy + 12} Z`, fill: C.steel3 }, hair);
  }
  el('circle', { cx: hx, cy: hy, r: 17.5, fill: 'none', stroke: C.steel, 'stroke-width': 1.8 }, head);
  const front = arm(root, shirt, 20, -194);
  if (kind === 'est') {                              // clipboard rides on the front hand
    el('rect', { x: -4, y: -30, width: 27, height: 35, rx: 2, fill: C.sheet, stroke: C.steel, 'stroke-width': 1.7 }, front.extra);
    el('rect', { x: 4, y: -33, width: 11, height: 6, rx: 1.5, fill: C.steel }, front.extra);
    for (const yy of [-20, -13, -6]) el('line', { x1: 1, y1: yy, x2: 18, y2: yy, stroke: C.pencil, 'stroke-width': 1.4 }, front.extra);
    front.g.insertBefore(front.extra, front.up[0]);
  }
  return { root, head, back, front, hx, hy };
}
function poseHead(f, deg) {
  f.head.setAttribute('transform', `rotate(${deg} 1 -211)`);
}

// ── speech bubbles ────────────────────────────────────────────────────────
function bubble(who, lines, tip, side) {
  const g = grp(svg);
  const shape = el('path', { fill: '#FFFFFF', stroke: C.steel, 'stroke-width': 2.6, 'stroke-linejoin': 'round' }, g);
  const pad = 26, lh = 56;
  const w0 = el('text', { class: 'who' }, g); w0.textContent = who;
  const ts = lines.map(s => { const t = el('text', { class: 'say' }, g); t.textContent = s; return t; });
  const tw = Math.max(w0.getComputedTextLength(), ...ts.map(t => t.getComputedTextLength()));
  const w = Math.ceil(tw + pad * 2), h = pad + 15 + 16 + 42 + (lines.length - 1) * lh + 12 + pad;
  const bottom = 232, top = bottom - h;
  let left = side === 'L' ? tip.x - w / 2 : tip.x - 64;
  left = clamp(left, 24, W - 24 - w);
  w0.setAttribute('x', left + pad); w0.setAttribute('y', top + pad + 15);
  ts.forEach((t, i) => { t.setAttribute('x', left + pad); t.setAttribute('y', top + pad + 15 + 16 + 42 + i * lh); });
  const r = 16, b0 = clamp(tip.x - 16, left + r + 4, left + w - r - 40), b1 = b0 + 32;
  shape.setAttribute('d', `M ${left + r} ${top} H ${left + w - r} Q ${left + w} ${top} ${left + w} ${top + r} V ${bottom - r} ` +
    `Q ${left + w} ${bottom} ${left + w - r} ${bottom} H ${b1} L ${tip.x} ${tip.y} L ${b0} ${bottom} H ${left + r} ` +
    `Q ${left} ${bottom} ${left} ${bottom - r} V ${top + r} Q ${left} ${top} ${left + r} ${top} Z`);
  return { g, tip };
}
function showBubble(b, v) {
  b.g.setAttribute('opacity', v.toFixed(3));
  const s = .9 + .1 * v;
  b.g.setAttribute('transform', `translate(${b.tip.x} ${b.tip.y}) scale(${s}) translate(${-b.tip.x} ${-b.tip.y})`);
}

// ══════════════════════════════════════════════════════════════════ build
function build() {
  const defs = el('defs', {});
  const hp = el('pattern', { id: 'hatch', width: 15, height: 15, patternUnits: 'userSpaceOnUse', patternTransform: 'rotate(45)' }, defs);
  el('line', { x1: 0, y1: 0, x2: 0, y2: 15, stroke: C.rule2, 'stroke-width': 1.3 }, hp);
  const cp = el('pattern', { id: 'conc', width: 16, height: 16, patternUnits: 'userSpaceOnUse' }, defs);
  el('rect', { width: 16, height: 16, fill: C.conc }, cp);
  [[4, 5, 1.4], [11, 11, 1.1], [13, 3, .9], [6, 13, .8]].forEach(([cx, cy, r]) => el('circle', { cx, cy, r, fill: C.pencil }, cp));

  el('rect', { width: W, height: H, fill: C.sheet });
  el('rect', { x: 0, y: GY, width: W, height: H - GY, fill: C.vellum });
  el('rect', { x: 0, y: GY, width: W, height: H - GY, fill: 'url(#hatch)' });

  // neighbour's trees, behind the fence line
  const trees = grp(svg);
  for (const [x, h, sp] of [[880, 362, 102], [1068, 404, 120], [1232, 336, 94]]) {
    const cy = GY - h * .68;
    el('rect', { x: x - 7, y: GY - h * .5, width: 14, height: h * .5, fill: C.wood2, stroke: C.steel, 'stroke-width': 1.6 }, trees);
    cloud(trees, [[x, cy - sp * .35, sp * .55], [x - sp * .55, cy + 2, sp * .45], [x + sp * .55, cy + 4, sp * .45],
      [x - sp * .2, cy + sp * .3, sp * .42], [x + sp * .25, cy - sp * .05, sp * .5]], C.canopy);
  }

  // existing fence: leaning, gappy, dashed (drafting convention for "remove")
  R.old = grp(svg);
  const oldPosts = [[70, -3], [300, 4], [520, -2], [760, -8], [1000, 5], [1240, 3]];
  const oh = 248;
  oldPosts.forEach(([x, lean], i) => {
    const nxt = oldPosts[i + 1];
    if (nxt) {
      const bay = grp(R.old, { transform: `translate(${x} ${GY}) skewX(${(lean + nxt[1]) / 2}) translate(${-x} ${-GY})` });
      for (const ry of [GY - 52, GY - 196]) el('rect', { x, y: ry, width: nxt[0] - x, height: 9, fill: C.old, stroke: C.pencil, 'stroke-width': 1.3, 'stroke-dasharray': '6 4' }, bay);
      let k = 0;
      for (let bx = x + 10; bx < nxt[0] - 16; bx += 25, k++) {
        if ((i === 1 && (k === 4 || k === 5)) || (i === 3 && k === 2)) continue;
        const crooked = i === 2 && k === 6;
        el('path', { d: `M ${bx} ${GY - 4} V ${GY - oh + 7} L ${bx + 9} ${GY - oh} L ${bx + 18} ${GY - oh + 7} V ${GY - 4} Z`,
          fill: C.old, stroke: C.pencil, 'stroke-width': 1.3, 'stroke-dasharray': '6 4',
          transform: crooked ? `rotate(9 ${bx + 9} ${GY - 196})` : '' }, bay);
      }
    }
    el('rect', { x: x - 6, y: GY - oh - 6, width: 12, height: oh + 6, fill: C.old, stroke: C.pencil, 'stroke-width': 1.5, 'stroke-dasharray': '6 4',
      transform: `rotate(${lean} ${x} ${GY})` }, R.old);
  });
  el('line', { x1: 760, y1: GY, x2: 760, y2: GY - oh - 14, stroke: C.alert, 'stroke-width': 1.6, 'stroke-dasharray': '5 4' }, R.old);
  const ol = grp(R.old);
  leader(ol, [[905, 282], [905, 300], [745, 380]], C.alert);
  label(ol, 905, 276, 'EXISTING FENCE · LEANING — REMOVE', 'lbl lbl-alert', 'middle');

  // layout: stakes + string line along the property line
  R.stakes = POSTS.concat([1262]).map(x => {
    const g = grp(svg);
    el('rect', { x: x - 4, y: GY - 34, width: 8, height: 44, fill: C.wood2, stroke: C.steel, 'stroke-width': 1.4 }, g);
    el('rect', { x: x - 4, y: GY - 34, width: 8, height: 9, fill: C.cedar }, g);
    return g;
  });
  R.stringClip = el('rect', { x: 0, y: GY - 40, width: 0, height: 20 }, el('clipPath', { id: 'strc' }, defs));
  R.string = el('line', { x1: 90, y1: GY - 28, x2: 1262, y2: GY - 28, stroke: C.cedar, 'stroke-width': 2, 'clip-path': 'url(#strc)' });

  // footings, below grade
  R.footClip = el('rect', { x: 0, y: GY - 14, width: W, height: 0 }, el('clipPath', { id: 'ftc' }, defs));
  R.foot = grp(svg, { 'clip-path': 'url(#ftc)' });
  for (const x of POSTS) {
    el('path', { d: `M ${x - 24} ${GY + 136} V ${GY + 1} Q ${x} ${GY - 13} ${x + 24} ${GY + 1} V ${GY + 136} Z`, fill: 'url(#conc)', stroke: C.steel, 'stroke-width': 1.7 }, R.foot);
    el('rect', { x: x - 6, y: GY - 4, width: 12, height: 122, fill: C.steel3, stroke: C.steel, 'stroke-width': 1.2 }, R.foot);
  }
  el('line', { x1: 0, y1: GY, x2: W, y2: GY, stroke: C.steel, 'stroke-width': 2.8 });
  R.footLbl = grp(svg);
  dimV(R.footLbl, 42, GY, GY + 136, "3'-0\"");
  leader(R.footLbl, [[126, 658], [104, 640]]);
  label(R.footLbl, 132, 664, 'CROWNED CONCRETE FOOTINGS', 'lbl');

  // new fence
  R.railClip = el('rect', { x: 84, y: 0, width: 0, height: H }, el('clipPath', { id: 'rlc' }, defs));
  R.rails = grp(svg, { 'clip-path': 'url(#rlc)' });
  for (const ry of [GY - 44, GY - 142, GY - 240]) {
    el('rect', { x: 96, y: ry, width: 714, height: 10, fill: C.wood2, stroke: C.steel, 'stroke-width': 1.2 }, R.rails);
    el('rect', { x: 990, y: ry, width: 300, height: 10, fill: C.wood2, stroke: C.steel, 'stroke-width': 1.2 }, R.rails);
  }
  R.boardClip = el('rect', { x: 84, y: 0, width: 0, height: H }, el('clipPath', { id: 'bdc' }, defs));
  R.boards = grp(svg, { 'clip-path': 'url(#bdc)' });
  const span = (x0, x1) => {
    for (let x = x0; x < x1; x += 30) el('rect', { x, y: TOP + 14, width: 20, height: GY - 4 - TOP - 14, fill: C.wood2, stroke: C.steel, 'stroke-width': 1.1 }, R.boards);
    for (let x = x0 + 15; x < x1 - 8; x += 30) el('rect', { x, y: TOP + 14, width: 20, height: GY - 4 - TOP - 14, fill: C.wood, stroke: C.steel, 'stroke-width': 1.1 }, R.boards);
  };
  span(96, 806); span(994, 1300);
  R.pencil = el('line', { x1: 0, y1: TOP - 10, x2: 0, y2: GY + 4, stroke: C.cedar, 'stroke-width': 3, opacity: 0 });
  R.posts = POSTS.map(x => {
    const g = grp(svg);
    el('rect', { x: x - 7, y: TOP + 2, width: 14, height: GY - TOP - 2, fill: C.steel, stroke: C.steel, 'stroke-width': 1 }, g);
    el('rect', { x: x - 9, y: TOP - 6, width: 18, height: 9, rx: 2, fill: C.steel3, stroke: C.steel, 'stroke-width': 1 }, g);
    return g;
  });
  R.cap = grp(svg);
  for (const [a, b] of [[84, 816], [984, 1290]]) {
    el('rect', { x: a, y: TOP, width: b - a, height: 9, fill: C.wood2, stroke: C.steel, 'stroke-width': 1.4 }, R.cap);
    el('rect', { x: a + 4, y: TOP + 9, width: b - a - 8, height: 6, fill: C.wood3, stroke: C.steel, 'stroke-width': 1.1 }, R.cap);
  }
  R.gate = grp(svg);
  const gt = TOP + 18, gb = GY - 8;
  for (let x = 822; x < 978; x += 30) el('rect', { x, y: gt, width: Math.min(20, 978 - x), height: gb - gt, fill: C.wood2, stroke: C.steel, 'stroke-width': 1.1 }, R.gate);
  for (let x = 837; x < 970; x += 30) el('rect', { x, y: gt, width: 20, height: gb - gt, fill: C.wood, stroke: C.steel, 'stroke-width': 1.1 }, R.gate);
  el('rect', { x: 820, y: gt, width: 160, height: gb - gt, fill: 'none', stroke: C.steel, 'stroke-width': 4.5 }, R.gate);
  el('line', { x1: 824, y1: gb - 6, x2: 976, y2: gt + 6, stroke: C.steel, 'stroke-width': 3.6 }, R.gate);
  for (const hy of [gt + 30, gb - 46]) el('rect', { x: 811, y: hy, width: 18, height: 12, rx: 2, fill: C.steel3, stroke: C.steel, 'stroke-width': 1.2 }, R.gate);
  el('rect', { x: 966, y: 418, width: 22, height: 12, rx: 2, fill: C.cedar, stroke: C.steel, 'stroke-width': 1.2 }, R.gate);
  R.swing = grp(svg);
  for (const yy of [gt, gb]) el('line', { x1: 980, y1: yy, x2: 822, y2: (gt + gb) / 2, stroke: C.cedar, 'stroke-width': 2, 'stroke-dasharray': '9 7' }, R.swing);

  // garden bed + lawn, in front of the fence line
  const bed = grp(svg);
  el('rect', { x: 14, y: GY - 11, width: 300, height: 11, fill: C.mulch, stroke: C.steel, 'stroke-width': 1.4 }, bed);
  cloud(bed, [[42, GY - 38, 30], [92, GY - 52, 40], [146, GY - 36, 29], [196, GY - 50, 38], [252, GY - 40, 31], [290, GY - 30, 22]], C.scrub);
  const blooms = ['#E8C76A', C.cedarTint, '#D98A7A', '#E8C76A', '#D98A7A', C.cedarTint, '#E8C76A', '#D98A7A'];
  [40, 70, 104, 128, 168, 210, 236, 272].forEach((x, i) => {
    const hgt = 22 + (i * 13) % 20;
    el('line', { x1: x, y1: GY - 10, x2: x + 2, y2: GY - 10 - hgt, stroke: C.stamp, 'stroke-width': 2 }, bed);
    el('circle', { cx: x + 2, cy: GY - 14 - hgt, r: 7, fill: blooms[i], stroke: C.steel, 'stroke-width': 1.4 }, bed);
    el('circle', { cx: x + 2, cy: GY - 14 - hgt, r: 2, fill: C.steel3 }, bed);
  });
  for (let x = 330; x < W; x += 26 + rnd() * 34) {
    const g = grp(svg, { stroke: C.stamp, 'stroke-width': 1.8, 'stroke-linecap': 'round', opacity: .75 });
    el('line', { x1: x, y1: GY - 1, x2: x - 4, y2: GY - 11 }, g);
    el('line', { x1: x + 2, y1: GY - 1, x2: x + 6, y2: GY - 9 }, g);
  }

  // layout dimension + finished-fence callouts
  R.layoutDim = grp(svg);
  dimH(R.layoutDim, 450, 810, GY + 36, "8'-0\" O.C.");
  R.co = [grp(svg), grp(svg), grp(svg), grp(svg)];
  dimV(R.co[0], 42, TOP, GY, "6'-0\"");
  leader(R.co[1], [[116, 282], [116, 300], [236, 392]]);
  label(R.co[1], 98, 276, 'BOARD-ON-BOARD CEDAR', 'lbl');
  leader(R.co[2], [[1002, 282], [1002, 300], [990, 330]]);
  label(R.co[2], 984, 276, 'GALV. STEEL POSTS', 'lbl');
  dimH(R.co[3], 810, 990, GY + 36, "4'-0\" GATE");

  // people
  R.ho = figure('ho', 404, 1, false, C.stamp, C.steel3, 'ho');
  R.est = figure('est', 604, 1.074, true, C.cedar, C.steel3, 'est');

  // title block
  const tb = grp(svg);
  el('rect', { x: 1030, y: 642, width: 232, height: 64, fill: C.sheet, stroke: C.steel, 'stroke-width': 1.6 }, tb);
  el('line', { x1: 1030, y1: 662, x2: 1262, y2: 662, stroke: C.graphite, 'stroke-width': 1 }, tb);
  el('line', { x1: 1092, y1: 662, x2: 1092, y2: 706, stroke: C.graphite, 'stroke-width': 1 }, tb);
  [[1040, 657, 'KEYSTONE FENCE & DECK CO.', 'tbh'], [1040, 678, 'SHEET', 'tbl'], [1040, 698, '00', 'tbv'],
   [1102, 680, 'SITE WALK', 'tbv'], [1102, 698, 'BACKYARD · PLANO, TX', 'tbl']].forEach(([x, y, s, c]) => {
    const t = el('text', { x, y, class: c }, tb); t.textContent = s;
  });

  // conversation
  R.b = [
    bubble('HOMEOWNER', ['We want privacy out back —', 'and a gate for the mower.'], { x: 410, y: 306 }, 'L'),
    bubble('KEYSTONE ESTIMATOR', ['Board-on-board cedar,', 'on galvanized steel posts.'], { x: 596, y: 288 }, 'R'),
    bubble('HOMEOWNER', ['Will it stay straight?'], { x: 410, y: 306 }, 'L'),
    bubble('KEYSTONE ESTIMATOR', ['Footings go 3 ft deep.', 'It’ll stay straight.'], { x: 596, y: 288 }, 'R'),
  ];
}

// ══════════════════════════════════════════════════════════════════ render
const op = (n, v) => n.setAttribute('opacity', clamp(v).toFixed(3));
function render(t) {
  const reset = ease(seg(t, 15.0, 15.85));          // loop: fade back to the opening frame
  const keep = 1 - reset;
  op(R.old, Math.max(1 - ease(seg(t, 4.2, 5.0)), reset));

  R.stakes.forEach((g, i) => {
    const p = easeOut(seg(t, 5.0 + i * .18, 5.35 + i * .18));
    const gone = i < POSTS.length ? seg(t, 7.3 + i * .3 + .2, 7.3 + i * .3 + .45) : seg(t, 8.6, 9.0);
    op(g, p * (1 - gone));
    g.setAttribute('transform', `translate(0 ${-26 * (1 - p)})`);
  });
  R.stringClip.setAttribute('width', 1300 * ease(seg(t, 5.3, 6.4)));
  op(R.string, 1 - seg(t, 8.6, 9.0));
  op(R.layoutDim, easeOut(seg(t, 6.0, 6.4)) * keep);

  R.posts.forEach((g, i) => {
    const p = easeOut(seg(t, 7.3 + i * .3, 7.65 + i * .3));
    op(g, p * keep);
    g.setAttribute('transform', `translate(0 ${-90 * (1 - p)})`);
  });
  R.footClip.setAttribute('height', 160 * ease(seg(t, 8.4, 9.4)));
  op(R.foot, keep);
  op(R.footLbl, easeOut(seg(t, 9.0, 9.4)) * keep);

  R.railClip.setAttribute('width', 1220 * ease(seg(t, 9.9, 10.4)));
  op(R.rails, keep);
  const bw = ease(seg(t, 10.2, 11.8));
  R.boardClip.setAttribute('width', 1220 * bw);
  op(R.boards, keep);
  const px = 84 + 1220 * bw;
  R.pencil.setAttribute('x1', px); R.pencil.setAttribute('x2', px);
  op(R.pencil, bw > 0 && bw < 1 ? 1 : 0);
  const cp = easeOut(seg(t, 11.8, 12.1));
  op(R.cap, cp * keep); R.cap.setAttribute('transform', `translate(0 ${-12 * (1 - cp)})`);
  op(R.gate, easeOut(seg(t, 12.0, 12.5)) * keep);
  op(R.swing, easeOut(seg(t, 12.3, 12.7)) * keep);
  R.co.forEach((g, i) => op(g, easeOut(seg(t, 12.6 + i * .2, 12.9 + i * .2)) * keep));

  // conversation
  const B = [[.5, 3.6], [3.8, 7.0], [7.2, 9.6], [9.8, 14.4]];
  R.b.forEach((b, i) => showBubble(b, win(t, B[i][0], B[i][1], .28, .28)));

  // people: talk, nod, gesture
  const talk = (a, b) => 2.6 * Math.sin(t * Math.PI * 2 * 2.3) * win(t, a, b, .2, .2);
  const nod = n => 7 * Math.sin(Math.PI * seg(t, n, n + .55));
  poseHead(R.ho, talk(.6, 3.4) + talk(7.3, 9.4) + nod(5.6) + nod(11.0) + nod(12.9));
  poseHead(R.est, talk(3.9, 6.8) + talk(9.9, 14.1) + nod(2.4) + nod(8.4));
  const hg = win(t, .7, 3.5, .4, .4), hs = win(t, 7.3, 9.5, .35, .35);
  poseArm(R.ho.front, 4 + 24 * hg + 10 * hs, 8 + 88 * hg + 62 * hs);
  poseArm(R.ho.back, -4 + 12 * hs, 2 + 58 * hs);
  const ep = win(t, 4.0, 6.9, .4, .4), e4 = win(t, 10.0, 12.6, .4, .4);
  poseArm(R.est.back, -4 - 116 * ep - 88 * e4, 2 - 116 * ep - 90 * e4);
  poseArm(R.est.front, 6, 76);
}
window.build = build; window.render = render; window.DUR = DUR;
