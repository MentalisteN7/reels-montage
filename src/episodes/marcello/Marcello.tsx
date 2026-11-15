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
export const MARCELLO_FRAMES = F(edl.duration);

// contour noir fin + légère ombre (comme les sous-titres TikTok)
const OUTLINE = (px: number) => {
  const d: string[] = [];
  for (let a = 0; a < 16; a++) {
    const r = (a / 16) * Math.PI * 2;
    d.push(`${(Math.cos(r) * px).toFixed(1)}px ${(Math.sin(r) * px).toFixed(1)}px 0 #000`);
  }
  return d.join(', ') + ', 0 4px 10px rgba(0,0,0,0.45)';
};

// ------------------------------------------------------------------ papier froissé
const NOISE = `url("data:image/svg+xml;utf8,${encodeURIComponent(
  `<svg xmlns='http://www.w3.org/2000/svg' width='600' height='600'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.012' numOctaves='5' seed='7'/><feDiffuseLighting lighting-color='#fff' surfaceScale='2.2'><feDistantLight azimuth='45' elevation='55'/></feDiffuseLighting></filter><rect width='100%' height='100%' filter='url(#n)'/></svg>`,
)}")`;
const Paper: React.FC<{children?: React.ReactNode}> = ({children}) => (
  <AbsoluteFill style={{background: STYLE.paper}}>
    <AbsoluteFill style={{backgroundImage: NOISE, backgroundSize: '1080px 1080px', mixBlendMode: 'multiply', opacity: 0.55}} />
    <AbsoluteFill style={{background: 'radial-gradient(ellipse at center, rgba(255,255,255,0) 55%, rgba(120,100,70,0.18) 100%)'}} />
    {children}
  </AbsoluteFill>
);

const Tricolore: React.FC<{width: number}> = ({width}) => (
  <div style={{display: 'flex', width, height: 12, borderRadius: 6, overflow: 'hidden'}}>
    <div style={{flex: 1, background: STYLE.green}} />
    <div style={{flex: 1, background: '#fff', borderTop: '1px solid #ddd', borderBottom: '1px solid #ddd'}} />
    <div style={{flex: 1, background: STYLE.red}} />
  </div>
);

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
      <AbsoluteFill style={{alignItems: 'center', paddingTop: 330, gap: 90}}>
        <Img src={staticFile('img/sticker_marcello.png')} style={{width: 640, transform: `scale(${sc}) rotate(${rot}deg)`}} />
        <div style={{textAlign: 'center', color: STYLE.red}}>
          <div style={{fontFamily: 'Arial, sans-serif', fontSize: 62, lineHeight: 1.3}}>Pizzeria napolitaine :</div>
          <div style={{fontFamily: SLAB, fontWeight: 800, fontSize: 128, lineHeight: 1.05}}>Marcello</div>
          <div style={{fontFamily: SLAB, fontWeight: 800, fontSize: 72, lineHeight: 1.1}}>Toulouse</div>
        </div>
      </AbsoluteFill>
    </PaperFlip>
  );
};

// ------------------------------------------------------------------ carte Google Maps (nom + note)
const MapsCard: React.FC = () => {
  const f = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();
  const s = spring({frame: f, fps, config: {damping: 11, stiffness: 160}});
  const out = interpolate(f, [durationInFrames - 6, durationInFrames], [1, 0], {extrapolateLeft: 'clamp'});
  return (
    <AbsoluteFill style={{alignItems: 'center', paddingTop: 300}}>
      <div style={{transform: `scale(${0.55 + 0.45 * s})`, opacity: Math.min(s * 1.6, 1) * out,
        borderRadius: 14, overflow: 'hidden', boxShadow: '0 16px 40px rgba(0,0,0,0.45)', background: '#fff'}}>
        <Img src={staticFile('img/maps_marcello_card.png')} style={{width: 600, display: 'block'}} />
      </div>
    </AbsoluteFill>
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

// ------------------------------------------------------------------ carton résultat (validé)
const ResultCard: React.FC<{notes: string[][]; avg: string}> = ({notes, avg}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const pop = (t: number) => spring({frame: f - F(t), fps, config: {damping: 10, stiffness: 180}});
  const avgIn = pop(0.35 + notes.length * 0.45 + 0.1);
  return (
    <Paper>
      <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', gap: 40}}>
        <div style={{fontFamily: STYLE.script, fontSize: 120, color: STYLE.red, transform: 'rotate(-3deg)'}}>Marcello</div>
        <Tricolore width={360} />
        <div style={{display: 'flex', flexDirection: 'column', gap: 18, marginTop: 20}}>
          {notes.map(([name, note], k) => {
            const p = pop(0.35 + k * 0.45);
            return (
              <div key={name} style={{display: 'flex', justifyContent: 'space-between', width: 640,
                opacity: Math.min(p * 1.5, 1), transform: `translateX(${(1 - p) * -60}px)`,
                fontFamily: STYLE.script, fontSize: 82, color: '#222'}}>
                <span>{name}</span><span style={{color: STYLE.red}}>{note}/10</span>
              </div>
            );
          })}
        </div>
        <div style={{marginTop: 40, transform: `scale(${avgIn}) rotate(-2deg)`, background: STYLE.red, color: '#fff',
          padding: '18px 46px', borderRadius: 20, fontFamily: STYLE.serif, fontWeight: 900, fontSize: 96,
          boxShadow: '0 12px 30px rgba(0,0,0,0.25)'}}>
          Moyenne {avg}/10
        </div>
      </AbsoluteFill>
    </Paper>
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

export const Marcello: React.FC = () => {
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
      {ov.filter((o) => o.type === 'maps').map((o, i) => (
        <Sequence key={`m${i}`} from={F(o.at)} durationInFrames={F(o.dur)}><MapsCard /></Sequence>
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
      {ov.filter((o) => o.type === 'title' || o.type === 'result').map((o, i) => (
        <Sequence key={`o${i}`} from={F(o.at)} durationInFrames={F(o.dur)}>
          {o.type === 'title' ? <TitleCard /> : <ResultCard notes={o.notes} avg={o.avg} />}
        </Sequence>
      ))}
      {/* tout l'audio (VO, interviews, bruitages) = un seul mix à l'échantillon près (tools/mixdown.py) */}
      <Audio src={staticFile((e as any).mix)} />
    </AbsoluteFill>
  );
};
