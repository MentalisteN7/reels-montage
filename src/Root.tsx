import React from 'react';
import {Composition, AbsoluteFill, useCurrentFrame, interpolate} from 'remotion';

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
  <Composition id="Test" component={Test} durationInFrames={30} fps={30} width={1080} height={1920} />
);
