import {Config} from '@remotion/cli/config';
import fs from 'fs';

// Conteneur cloud Linux : utiliser le Chromium préinstallé. Sur Windows/Mac, Remotion télécharge le sien.
const cloudChrome = '/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell';
if (fs.existsSync(cloudChrome)) {
  Config.setBrowserExecutable(cloudChrome);
}
Config.setVideoImageFormat('jpeg');
