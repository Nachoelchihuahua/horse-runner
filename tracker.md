# Création du jeu horse runner
## on va créer un jeu de cheval qui s'apparente au jeu google avec le dinosaure lorsqu'il n'y a pas internet

---

## Étapes de développement

### Étape 1 — Base ✅
- Fenêtre pygame 800x400
- Rectangle marron représentant le cheval (provisoire)
- Boucle de jeu principale

---

### Étape 2 — Physique du saut ✅
**Ce qu'on a fait :**
- Ajout d'une constante `GRAVITY = 0.8` appliquée chaque frame sur `vel_y`
- Ajout d'une force de saut `JUMP_FORCE = -15` (valeur négative = vers le haut)
- Le cheval saute avec **espace** ou **flèche haut**
- Saut impossible si `on_ground = False` (pas de double saut)
- Atterrissage détecté quand `horse_y >= GROUND_Y` → `vel_y` remis à 0, `on_ground = True`
- Ajout d'un sol visible : ligne noire en bas de l'écran
- Ajout de `clock.tick(60)` pour limiter à 60 FPS (physique stable)

**Constantes clés :**
| Nom | Valeur | Rôle |
|---|---|---|
| `GROUND_Y` | 320 | Position Y du sol |
| `GRAVITY` | 0.8 | Accélération vers le bas par frame |
| `JUMP_FORCE` | -15 | Vitesse initiale du saut |

---

### Étape 3 — Le sol et le décor ✅
**Ce qu'on a fait :**
- Ajout d'une constante `SPEED = 6` (vitesse de défilement en pixels/frame)
- Le sol défile via un `ground_offset` qui avance de `SPEED` px à chaque frame et boucle avec `% (DASH_W + DASH_GAP)`
- Ligne de sol fixe noire tracée en `GROUND_LINE_Y`
- Tirets gris dessinés sous la ligne, recalculés depuis `ground_offset` pour remplir tout l'écran en boucle

**Constantes clés :**
| Nom | Valeur | Rôle |
|---|---|---|
| `SPEED` | 6 | Vitesse de défilement (px/frame) |
| `DASH_W` | 40 | Largeur d'un tiret |
| `DASH_GAP` | 30 | Espace entre deux tirets |
| `GROUND_LINE_Y` | GROUND_Y + 60 | Y de la ligne de sol visible |

### Étape 4 — Les obstacles ✅
**Ce qu'on a fait :**
- Les obstacles sont des dicts `{x, w, h}` stockés dans une liste `obstacles`
- Spawn déclenché par un timer (`obstacle_timer`) : quand il atteint `next_obstacle_in`, un obstacle apparaît à `x = WIDTH` (bord droit)
- Hauteur et largeur aléatoires (`h` entre 40 et 80 px, `w` entre 20 et 40 px)
- Chaque frame : `obs["x"] -= SPEED` → les obstacles glissent vers la gauche à la même vitesse que le sol
- Nettoyage : les obstacles dont `x + w <= 0` sont retirés de la liste
- `next_obstacle_in` est re-tiré aléatoirement après chaque spawn pour varier le rythme

**Constantes clés :**
| Nom | Valeur | Rôle |
|---|---|---|
| `OBSTACLE_MIN_INTERVAL` | 60 | Minimum de frames entre deux obstacles |
| `OBSTACLE_MAX_INTERVAL` | 120 | Maximum de frames entre deux obstacles |

### Étape 5 — Détection de collision ✅
**Ce qu'on a fait :**
- Hitbox du cheval : `pygame.Rect(horse_x + 5, horse_y + 18, 44, 24)` — correspond exactement au corps (sans les pattes ni la tête) pour être fair envers le joueur
- Hitbox obstacle : `pygame.Rect(obs_x, GROUND_LINE_Y - obs_h, obs_w, obs_h)`
- `horse_rect.colliderect(obs_rect)` déclenche `state = "gameover"` et sauvegarde le `best_score`

---

