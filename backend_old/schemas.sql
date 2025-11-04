-- ========================
-- 1) DROP si déjà existant
-- ========================
DROP TABLE IF EXISTS commentaires CASCADE;
DROP TABLE IF EXISTS notes CASCADE;
DROP TABLE IF EXISTS utilisateurs CASCADE;

-- ========================
-- 2) Création des tables
-- ========================

-- Table utilisateurs
CREATE TABLE utilisateurs (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    mot_de_passe VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    equipe VARCHAR(100),
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index
CREATE INDEX idx_utilisateur_nom ON utilisateurs (nom);
CREATE INDEX idx_utilisateur_email ON utilisateurs (email);
CREATE INDEX idx_utilisateur_type ON utilisateurs (type);
CREATE INDEX idx_utilisateur_equipe ON utilisateurs (equipe);
CREATE INDEX idx_utilisateur_date ON utilisateurs (date);


-- Table notes
CREATE TABLE notes (
    id SERIAL PRIMARY KEY,
    titre VARCHAR(255) NOT NULL,
    contenu TEXT NOT NULL,
    equipe VARCHAR(100),
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    auteur_id INT NOT NULL REFERENCES utilisateurs(id) ON DELETE CASCADE
);

-- Index
CREATE INDEX idx_note_titre ON notes (titre);
CREATE INDEX idx_note_equipe ON notes (equipe);
CREATE INDEX idx_note_date ON notes (date);
CREATE INDEX idx_note_auteur ON notes (auteur_id);


-- Table commentaires
CREATE TABLE commentaires (
    id SERIAL PRIMARY KEY,
    contenu TEXT NOT NULL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    auteur_id INT NOT NULL REFERENCES utilisateurs(id) ON DELETE CASCADE,
    note_id INT NOT NULL REFERENCES notes(id) ON DELETE CASCADE
);

-- Index
CREATE INDEX idx_commentaire_date ON commentaires (date);
CREATE INDEX idx_commentaire_auteur ON commentaires (auteur_id);
CREATE INDEX idx_commentaire_note ON commentaires (note_id);


-- ========================
-- 3) Données de test
-- ========================
/*
-- Utilisateurs
INSERT INTO utilisateurs (nom, email, mot_de_passe, type, equipe) VALUES
('Alice', 'alice@example.com', 'hashedpass1', 'admin', 'Dev'),
('Bob', 'bob@example.com', 'hashedpass2', 'user', 'QA'),
('Charlie', 'charlie@example.com', 'hashedpass3', 'user', 'DevOps');

-- Notes
INSERT INTO notes (titre, contenu, equipe, auteur_id) VALUES
('Première Note', 'Ceci est le contenu de la première note.', 'Dev', 1),
('Deuxième Note', 'Voici quelques infos dans la deuxième note.', 'QA', 2);

-- Commentaires
INSERT INTO commentaires (contenu, auteur_id, note_id) VALUES
('Super note, merci !', 2, 1),
('Je vais vérifier ça.', 3, 1),
('Bonne explication.', 1, 2);

*/