# Analyse Instagram @guestlunch (contexte pour Claude Code)

## Contexte
- Compte : @guestlunch, page de tests de restos/bars/glaciers/guinguettes à Toulouse (Harrison Sportes).
- Source : export des Insights Instagram, 81 posts (80 reels + 1 photo), de la 1re vidéo (11/12/2024, "Episode 1") à mi-2026.
- Données brutes : `guestlunch_stats_81_posts.csv` (dans ce dossier), ordre = du plus récent au plus ancien.
- Une version v3 du CSV existait avec 2 colonnes en plus (`Nom de la vidéo` = nom du resto, `Date de publication` au format JJ/MM/AAAA). Elle n'est pas récupérable ici : à réimporter si besoin.
- Analyse d'origine faite dans la conversation claude.ai "Création d'un fichier Excel organisé" (juillet 2026).

## Dictionnaire des colonnes
| Colonne | Sens |
|---|---|
| Shortcode, URL | identifiant / lien du post (`/reel/` = reel, `/p/` = photo) |
| Vues | vues totales |
| Vues_Followers_% / Vues_NonFollowers_% | part des vues venant d'abonnés / non-abonnés (en %, pas en fraction) |
| ComptesTouches | portée (comptes uniques) |
| Interactions | total likes + commentaires + enregistrements + partages... |
| Interactions_Followers_% / _NonFollowers_% | répartition des interactions |
| MentionsJaime, Commentaires, Enregistrements, Partages | détail des interactions |
| ComptesAyantInteragi | comptes uniques ayant interagi |
| ActiviteProfil | activité profil générée |
| FollowersEnPlus | nouveaux abonnés générés |
| Note | remarques manuelles (format boosté, stats Facebook, etc.) |

## Points d'attention sur les données (à vérifier)
- **`Partages` = 0 partout** : quasi certainement une erreur d'extraction (une autre conversation mentionne 8000 partages sur une vidéo). Ne pas conclure sur les partages avec ce fichier.
- **`ActiviteProfil` est identique à `FollowersEnPlus`** sur 80 lignes sur 81 : probablement un mauvais mapping à l'export.
- `DaS_dEnsIjv` : reel boosté (pub), structure différente, % et Interactions vides.
- `DXmdooAsin-` : "ComptesTouches" = comptes Meta touchés, pas comparable aux autres.
- `DR97Wq4jOmr` : seule photo (n=1, non représentatif).
- Notes "FB: ..." = stats du repost Facebook (négligeables : 180 à 430 vues).

## Chiffres clés (vérifiés le 13/11/2026 sur le CSV)
- Total vues : 3 206 904. Total nouveaux abonnés : 8 782.
- Reels : moyenne 39 970 vues, médiane 16 584 (distribution très asymétrique, quelques vidéos virales tirent la moyenne).
- Photo unique : 9 274 vues.

### Top 8 reels par vues
| Shortcode | Vues | Enregistrements | Nouveaux abonnés |
|---|---|---|---|
| DT0hcKADHLN | 500 412 | 9 811 | 971 |
| DSaS5ruDANV | 271 072 | 990 | 1 185 |
| DVysehhDBlx | 226 299 | 4 851 | 897 |
| DXmdooAsin- | 213 255 | 156 | 12 |
| DU8qHQuDIML | 131 678 | 310 | 58 |
| DRkUthJjM_X | 128 938 | 3 254 | 804 |
| DQHe6y2jG5i | 93 444 | 2 453 | 256 |
| DRATb5rjBsN | 76 510 | 1 163 | 464 |

À noter : `DXmdooAsin-` et `DU8qHQuDIML` ont beaucoup de vues mais très peu d'enregistrements et d'abonnés (portée large mais peu de conversion). `DSaS5ruDANV` est la meilleure vidéo pour gagner des abonnés.

