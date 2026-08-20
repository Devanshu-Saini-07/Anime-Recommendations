CREATE DATABASE IF NOT EXISTS anime_tracker;
USE anime_tracker;

CREATE TABLE IF NOT EXISTS anime (
    anime_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    genre VARCHAR(50),
    status VARCHAR(50),
    total_episodes INT
);