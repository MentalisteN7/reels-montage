# @guestlunch : analyse par type de vidéo et rythme (13/11/2026)

> **Sources :**
> - Légendes et vues des 96 Reels lus sur Instagram (compte connecté, onglet Reels).
> - Rythme (plans/s) mesuré sur 16 Reels : 14 déjà découpés dans `docs/analyses/` et 2 mesurés directement sur Instagram (Matsuya, Grands Buffets).
>
> **Limite :** la mesure en direct sur Instagram ne fonctionne que si la fenêtre Chrome est au premier plan, d'où seulement 2 Reels mesurés là-bas.

## 1. Classement des 96 Reels par type

**⚠️ À valider par Harry.** Le classement vient des légendes et des transcriptions.
- « ? » = je ne suis pas sûr si la vidéo est solo ou avec invités.
- La liste complète est dans [types_videos.csv](types_videos.csv) : corrige la colonne `type` et je relance les chiffres.

| Type | Nb | Médiane vues | Moyenne vues | Reels ≥ 50k | Médiane 2026 |
|---|---|---|---|---|---|
| Guest Lunch (avec invités, notes) | 55 (11 ?) | 16k | 31k | 6 | 22k |
| Série Kebab (Guest Lunch) | 2 | 66k | 66k | 2 | 66k |
| Test solo | 27 (14 ?) | 25k | 60k | 7 | 22k |
| Divers (Bayonne, voyages, compil, présentation) | 9 | 36k | 61k | 4 | 70k |
| Com 10k / événement / concours | 3 | 6k | 7k | 0 | 5k |

**Lecture :**
- **Guest Lunch :**
  - C'est le format fondateur : régulier, mais avec un plafond plus bas.
  - Le format a pris de l'ampleur : médiane 9k sur déc. 2024 – août 2025, puis 27k de sept. 2025 à juin 2026.
  - Ses gros cartons sont des « bons plans » au titre-promesse fort :
    - Resto U 76k (« Le meilleur Crous de France ») ;
    - Spotes 129k (« le meilleur sandwich ») ;
    - Nachos 213k ;
    - Le Jeez 233k (« les burgers les moins chers »).
- **Test solo :**
  - Les deux plus gros succès du compte sont des tests solo : Matsuya (508k) et Grands Buffets (275k).
  - La médiane est proche de celle de Guest Lunch : le solo ne marche pas mieux en soi.
  - Ce qui fait le carton, c'est le **sujet** : à volonté, prix choc, « le plus grand d'Europe ».
- **Série Kebab :** 2 épisodes sur 2 au-dessus de 50k. C'est le format « série + classement » qui donne envie de revenir.
- **Divers :**
  - Peu de vidéos, mais une forte moyenne, tirée par « Tu viens d'arriver à Toulouse » (210k) et les compilations (« 3 restos avant de quitter Toulouse », 84k).
  - Les formats **liste / compilation** marchent bien.
- **Com 10k / événement :** environ 6k vues, normal pour de l'annonce (peu de non-abonnés). Ce n'est pas un problème de montage.

**Point commun des gros cartons, tous types confondus :** un titre-promesse chiffré ou superlatif dès la 1re seconde, par exemple :
- « le moins cher » ;
- « à volonté » ;
- « 5€ » ;
- « le plus grand » ;
- « le meilleur … de Toulouse ».

## 2. Rythme de montage

| Reel | Vues | s/plan (moy.) | s/plan (médiane) | Plans < 3 s |
|---|---|---|---|---|
| Matsuya (IG) | 508k | **1,17** | – | – |
| Grands Buffets solo (IG) | 275k | **1,22** | – | – |
| Le Jeez | 233k | **1,30** | 0,92 | 4 |
| Kebab Régal d'Orient | 80k | 1,42 | 1,28 | 6 |
| La Côte de Bœuf | 77k | 1,54 | 1,37 | 5 |
| Les Thermes | 47k | 1,75 | 1,30 | 3 |
| Le Roll | 40k | 1,39 | 1,12 | 4 |
| Bêp Chay | 29k | 1,85 | 1,33 | 1 |
| Les 2 potes | 28k | 1,71 | 1,47 | 4 |
| Maison du Curry | 25k | 2,78 | 2,20 | 2 |
| Joshore | 19k | 1,41 | 1,23 | 3 |
| Gigiland | 17k | 1,87 | 1,48 | 3 |
| Le May 2 | 16k | 1,57 | 1,33 | 3 |
| Ligot | 14k | 1,38 | 0,97 | 6 |
| Le Bouillon | 12k | 2,05 | 1,94 | 2 |
| Le Mood | 8k | 1,48 | 1,20 | 2 |

**Ce que ça montre :**
- **Plus c'est découpé, plus ça marche :**
  - Corrélation de Spearman entre vues et durée moyenne de plan : **-0,51** sur 16 Reels.
  - Médiane de **1,39 s/plan** pour les Reels à 40k vues ou plus, contre **1,71 s/plan** en dessous.
  - Attention : 16 Reels, c'est un petit échantillon, et le sujet joue plus que le montage. Mais la tendance est nette.
- **Les 3 plus gros Reels sont à 1,2–1,3 s/plan.**
  - Les plus lents (Maison du Curry 2,8 s, Bouillon 2,0 s) sont parmi les plus faibles.
  - Ces deux-là sont des Guest Lunch de l'ancien format, avec de longues prises d'invités.
- **Hook :**
  - Les Reels qui marchent ont 4 à 6 plans dans les 3 premières secondes.
  - Les plus faibles en ont 1 ou 2.

**Règles proposées pour le montage (à valider, puis à reporter dans DA.md) :**
1. Viser **≈ 1,0–1,3 s/plan** en moyenne. Le hook doit être plus rapide : **≥ 4 plans dans les 3 premières secondes**.
2. Interviews d'invités : pas de prise face cam de plus de ~2 s sans B-roll (plat nommé, bouchée, réaction).
3. Première phrase = **titre-promesse** chiffré ou superlatif. Pour Marcello, c'est « Les meilleures pizzas de Toulouse… ».

**Pour comparer, Marcello v3 :**
- 1,02 s/plan ;
- 6 plans dans les 3 premières secondes ;
- 78 s au total.

## 3. Ce que je n'ai pas pu faire
- **Rythme sur plus de Reels :** il faudrait que Chrome reste au premier plan pendant la mesure, environ 1 min par Reel. Autre option : me donner les fichiers vidéo, et `tools/analyze.py` fait le reste.
- **Durée de visionnage / taux de rétention :** il faudrait les statistiques Instagram (onglet Insights de chaque Reel). Elles ne sont pas dans l'export actuel.
