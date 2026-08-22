USE anime_tracker;

ALTER TABLE users
ADD COLUMN IF NOT EXISTS preferences_completed_at TIMESTAMP NULL DEFAULT NULL;

CREATE TABLE IF NOT EXISTS user_preferences (
    preference_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    genre_name VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_user_genre (user_id, genre_name),
    CONSTRAINT fk_user_preferences_user
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
