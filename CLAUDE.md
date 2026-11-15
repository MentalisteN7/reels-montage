# Projet reels-montage — contexte pour Claude

Montage de Reels (Instagram/TikTok, 9:16) pour **@guestlunch** (Harry, « l'influenceur en carton », Toulouse) avec **Remotion**.

## À lire en premier
- `DA.md` : direction artistique complète (✅ validé par Harry, 🟡 observé par Claude, ✏️ corrigé). **Source de vérité.**
- `docs/analyses/` : 16 Reels analysés (planches de plans, découpage, transcriptions Whisper)
- `docs/stats/` : stats Instagram (xlsx avec noms des vidéos) + analyse précédente
- `docs/invites/` : **prénoms, surnoms et visages** d'Harry et des invités récurrents (à relire pour reconnaître les gens dans les rushes)
- `docs/montage_harry/COMMENT_HARRY_MONTE.md` : **comment Harry monte vraiment** (mesuré sur ses 84 projets Premiere : rythme, coupe de la parole, structure, choix des rushes) — à appliquer à chaque montage
- `docs/stats/ANALYSE_TYPES_RYTHME.md` : vues par type de vidéo + rythme (s/plan) des Reels qui marchent

## Méthode de travail (voulue par Harry)
1. Avant tout montage : **poser toutes les questions** et valider un plan de montage avec Harry.
2. Rendu de validation en **720p**, Harry corrige (timecodes + retours généraux), on itère.
   - **Avant d'envoyer un rendu à Harry : le faire relire par l'agent `relecteur`** (`.claude/agents/relecteur.md`, outil `tools/relecture.py`) → corriger les « Bloquant », puis envoyer la vidéo avec un résumé du rapport
3. Toute correction de Harry sur le style → **mettre à jour `DA.md`** (statut ✏️/✅).
4. Si incertain : le dire. Si une approche est mauvaise : le dire et proposer autre chose.

## Rushes
- Rushes d'origine smartphone, **souvent 4K portrait (2160×3840) avec cadences mixtes (30/60/120/240 fps)** → toujours passer par des proxies 1080×1920 30 fps : `python tools/make_proxies.py <rushes> public/rushes/<episode>` (vitesse réelle, pas de ralenti). Voix off de Harry **enregistrée à part**, invités en son direct (micro-cravate).
- Les rushes ne vont **jamais** dans git (`.gitignore`). Les mettre dans `rushes/<episode>/`.

## Outils
- `python tools/prproj.py <projet.prproj> [out.json]` → timeline réelle d'un projet Premiere d'Harry ; `tools/batch_prproj.py`, `tools/analyse_timelines.py`, `tools/cut_margins.py`, `tools/choix_rushes.py`, `tools/planche_annotee.py` → étude de son montage (`docs/montage_harry/`)
- `python tools/transcribe.py <video_ou_audio> medium` → transcription FR avec timestamps par mot (`.words.json`)
- `python tools/analyze.py <video> <dossier_sortie>` → coupes, planche contact, `shots.json`
- `bash tools/batch_analyze.sh <dossier_videos> <dossier_sortie>` (Git Bash sous Windows)
- `npm run studio` → Remotion Studio ; `npm run render -- <Composition> out/x.mp4`
- `python tools/speech_regions.py <fichier> [seuil_dB] [silence_min]` → zones de parole (sert à couper blancs et « euh »)
- **Audio : jamais l'audio Remotion pour la parole** (coupé sur la grille des images = coupes hachées). `build_edl.py` appelle `tools/mixdown.py` → `public/mix/<ep>.wav` (assemblé à l'échantillon depuis les fichiers ORIGINAUX, fondus 6 ms, gain fixe par personne, -14 LUFS + limiteur) ; Remotion ne lit que ce WAV. Rendu avec `--audio-bitrate=320k`
- Whisper peut mal placer un mot (Marcello : « pistaches » décalé de 1,5 s) → re-transcrire le rendu et comparer au texte attendu
- Rendu 720p : Remotion refuse `--scale=0.667` (dimensions non entières) → rendre en 1080p puis `ffmpeg -vf scale=720:1280`
- Windows : ffmpeg `drawtext` a besoin de `fontfile='C\:/Windows/Fonts/arial.ttf'` ; git sur D: demande `-c safe.directory=...`

## Structure d'un épisode (modèle : `src/episodes/marcello/`)
- `build_edl.py` : **le montage** (choix des prises VO, plages d'interview, plans, B-roll ancrés sur les mots, sous-titres) → `edl.json`
  - Sous-titres écrits à la main : `|` sépare les apparitions (≤ 4 mots, 1 ligne, découpe cohérente), `*mot*` = jaune, `{🍕}` = emoji sur sa ligne
  - Dynamisme automatique : silences et « euh » coupés, fins de phrase raccourcies (TRIM), coupes d'interview cachées par du B-roll
  - Affiche les contrôles : blancs audio, trous vidéo, sous-titres > 4 mots
- `Marcello.tsx` : rendu Remotion (styles paramétrables dans `STYLE`), `words/` : transcriptions Whisper utilisées
- Assets non versionnés : `public/rushes/<ep>/` (proxies), `public/vo/`, `public/img/`, `public/sfx/` (Mixkit)
