// Logo animé « Guest Interview » : salière qui bascule, secousse, grains qui tombent.
// Géométrie = celle du SVG d'Harry (grain_de_sel_noir.svg), structure de calques conservée
// (saliere > corps / bouchon > trous, grains > grain-1..7). La dernière image = le logo exact.
import React from 'react';
import {AbsoluteFill, Easing, interpolate, OffthreadVideo, staticFile, useCurrentFrame} from 'remotion';
import {loadFont} from '@remotion/google-fonts/TikTokSans';

const {fontFamily: TIKTOK} = loadFont('normal', {weights: ['800'], subsets: ['latin']});

export const NAVY = '#1F2A44';
const PIVOT = {x: 104, y: 80};
const SCALE = 1.08;
const ANGLE = -128; // position du logo
const HOLES: [number, number][] = [[-5, -25.5], [0, -28.5], [5, -25.5], [-2.5, -20], [2.5, -20]];
const GRAINS = [
  {x: 76, y: 115, r: 20, s: 3},
  {x: 71, y: 125, r: 50, s: 2.8},
  {x: 78, y: 134, r: 10, s: 3.2},
  {x: 69, y: 144, r: 35, s: 2.8},
  {x: 76, y: 153, r: 62, s: 3},
  {x: 67, y: 162, r: 15, s: 2.6},
  {x: 73, y: 170, r: 40, s: 2.4},
];
// viewBox du SVG d'origine (61 27 102 149) élargi : la salière dépasse pendant la bascule
export const VB = {x: 52, y: 18, w: 120, h: 164};

// ---------- Rythmes (images à 30 fps) ----------
export type Rythme = {
  pop: [number, number]; // pastille + salière apparaissent
  tilt: [number, number, number]; // début bascule, pic (dépassement), retour à -128°
  overshoot: number; // degrés au-delà de -128
  tiltEase: (t: number) => number;
  shake: [number, number];
  shakeN: number; // nombre de coups
  shakeA: number; // amplitude (unités SVG, le long de la salière)
  shakeRot: number; // degrés
  r0: number; // sortie du 1er grain
  stagger: number; // décalage entre grains (images)
  fallMax: number; // durée de chute du grain le plus loin (images)
  duree: number; // fin de l'animation (image où tout est posé)
};

export const RYTHMES: Record<'douce' | 'punchy', Rythme> = {
  douce: {
    pop: [0, 9], tilt: [7, 20, 27], overshoot: 8, tiltEase: Easing.bezier(0.45, 0, 0.25, 1),
    shake: [27, 37], shakeN: 2, shakeA: 2.6, shakeRot: 3,
    r0: 29, stagger: 1.8, fallMax: 9, duree: 50,
  },
  punchy: {
    pop: [0, 5], tilt: [3, 11, 16], overshoot: 13, tiltEase: Easing.bezier(0.3, 0, 0.1, 1),
    shake: [16, 23], shakeN: 2, shakeA: 3.4, shakeRot: 4,
    r0: 17, stagger: 1.3, fallMax: 7, duree: 33,
  },
};

const rad = (d: number) => (d * Math.PI) / 180;
const clamp01 = (v: number) => Math.min(1, Math.max(0, v));

type Pose = {angle: number; tx: number; ty: number};

// secousse : coups le long de l'axe de la salière (vers les trous), enveloppe nulle aux bords
const shakeAt = (f: number, a: number, b: number, n: number, A: number, rotA: number): Pose => {
  if (f <= a || f >= b) return {angle: 0, tx: 0, ty: 0};
  const u = (f - a) / (b - a);
  const v = Math.sin(Math.PI * u) * Math.sin(2 * Math.PI * n * u);
  // axe bouchon (local 0,-1) tourné de -128° → vers le bas-gauche
  const ax = Math.sin(rad(ANGLE));
  const ay = -Math.cos(rad(ANGLE));
  return {angle: -rotA * v, tx: ax * A * v, ty: ay * A * v};
};

