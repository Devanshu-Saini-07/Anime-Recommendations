CREATE DATABASE IF NOT EXISTS anime_db;
USE anime_db;

CREATE TABLE IF NOT EXISTS Anime (
    anime_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    genre VARCHAR(50),
    status VARCHAR(50),
    total_episodes INT
);