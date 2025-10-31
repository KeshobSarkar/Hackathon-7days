CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50),
    points INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE quiz_sessions (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    theme VARCHAR(50),
    score INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE rewards (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    points_awarded INT,
    coupon_code VARCHAR(50),
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);