const poseAt = (f: number, R: Rythme): Pose => {
  const [t0, t1, t2] = R.tilt;
  let angle = 0;
  if (f >= t2) angle = ANGLE;
  else if (f > t1) angle = interpolate(f, [t1, t2], [ANGLE - R.overshoot, ANGLE], {easing: Easing.inOut(Easing.quad)});
  else if (f > t0) angle = interpolate(f, [t0, t1], [0, ANGLE - R.overshoot], {easing: R.tiltEase});
  const s = shakeAt(f, R.shake[0], R.shake[1], R.shakeN, R.shakeA, R.shakeRot);
  return {angle: angle + s.angle, tx: s.tx, ty: s.ty};
};

const holeWorld = (h: [number, number], p: Pose) => {
  const a = rad(p.angle);
  const x = h[0] * SCALE, y = h[1] * SCALE;
  return {x: PIVOT.x + p.tx + x * Math.cos(a) - y * Math.sin(a), y: PIVOT.y + p.ty + x * Math.sin(a) + y * Math.cos(a)};
};

type GrainState = {x: number; y: number; r: number; k: number; op: number};

// chute avec gravité : x linéaire, y en t² ; durée ∝ √distance
const fall = (f: number, rel: number, T: number, from: {x: number; y: number}, to: {x: number; y: number}, r: number) => {
  const p = clamp01((f - rel) / T);
  return {
    x: from.x + (to.x - from.x) * p,
    y: from.y + (to.y - from.y) * p * p,
    r: r - 70 * (1 - p),
    k: interpolate(p, [0, 0.3], [0.45, 1], {extrapolateRight: 'clamp'}),
    op: f < rel ? 0 : interpolate(f, [rel, rel + 1.5], [0, 1], {extrapolateRight: 'clamp'}),
  };
};

const grainsAt = (f: number, R: Rythme): GrainState[] => {
  const starts = GRAINS.map((_, i) => holeWorld(HOLES[[1, 0, 2, 3, 4][i % 5]], poseAt(R.r0 + i * R.stagger, R)));
  const dMax = Math.max(...GRAINS.map((g, i) => g.y - starts[i].y));
  const gAcc = (2 * dMax) / (R.fallMax * R.fallMax);
  return GRAINS.map((g, i) => {
    const rel = R.r0 + i * R.stagger;
    const T = Math.sqrt((2 * (g.y - starts[i].y)) / gAcc);
    return fall(f, rel, T, starts[i], g, g.r);
  });
};

// ---------- Dessin ----------
type Etat = {pastille: number; op: number; s: number; pose: Pose; grains: GrainState[]; extra?: GrainState};

const REST: Etat = {
  pastille: 1, op: 1, s: 1, pose: {angle: ANGLE, tx: 0, ty: 0},
  grains: GRAINS.map((g) => ({x: g.x, y: g.y, r: g.r, k: 1, op: 1})),
};

const Grain: React.FC<{id: string; g: GrainState; s: number}> = ({id, g, s}) => (
  <rect id={id} x={-s / 2} y={-s / 2} width={s} height={s} opacity={g.op}
    transform={`translate(${g.x},${g.y}) rotate(${g.r}) scale(${g.k})`} />
);

// Pas de pastille (fond 100 % transparent, retour d'Harry) : un fin halo clair autour du trait
// garde le bleu marine lisible sur fond sombre.
const halo = (h: number) =>
  `drop-shadow(0 0 ${(h * 0.006).toFixed(2)}px rgba(255,255,255,0.95)) drop-shadow(0 0 ${(h * 0.02).toFixed(2)}px rgba(255,255,255,0.7))`;

