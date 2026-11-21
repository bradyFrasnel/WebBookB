# CAHIER DES CHARGES
## Gestionnaire personnel de sites web

Version  1.1  
Type  Progressive Web App (PWA)  
Statut  Conception

## 1. Présentation du projet

### 1.1. Contexte

Au quotidien, nous créons des comptes sur de nombreuses plateformes et utilisons différents services en ligne  développement, hébergement, stockage, réseaux sociaux, divertissement, etc.

Il devient progressivement difficile de retrouver toutes ces plateformes.

Le projet consiste à développer une application permettant de centraliser les sites Internet importants dans un espace personnel unique.

### 1.2. Objectif général

Développer une application web progressive permettant de répertorier, organiser, rechercher et retrouver rapidement les sites Internet utilisés par son propriétaire.

L'application doit également permettre une redirection directe vers les plateformes enregistrées.

### 1.3. Public cible

Application initialement destinée à un usage personnel, avec une architecture pouvant éventuellement évoluer vers une utilisation publique.

## 2. Fonctionnalités principales

### 2.1. Gestion des sites

L'utilisateur doit pouvoir 
- Ajouter un site.
- Modifier un site.
- Supprimer un site.
- Consulter les sites enregistrés.
- Accéder directement à un site depuis son URL.
- Ajouter un site à ses favoris ou le retirer des favoris.

Informations enregistrées pour chaque site 

 Champ  Description 
------
 ID  Identifiant unique 
 Nom  Nom de la plateforme 
 URL  Adresse du site 
 Catégorie  Catégorie associée 
 Icône  Logo ou favicon 
 Favori  Indique si le site est favori 
 Date de création  Date d'enregistrement 

Le formulaire d'ajout comporte trois champs principaux 
1. Nom du site.
2. URL du site.
3. Catégorie.

L'icône et les autres informations techniques sont gérées automatiquement ou lors de la consultation du site.

### 2.2. Gestion des catégories

L'application adoptera un système hybride de gestion des catégories.

A. Catégories prédéfinies

L'application proposera initialement plusieurs catégories 

- Professionnel
- Divertissement
- Réseaux sociaux
- Éducation
- Développement
- Stockage
- Finance
- Communication
- Autres

B. Catégories personnalisées

L'utilisateur pourra 
- Créer une nouvelle catégorie.
- Modifier le nom d'une catégorie.
- Supprimer une catégorie.
- Consulter les sites associés à une catégorie.

Les catégories personnalisées seront enregistrées dans la base de données.

Règles de gestion 
- Chaque site doit appartenir à une catégorie.
- Une catégorie peut contenir plusieurs sites.
- Une catégorie ne doit pas être supprimée si elle contient encore des sites sans avoir préalablement défini leur nouvelle catégorie.
- Les catégories prédéfinies doivent être disponibles dès l'installation de l'application.

### 2.3. Recherche

L'application proposera une recherche permettant de retrouver un site à partir de son nom ou de son URL.

La recherche devra être accessible depuis le tableau de bord.

### 2.4. Gestion des favoris

L'utilisateur pourra marquer ses sites préférés.

Une section dédiée permettra de retrouver rapidement ces plateformes.

### 2.5. Gestion des icônes

Chaque site sera représenté par une icône.

L'application devra 
- Récupérer automatiquement le favicon lorsque cela est possible.
- Permettre l'utilisation d'une icône personnalisée.
- Afficher une icône générique en cas d'échec.

### 2.6. Statistiques

Le tableau de bord affichera 
- Nombre total de sites.
- Nombre de catégories.
- Nombre de favoris.
- Répartition des sites par catégorie.

## 3. Interface utilisateur

L'application devra proposer une interface moderne, responsive et intuitive.

### Pages principales

1. Tableau de bord.
2. Tous les sites.
3. Catégories.
4. Favoris.
5. Ajouter un site.
6. Modifier un site.
7. Gestion des catégories.

## 4. Architecture technique

### Frontend
- React.
- JavaScript.
- CSS.
- PWA  Web App Manifest et Service Worker.

### Backend
- Python.
- FastAPI.
- API REST.
- Pydantic.

### Base de données
- PostgreSQL.
- SQLAlchemy.

### Hébergement
- Frontend sur une plateforme compatible avec React.
- Backend sur un serveur cloud.
- PostgreSQL sur un service cloud.

## 5. Sécurité

- Authentification obligatoire.
- Protection des routes privées.
- Validation des données.
- Communication HTTPS.
- Gestion sécurisée des sessions.
- Protection des informations personnelles.

L'application ne stockera pas les mots de passe des comptes associés aux sites répertoriés.

## 6. Caractéristiques PWA

- Installation sur ordinateur et smartphone.
- Icône d'application.
- Interface responsive.
- Mise en cache des ressources essentielles.
- Consultation hors ligne des données préalablement synchronisées, dans une évolution prévue du projet.

## 7. Contraintes

- Usage initialement personnel.
- Stockage distant.
- Connexion Internet nécessaire pour la synchronisation.
- Les URL doivent être validées.
- Les catégories doivent respecter les règles de gestion définies.

## 8. Évolutions envisageables

- Importation et exportation des sites.
- Détection automatique des liens indisponibles.
- Historique des sites récemment consultés.
- Notes personnelles.
- Synchronisation hors ligne avancée.
- Gestion de plusieurs utilisateurs.

## 9. Résultat attendu

Disposer d'une application personnelle, sécurisée, installable et accessible depuis plusieurs appareils, permettant de centraliser les plateformes numériques, de les organiser par catégories et de les retrouver rapidement.