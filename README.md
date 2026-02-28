# 🏛️ Augustinus Citator — Add-in Word pour citer Augustin d'Hippone

## Présentation

Cet add-in Word permet de **citer directement les œuvres d'Augustin** et de les insérer comme **notes de bas de page** (ou de fin, ou inline) dans vos documents Word.

### Fonctionnalités

- **Base de données de 55+ œuvres** d'Augustin classées par catégorie
- **Recherche instantanée** par titre latin, anglais ou abréviation standard
- **5 styles de citation** : CCSL/CSEL, PL (Migne), BA, WSA, abrégé
- **Insertion directe** en note de bas de page, note de fin, ou parenthèse
- **Formatage configurable** : chiffres romains, titres latins/anglais, dates
- **Historique** des citations récentes (réutilisation en un clic)
- **Copier-coller** en fallback si Word n'est pas connecté

---

## Installation rapide (5 minutes)

### Prérequis

- **Node.js** (v16+) — [nodejs.org](https://nodejs.org)
- **Microsoft Word** (desktop ou Word Online)
- **OpenSSL** (inclus sur Mac/Linux ; sur Windows, utilisez Git Bash)

### Étapes

#### 1. Générer les certificats SSL (une seule fois)

```bash
cd augustine-word-addin
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/CN=localhost"
```

#### 2. Lancer le serveur

```bash
node server.js
```

#### 3. Accepter le certificat dans le navigateur

Ouvrez **https://localhost:3000** dans votre navigateur et acceptez l'avertissement de sécurité (certificat auto-signé).

#### 4. Charger l'add-in dans Word (sideloading)

**Word Desktop (Windows)** :
1. Ouvrez Word
2. Allez dans **Insertion** → **Compléments** → **Mes compléments**
3. Cliquez sur **Télécharger mon complément**
4. Sélectionnez le fichier `manifest.xml`

**Word Desktop (Mac)** :
1. Ouvrez Word
2. Allez dans **Insertion** → **Compléments** → **Mes compléments**
3. Cliquez sur le **⋯** en bas à gauche → **Télécharger mon complément**
4. Sélectionnez le fichier `manifest.xml`

**Word Online** :
1. Ouvrez un document dans Word Online
2. Allez dans **Insertion** → **Compléments** → **Télécharger mon complément**
3. Sélectionnez le fichier `manifest.xml`

#### 5. Utiliser l'add-in

Un bouton **"Cite Augustine"** apparaît dans le ruban **Accueil**. Cliquez dessus pour ouvrir le panneau latéral.

---

## Utilisation

### Citer une œuvre

1. **Recherchez** une œuvre (ex: tapez "conf" pour les Confessions)
2. **Cliquez** sur l'œuvre souhaitée
3. **Remplissez** les champs : Livre, Chapitre, Paragraphe
4. **Vérifiez** l'aperçu en bas du formulaire
5. **Cliquez** sur « Insert Footnote » pour insérer dans Word

### Styles de citation disponibles

| Style | Exemple |
|-------|---------|
| **CCSL** | Augustine, *Confessiones* X, 27, 38 (CCSL 27, ed. L. Verheijen) |
| **PL** | Augustine, *Confessiones* X, 27, 38 (PL 32, 659–868) |
| **BA** | Augustin, *Confessiones* X, 27, 38 (BA 13–14, p. 175) |
| **Short** | Aug., *conf.* X, 27, 38 |
| **WSA** | Augustine, "Confessions," X, 27, 38, in WSA I/1 |

### Options configurables (onglet Settings)

- Titres en latin ou anglais
- Chiffres romains pour les livres
- Inclusion de la date de composition
- Insertion en footnote, endnote, ou inline

---

## Structure du projet

```
augustine-word-addin/
├── manifest.xml      ← Manifeste de l'add-in Word
├── taskpane.html     ← Interface complète (UI + base de données + logique)
├── server.js         ← Serveur HTTPS local
├── README.md         ← Ce fichier
├── key.pem           ← (généré) Clé SSL
└── cert.pem          ← (généré) Certificat SSL
```

---

## Ajout d'œuvres à la base de données

La base de données est directement dans `taskpane.html` dans l'objet `WORKS`. Pour ajouter une œuvre, ajoutez un objet au tableau :

```javascript
{
  id: "identifiant_unique",
  abbrev: "abrév.",
  latin: "Titre latin",
  english: "English Title",
  date: "dates",
  category: "catégorie",   // major, education, exegetical, anti-pelagian, etc.
  books: 1,                // nombre de livres
  ccsl: "CCSL XX",
  csel: "CSEL XX",
  pl: "PL XX, col-col",
  ba: "BA XX",
  wsa: "WSA I/XX",
  editor: "Nom de l'éditeur"
}
```

---

## Dépannage

| Problème | Solution |
|----------|----------|
| Le panneau ne s'ouvre pas | Vérifiez que le serveur tourne (`node server.js`) |
| Erreur de certificat | Ouvrez https://localhost:3000 dans le navigateur et acceptez |
| Le bouton n'apparaît pas | Re-sideloadez le manifest.xml |
| L'insertion ne fonctionne pas | L'add-in copie automatiquement dans le presse-papier en fallback |

---

## Licence

Outil libre pour usage académique.