export const LogoSVG: React.FC<{e: Etat; height: number; color?: string; pastille?: boolean}> = ({e, height, color = NAVY, pastille = false}) => {
  const w = (height * VB.w) / VB.h;
  const p = e.pose;
  return (
    <div style={{width: w, height, position: 'relative'}}>
      {pastille && (
        <div style={{
          position: 'absolute', inset: 0, borderRadius: height * 0.2, background: 'rgba(255,255,255,0.93)',
          boxShadow: `0 ${height * 0.015}px ${height * 0.07}px rgba(0,0,0,0.28)`,
          transform: `scale(${e.pastille})`, opacity: clamp01(e.pastille * 3),
        }} />
      )}
      <svg viewBox={`${VB.x} ${VB.y} ${VB.w} ${VB.h}`} width={w} height={height} style={{position: 'absolute', inset: 0, overflow: 'visible', filter: pastille ? undefined : halo(height)}}>
        <g id="saliere" fill="none" stroke={color} strokeWidth={2.2} strokeLinecap="round" strokeLinejoin="round" opacity={e.op}
          transform={`translate(${PIVOT.x + p.tx},${PIVOT.y + p.ty}) rotate(${p.angle}) scale(${SCALE * e.s})`}>
          <g id="corps">
            <path id="corps-contour" d="M-14,-6 C-15,10 -17,32 -18,46 Q-18,52 -12,52 L12,52 Q18,52 18,46 C17,32 15,10 14,-6" />
            <path id="corps-fond" d="M-16.6,42.5 L16.6,42.5" strokeWidth={1.3} />
            <path id="corps-reflet" d="M-7.5,3 C-8.5,16 -9.5,27 -10.5,36" strokeWidth={1.3} />
          </g>
          <g id="bouchon">
            <path id="bague" d="M-15.5,-6 L-15.5,-14 L15.5,-14 L15.5,-6 Z" />
            <path id="bague-ligne" d="M-15.5,-10 L15.5,-10" strokeWidth={1.1} />
            <path id="dome" d="M-15,-14 C-15,-29 -8,-34 0,-34 C8,-34 15,-29 15,-14" />
            <g id="trous" fill={color} stroke="none">
              {HOLES.map(([x, y], i) => <circle key={i} cx={x} cy={y} r={1.5} />)}
            </g>
          </g>
        </g>
        <g id="grains" fill={color}>
          {e.grains.map((g, i) => <Grain key={i} id={`grain-${i + 1}`} g={g} s={GRAINS[i].s} />)}
          {e.extra && <Grain id="grain-mini" g={e.extra} s={2.8} />}
        </g>
      </svg>
    </div>
  );
};

export const etatAnim = (f: number, R: Rythme): Etat => {
  if (f >= R.duree) return REST;
  const [a, b] = R.pop;
  const u = clamp01((f - a) / (b - a));
  return {
    pastille: interpolate(u, [0, 1], [0.55, 1], {easing: Easing.out(Easing.back(R === RYTHMES.punchy ? 2.2 : 1.4))}),
    op: interpolate(u, [0, 0.6], [0, 1], {extrapolateRight: 'clamp'}),
    s: interpolate(u, [0, 1], [0.8, 1], {easing: Easing.out(Easing.cubic)}),
    pose: poseAt(f, R),
    grains: grainsAt(f, R),
  };
};

// mini (0,5 s) : secousse + un grain qui traverse la traînée et s'efface → finit sur le logo fixe
export const MINI_FRAMES = 15;
export const etatMini = (f: number): Etat => {
  if (f >= MINI_FRAMES - 1) return REST;
  const poseMini = (t: number): Pose => {
    const s = shakeAt(t, 0, 9, 2, 2.2, 3);
    return {angle: ANGLE + s.angle, tx: s.tx, ty: s.ty};
  };
  const pose = poseMini(f);
  const g = fall(f, 3, 10, holeWorld(HOLES[1], poseMini(3)), {x: 70, y: 178}, 30);
  const p = clamp01((f - 3) / 10);
  g.op *= interpolate(p, [0.65, 1], [1, 0], {extrapolateLeft: 'clamp'});
  return {...REST, pose, extra: g};
};

// ---------- Placement dans le 1080×1920 ----------
// Haut-droite, hors interface Insta/TikTok : marge droite 90 px (règle DA), haut 280 px (bandeau Reels/TikTok)
export const PLACE = {right: 90, top: 280, height: 246}; // ×1,5 (retour d'Harry) → dessin du logo ≈ 225 px

const Overlay: React.FC<{e: Etat}> = ({e}) => (
  <AbsoluteFill>
    <div style={{position: 'absolute', right: PLACE.right, top: PLACE.top}}>
      <LogoSVG e={e} height={PLACE.height} />
    </div>
  </AbsoluteFill>
);

