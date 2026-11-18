import React from 'react';
import {
  AbsoluteFill, Audio, Img, OffthreadVideo, Sequence, interpolate, spring,
  staticFile, useCurrentFrame, useVideoConfig,
} from 'remotion';
import {loadFont} from '@remotion/google-fonts/TikTokSans';
import {loadFont as loadSlab} from '@remotion/google-fonts/RobotoSlab';
import edl from './edl.json';

// TikTok Sans = police « Classique » de TikTok (libre, Google Fonts) — DA §6bis
const {fontFamily: TIKTOK} = loadFont('normal', {weights: ['600', '700', '800'], subsets: ['latin', 'latin-ext']});
const {fontFamily: SLAB} = loadSlab('normal', {weights: ['800'], subsets: ['latin']});

// ------------------------------------------------------------------ style (paramétrable, cf. DA §6bis)
export const STYLE = {
  subFont: TIKTOK,
  subWeight: 700,
  subSize: 64,            // petits mots
  subHlScale: 1.16,       // mots clés un peu plus gros
  subTop: 1190,           // ~62 % de 1920, hors zones d'UI Insta/TikTok
  subMaxWidth: 820,       // une seule ligne, marge pour like/comment
  hlColor: '#F0FF00',     // jaune exact mesuré sur le Kebab publié (RGB 240,255,0)
  titleTop: 250,          // titres surnoms ~13 % du haut (réf. Kebab)
  titleSize: 76,
  green: '#1E8449',
  red: '#C8102E',
  paper: '#F5F1E8',
  script: '"Segoe Script", "Brush Script MT", cursive',
  serif: '"Rockwell Extra Bold", "Rockwell", Georgia, serif',
};

type Edl = typeof edl;
const F = (s: number) => Math.round(s * edl.fps);
export const ALIGOFEST_FRAMES = F(edl.duration);

// contour noir fin + légère ombre (comme les sous-titres TikTok)
const OUTLINE = (px: number) => {
  const d: string[] = [];
  for (let a = 0; a < 16; a++) {
    const r = (a / 16) * Math.PI * 2;
    d.push(`${(Math.cos(r) * px).toFixed(1)}px ${(Math.sin(r) * px).toFixed(1)}px 0 #000`);
  }
  return d.join(', ') + ', 0 4px 10px rgba(0,0,0,0.45)';
};

