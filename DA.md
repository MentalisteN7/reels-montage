# Direction Artistique — Reels

> Statuts : 🟡 observé par Claude (à valider) · ✅ validé · ✏️ corrigé
> Référence analysée : « Mac Ankara » — Episode 2, *Meilleur Kebab de Toulouse* (57 s)
> Planches : `docs/ref/sheet0-3.jpg` (1 image par plan, numérotés 0→47), `docs/ref/hisheet.jpg`

## 1. Format technique
- 🟡 1080×1920 (9:16), 29.97 fps, H.264 ~20 Mb/s, AAC 48 kHz stéréo
- ✏️ Durée cible : **60 s – 90 s** (réf. Mac Ankara : 57 s)
- 🟡 Tourné au smartphone, à la main (pas de stabilisateur visible)
- ✅ Rushes à 60/120/240 fps (le téléphone change seul de cadence) : **toujours traités à vitesse réelle, conformés en 30 fps. Pas de ralenti.**

## 2. Concept / série
- ✅ Page Instagram/TikTok **@guestlunch** : je (Harry, « l'influenceur en carton ») mange avec des amis.
  **Je décris le resto, ce sont les invités qui notent.**
- ✅ Notes sur **cartons** façon *Un dîner presque parfait* (feuille blanche, note au feutre)
- ✅ « Meilleur Kebab de Toulouse » = nouvelle série *dans* Guest Lunch (épisodes numérotés, classement cumulé).
  La réf. analysée est un épisode spécial de cette série.
- 🟡 Ton : humour, surnoms pour chaque invité (« Goose le bulldog », « Erwan le rugbyman », « Ulrich le runner fou »)

## 3. Structure (timecodes de la réf.)
| Bloc | TC | Contenu | Plans |
|---|---|---|---|
| Hook | 0:00–0:03 | ✅ **5 plans dans les 3 premières secondes**, belles images qui donnent envie (voir §4bis) | ~0,5 s/plan |
| Carton titre | 0:01.6–0:02.8 | « Episode N » + « Meilleur Kebab de Toulouse » | ~1,2 s |
| Dégustation | 0:02.8–0:12 | Bouchées, gros plans food, réactions | 0,5–1 s/plan |
| Présentation lieu | 0:12–0:21 | Façade, carte Google Maps en overlay, intérieur, menu/prix | 1–2 s/plan |
| Avis invités | 0:21–0:44 | Face cam devant la façade (micro-cravate à la main) + B-roll de leur assiette/bouchée | plans longs 1,5–7 s |
| Carton résultat | 0:44–0:45 | Note du lieu + classement cumulé | ~1 s |
| Outro | 0:45–0:57 | Retour sur moi qui mange (✏️ dernier plan = premier plan : hasard, pas une règle) | |

## 4. Rythme
- 🟡 48 plans / 57 s → **~1,2 s par plan en moyenne**
- 🟡 (13/11/2026, `docs/stats/ANALYSE_TYPES_RYTHME.md`) Sur 16 Reels : plus c'est découpé, plus ça marche (Spearman −0,51). Top 3 du compte à **1,2–1,3 s/plan** ; ≥ 40k vues : médiane 1,39 s/plan, < 40k : 1,71. Cible proposée **1,0–1,3 s/plan**, ≥ 4 plans dans les 3 premières secondes
- 🟡 Hook ultra rapide (0,43 s/plan), parties « avis » beaucoup plus posées
- ✅ Coupes franches uniquement — pas de transitions
- ✅ Pas de zoom dans la réf. Autorisé mais **très très peu** (ponctuel, pour souligner une réaction ou un détail)

## 4bis. Pourquoi le hook marche (plans 0→3 de la réf.)
- 🟡 **Un visage d'abord** (plan 0) : Harry regard caméra, yeux grands ouverts, kebab tenu près du visage → connexion + promesse
- 🟡 **Matière / texture** (plan 1) : main qui ouvre le pain, viande et sauce débordantes, très serré → « food porn »
- 🟡 **Vue d'ensemble / abondance** (plan 2) : plongée verticale sur toute la table → on comprend la quantité et le contexte
- 🟡 **Action** (plan 3) : grosse bouchée en très gros plan → mouvement + envie
- 🟡 Règles qui en découlent : varier l'échelle à chaque plan (visage → macro → plongée → bouchée), toujours **une main ou une bouche en action**, nourriture qui remplit le cadre, couleurs chaudes (frites, sauce, fromage)
- 🟡 La voix off commence dès la 1re frame avec la promesse : « Je cherche le meilleur kebab de Toulouse… »

## 5. Cartons (titre & résultat)
- 🟡 Fond : texture **papier blanc froissé** plein écran
- ✅ **Série Kebab : garder cette DA et l'améliorer. Autres séries : innover (nouvelle DA à proposer).**
- ✅ À recréer moi-même (texture papier, typos, détourage)
- ✏️ (v4, d'après la réf. Kebab image par image) **Animation du carton titre** : ~36 images (1,2 s). Papier : la texture reste **12 images, puis son reflet miroir 12 images**, et ainsi de suite (pas de tremblement). Plat détouré : apparaît à l'image 1 avec un **zoom/dézoom** (petit → trop gros → taille finale en ~6 images), puis **rotation lente** sur tout le carton (Harry : « de -45° à 45° » ; mesuré dans la réf. ≈ -4,5° → +4,5° — à confirmer). Textes rouges fixes, sans animation. **Son « pop »** à l'apparition du plat (pas de whoosh). ✏️ (v7) **Utiliser le pop d'Harry** : `D:\Harrison\Influencer\sound_effects\pop.mp4` (copié en `public/sfx/pop_harry.wav`), posé au début du carton / de la carte Maps, niveau d'origine
- ✏️ **Carton titre de présentation = la DA Kebab pour tous les épisodes** (Marcello v2 → v3) : papier froissé **qui bouge** (stop-motion, la feuille change de pose toutes les 3 images), photo du plat **détourée en sticker** (liseré blanc) en haut, textes **rouges** en bas (petite ligne fine + nom du lieu en slab gras). Texture papier fournie par Harry : `public/img/paper.jpg`
- ✅ Hors série Kebab, carton titre **posé sur le mot de la voix off qui nomme le lieu** (ex. « On se retrouve chez *Marcello* ») → pas besoin de voix off dédiée
- ✅ Carton résultat sans voix off : les notes des invités apparaissent une à une (SFX) puis la moyenne — **validé (« TOP ! », Marcello v1)**
- 🟡 Titre : photo de l'assiette **détourée façon sticker** (liseré blanc) en haut + texte centré en bas
  - « Episode 2 » : rouge, sans-serif fin
  - « Meilleur Kebab de Toulouse » : rouge (~#D0021B), **serif slab gras**, 2 lignes
  - Animation : l'assiette semble se révéler de gauche à droite (wipe) — *incertain*
- 🟡 Résultat : même papier, **police script/manuscrite rouge** : « Mac Ankara 8 / 10 », puis « 1er : … 8/10 / 2ème : Délices d'Orient 6/10 »

## 6. Overlays
- ✅ Carte **Google Maps** incrustée sur un plan de rue — **à garder**
  - ✏️ Format = **carte compacte : nom du lieu + ligne de note** (« 4,4 ★★★★★ (398) »), fond blanc, comme dans la réf. Kebab (« Le Regal d'Orient 4,5 ★ (2 566) »). Pas la photo de la fiche.
  - ✏️ **Petite** : ~55 % de la largeur (600 px sur 1080), en haut (~15 %), comme la réf. Kebab — la v2 à 880 px était trop grosse
  - ✅ Ajouter des **bruitages** d'apparition (pop-up, etc.) ; ✅ animation d'apparition « pop » (ressort) validée
  - ✅ C'est moi (Claude) qui vais chercher la capture
- ✅ **Titres « surnoms »** en haut de l'écran (~13 % de la hauteur), texte blanc sur 2 lignes, ombre douce, pas de fond
  - ✏️ (v4) **Sobre, rien d'extravagant** : police type TikTok « Classique » semi-grasse, blanc, ombre légère
  - ✏️ (v5) **Contour noir** autour des lettres (Harry « surligne en noir les bordures ») — mesuré sur le Kebab publié : trait fin ≈ 4 px en 1080p, police grasse (~700), ~76 px
  - ✏️ (v5) **Jamais deux fois la même entrée ni la même sortie dans une vidéo** (v4 : Guigui avait la même entrée que Harry). Harry utilise les animations texte de **CapCut** (simples) : glissé, montée, machine à écrire, balayage, zoom / sortie glissée, vers le haut, flou, vers le bas, rétrécit
  - ✏️ **Chaque surnom a une entrée/sortie différente** (réf. Kebab : glissé depuis la droite en italique + flou → sortie glissée à gauche ; montée en fondu → sortie vers le haut en fondu) — ~8 images d'entrée, ~7 de sortie, ~2,7 s à l'écran
  - ✏️ **Démarre dès que la personne est annoncée** (mot de la VO « … avec *Guigui* »), pas au début de son interview
  - ✅ Harry dit souvent les surnoms en voix off ; à décider **au cas par cas** (Marcello : oubliés en VO)
  - Fiche prénoms / surnoms / visages : `docs/invites/`
  - Harry : « L'influenceur / en carton » sur **Harry à l'image** (il mange face cam) quand il se présente
  - Invités : « Le bouledogue / & / Sa sœur », « Le Rugbyman / & / L'expert » au moment où on présente l'invité
  - Animation : entrée rapide (glissé depuis la droite avec flou de mouvement, ~4 images) ou fondu + flou ; ~2,5-3 s à l'écran
- ✅ **Harry à l'image** : quand la VO dit « moi c'est Harry », montrer **Harry** (selfie / face cam), jamais un invité. Harry filme : ses selfies sont reconnaissables (rush face caméra frontale).
- ✅ Sous-titres : **oui** — voir §6bis

## 6bis. Sous-titres
- ✏️ (v4) **Aucune animation** sur les sous-titres (pas de zoom/dézoom) : juste l'affichage, mots clés en jaune
- ✏️ Police : **TikTok Sans** (la police « Classique » de TikTok, libre, Google Fonts), graisse ~700, **blanc avec fin contour noir** + légère ombre
- ✏️ (v5) **Mot(s) clé(s) en jaune exact #F0FF00** (RGB 240,255,0, jaune-vert citron, mesuré au pixel sur le Kebab publié ; la v4 en #FFF200 tirait vers l'orange), **un peu plus gros** que les petits mots (« **Palais** de **justice** », « **L'influenceur** en **carton** ») — 1 ou 2 mots par apparition
- ✏️ **4 mots max, UNE seule ligne par apparition** (jamais 2 lignes)
- ✏️ **Découpe cohérente avec le sens de la phrase**, pas seulement le rythme : « Les meilleures pizzas » / « de Toulouse », jamais « Les meilleures pizzas de » / « Toulouse ». Ne jamais finir une apparition sur un petit mot (de, les, à, et, une…).
- ✅ Placement **hors des zones d'UI TikTok/Insta** : centré, vers ~62 % de la hauteur, largeur max ~75 %
- ✅ **Emojis uniquement pendant les 5 premières secondes**, ✏️ **en fin de phrase, sur une ligne à part** (sous le texte), pas sur la même ligne
- ✅ Rien n'est figé : style amené à évoluer, garder ça paramétrable
- ✅ Paroles des invités : **corriger les fautes** dans les sous-titres (ne pas transcrire mot à mot les erreurs)

## 7. Image / étalonnage
- ✅ Look naturel, pas de LUT marquée, ciel couvert, couleurs telles que sorties du téléphone
- 🟡 Gros plans food très serrés, souvent plongée ; visages proches en grand-angle

## 8. Son
- ✅ **Pas de musique**
- ✅ **Voix off de Harry enregistrée à part**, posée sur les rushes ; puis passages où les invités parlent face cam (son direct, micro-cravate)
- ✏️ (v5) **Pluie / bruit de fond** (Marcello, passage de Meg) : c'était la pluie, pas un défaut de traitement. Dans Premiere, Harry applique le préréglage **Essential Sound « Dialogue »** (Restauration + Clarté) sur toutes les paroles → piste pour la suite : réduction de bruit douce sur les interviews tournées dehors, à valider à l'oreille
- ✏️ (v4) **Qualité du son des interviews** : garder la qualité d'origine, juste **monter le volume sans saturer** (pas de traitement « amélioration »). Les micro-cravates sont déjà très forts au tournage (crêtes à 0 dB) → mixage depuis les fichiers originaux, gain fixe, limiteur à -1 dB
- ✏️ Pas de whoosh sur le carton titre (bruit bizarre) → pop
- ✅ Audio continu, **aucun blanc — priorité n°1 du dynamisme**
  - ✏️ **Fin de phrase coupée 1-2 images avant la fin du mot** : on comprend le mot mais on raccourcit la dernière syllabe (« restau-rant » : la syllabe dure 3-4 images, en garder 2)
  - ✏️ **Aucun silence entre les phrases de VO** (on enchaîne directement)
  - ✏️ Invités : **couper les « euh », hésitations et silences** dans les interviews
  - ✏️ Pour cacher ces coupes : **plan de plat / B-roll par-dessus** (on n'entend que la voix) — déjà bien fait, à systématiser
  - ✏️ (v3) **Rogner encore quelques images à gauche et à droite de chaque coupe** pour accélérer la parole : attaque prise au ras, fin raccourcie de ~2 images. Limite constatée : à ~2,7 images on mange les mots courts de fin (« dix », « neuf ») → **les notes des invités ne sont presque pas rognées**
- ✅ Bruitages (SFX) sur les overlays (pop-up Google Maps…) — banques libres de droits (Mixkit…), Harry n'a pas de banque perso
- ✅ **L'ordre des phrases de la voix off est intouchable.** On choisit la meilleure prise de chaque phrase, on peut resserrer les silences, jamais réordonner.
- ✅ Son direct des rushes (réactions à table) : en général non (mauvais son) ; seulement s'il est propre et s'intègre bien.
- ✅ Les blagues de la voix off restent telles quelles (ex. « les meilleures pizzas de Toulouse se trouvent à Toulouse », « ami d'enfance depuis un an »).
- ✅ Harry ne teste que des restos à Toulouse.
- Transcription : `tools/transcribe.py` (faster-whisper medium, FR, timestamps par mot) — voir `docs/ref/macankara.words.json`

### Script de la réf. (pattern de narration)
1. Promesse : « Je cherche le meilleur kebab de Toulouse et pour ce 2e épisode je teste le meilleur selon vous. »
2. Signature : « Moi c'est Harry, l'influenceur en carton, et je m'engage à… »
3. Lieu + localisation : « Rendez-vous chez Mac Ankara à 2 min du Capitole. »
4. Déco / prix avec une vanne
5. Invité n°1 présenté avec un surnom → il décrit son plat → montre son carton → justifie la note
6. Invité n°2 idem
7. Moyenne + classement : « On termine avec une moyenne de 8/10, il prend la tête de la compétition. »
8. Sortie : « À bientôt pour le prochain kebab. »

## 9. À ne jamais faire
- (à compléter)

## 10. Patterns du compte @guestlunch (analyse en cours : 2 Reels / 16)
Réfs : Mac Ankara (57 s, 48 plans, ~1,2 s/plan) · La Côte de Bœuf (63 s, 41 plans, ~1,5 s/plan, `docs/ref/cote/`)
- 🟡 **Phrase d'accroche qui interpelle le spectateur au « tu »** et cible un besoin : « Si t'es fauché mais que t'adores la bonne viande, j'ai trouvé le resto idéal pour toi. »
- 🟡 **Signature fixe à ~3-5 s** : « Moi c'est Harry, l'influenceur en carton, et je… »
- ✅ **« PAS CHER » + viande = ce qui a le mieux marché** (confirmé par Harry)
- 🟡 Hook visuel Côte de Bœuf : plongée table pleine → **flammes du grill** (mouvement + chaleur) → dessert à la cuillère (texture) → invité qui mange. Toujours 5 plans / 3 s
- 🟡 Présentation lieu : extérieur (enseigne, rue), entrée, déco intérieure, ardoise/menu + **prix toujours dits**
- 🟡 Invités récurrents avec surnom (Goose le bulldog, Erwan le rugbyman…) — interviewés **devant la façade**, micro-cravate, carton de note
- ✏️ Pendant qu'un invité décrit son plat → **B-roll du BON plat qu'il nomme** (synchro parole/image). Vérifier chaque insert (planche plan + sous-titre) : pas de pizza mortadelle quand on parle de la tartufata
- ✏️ **Début d'interview** : « Alors moi j'ai pris un… » → on voit l'invité (~0,6 s, titre surnom) puis **le plat apparaît sur le mot du plat**, ensuite on **jongle** : plat → description (gros plan) → invité qui parle → invité qui mange → …
- 🟡 (v6, mesuré sur les 84 projets Premiere d'Harry) **Le visage de l'invité domine** : le B-roll ne couvre que ~23 % du temps d'interview (2–3 inserts de ~1,2–1,5 s par invité, sur les plats nommés) et **~76 % des coupes internes restent en jump cut visible** — on ne cache pas chaque coupe. Pas de prise face cam > ~4 s sans insert
- 🟡 (v6) **Accroche** : glisser un **teaser du carton de note** (invité qui brandit son 10) dans les 5 premières secondes (Jeez, Le Roll)
- 🟡 (v6) **Présentation d'Harry** : jump cuts du même rush de bouchée (sourire → bouchée → mâche → satisfait), ~0,8 s chacun (Les Thermes)
- Référence complète : `docs/montage_harry/COMMENT_HARRY_MONTE.md`
- 🟡 On **garde les moments drôles** (carton « 999 », « Merci pour cette blague »)
- 🟡 Fin avec **appel à l'engagement** (« si vous aimez ce personnage je le réinviterai », débat en commentaires)
- 🟡 La Côte de Bœuf : pas de carton titre, pas de sous-titres (cartons = nouveauté série Kebab)

## 11. Ce qui sépare les Reels qui marchent des autres (16 Reels analysés, 8 avec stats)
> n petit → tendances, pas des lois. Données : `docs/stats/`, analyses : `docs/analyses/`

| Reel | Vues | Save % | Plan moyen | Plans < 3 s | 1re phrase |
|---|---|---|---|---|---|
| Le Jeez | 226 k | 2,14 | 1,30 s | 4 | « Les burgers **les moins chers** de Toulouse, **tu devineras jamais** combien on a payé… » |
| Côte de Bœuf | 76 k | 1,52 | 1,54 s | 5 | « Si **t'es fauché** mais que t'adores la bonne viande… » |
| Les Thermes | 45 k | 1,57 | 1,75 s | 3 | « Les célèbres **nouilles de 2 mètres**… reviennent enfin » |
| Le Roll | 39 k | 2,30 | 1,39 s | 4 | « Des brioches gourmandes… à tester de toute urgence » |
| Maison du Curry | 25 k | 0,36 | **2,78 s** | 2 | « POV, tu juges les restos avec les copains… peut-être le meilleur indien » |
| Joshore Road | 17 k | 2,18 | 1,41 s | 3 | « Ce resto m'a fait redécouvrir la gastronomie indienne… » |
| Le May 2 | 15 k | 0,64 | 1,57 s | 3 | « Je vous ai négocié un bon plan… » |
| Bouillon Capitole | 12 k | 0,11 | **2,05 s** | 2 | « Quelle note pour ce plat ! » |

### Règles tirées
1. 🟡 **De la nourriture dans le cadre dès la 1re frame.** Bouchée, table pleine, plat qui déborde.
   Contre-exemples : Bouillon (2,7 s de place du Capitole avant le 1er plat → le pire score), Bep Chay (invité + façade d'abord).
2. 🟡 **1re phrase = prix bas / bon plan OU élément spectaculaire, avec une promesse ou une énigme** (« tu devineras jamais combien »).
   Une phrase sortie d'une interview (« Quelle note pour ce plat ») ne fonctionne pas comme hook.
3. 🟡 **Le top coupe plus vite** : ~1,3-1,5 s/plan, ≥ 4 plans dans les 3 premières secondes. Le moins bon est à 2 s/plan.
4. 🟡 **Abondance** : plongée sur une table remplie (Jeez, Côte de Bœuf, Joshore, Le May) = image de hook récurrente.
5. 🟡 **Le spectaculaire filmé en action** (nouilles de 2 m, flammes du grill) remplace le prix quand il n'y en a pas.
6. 🟡 Les Reels en dessous ont souvent un hook « description » (gastronomie, ambiance) sans prix ni promesse.
7. 🟡 Le Mood : ouvrir sur une **capture d'un média** (La Dépêche) = preuve sociale + prix (5 €) — piste à tester (pas de stats).

## 12. Vidéos « divers » (ni Guest Lunch ni test solo) — Aligofest, nov. 2026
- ✅ **Orthographe voulue : « toulousaign »** (toujours, dans « Fier d'être *toulousaign* »)
- ✏️ (10K v4) **Orthographe voulue : « copaign »** (« mon *copaign* », « tague le ou la copaign ») — même logique que « toulousaign »
- ✅ Carton titre (DA Kebab) pour présenter l'événement, même hors série
- ✅ Pas de surnom à l'écran pour les amis (Gouz, Marie) ; seulement Harry « L'influenceur en carton »
- ✅ Défi chiffré (« manger 5 assiettes ») → **compteur d'assiettes** à l'écran ; la VO est **interrompue par le son direct** des « Et d'une ! / Et de deux ! » face cam
- 🟡 Scores finaux en texte sur le dernier plan (pas de carton), **la vidéo finit sur la VO**, pas sur un bruitage
- 🟡 Son direct d'ambiance (foule, fanfare / peña baiona) sous la VO, très bas, quand il est propre
- ✅ Voix off : Harry répète une phrase quand il la rate → **toujours la dernière prise**
- ✏️ (v2) Compteur : **pas affiché en permanence** → il apparaît juste autour de chaque « Et de N » et disparaît peu après ; icônes = **l'assiette aligot-saucisse du carton titre** (pas des ronds)
- ✏️ (v2) **Ne jamais manger la fin d'un mot** en resserrant (« compèt », « attaqu », « direc », « a(vec) ») : la coupe se fait après la queue du mot, même si la vidéo s'allonge un peu
- ✏️ (v2) **Ce qu'on dit = ce qu'on voit** : chaque élément cité en VO (beer pong, cookies, peña…) doit apparaître à l'image sur son mot ; montrer l'**action** (foule portée pendant la peña) plutôt que juste les musiciens
- ✏️ (v2) Accroche : ouvrir sur le **plan le plus spectaculaire du lieu** (le cuisinier qui mélange l'aligot géant), assez long pour être lu (≥ 1,2 s) — un plan caché par le carton titre ne compte pas
- ✏️ (v2) Plans où Harry joue la comédie : prendre **à partir du moment où il joue**, jamais l'attente avant
- ✅ Harry aime les moments vrais où il galère (souffle à la 4e assiette) → les garder, en son direct
- ✏️ (v3) **Jamais deux plans du même rush à la suite** (coupe puis retour sur le même plan = bizarre, ex. présentation « Sinon moi c'est Harry ») → alterner avec un autre rush
- ✏️ (v3) Accroche : plans de **durée régulière** (~0,8 s chacun), pas un long puis des courts ; **Harry qui croque la saucisse dès l'accroche** (et dans sa présentation)
- ✏️ (v3) Musique sous droits (peña baiona…) : ne pas l'intégrer au montage → Harry l'ajoute dans l'app à la publication

### Halloween Mercure Compans (solo, nov. 2026) — corrections d'Harry (V7 validée le 18/11/2026)
- ✏️ **Vérifier l'orientation de chaque rush** avant de monter : certains sont filmés en paysage ou ont une métadonnée de rotation fausse (image couchée ou écrasée) → les redresser dans le proxy (`transpose`), jamais d'image couchée à l'écran
- ✏️ **Le surnom d'Harry s'adapte au déguisement / thème** : « *Le vampire en carton* » à Halloween (Harry réenregistre la phrase de présentation ; la nouvelle prise est dans le même dossier VO, ex. `Audio 1_1.wav`)
- ✏️ **Présentation d'Harry** : un plan où il **fait une grimace / joue la comédie**, puis un plan où il **mange un truc sympa**
- ✏️ Phrase générale sur le lieu (« ils ont métamorphosé l'hôtel… ») : **ne pas rester sur une seule séquence** → enchaîner vite les plats les plus marquants (ici des plats sanglants), même rythme que le reste
- ✏️ « C'était vraiment excellent » → montrer **Harry qui mime qu'il se régale**, idéalement jusqu'à son oui de la tête
- ✏️ Chaque plat cité doit être **le plat exact** (« 10 sushis » = le sushi, « patates douces » = Harry qui mange la patate douce)
- ✏️ Pour un jugement sur un ensemble (« les desserts étaient visuellement horribles ») → **une vue d'ensemble** (milieu du rush qui balaie le buffet), pas une assiette
- ✏️ (v5) **Jamais d'arrêt sur image** : un plan ne doit jamais dépasser la fin de son rush (build_edl refuse désormais, et la relecture lance `freezedetect`)
- ✏️ (v5) Un nouvel enregistrement de VO peut aussi contenir **plusieurs prises** (« Bref moi c'est… » ratée puis la bonne) → même règle, la dernière complète
- ✏️ (v5) **Écouter le son de chaque rush et en évaluer le potentiel**, même si Harry ne met jamais le son de ses vidéos : un son direct fort (poupée de l'escape game qui s'allume) peut passer sous la VO ou seul ~1 s
- ✏️ (v5) Plans où Harry joue la comédie : **couper avant qu'il sorte de son personnage** (fin de rush = il reprend une tête normale, ça se voit) → décaler l'entrée plus tôt plutôt que d'aller au bout du rush
- ✏️ (v5) Quand la VO parle des plats, **montrer au moins une fois Harry en train d'en manger un**
- ✏️ (v5) **Pas deux fois la même séquence** à quelques secondes d'écart (mains de l'escape game à 0:20 et 0:23) → prendre un autre rush

## Questions ouvertes
- Analyse du compte @guestlunch (bloquée : Instagram refuse l'accès automatisé)

## 13. Annonce « Soirée 10K » (nov. 2026) — choix SPÉCIFIQUES à cette vidéo (pas des règles globales)
- ✅ Vidéo d'annonce : but = que les gens retiennent **date, lieu, prix** et viennent (les vidéos « com » font ~5k vues, ce n'est pas un problème de montage)
- ✅ Pas de voix off séparée : Harry parle face cam (son direct). On garde la dernière prise, on retire les bavardages avec la personne qui filme
- ✅ **Musique épique** cette fois (exception au « pas de musique ») : libre de droits (Mixkit « I Won't Surrender »), forte sur l'intro et le récap, basse sous la parole
- ✏️ (v3) Page Insta @guestlunch recréée avec compteur 0 → 10 000 : **pas au début** → posée sur « pour fêter mes 10 000 abonnés », le compteur touche 10 000 sur le mot. **Pas de rushes/flash de Reels sur cette phrase**
- ✏️ (v3) **Respecter l'ordre de tournage des rushes** (Harry les enregistre dans l'ordre). 2 versions : A ouvre sur « soirée exceptionnelle », B sur « Moi c'est Harry, l'influenceur en carton »
- ✏️ (v3) **Trop de pops** → seulement sur les moments forts (date, tampon 10 €, récap) ; ding sur 10 000, bruit de papier sur le calendrier
- ✏️ (v3) Vérifier **qui est à l'image** sur chaque B-roll (Antho sur « boissons maison » → remplacé par Harry qui boit)
- ✏️ (v3) « Note ça dans ton agenda » → **animation de calendrier** (le 10 entouré au feutre)
- ✏️ (v3) Texte du récap dans les **zones sûres TikTok/Insta** (x 80–900, y 220–1400 sur 1080×1920)
- ✏️ (v7) Surveiller les **éléments parasites** qui entrent dans le cadre (vélo sur « officiellement ») → couvrir/décaler (compteur Insta lancé plus tôt)
- ✏️ (v4) **Jamais de rush qui « attend le signal »** : quand Harry marche vers la caméra, l'image commence quand il marche déjà (pas statique). S'il parle avant, on décale l'image tant qu'il est loin (lèvres illisibles), puis on resynchronise derrière un B-roll
- ✏️ (v4) Le plan où le téléphone se relève sur la place (« lieu exceptionnel ») : **non** → rester sur Harry qui parle
- ✅ (v4) Voix « clarifiée » : « le son est bien »
- ✏️ (v7) **Popups d'info : DA v1 (texte ROUGE slab, gros, penché, effet pop + bruit) mais fond BLANC au lieu du papier** (le papier seulement pour le carton final). Variante papier transparent « pas mal », retour d'Harry à venir. (v6 : le look sobre façon POV et l'entrée en fondu = mal compris, abandonnés)
- ✏️ (v7) **Quand une popup affiche l'info, on RETIRE le sous-titre qui la répète** (Jeudi 10 décembre, L'Annexe Saint-Georges, tapas/boissons, 10 €) — pas l'inverse → ✏️ (v8) **finalement sous-titres remis partout**, sauf « Jeudi 10 décembre » (1re séquence)
- ✏️ (v8) **Look retenu : papier transparent** pour les popups ; **la 1re popup (date) en fond blanc plein**
- ✏️ (v8) **Sous-titres : toujours une majuscule au début de chaque apparition** (règle générale, s'applique aux autres vidéos)
- ✏️ (v8) **Apparition d'un prix : bruit d'argent** (pièces, Mixkit « Clinking coins ») au lieu du pop → ✏️ (v9) trop « cash » : **son « Coin » de jeu vidéo, discret** (Mixkit « Winning a coin, video game » → `public/sfx/coin_2069.mp3`, vol 0,45)
- ✏️ (v10) **SON DE PRIX VALIDÉ ✅ : Pixabay « Cashier "ka-ching" sound effect » (u_byub5wd934, n°129698)** → `public/sfx/kaching.wav` (blanc de 0,19 s retiré pour tomber pile sur l'apparition du prix), vol 0,9. Harry le compare au « Money Chakin » de CapCut. Le « Coin » de jeu vidéo et les pièces réalistes = refusés. **À réutiliser à chaque apparition d'un prix.**
  ⚠️ Sur Pixabay, ne pas déduire le fichier d'un clic « play » dans une liste (mauvaises correspondances) : prendre l'URL de téléchargement de la page du son (`?filename=...-<n°>.mp3`)
- ✏️ (v6) Récap : police des 3 premières lignes « pas jolie » (Arial + Roboto Slab) → Playfair Display (à valider)
- ✏️ (v5) Antho = le gars à la casquette beige de la vidéo Annexe n°2 ; ne pas présenter des gens comme « en couple » sans savoir
- 🟡 (v3) Harry trouve qu'il n'articule pas assez → voix « clarifiée » (EQ de présence, débruitage léger, compression) — avant/après à valider
- ✏️ **Pas de carte Google Maps avec la note pour l'Annexe Saint-Georges** (note pas assez bonne) → simple étiquette du lieu. Décision propre à cette vidéo : la carte Maps reste la règle ailleurs (§6)
- 🟡 Étiquettes papier rouges pour chaque info (date, lieu, tapas, tampon « 10 € », jeu concours) + carton récap plein écran à la fin (à capturer) — « top » (v2) ; ✏️ « Places limitées » sans « sans résa »
