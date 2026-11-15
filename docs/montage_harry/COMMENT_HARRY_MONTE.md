# Comment Harry monte : ce que ses projets Premiere révèlent (15/11/2026)

> **Sources :**
> - les **84 projets Premiere** de `D:\Harrison\Influencer\Guest-Lunch\` (marcello exclu), décodés par `tools/prproj.py` ;
> - les mesures audio de **3 533 coupes** (`tools/cut_margins.py`) ;
> - les planches plan par plan de 6 épisodes (`etudes/*.jpg`, `tools/planche_annotee.py`).
>
> Ce sont des **mesures sur son vrai montage**, pas des impressions. Les chiffres bruts sont dans `stats.csv`, `marges.csv` et `choix_rushes.csv`.
>
> **Limite :** les sous-titres, surnoms, musique et bruitages sont ajoutés **dans CapCut**, donc absents de Premiere. Pour cette couche, la seule référence reste les Reels publiés.

## 1. Le workflow d'Harry
1. Tous les rushes dans `02 RUSHES/`, la voix off enregistrée **dans Premiere** (`Audio 2_x.wav`).
2. Séquence **`01_rushes_sorted`** : tous les rushes posés bout à bout, **sans coupe**. C'est juste un rangement (54 rushes / 7,9 min pour Jeez).
3. Séquence finale (60–90 s) :
   - **V1 :** plans principaux ;
   - **V2 :** inserts B-roll posés *par-dessus* le son direct des interviews, plus les images (carte Maps, papier) ;
   - **V3 :** plat détouré du carton titre ;
   - **A1 :** son direct ;
   - **A2 :** voix off.
4. Essential Sound : préréglage **« Dialogue »** sur toutes les paroles (rubriques Restauration et Clarté).
5. Export, puis **CapCut** pour les sous-titres, surnoms, musique et bruitages.

## 2. Rythme (médianes sur 84 épisodes)

| Mesure | Valeur |
|---|---|
| Durée | 75 s (Guest Lunch 65–90 s ; test solo 40–60 s) |
| Durée moyenne d'un plan | **1,25 s** (médiane d'un plan 1,10 s) |
| Accroche (5 premières s) | **5 à 7 plans de 0,7–1,0 s** dans les épisodes récents. L'ancien format (Maison du Curry, Le Mood) n'en a qu'1 ou 2, de 2,5–5 s |
| Rushes utilisés | ~22 par vidéo, soit 60–75 % des rushes tournés |
| Rushes réutilisés | **~1/3** des rushes servent 2 fois ou plus (le plan « héros » du plat revient dans l'accroche puis dans l'interview) |
| Ordre | Pas chronologique : ~35 % des enchaînements reviennent en arrière dans l'ordre de tournage. **L'histoire prime** |

## 3. La coupe de la parole : le cœur du dynamisme
Mesuré sur l'énergie audio, à chaque point d'entrée et de sortie :

| | Silence gardé avant le 1er mot | Silence gardé après le dernier mot | Pause perçue au raccord |
|---|---|---|---|
| **Voix off** (2 015 morceaux) | 10 ms | **0 ms** | **20 ms** (90 % < 80 ms) |
| **Son direct** (1 518 morceaux) | 30 ms | 0 ms | 40 ms (90 % < 190 ms) |

- La voix off est découpée en **morceaux de ~1 s** (médiane 0,96 s ; 26 morceaux par vidéo). Entre deux morceaux, Harry retire en médiane **0,41 s** (souffles, « euh », hésitations).
- **61 % des sorties VO tombent dans la queue du dernier mot.** Harry coupe pile au bord du mot, voire un peu dedans : aucune respiration n'est gardée.
- Marcello v4/v5 est déjà à ce niveau (pause médiane 0 ms en VO, 5 ms en interview). Les réglages `TRIM`/`PAD_IN` sont bons, ne pas les desserrer.

## 4. Image et parole : la règle du mot
Vu plan par plan sur Jeez, Le Roll, Les Thermes et Kebab :
- **Chaque morceau de VO ≈ un plan.** ~43 % des coupes vidéo tombent exactement sur une coupe VO.
- **L'image illustre le mot dit, littéralement :**

  | VO | Image |
  |---|---|
  | « frites maison » | la friteuse |
  | « hot dogs » | quelqu'un qui mord un hot dog |
  | « Compense, en face du Botaniste » | la façade |
  | « la déco » | 2–3 plans d'intérieur |
  | « menu à seulement… 7,50 € pour les étudiants » | l'affiche du menu |
  | « tous les produits sont de la région » | la carte de la région au mur |
  | « moi c'est Harry » | selfie d'Harry |
  | « on démarre avec Antoine » | l'invité en train de mordre / arriver |

- **Présentation d'Harry** (« Salut, moi c'est Harry, l'influenceur en carton ») : selfie large, puis **jump cuts du même rush** d'Harry qui mange (Les Thermes : 4 plans de ~1 s du même rush).

## 5. Structure type Guest Lunch
1. **Accroche, 0–5 s :** le plat le plus spectaculaire ou une action (nouilles de 2 m tirées, burger qu'on croque), en 5–7 plans courts. La phrase est un **titre-promesse** (« Les burgers les moins chers de Toulouse, tu devineras jamais combien on a payé »).
   - Souvent un **carton de note en teaser** dès l'accroche : invité qui brandit son « 10 » (Jeez plan 8, Le Roll plan 3).
2. **Présentation d'Harry, ~6–12 s :** selfie et bouchées, avec le titre surnom.
3. **Lieu, ~12–20 s :** façade, enseigne, quartier, déco, menu et prix. Carte Maps avec un pop.
4. **Interviews :** la 1re commence vers **20 s**. En général **3 blocs** (1 à 4 selon le nombre d'invités) d'environ **15 s** chacun.
   - L'invité est **annoncé en VO** sur un plan où il mange ou arrive ;
   - « J'ai pris un… » puis le plat en B-roll sur V2, posé sur le son direct ;
   - il décrit, avec des inserts du bon plat et de sa bouchée ;
   - il **montre son carton** et justifie la note.
   - **~76 % des coupes internes d'une interview restent visibles en jump cut** (856 sur 1 125) : Harry ne cache pas chaque coupe par du B-roll.
  - Le B-roll couvre **~23 %** du temps d'interview, par inserts de **~1,5 s**. Les prises face cam durent 1,5 à 4 s, parfois plus si c'est drôle.
5. **Fin :** 0 à 3 s après la dernière note. On garde un moment drôle ou complice (« 9, 9, 9, 9 », « Attendez, attendez ! »), ou la **réponse à la promesse de l'accroche** (Jeez : le tableau des prix « à partir de 6,90 € »).

## 6. Choix des rushes
- Un rush dure ~9 s ; Harry en garde **~14 %** (~1,2 s), le plus souvent **vers 40 % du rush** (médiane 3 s après le début). Il prend rarement la première demi-seconde (12 % des cas), où la caméra bouge encore.
- **Le mouvement de caméra et la netteté ne départagent pas ses choix** : rang médian 0,47 et 0,58, soit le hasard. Il choisit le **moment de contenu** :
  - la bouchée ;
  - la sauce qui coule ;
  - le plat qui arrive ;
  - la réaction ;
  - le geste.

  → Pour l'automatiser, il faut repérer ces **moments** (fourchette qui monte, bouche, plat qui entre dans le cadre). La stabilité de l'image n'y suffit pas.

## 7. Tests solo (Matsuya 508k, Grands Buffets 275k…)
- **40–60 s, 100 % voix off**, plans de 0,6–1,5 s du début à la fin, aucune interview.
- **Matsuya, plan par plan** (`etudes/matsuya.jpg`) :
  1. **0–1 s :** Harry croque, gros plan, expression forte. La 1re image est **une bouchée**, pas un plan d'ambiance.
  2. **0–4 s :** la promesse en une phrase : « Le meilleur sushi à volonté de Toulouse vient d'ouvrir et c'est vraiment pas cher ».
  3. **4–8 s :** où (« à deux pas de Jean Jaurès ») puis **le prix** (« pour seulement 20 € »).
  4. **8–14 s :** preuve de qualité (chefs, plats élaborés, salle), puis la conclusion d'Harry sur **3 visages de plaisir** (yeux fermés, bouchée, mmh).
  5. **« Salut, moi c'est Harry » n'arrive qu'à 14,5 s**, après la promesse et le prix. En solo, la présentation passe **après** l'accroche.
  6. **La nouveauté ou l'expérience :** robot serveur (« Bienvenue dans le futur »), commande sur tablette (4 plans courts du doigt sur l'écran).
  7. **Classement « mon top 3 » :** pour chaque plat, plat, puis Harry qui le mange, puis sa réaction. On finit sur le dernier plat, **sans conclusion**.
- **Différences avec Guest Lunch :**
  - plus court ;
  - la promesse et le prix d'abord, la présentation ensuite ;
  - le visage d'Harry remplace les interviews : **réaction = preuve**.

## 8. Ce que j'applique désormais au montage automatique
1. Accroche : 5–7 plans ≤ 1 s, le plus spectaculaire d'abord, avec un carton de note en teaser si l'invité en brandit un.
2. Un plan par morceau de VO ; l'image illustre **le mot exact**.
3. Présentation d'Harry : jump cuts du même rush de bouchée.
4. Interviews d'environ 15 s chacune, inserts B-roll de ~1,5 s sur ~25 % du temps.
5. Rushes : entrer vers 40 % du rush, garder ~1 s, réutiliser le plan héros.
6. Fin : moment drôle ou réponse à la promesse, sans traîner (≤ 3 s après la dernière note).