// ------------------------------------------------------------------ carton titre (DA §5 : papier froissé « qui bouge » + rouge, comme la série Kebab)
// Papier (réf. Kebab) : la texture reste 12 images, puis son reflet miroir 12 images, et ainsi de suite
const PaperFlip: React.FC<{children?: React.ReactNode}> = ({children}) => {
  const f = useCurrentFrame();
  const mirror = Math.floor(f / 12) % 2 === 1;
  return (
    <AbsoluteFill style={{background: '#e9e9e7', overflow: 'hidden'}}>
      <Img src={staticFile('img/paper.jpg')} style={{position: 'absolute', width: '100%', height: '100%', objectFit: 'cover',
        transform: mirror ? 'scaleX(-1)' : undefined}} />
      {children}
    </AbsoluteFill>
  );
};
// Plat détouré : zoom/dézoom à l'apparition (image 1), puis rotation lente de ROT[0] à ROT[1] sur tout le carton
const POP = [0, 0.25, 0.62, 1.15, 1.08, 1.03, 1.0];
const ROT = [-4.5, 4.5];   // mesuré dans la réf. Kebab (~±4,5°) ; Harry a dit « -45° → 45° » : à confirmer
const TitleCard: React.FC = () => {
  const f = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const sc = f < POP.length ? POP[f] : 1;
  const rot = interpolate(f, [1, durationInFrames], ROT, {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <PaperFlip>
      <AbsoluteFill style={{alignItems: 'center', paddingTop: 360, gap: 90}}>
        <Img src={staticFile('img/sticker_aligot.png')} style={{width: 700, transform: `scale(${sc}) rotate(${rot}deg)`}} />
        <div style={{textAlign: 'center', color: STYLE.red}}>
          <div style={{fontFamily: 'Arial, sans-serif', fontSize: 62, lineHeight: 1.3}}>Le plus grand aligot du monde :</div>
          <div style={{fontFamily: SLAB, fontWeight: 800, fontSize: 138, lineHeight: 1.05}}>Aligofest</div>
          <div style={{fontFamily: SLAB, fontWeight: 800, fontSize: 72, lineHeight: 1.1}}>Toulouse</div>
        </div>
      </AbsoluteFill>
    </PaperFlip>
  );
};

// ------------------------------------------------------------------ titres « surnoms » (DA §6, réf. Kebab)
// Sobre : blanc, contour noir fin (mesuré sur le Kebab publié), police type TikTok « Classique ».
// Chaque surnom a une entrée ET une sortie différentes des autres (animations simples type CapCut) :
//   in  : slide (glisse de la droite, italique + flou) | rise (monte en fondu) | type (machine à écrire)
//         | wipe (révélé de gauche à droite) | zoom (arrive de plus grand, flou → net)
//   out : slide (part à gauche) | rise (part vers le haut en fondu) | blur (se floute et disparaît)
//         | drop (descend en fondu) | shrink (rétrécit en fondu)
const NICK_IN = 8, NICK_OUT = 7;
const Nickname: React.FC<{lines: string[]; inAnim: string; outAnim: string}> = ({lines, inAnim, outAnim}) => {
  const f = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const e = (x: number) => 1 - Math.pow(1 - x, 3);
  const cl = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
  const inLen = inAnim === 'type' ? 14 : inAnim === 'wipe' ? 10 : NICK_IN;
  const pi = e(interpolate(f, [0, inLen], [0, 1], cl));
  const po = interpolate(f, [durationInFrames - NICK_OUT, durationInFrames], [0, 1], cl);
  const q = po * po;
  let x = 0, y = 0, skew = 0, blur = 0, op = 1, sc = 1, clip: string | undefined;
  if (inAnim === 'slide') { x += (1 - pi) * 520; skew -= (1 - pi) * 14; blur += (1 - pi) * 8; }
  if (inAnim === 'rise') { y += (1 - pi) * 70; op *= pi; }
  if (inAnim === 'wipe') { clip = `inset(-20px ${(1 - pi) * 100}% -20px -20px)`; }
  if (inAnim === 'zoom') { sc *= 1 + (1 - pi) * 0.35; blur += (1 - pi) * 10; op *= pi; }
  if (outAnim === 'slide') { x -= q * 620; }
  if (outAnim === 'rise') { y -= po * 45; op *= 1 - po; }
  if (outAnim === 'blur') { blur += po * 12; op *= 1 - po; }
  if (outAnim === 'drop') { y += po * 50; op *= 1 - po; }
  if (outAnim === 'shrink') { sc *= 1 - po * 0.3; op *= 1 - po; }
  // machine à écrire : lettres révélées une à une sur les 2 lignes
  const total = lines.join('').length;
  const shown = inAnim === 'type' ? Math.floor(interpolate(f, [0, inLen], [0, total], cl)) : total;
  let used = 0;
  return (
    <div style={{position: 'absolute', top: STYLE.titleTop, left: 0, right: 0, textAlign: 'center', opacity: op, clipPath: clip,
      transform: `translate(${x}px, ${y}px) skewX(${skew}deg) scale(${sc})`, filter: blur > 0.2 ? `blur(${blur}px)` : undefined}}>
      {lines.map((l, i) => {
        const n = Math.max(0, Math.min(l.length, shown - used)); used += l.length;
        return (
          <div key={i} style={{fontFamily: TIKTOK, fontWeight: 700, fontSize: STYLE.titleSize, lineHeight: 1.1, color: '#fff',
            textShadow: OUTLINE(4)}}>
            {l.slice(0, n)}<span style={{opacity: 0}}>{l.slice(n)}</span>
          </div>
        );
      })}
    </div>
  );
};

// ------------------------------------------------------------------ compteur d'assiettes (objectif 5)
// Badge en haut à droite : 5 assiettes en pointillé, la n-ième se remplit avec un « pop » à chaque nouvelle assiette
const PlateIcon: React.FC<{on: boolean; s: number}> = ({on, s}) => (
  // l'assiette aligot-saucisse du carton titre (Harry v2) ; pas encore mangée = grisée, transparente
  <Img src={staticFile('img/sticker_aligot.png')} style={{width: 155, transform: `scale(${s})`,
    filter: on ? 'drop-shadow(0 4px 8px rgba(0,0,0,0.45))' : 'grayscale(1) brightness(1.4)', opacity: on ? 1 : 0.4}} />
);
const Counter: React.FC<{steps: number[][]}> = ({steps}) => {
  // steps : [[t_local, n]] — n assiettes mangées à partir de t_local
  const f = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();
  let n = 0, t0 = 0;
  for (const [t, k] of steps) if (f >= F(t)) { n = k; t0 = F(t); }
  const p = spring({frame: f - t0, fps, config: {damping: 9, stiffness: 200}});
  const show = spring({frame: f, fps, config: {damping: 14}});
  const out = interpolate(f, [durationInFrames - 6, durationInFrames], [1, 0], {extrapolateLeft: 'clamp'});
  return (
    <div style={{position: 'absolute', top: 210, left: 0, right: 0, display: 'flex', flexDirection: 'column', alignItems: 'center',
      gap: 10, opacity: show * out, transform: `translateY(${(1 - show) * -40}px)`}}>
      <div style={{fontFamily: TIKTOK, fontWeight: 800, fontSize: 64, color: '#fff', textShadow: OUTLINE(4)}}>
        Assiette <span style={{color: STYLE.hlColor, display: 'inline-block', transform: `scale(${0.6 + 0.4 * p})`}}>{n}</span>/5
      </div>
      <div style={{display: 'flex', gap: 6}}>
        {[1, 2, 3, 4, 5].map((k) => <PlateIcon key={k} on={k <= n} s={k === n ? 0.5 + 0.5 * p : 1} />)}
      </div>
    </div>
  );
};

// ------------------------------------------------------------------ scores de fin (sur le plan où Harry rentre en boitant)
const Scores: React.FC<{rows: string[][]; step: number}> = ({rows, step}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  return (
    <div style={{position: 'absolute', top: 190, left: 0, right: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4}}>
      {rows.map(([name, score, extra], k) => {
        const p = spring({frame: f - F(k * step), fps, config: {damping: 10, stiffness: 180}});
        return (
          <div key={name} style={{fontFamily: TIKTOK, fontWeight: 700, fontSize: 70, color: '#fff', textShadow: OUTLINE(4),
            whiteSpace: 'nowrap', opacity: Math.min(p * 1.5, 1), transform: `scale(${0.5 + 0.5 * p})`}}>
            {name} : <span style={{color: STYLE.hlColor, fontSize: 70 * STYLE.subHlScale}}>{score}</span>
            {extra ? <div style={{textAlign: 'center', color: STYLE.hlColor, fontSize: 70 * STYLE.subHlScale}}>{extra}</div> : null}
          </div>
        );
      })}
    </div>
  );
};

// ------------------------------------------------------------------ sous-titres : 1 ligne, ≤ 4 mots, mots clés jaunes
const Sub: React.FC<{words: string[]; hl: number[]; emoji: string}> = ({words, hl, emoji}) => {
  // pas d'animation (Harry v3 : pas de zoom/dézoom) ; estimation de largeur -> réduction si la ligne dépasse (jamais de retour à la ligne)
  const est = words.reduce((acc, w, k) => acc + (w.length * 0.56 + 0.3) * STYLE.subSize * (hl.includes(k) ? STYLE.subHlScale : 1), 0);
  const fit = Math.min(1, STYLE.subMaxWidth / est);
  return (
    <div style={{position: 'absolute', top: STYLE.subTop, left: 0, right: 0, display: 'flex', flexDirection: 'column',
      alignItems: 'center', transform: `scale(${fit})`, transformOrigin: 'center top'}}>
      <div style={{whiteSpace: 'nowrap', fontFamily: STYLE.subFont, fontWeight: STYLE.subWeight, fontSize: STYLE.subSize,
        lineHeight: 1.2, color: '#fff', textShadow: OUTLINE(3.2), display: 'flex', alignItems: 'baseline', gap: '0.26em'}}>
        {words.map((w, k) => (
          <span key={k} style={hl.includes(k) ? {color: STYLE.hlColor, fontSize: STYLE.subSize * STYLE.subHlScale} : undefined}>{w}</span>
        ))}
      </div>
      {emoji ? <div style={{fontSize: 76, lineHeight: 1.1, marginTop: 6}}>{emoji}</div> : null}
    </div>
  );
};

export const Aligofest: React.FC = () => {
  const e = edl as Edl;
  const ov = e.overlays as any[];
  return (
    <AbsoluteFill style={{background: '#000'}}>
      {e.video.map((v, i) => (
        <Sequence key={`v${i}`} from={F(v.at)} durationInFrames={Math.max(1, F(v.at + v.dur) - F(v.at))} premountFor={20}>
          <OffthreadVideo src={staticFile(v.src)} trimBefore={F(v.in)} muted
            style={{width: '100%', height: '100%', objectFit: 'cover'}} />
        </Sequence>
      ))}
      {ov.filter((o) => o.type === 'counter').map((o, i) => (
        <Sequence key={`c${i}`} from={F(o.at)} durationInFrames={F(o.dur)}><Counter steps={o.steps} /></Sequence>
      ))}
      {ov.filter((o) => o.type === 'scores').map((o, i) => (
        <Sequence key={`sc${i}`} from={F(o.at)} durationInFrames={F(o.dur)}><Scores rows={o.rows} step={o.step} /></Sequence>
      ))}
      {ov.filter((o) => o.type === 'nickname').map((o, i) => (
        <Sequence key={`n${i}`} from={F(o.at)} durationInFrames={F(o.dur)}><Nickname lines={o.lines} inAnim={o.in} outAnim={o.out} /></Sequence>
      ))}
      {e.subs.map((s, i) => (
        <Sequence key={`s${i}`} from={F(s.at)} durationInFrames={Math.max(1, F(s.end) - F(s.at))}>
          <Sub words={s.words} hl={s.hl} emoji={s.emoji} />
        </Sequence>
      ))}
      {/* cartons plein écran au-dessus des sous-titres */}
      {ov.filter((o) => o.type === 'title').map((o, i) => (
        <Sequence key={`o${i}`} from={F(o.at)} durationInFrames={F(o.dur)}>
          <TitleCard />
        </Sequence>
      ))}
      {/* tout l'audio (VO, interviews, bruitages) = un seul mix à l'échantillon près (tools/mixdown.py) */}
      <Audio src={staticFile((e as any).mix)} />
    </AbsoluteFill>
  );
};
