import React from 'react';
import {
  AbsoluteFill, Audio, Img, OffthreadVideo, Sequence, interpolate, spring, Easing,
  staticFile, useCurrentFrame, useVideoConfig,
} from 'remotion';
import {loadFont} from '@remotion/google-fonts/TikTokSans';
import {loadFont as loadSlab} from '@remotion/google-fonts/RobotoSlab';
import {loadFont as loadPlayfair} from '@remotion/google-fonts/PlayfairDisplay';
import edlA from './edl_A.json';
import edlB from './edl_B.json';

const {fontFamily: TIKTOK} = loadFont('normal', {weights: ['400', '600', '700', '800'], subsets: ['latin', 'latin-ext']});
const {fontFamily: PLAYFAIR} = loadPlayfair('normal', {weights: ['900'], subsets: ['latin']});
const {fontFamily: PLAYFAIR_I} = loadPlayfair('italic', {weights: ['500'], subsets: ['latin']});
const {fontFamily: SLAB} = loadSlab('normal', {weights: ['800'], subsets: ['latin']});

// ------------------------------------------------------------------ style (paramétrable, cf. DA §6bis)
export const STYLE = {
  subFont: TIKTOK, subWeight: 700, subSize: 64, subHlScale: 1.16, subTop: 1190, subMaxWidth: 820,
  hlColor: '#F0FF00', titleTop: 250, titleSize: 76,
  red: '#C8102E',
  cardTop: 300,            // étiquettes d'info : en haut, hors sous-titres
  igBlue: '#0095F6',
};

type Edl = typeof edlA;
const F = (s: number) => Math.round(s * 30);
export const ANNONCE10K_A_FRAMES = F(edlA.duration);
export const ANNONCE10K_B_FRAMES = F(edlB.duration);
const cl = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

const OUTLINE = (px: number) => {
  const d: string[] = [];
  for (let a = 0; a < 16; a++) {
    const r = (a / 16) * Math.PI * 2;
    d.push(`${(Math.cos(r) * px).toFixed(1)}px ${(Math.sin(r) * px).toFixed(1)}px 0 #000`);
  }
  return d.join(', ') + ', 0 4px 10px rgba(0,0,0,0.45)';
};