## Analyse 1 : corrélations avec les vues (reels uniquement, Pearson)
| Variable | r avec Vues |
|---|---|
| ComptesTouches | 0.99 (quasi tautologique) |
| Likes | 0.92 |
| Interactions | 0.91 |
| Enregistrements | 0.85 |
| Nouveaux abonnés | 0.80 |
| Commentaires | 0.72 |
| Taux d'engagement (Interactions/ComptesTouches) | 0.42 |
| Taux de sauvegarde (Enregistrements/Vues) | 0.26 |
| Taux de commentaire (Commentaires/Vues) | -0.16 |

Interprétation : les volumes absolus sont des conséquences des vues, pas des leviers. Il faut regarder les **taux**.

## Analyse 2 : ce qui pousse vers les non-abonnés (proxy de la mise en avant algorithmique)
Corrélation avec `Vues_NonFollowers_%` :
- Taux de sauvegarde : **0.39** (meilleur signal)
- Taux d'engagement : 0.36
- Taux de like : 0.09
- Taux de commentaire : -0.25

## Analyse 3 : quartiles de vues (80 reels)
| | Q1 (bas) | Q2 | Q3 | Q4 (haut) |
|---|---|---|---|---|
| Vues moyennes | 5 507 | 11 591 | 27 509 | 115 274 |
| Taux de sauvegarde | 0.33 % | 0.79 % | 1.17 % | **1.55 %** |
| Taux d'engagement | 3.7 % | 4.5 % | 5.8 % | **7.9 %** |
| % vues non-abonnés | 74 % | 81 % | 91 % | **95 %** |
| Nouveaux abonnés / 1000 vues | 2.3 | 2.5 | 2.9 | 2.9 |

## Conclusions
1. **Le taux d'enregistrement est le levier le plus net** : x5 entre Q1 et Q4, et meilleur prédicteur de la diffusion aux non-abonnés.
2. Les commentaires ne sont pas un levier (légèrement anti-corrélés).
3. Pour maximiser les vues : tout ce qui pousse à enregistrer (adresse et infos pratiques à l'écran, prix, "à tester", format carnet d'adresses / liste).
4. Corrélation ne veut pas dire causalité : un bon resto peut à la fois faire enregistrer et être poussé. Avec n=80, rester prudent.

## Tendances externes relevées (recherche web, juillet 2026, non vérifiées sur ce compte)
- Le hook des 3 premières secondes est décisif.
- Les partages en message privé pèsent plus que les likes dans la distribution.
- Reels de 15 à 30 s : meilleur taux de complétion pour du contenu food/ambiance.
- Un visage humain à l'écran performe mieux que des plans produit seuls.
- Avis nuancés et authentiques > contenu trop lisse.

## Pistes non réalisées (à faire avec Claude Code)
- Ré-exporter les Insights pour corriger `Partages` et `ActiviteProfil`.
- Réimporter le CSV v3 (noms des restos + dates) et analyser : type d'établissement, jour/heure de publication, évolution dans le temps.
- Analyse des 5 premières secondes : extraire des frames avec ffmpeg (ex. toutes les 0.5 s) + transcription audio (Whisper), puis faire classer les hooks par Claude (plat visible dès la 1re seconde, texte à l'écran, visage, prix affiché...) et croiser avec le taux d'enregistrement.
- Régression simple (log(Vues) ~ taux de sauvegarde + taux d'engagement + ancienneté du compte) pour isoler l'effet de la croissance du compte.

## Code de base pour reproduire
```python
import pandas as pd
df = pd.read_csv("guestlunch_stats_81_posts.csv")
df["Type"] = df.URL.apply(lambda u: "Reel" if "/reel/" in u else "Photo")
r = df[df.Type == "Reel"].copy()
r["TauxSave"] = r.Enregistrements / r.Vues
r["TauxComment"] = r.Commentaires / r.Vues
r["TauxEng"] = r.Interactions / r.ComptesTouches
r["q"] = pd.qcut(r.Vues, 4, labels=["Q1", "Q2", "Q3", "Q4"])
print(r.groupby("q", observed=True)[["TauxSave", "TauxEng", "Vues_NonFollowers_%"]].mean())
```
