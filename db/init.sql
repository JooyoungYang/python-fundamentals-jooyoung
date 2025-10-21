CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,
  email VARCHAR(255) NOT NULL UNIQUE,
  full_name VARCHAR(100) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CHECK (CHAR_LENGTH(username) >= 3)
);

INSERT INTO users (username,email,full_name,password_hash,is_active) VALUES
('alice','alice@example.com','Alice Liddell','hash',1),
('bob','bob@example.com','Bob Builder','hash',1),
('charlie','charlie@example.com','Charlie Brown','hash',0)
ON DUPLICATE KEY UPDATE email=VALUES(email);