export const TENUE = 15; // 0,5 s de logo fixe après l'animation
export const LogoAnim: React.FC<{rythme: 'douce' | 'punchy'}> = ({rythme}) => {
  const f = useCurrentFrame();
  return <Overlay e={etatAnim(f, RYTHMES[rythme])} />;
};
export const LogoMini: React.FC = () => <Overlay e={etatMini(useCurrentFrame())} />;
export const LogoFixe: React.FC = () => <Overlay e={REST} />;

// ---------- Version titre (grande) ----------
export const TITRE_FRAMES = 90;
export const LogoTitre: React.FC<{rythme: 'douce' | 'punchy'}> = ({rythme}) => {
  const f = useCurrentFrame();
  const R = RYTHMES[rythme];
  const t = f - (R.duree - 8);
  const k = interpolate(t, [0, 7], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.back(1.6))});
  return (
    <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center'}}>
      <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 36, marginTop: -120}}>
        <LogoSVG e={etatAnim(f, R)} height={560} />
        <div style={{
          fontFamily: TIKTOK, fontWeight: 800, fontSize: 104, color: NAVY, lineHeight: 1,
          textShadow: '0 0 4px rgba(255,255,255,0.95), 0 0 16px rgba(255,255,255,0.7)', opacity: clamp01(k * 2), transform: `scale(${0.7 + 0.3 * k})`,
          letterSpacing: -1, whiteSpace: 'nowrap',
        }}>
          Guest Interview
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ---------- Aperçus (fond clair / sombre, vraie taille + zoom) ----------
const FONDS = {
  clair: {src: 'rushes/10k/20261121_153142.mp4', start: 20},
  sombre: {src: 'rushes/halloween/20261030_223640.mp4', start: 20},
};
const DEBUT = 15; // l'anim démarre à 0,5 s

const Phone: React.FC<{fond: 'clair' | 'sombre'; children: React.ReactNode}> = ({fond, children}) => (
  <div style={{position: 'absolute', width: 1080, height: 1920, overflow: 'hidden'}}>
    <OffthreadVideo src={staticFile(FONDS[fond].src)} startFrom={FONDS[fond].start} muted
      style={{width: 1080, height: 1920, objectFit: 'cover'}} />
    <div style={{position: 'absolute', inset: 0}}>{children}</div>
  </div>
);

export const APERCU_FRAMES = 75;
export const LogoApercu: React.FC = () => {
  const f = useCurrentFrame() - DEBUT;
  const cells: {r: 'douce' | 'punchy'; fond: 'clair' | 'sombre'}[] = [
    {r: 'douce', fond: 'clair'}, {r: 'douce', fond: 'sombre'},
  ];
  const cx = 1080 - PLACE.right - (PLACE.height * VB.w) / VB.h / 2;
  const cy = PLACE.top + PLACE.height / 2;
  const Z = 1.6;
  return (
    <AbsoluteFill style={{background: '#111'}}>
      {cells.map((c, i) => {
        const e = etatAnim(Math.max(0, f), RYTHMES[c.r]);
        const scene = <Phone fond={c.fond}><Overlay e={f < 0 ? {...e, op: 0, pastille: 0, grains: []} : e} /></Phone>;
        return (
          <React.Fragment key={i}>
            {/* vraie taille réduite de moitié */}
            <div style={{position: 'absolute', left: i * 540, top: 0, width: 540, height: 960, overflow: 'hidden'}}>
              <div style={{transform: 'scale(0.5)', transformOrigin: '0 0'}}>{scene}</div>
            </div>
            {/* zoom sur le logo */}
            <div style={{position: 'absolute', left: i * 540, top: 960, width: 540, height: 960, overflow: 'hidden', borderTop: '4px solid #111', borderLeft: i ? '4px solid #111' : undefined}}>
              <div style={{transform: `translate(${270 - Z * cx}px, ${480 - Z * cy}px) scale(${Z})`, transformOrigin: '0 0'}}>{scene}</div>
              <div style={{position: 'absolute', left: 0, right: 0, bottom: 40, textAlign: 'center', fontFamily: TIKTOK, fontWeight: 800, fontSize: 44, color: '#fff', textShadow: '0 0 6px #000, 0 0 2px #000'}}>
                {c.r === 'douce' ? 'Douce' : 'Punchy'} · fond {c.fond}
              </div>
            </div>
          </React.Fragment>
        );
      })}
    </AbsoluteFill>
  );
};
