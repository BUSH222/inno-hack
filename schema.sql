CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(32) NOT NULL,
    password VARCHAR(32) NOT NULL
);

CREATE TABLE IF NOT EXISTS repositories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(32),
    user_creator_id INT REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS repo_access (
    repoid INT REFERENCES repositories(id),
    userid INT REFERENCES users(id),
    PRIMARY KEY (repoid, userid)
);

CREATE TABLE IF NOT EXISTS commits (
    id SERIAL PRIMARY KEY,
    name VARCHAR(32) NOT NULL,
    creation_time TIMESTAMP,
    author INT REFERENCES users(id),
    repository INT REFERENCES repositories(id),
    data BYTEA
);