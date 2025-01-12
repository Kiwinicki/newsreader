CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS user_friends (
    user_id INTEGER REFERENCES users(id),
    friend_id INTEGER REFERENCES users(id),
    PRIMARY KEY (user_id, friend_id)
);

-- Table to store user favorites
CREATE TABLE IF NOT EXISTS user_favorites (
    user_id INTEGER REFERENCES users(id),
    news_id VARCHAR(255) NOT NULL,
    title TEXT NOT NULL,
    PRIMARY KEY (user_id, news_id)
);

-- Table to store user read later
CREATE TABLE IF NOT EXISTS user_read_later (
    user_id INTEGER REFERENCES users(id),
    news_id VARCHAR(255 ) NOT NULL,
    title TEXT NOT NULL,
    PRIMARY KEY (user_id, news_id)
);

-- Insert users
INSERT INTO users (name) VALUES ('Alice'), ('Bob'), ('Charlie');

-- Insert user friendships
INSERT INTO user_friends (user_id, friend_id) VALUES (1, 2), (2, 1), (1, 3), (3, 1), (3, 2);

-- Alice's favorites
INSERT INTO user_favorites (user_id, news_id, title) VALUES
    (1, '58e20467-c2ef-478f-8723-130691f3e920', 'Trump Organization leases brand to 2 new projects in Saudi Arabia'),
    (1, 'd8815c3a-9fce-46d1-a531-5ad17eaab376', 'Showrunners’ Mentorship Matters Diverse Writers Initiative Selects 2024-2025 Participants');

-- Bob's favorites
INSERT INTO user_favorites (user_id, news_id, title) VALUES
    (2, '96ce3bea-c2a7-4145-a36d-7c93c5d9b529', 'How UnitedHealthcare became the face of a broken health care system');

-- Alice's read later
INSERT INTO user_read_later (user_id, news_id, title) VALUES
    (1, 'e7869452-a34c-40c4-9330-de4433ee76ff', 'Banana Republic Outlet Sale: 50% off Everything, +20% off with $6 Finds'),
    (1, '6a957f44-22c6-4d2f-82b1-0044f2acef9b', 'Spider-Man''s Marisa Tomei Reacts to Tom Holland''s Engagement');