### Étape 6 — Score ✅
**Ce qu'on a fait :**
- `score` incrémenté de 1 chaque frame pendant `state == "playing"` (≈ distance parcourue à 60 FPS)
- `speed = 6 + score // 200` : le jeu accélère d'1 px/frame tous les ~3 secondes
- `best_score` conservé entre les parties (en mémoire, pas sauvegardé sur disque)
- Score et meilleur score affichés en haut à droite pendant la partie

---

### Étape 7 — Écrans de jeu ✅
**Ce qu'on a fait :**
- Machine à états : `state` vaut `"start"`, `"playing"` ou `"gameover"`
- **Écran start** : titre + instruction, n'importe quelle touche lance la partie
- **Écran game over** : score de la partie + meilleur score + instruction pour rejouer (Espace ou Entrée)
- `reset_game()` remet toutes les variables à zéro proprement

---

### Étape 8 — Sprites et animations ✅
**Ce qu'on a fait :**
- Fonction `draw_horse(surface, x, y, frame, jumping)` remplace le rectangle
- Corps, cou, tête, œil, naseau, crinière, queue dessinés avec `pygame.draw.rect`
- **2 frames d'animation** (frame 0 / frame 1) : les 4 pattes s'inclinent en sens opposé pour simuler la foulée, bascule toutes les 8 frames
- **Animation du saut** : pattes repliées vers le haut quand `on_ground = False`
- Cheval affiché sur l'écran de démarrage en aperçu

### Étape 9 — Musique de fond ✅
**Ce qu'on a fait :**
- `pygame.mixer.pre_init(44100, -16, 2, 512)` appelé **avant** `pygame.init()` pour garantir le bon format audio (stéréo 16-bit, 44100 Hz)
- Musique générée **sans fichier audio** : `build_music_loop()` fabrique un buffer PCM avec les modules Python `math` et `array`
- Chaque note = onde sinusoïdale + harmonique (×2) avec un `decay = exp(-t * 12)` pour un son type piano staccato
- 16 notes définies dans `MELODY` (gamme de do majeur, rythme galopant en 4/4)
- Le buffer complet est empaqueté dans un `pygame.mixer.Sound` et joué en boucle infinie sur `Channel(0)`
- Musique **stoppée** à la collision (`music_ch.stop()`) et **relancée** au redémarrage (`music_ch.play(music, loops=-1)`)
- **Jingle game over** : mélodie descendante E5→C5→A4→G4→E4→C4 jouée sur `Channel(1)` dès la collision

**Constantes clés :**
| Nom | Valeur | Rôle |
|---|---|---|
| `SAMPLE_RATE` | 44100 | Échantillons par seconde |
| `volume` | 0.20 | Volume de la musique (0 → 1) |
| `decay` | exp(-t × 12) | Enveloppe d'extinction de la note |

### Étape 10 — Polish final ✅
**Ce qu'on a fait :**
- **Fond** : ciel bleu clair `(220, 235, 255)` remplace le blanc
- **Nuages roses** : 5 nuages générés avec `make_cloud()`, dessinés en 3 ellipses roses superposées, défilement lent (0.8 px/frame) pour effet parallaxe. Nouveaux nuages spawned à droite quand les anciens sortent
- **Mouches noires** : 6 mouches (`make_fly()`) avec corps noir + 2 ailes grises, oscillation sinusoïdale verticale (`math.sin(buzz) * 0.8`) pour simuler le vol, vitesse aléatoire 1.5–3.5 px/frame
- **Nuages et mouches animent dans tous les états** (start, playing, gameover)
- **Titre fenêtre** : `pygame.display.set_caption("Horse Runner 🐴")`
- **Icône fenêtre** : surface 32×32 avec silhouette du cheval (corps/cou/tête/pattes/queue) dessinée avant `set_icon()`
- Tirets du sol passés en brun sable `(140, 120, 80)` pour cohérence visuelle

---

### Bonus — Sauvegarde du meilleur score ✅
**Ce qu'on a fait :**
- Meilleur score lu depuis `best_score.txt` au lancement (`try/except` pour gérer l'absence du fichier)
- Fichier écrit uniquement quand le score actuel **bat** le record (évite les écritures inutiles)
- Format : entier brut sur une ligne, lisible et modifiable à la main
