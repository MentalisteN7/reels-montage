import React from 'react';
import {Composition, AbsoluteFill, useCurrentFrame, interpolate} from 'remotion';
import {Marcello, MARCELLO_FRAMES} from './episodes/marcello/Marcello';
import {Aligofest, ALIGOFEST_FRAMES} from './episodes/aligofest/Aligofest';
import {Halloween, HALLOWEEN_FRAMES} from './episodes/halloween/Halloween';
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
  </>
);
