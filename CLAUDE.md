# Projet reels-montage — contexte pour Claude

Montage de Reels (Instagram/TikTok, 9:16) pour **@guestlunch** (Harry, « l'influenceur en carton », Toulouse) avec **Remotion**.

## À lire en premier
- `DA.md` : direction artistique complète (✅ validé par Harry, 🟡 observé par Claude, ✏️ corrigé). **Source de vérité.**
- `docs/analyses/` : 16 Reels analysés (planches de plans, découpage, transcriptions Whisper)
- `docs/stats/` : stats Instagram (xlsx avec noms des vidéos) + analyse précédente

## Méthode de travail (voulue par Harry)
1. Avant tout montage : **poser toutes les questions** et valider un plan de montage avec Harry.
2. Rendu de validation en **720p**, Harry corrige (timecodes + retours généraux), on itère.
3. Toute correction de Harry sur le style → **mettre à jour `DA.md`** (statut ✏️/✅).
4. Si incertain : le dire. Si une approche est mauvaise : le dire et proposer autre chose.

## Rushes
- Rushes d'origine H.264, ~1080×1920, 30 fps. Voix off de Harry **enregistrée à part**, invités en son direct (micro-cravate).
- ⚠️ **La voix off contient des prises répétées** (Harry redit une phrase s'il a mal articulé ou si l'intonation ne lui plaît pas).
  Il faut : transcrire (timestamps par mot) → regrouper les prises d'une même phrase (similarité de texte) → choisir.
  Règle par défaut : **la dernière prise complète sans accroc** (pas de « euh », pas de mot écorché, confiance Whisper correcte, phrase non coupée).
  Ne pas prétendre juger l'intonation : signaler les choix incertains et lister les prises alternatives avec leurs timecodes pour que Harry tranche.
  Noter dans `DA.md` les préférences de Harry au fil des corrections.
- Les rushes ne vont **jamais** dans git (`.gitignore`). Les mettre dans `rushes/<episode>/`.

## Outils
- `python tools/transcribe.py <video_ou_audio> medium` → transcription FR avec timestamps par mot (`.words.json`)
- `python tools/analyze.py <video> <dossier_sortie>` → coupes, planche contact, `shots.json`
- `bash tools/batch_analyze.sh <dossier_videos> <dossier_sortie>` (Git Bash sous Windows)
- `npm run studio` → Remotion Studio ; `npm run render -- <Composition> out/x.mp4`
