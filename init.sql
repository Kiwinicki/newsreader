CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS user_friends (
    user_id INTEGER REFERENCES users(id),
    friend_id INTEGER REFERENCES users(id),
    PRIMARY KEY (user_id, friend_id)
);

INSERT INTO users (name) VALUES ('Alice');
INSERT INTO users (name) VALUES ('Bob');
INSERT INTO users (name) VALUES ('Charlie');

INSERT INTO user_friends (user_id, friend_id) VALUES (1, 2), (2, 1), (1, 3), (3, 1);