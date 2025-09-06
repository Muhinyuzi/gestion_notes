-- Supprimer les tables si elles existent déjà (attention à la perte de données)
DROP TABLE IF EXISTS commentaires CASCADE;
DROP TABLE IF EXISTS notes CASCADE;
DROP TABLE IF EXISTS utilisateurs CASCADE;

-- ---------------- UTILISATEURS ----------------
CREATE TABLE utilisateurs (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    mot_de_passe VARCHAR(255) NOT NULL,
    equipe VARCHAR(100)
);

-- ---------------- NOTES ----------------
CREATE TABLE notes (
    id SERIAL PRIMARY KEY,
    titre VARCHAR(200) NOT NULL,
    contenu TEXT NOT NULL,
    equipe VARCHAR(100),
    auteur_id INTEGER REFERENCES utilisateurs(id) ON DELETE CASCADE
);

-- ---------------- COMMENTAIRES ----------------
CREATE TABLE commentaires (
    id SERIAL PRIMARY KEY,
    contenu TEXT NOT NULL,
    auteur_id INTEGER REFERENCES utilisateurs(id) ON DELETE CASCADE,
    note_id INTEGER REFERENCES notes(id) ON DELETE CASCADE
);

-- ---------------- INSERTIONS EXEMPLE ----------------
INSERT INTO utilisateurs (nom, email, mot_de_passe, equipe)
VALUES
('Alice', 'alice@example.com', 'secret1', 'Dev'),
('Bob', 'bob@example.com', 'secret2', 'QA');

INSERT INTO notes (titre, contenu, equipe, auteur_id)
VALUES
('Première note', 'Ceci est une note de test.', 'Dev', 1),
('Deuxième note', 'Une autre note de test.', 'QA', 2);

INSERT INTO commentaires (contenu, auteur_id, note_id)
VALUES
('Super note !', 2, 1),
('Merci pour le retour !!', 1, 1),
('Besoin de détails ?', 1, 2);