// ------------------------------------------------------------------ INTRO : la page Insta @guestlunch recréée
// Compteur d'abonnés 0 -> 10 000 (accélère), la grille se remplit des Reels d'Harry ; à 10 000 : pop + confettis
// puis zoom dans le chiffre qui amène le plan suivant.
const fmt = (n: number) => Math.round(n).toLocaleString('fr-FR').replace(/ | /g, ' ');
const TILES = Array.from({length: 12}, (_, i) => `img/ig_tiles/t${i + 1}.jpg`);
const InstaIntro: React.FC<{hit: number}> = ({hit}) => {
  const f = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();
  const H = F(hit);
  const p = interpolate(f, [3, H], [0, 1], {...cl, easing: Easing.in(Easing.cubic)});
  const n = f >= H ? 10000 : Math.floor(p * 10000);
  const pulse = spring({frame: f - H, fps, config: {damping: 8, stiffness: 220}});
  const numScale = f >= H ? 1 + 0.22 * Math.sin(Math.min(1, (f - H) / 8) * Math.PI) : 1;
  // zoom final vers le chiffre (centre ~ x 600, y 330)
  const z = interpolate(f, [H + 6, durationInFrames], [1, 4.5], {...cl, easing: Easing.in(Easing.cubic)});
  const fadeOut = interpolate(f, [durationInFrames - 4, durationInFrames], [1, 0], cl);
  const stat = (num: string, label: string, hl = false) => (
    <div style={{textAlign: 'left', minWidth: hl ? 250 : 170}}>
      <div style={{fontWeight: 700, fontSize: 52, lineHeight: 1.15, color: hl && f >= H ? STYLE.red : '#000',
        transform: hl ? `scale(${numScale})` : undefined, transformOrigin: 'left center', display: 'inline-block'}}>{num}</div>
      <div style={{fontSize: 38, color: '#000'}}>{label}</div>
    </div>
  );
  const confetti = Array.from({length: 26}, (_, i) => {
    const a = (i / 26) * Math.PI * 2 + i;
    const d = pulse * (160 + (i % 5) * 50);
    const col = ['#F0FF00', '#C8102E', '#0095F6', '#FF8A00', '#2ECC71'][i % 5];
    return <div key={i} style={{position: 'absolute', left: 600 + Math.cos(a) * d, top: 300 + Math.sin(a) * d * 0.8,
      width: 16, height: 26, background: col, borderRadius: 4, opacity: f >= H ? 1 - Math.max(0, (f - H - 10) / 10) : 0,
      transform: `rotate(${i * 37 + f * 12}deg)`}} />;
  });
  return (
    <AbsoluteFill style={{background: '#fff', fontFamily: TIKTOK, overflow: 'hidden', opacity: fadeOut}}>
      <AbsoluteFill style={{transform: `scale(${z})`, transformOrigin: '600px 330px'}}>
        {/* barre du haut */}
        <div style={{position: 'absolute', top: 60, left: 45, right: 45, display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}>
          <div style={{fontWeight: 800, fontSize: 58, color: '#000'}}>guestlunch <span style={{fontSize: 40}}>⌄</span></div>
          <div style={{display: 'flex', gap: 50, fontSize: 60, color: '#000'}}><span>⊕</span><span>☰</span></div>
        </div>
        {/* avatar avec anneau */}
        <div style={{position: 'absolute', top: 175, left: 40, width: 260, height: 260, borderRadius: '50%',
          background: 'conic-gradient(#feda75, #fa7e1e, #d62976, #962fbf, #4f5bd5, #feda75)', padding: 9}}>
          <div style={{width: '100%', height: '100%', borderRadius: '50%', background: '#fff', padding: 7, boxSizing: 'border-box'}}>
            <Img src={staticFile('img/ig_avatar.jpg')} style={{width: '100%', height: '100%', borderRadius: '50%', objectFit: 'cover'}} />
          </div>
        </div>
        <div style={{position: 'absolute', top: 190, left: 345, fontWeight: 700, fontSize: 46, color: '#000'}}>Guest Lunch</div>
        <div style={{position: 'absolute', top: 260, left: 345, display: 'flex', gap: 30}}>
          {stat('103', 'publications')}
          {stat(fmt(n), 'followers', true)}
          {stat('81', 'suivi(e)s')}
        </div>
        {confetti}
        <div style={{position: 'absolute', top: 465, left: 45, right: 30, fontSize: 33, lineHeight: 1.4, color: '#000'}}>
          Avec les copaings, on juge les resto pas cher de Toulouse 😋<br />
          (Et parfois des resto plus chers si ce sont des pépites ✨)
        </div>
        <div style={{position: 'absolute', top: 640, left: 45, right: 45, display: 'flex', gap: 18}}>
          <div style={{flex: 1, height: 92, borderRadius: 22, background: '#EFEFEF', color: '#000', fontWeight: 700, fontSize: 40,
            display: 'flex', alignItems: 'center', justifyContent: 'center'}}>Modifier le profil</div>
          <div style={{flex: 1, height: 92, borderRadius: 22, background: '#EFEFEF', color: '#000', fontWeight: 700, fontSize: 40,
            display: 'flex', alignItems: 'center', justifyContent: 'center'}}>Partager le profil</div>
        </div>
        {/* grille : les Reels apparaissent un à un pendant que le compteur monte */}
        <div style={{position: 'absolute', top: 775, left: 0, right: 0, display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 4}}>
          {TILES.map((t, i) => {
            const s = spring({frame: f - 2 - i * 3, fps, config: {damping: 12, stiffness: 180}});
            return <div key={t} style={{aspectRatio: '3 / 4', background: '#eee', overflow: 'hidden'}}>
              <Img src={staticFile(t)} style={{width: '100%', height: '100%', objectFit: 'cover', opacity: s, transform: `scale(${0.6 + 0.4 * s})`}} />
            </div>;
          })}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ popups d'info (Harry v7)
// « Fais comme avant mais remplace le papier par du blanc, garde l'effet popup avec le bruit » :
//   même DA qu'en v1 (texte ROUGE slab, gros, penché, arrive en « pop » petit -> taille finale), fond :
//   look 'blanc'  : blanc plein (DA retenue pour l'instant)
//   look 'transp' : papier semi-transparent flouté (variante à comparer)
type Look = 'blanc' | 'transp';
const LookCtx = React.createContext<Look>('blanc');
const bgOf = (look: Look): React.CSSProperties => look === 'blanc'
  ? {background: '#fff'}
  : {background: 'rgba(255,255,255,0.38)', backdropFilter: 'blur(10px)', WebkitBackdropFilter: 'blur(10px)'};
const PaperTint: React.FC = () => (
  <Img src={staticFile('img/paper.jpg')} style={{position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'cover', opacity: 0.35}} />
);

const Card: React.FC<{lines: string[]; kind: string; bg?: Look}> = ({lines, kind, bg}) => {
  const ctx = React.useContext(LookCtx);
  const look = bg ?? ctx;   // Harry v8 : la popup date reste en blanc même en look transparent
  const f = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();
  const s = spring({frame: f, fps, config: {damping: 10, stiffness: 200}});
  const out = interpolate(f, [durationInFrames - 5, durationInFrames], [1, 0], cl);
  if (kind === 'price') {
    // tampon « 10 € » : arrive trop gros et s'écrase (effet tampon)
    const st = interpolate(f, [0, 5], [2.2, 1], {...cl, easing: Easing.out(Easing.cubic)});
    return (
      <div style={{position: 'absolute', top: STYLE.cardTop - 20, left: 0, right: 0, display: 'flex', justifyContent: 'center', opacity: out}}>
        <div style={{transform: `scale(${st}) rotate(-9deg)`, border: `14px solid ${STYLE.red}`, borderRadius: 40, padding: '6px 50px',
          ...bgOf(look), color: STYLE.red, fontFamily: SLAB, fontWeight: 800, fontSize: 190, lineHeight: 1.1,
          boxShadow: look === 'blanc' ? '0 10px 30px rgba(0,0,0,0.35)' : undefined}}>{lines[0]}</div>
      </div>
    );
  }
  const rot = kind === 'date' ? -3 : kind === 'place' ? 2.5 : -2;
  return (
    <div style={{position: 'absolute', top: STYLE.cardTop, left: 0, right: 0, display: 'flex', justifyContent: 'center', opacity: out}}>
      <div style={{transform: `scale(${0.3 + 0.7 * s}) rotate(${rot}deg)`, position: 'relative', overflow: 'hidden',
        borderRadius: 18, padding: '30px 60px', textAlign: 'center', ...bgOf(look),
        boxShadow: look === 'blanc' ? '0 12px 34px rgba(0,0,0,0.4)' : undefined}}>
        {look === 'transp' ? <PaperTint /> : null}
        <div style={{position: 'relative', color: STYLE.red}}>
          {kind === 'place' ? (
            <svg width="70" height="90" viewBox="0 0 24 30" style={{display: 'block', margin: '0 auto 6px'}}>
              <path d="M12 0C5.4 0 0 5.2 0 11.7 0 20.5 12 30 12 30s12-9.5 12-18.3C24 5.2 18.6 0 12 0zm0 16a4.5 4.5 0 110-9 4.5 4.5 0 010 9z" fill={STYLE.red} />
            </svg>
          ) : null}
          <div style={{fontFamily: SLAB, fontWeight: 800, fontSize: 92, lineHeight: 1.08, whiteSpace: 'nowrap'}}>{lines[0]}</div>
          {lines[1] ? <div style={{fontFamily: 'Arial, sans-serif', fontWeight: 700, fontSize: 64, lineHeight: 1.25, whiteSpace: 'nowrap'}}>{lines[1]}</div> : null}
        </div>
      </div>
    </div>
  );
};

// ------------------------------------------------------------------ calendrier (« note vite ça dans ton agenda »)
// Même DA que les popups (pop + penché) ; sur « agenda », le 10 se fait entourer au feutre rouge.
const Calendar: React.FC<{circle: number}> = ({circle}) => {
  const look = React.useContext(LookCtx);
  const f = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();
  const s = spring({frame: f, fps, config: {damping: 10, stiffness: 190}});
  const out = interpolate(f, [durationInFrames - 4, durationInFrames], [1, 0], cl);
  const draw = interpolate(f, [F(circle), F(circle) + 10], [1, 0], {...cl, easing: Easing.out(Easing.cubic)});
  return (
    <div style={{position: 'absolute', top: 230, left: 0, right: 0, display: 'flex', justifyContent: 'center', opacity: out}}>
      <div style={{width: 460, transform: `scale(${0.3 + 0.7 * s}) rotate(-4deg)`, borderRadius: 26, overflow: 'hidden', position: 'relative',
        ...bgOf(look), boxShadow: look === 'blanc' ? '0 16px 40px rgba(0,0,0,0.45)' : undefined}}>
        {look === 'transp' ? <PaperTint /> : null}
        <div style={{position: 'relative', background: STYLE.red, color: '#fff', textAlign: 'center', fontFamily: SLAB, fontWeight: 800,
          fontSize: 54, padding: '14px 0', letterSpacing: 2, marginBottom: 16}}>DÉCEMBRE</div>
        <div style={{position: 'relative', textAlign: 'center', padding: '0 0 22px'}}>
          <div style={{position: 'relative', fontFamily: SLAB, fontWeight: 800, fontSize: 190, lineHeight: 1.0, color: '#111'}}>10</div>
          <div style={{position: 'relative', fontFamily: 'Arial, sans-serif', fontWeight: 700, fontSize: 50, color: '#111',
            letterSpacing: 3, marginTop: 18}}>JEUDI · 19H30</div>
          <svg viewBox="0 0 500 330" preserveAspectRatio="none" style={{position: 'absolute', left: 4, top: -30, width: 450, height: 306}}>
            <path d="M140 48 C 220 0, 362 12, 388 96 C 412 182, 354 240, 250 242 C 148 244, 90 186, 104 114 C 112 76, 150 46, 206 36"
              fill="none" stroke={STYLE.red} strokeWidth={11} strokeLinecap="round" pathLength={1}
              strokeDasharray={1} strokeDashoffset={draw} />
          </svg>
        </div>
      </div>
    </div>
  );
};

// ------------------------------------------------------------------ récap final : carton d'invitation plein écran
// Zones sûres TikTok / Insta (Harry v2) : tout le texte tient dans x 80–900 (colonne de boutons à droite ~180 px)
// et y 220–1400 (légende + boutons en bas ~500 px, bandeau du haut ~200 px).
const SAFE = {left: 80, width: 820, top: 220};
const RECAP = [
  ['📅', 'Jeudi 10 décembre · 19h30'],
  ['📍', "L'Annexe Saint-Georges"],
  ['🍽️', 'Tapas + boissons maison'],
  ['💶', '10 €'],
  ['🎁', 'Jeu concours : lien en bio'],
  ['⚠️', 'Places limitées'],
];
const Recap: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const mirror = Math.floor(f / 12) % 2 === 1;   // papier : texture / reflet miroir toutes les 12 images (DA §5)
  const head = Easing.out(Easing.cubic)(interpolate(f, [0, 8], [0, 1], cl));   // fondu, plus de zoom depuis petit
  return (
    <AbsoluteFill style={{background: '#e9e9e7', overflow: 'hidden'}}>
      <Img src={staticFile('img/paper.jpg')} style={{position: 'absolute', width: '100%', height: '100%', objectFit: 'cover',
        transform: mirror ? 'scaleX(-1)' : undefined}} />
      <div style={{position: 'absolute', left: SAFE.left, top: SAFE.top, width: SAFE.width, display: 'flex', flexDirection: 'column',
        alignItems: 'center', color: STYLE.red, transformOrigin: 'center top',
        transform: `scale(${interpolate(f, [0, 110], [1, 1.04], cl)})`}}>
        <div style={{fontFamily: PLAYFAIR_I, fontStyle: 'italic', fontWeight: 500, fontSize: 58, opacity: head}}>Tu es invité à la</div>
        <div style={{fontFamily: PLAYFAIR, fontWeight: 900, fontSize: 158, lineHeight: 1.08, whiteSpace: 'nowrap', opacity: head, fontVariantNumeric: 'lining-nums',
          transform: `translateY(${(1 - head) * 30}px)`}}>Soirée 10K</div>
        <div style={{fontFamily: PLAYFAIR_I, fontStyle: 'italic', fontWeight: 500, fontSize: 48, marginTop: 2, marginBottom: 46, opacity: head}}>de @guestlunch</div>
        {RECAP.map(([e, t], k) => {
          const s = spring({frame: f - 6 - k * 3, fps, config: {damping: 12, stiffness: 200}});
          return (
            <div key={t} style={{display: 'flex', alignItems: 'center', gap: 20, fontFamily: SLAB, fontWeight: 800, fontSize: 52,
              lineHeight: 1.6, width: SAFE.width, whiteSpace: 'nowrap', opacity: s, transform: `translateX(${(1 - s) * 100}px)`}}>
              <span style={{fontSize: 54, width: 72, textAlign: 'center'}}>{e}</span><span>{t}</span>
            </div>
          );
        })}
        <div style={{marginTop: 50, fontFamily: TIKTOK, fontWeight: 700, fontSize: 54, lineHeight: 1.25, color: '#111', textAlign: 'center',
          opacity: interpolate(f, [30, 38], [0, 1], cl)}}>Tague le ou la copaign<br />qui vient avec toi 👇</div>
      </div>
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ surnom (DA §6)
const Nickname: React.FC<{lines: string[]}> = ({lines}) => {
  const f = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const e = (x: number) => 1 - Math.pow(1 - x, 3);
  const pi = e(interpolate(f, [0, 8], [0, 1], cl));
  const po = interpolate(f, [durationInFrames - 7, durationInFrames], [0, 1], cl);
  const x = (1 - pi) * 520, skew = -(1 - pi) * 14, blur = (1 - pi) * 8;
  return (
    <div style={{position: 'absolute', top: STYLE.titleTop, left: 0, right: 0, textAlign: 'center', opacity: 1 - po,
      transform: `translate(${x}px, ${-po * 45}px) skewX(${skew}deg)`, filter: blur > 0.2 ? `blur(${blur}px)` : undefined}}>
      {lines.map((l, i) => (
        <div key={i} style={{fontFamily: TIKTOK, fontWeight: 700, fontSize: STYLE.titleSize, lineHeight: 1.1, color: '#fff', textShadow: OUTLINE(4)}}>{l}</div>
      ))}
    </div>
  );
};

// ------------------------------------------------------------------ sous-titres : 1 ligne, ≤ 4 mots, mots clés jaunes
const Sub: React.FC<{words: string[]; hl: number[]}> = ({words, hl}) => {
  const est = words.reduce((acc, w, k) => acc + (w.length * 0.56 + 0.3) * STYLE.subSize * (hl.includes(k) ? STYLE.subHlScale : 1), 0);
  const fit = Math.min(1, STYLE.subMaxWidth / est);
  return (
    <div style={{position: 'absolute', top: STYLE.subTop, left: 0, right: 0, display: 'flex', justifyContent: 'center',
      transform: `scale(${fit})`, transformOrigin: 'center top'}}>
      <div style={{whiteSpace: 'nowrap', fontFamily: STYLE.subFont, fontWeight: STYLE.subWeight, fontSize: STYLE.subSize,
        lineHeight: 1.2, color: '#fff', textShadow: OUTLINE(3.2), display: 'flex', alignItems: 'baseline', gap: '0.26em'}}>
        {words.map((w, k) => (
          <span key={k} style={hl.includes(k) ? {color: STYLE.hlColor, fontSize: STYLE.subSize * STYLE.subHlScale} : undefined}>{w}</span>
        ))}
      </div>
    </div>
  );
};

export const Annonce10k: React.FC<{v: 'A' | 'B'; look?: Look}> = ({v, look = 'transp'}) => {
  const e = (v === 'B' ? edlB : edlA) as Edl;
  const ov = e.overlays as any[];
  return (
    <LookCtx.Provider value={look}>
    <AbsoluteFill style={{background: '#000'}}>
      {e.video.map((v, i) => (
        <Sequence key={`v${i}`} from={F(v.at)} durationInFrames={Math.max(1, F(v.at + v.dur) - F(v.at))} premountFor={20}>
          <OffthreadVideo src={staticFile(v.src)} trimBefore={F(v.in)} muted style={{width: '100%', height: '100%', objectFit: 'cover'}} />
        </Sequence>
      ))}
      {ov.filter((o) => o.type === 'nickname').map((o, i) => (
        <Sequence key={`n${i}`} from={F(o.at)} durationInFrames={F(o.dur)}><Nickname lines={o.lines} /></Sequence>
      ))}
      {ov.filter((o) => o.type === 'card').map((o, i) => (
        <Sequence key={`c${i}`} from={F(o.at)} durationInFrames={Math.max(6, F(o.dur))}><Card lines={o.lines} kind={o.kind} bg={o.bg} /></Sequence>
      ))}
      {ov.filter((o) => o.type === 'insta').map((o, i) => (
        <Sequence key={`i${i}`} from={F(o.at)} durationInFrames={F(o.dur)}><InstaIntro hit={o.hit} /></Sequence>
      ))}
      {ov.filter((o) => o.type === 'calendar').map((o, i) => (
        <Sequence key={`k${i}`} from={F(o.at)} durationInFrames={F(o.dur)}><Calendar circle={o.circle} /></Sequence>
      ))}
      {e.subs.map((s, i) => (
        <Sequence key={`s${i}`} from={F(s.at)} durationInFrames={Math.max(1, F(s.end) - F(s.at))}>
          <Sub words={s.words} hl={s.hl} />
        </Sequence>
      ))}
      {ov.filter((o) => o.type === 'recap').map((o, i) => (
        <Sequence key={`r${i}`} from={F(o.at)} durationInFrames={F(o.dur)}><Recap /></Sequence>
      ))}
      <Audio src={staticFile((e as any).mix)} />
    </AbsoluteFill>
    </LookCtx.Provider>
  );
};
