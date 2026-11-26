import React from 'react';
import {Composition, AbsoluteFill, useCurrentFrame, interpolate} from 'remotion';
import {Marcello, MARCELLO_FRAMES} from './episodes/marcello/Marcello';
import {Aligofest, ALIGOFEST_FRAMES} from './episodes/aligofest/Aligofest';
import {Halloween, HALLOWEEN_FRAMES} from './episodes/halloween/Halloween';
import {LogoAnim, LogoMini, LogoFixe, LogoTitre, LogoApercu, RYTHMES, TENUE, MINI_FRAMES, TITRE_FRAMES, APERCU_FRAMES} from './logo/GuestLogo';
import {Annonce10k, ANNONCE10K_A_FRAMES, ANNONCE10K_B_FRAMES} from './episodes/10k/Annonce10k';

const Test: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{background: '#f2f0ec', justifyContent: 'center', alignItems: 'center'}}>
      <div style={{color: '#d0021b', fontSize: 90, fontWeight: 800, opacity: interpolate(f, [0, 15], [0, 1])}}>
        Test Remotion
      </div>
    </AbsoluteFill>
  );
};

export const Root: React.FC = () => (
  <>
    <Composition id="Test" component={Test} durationInFrames={30} fps={30} width={1080} height={1920} />
    <Composition id="Marcello" component={Marcello} durationInFrames={MARCELLO_FRAMES} fps={30} width={1080} height={1920} />
    <Composition id="Aligofest" component={Aligofest} durationInFrames={ALIGOFEST_FRAMES} fps={30} width={1080} height={1920} />
    <Composition id="Halloween" component={Halloween} durationInFrames={HALLOWEEN_FRAMES} fps={30} width={1080} height={1920} />
    <Composition id="Annonce10kA" component={Annonce10k} defaultProps={{v: 'A' as const}} durationInFrames={ANNONCE10K_A_FRAMES} fps={30} width={1080} height={1920} />
    <Composition id="Annonce10kA-transp" component={Annonce10k} defaultProps={{v: 'A' as const, look: 'transp' as const}} durationInFrames={ANNONCE10K_A_FRAMES} fps={30} width={1080} height={1920} />
    <Composition id="Annonce10kB" component={Annonce10k} defaultProps={{v: 'B' as const}} durationInFrames={ANNONCE10K_B_FRAMES} fps={30} width={1080} height={1920} />
    {(['douce', 'punchy'] as const).map((r) => (
      <React.Fragment key={r}>
        <Composition id={`Logo-${r}`} component={LogoAnim} defaultProps={{rythme: r}} durationInFrames={RYTHMES[r].duree + TENUE} fps={30} width={1080} height={1920} />
        <Composition id={`LogoTitre-${r}`} component={LogoTitre} defaultProps={{rythme: r}} durationInFrames={TITRE_FRAMES} fps={30} width={1080} height={1920} />
      </React.Fragment>
    ))}
    <Composition id="Logo-mini" component={LogoMini} durationInFrames={MINI_FRAMES} fps={30} width={1080} height={1920} />
    <Composition id="Logo-fixe" component={LogoFixe} durationInFrames={1} fps={30} width={1080} height={1920} />
    <Composition id="Logo-apercu" component={LogoApercu} durationInFrames={APERCU_FRAMES} fps={30} width={1080} height={1920} />
  </>
);
