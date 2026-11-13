# Installation sur Windows

Dans **PowerShell** (clic droit sur Démarrer → Terminal) :

## 1. Les outils
```powershell
winget install OpenJS.NodeJS.LTS Python.Python.3.12 Gyan.FFmpeg Git.Git
```
Ferme et rouvre le terminal, puis vérifie : `node -v`, `python --version`, `ffmpeg -version`, `git --version`.

## 2. Claude Code
- Soit l'**application Claude de bureau** (https://claude.ai/download) → onglet Claude Code
- Soit en ligne de commande : `irm https://claude.ai/install.ps1 | iex`, puis `claude` dans le dossier du projet

## 3. Le projet
```powershell
cd $HOME\Documents
git clone https://github.com/MentalisteN7/reels-montage
cd reels-montage
npm install
python -m pip install -r requirements.txt
```

## 4. Test
```powershell
npm run studio
```
Le Remotion Studio s'ouvre dans le navigateur (composition « Test »).

## 5. Rushes
Copie les rushes dans `reels-montage\rushes\<nom_episode>\` (ignoré par git), puis lance Claude Code dans le dossier `reels-montage`.
