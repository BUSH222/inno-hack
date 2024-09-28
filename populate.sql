-- Insert users
INSERT INTO users (name, password, email) VALUES
('Alice', 'password123', 'email1@'),
('Bob', 'securepass', 'email2@'),
('Charlie', 'charlie123', 'email3@');

-- Insert repositories
INSERT INTO repositories (name, user_creator_id) VALUES
('Repo1', 1),
('Repo2', 2),
('Repo3', 3);

-- Insert repo_access
INSERT INTO repo_access (repoid, userid) VALUES
(1, 1),
(1, 2),
(2, 2),
(2, 3),
(3, 1),
(3, 3);

-- Insert commits
INSERT INTO commits (name, creation_time, author, repository, data) VALUES
('Initial commit', '2024-09-27 10:00:00', 1, 1, 'Initial data for Repo1'),
('Added feature X', '2024-09-27 11:00:00', 2, 1, 'Feature X data'),
('Fixed bug Y', '2024-09-27 12:00:00', 3, 2, 'Bug Y fix data'),
('Improved performance', '2024-09-27 13:00:00', 1, 3, 'Performance improvements'),
('Updated documentation', '2024-09-27 14:00:00', 3, 3, 'Documentation updates');