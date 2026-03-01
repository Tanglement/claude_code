-- Stock Information System Database Schema
-- MySQL Database

-- ============================================
-- User Tables
-- ============================================

-- User Information Table
CREATE TABLE IF NOT EXISTS user_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE COMMENT 'Username',
    password VARCHAR(255) NOT NULL COMMENT 'Password (hashed)',
    email VARCHAR(100) COMMENT 'Email',
    phone VARCHAR(20) COMMENT 'Phone number',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Updated time',
    INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='User information';

-- User Holdings Table (持仓)
CREATE TABLE IF NOT EXISTS user_holdings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT 'User ID',
    symbol VARCHAR(20) NOT NULL COMMENT 'Stock code',
    shares INT NOT NULL DEFAULT 0 COMMENT 'Number of shares',
    cost_price DECIMAL(10, 2) NOT NULL DEFAULT 0 COMMENT 'Cost price per share',
    purchase_date DATE COMMENT 'Purchase date',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Updated time',
    UNIQUE KEY uk_user_symbol (user_id, symbol),
    INDEX idx_user_id (user_id),
    FOREIGN KEY (user_id) REFERENCES user_info(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='User stock holdings';

-- User Watchlist Table (自选股)
CREATE TABLE IF NOT EXISTS user_watchlist (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT 'User ID',
    symbol VARCHAR(20) NOT NULL COMMENT 'Stock code',
    stock_name VARCHAR(100) DEFAULT '' COMMENT 'Stock name',
    notes VARCHAR(500) DEFAULT '' COMMENT 'Notes',
    alert_price DECIMAL(10, 2) COMMENT 'Alert price',
    alert_pct DECIMAL(5, 2) COMMENT 'Alert percentage',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Updated time',
    UNIQUE KEY uk_user_symbol (user_id, symbol),
    INDEX idx_user_id (user_id),
    FOREIGN KEY (user_id) REFERENCES user_info(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='User watchlist';

-- User Preference Table (推送设置)
CREATE TABLE IF NOT EXISTS user_preference (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE COMMENT 'User ID',
    push_enabled TINYINT(1) DEFAULT 1 COMMENT 'Enable push notification',
    push_time VARCHAR(10) DEFAULT '09:30' COMMENT 'Push time (HH:MM)',
    push_days VARCHAR(20) DEFAULT '1,2,3,4,5' COMMENT 'Push days (1-7, comma separated)',
    price_alert TINYINT(1) DEFAULT 1 COMMENT 'Enable price alert',
    news_alert TINYINT(1) DEFAULT 1 COMMENT 'Enable news alert',
    announcement_alert TINYINT(1) DEFAULT 1 COMMENT 'Enable announcement alert',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Updated time',
    INDEX idx_user_id (user_id),
    FOREIGN KEY (user_id) REFERENCES user_info(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='User notification preferences';

-- ============================================
-- Stock Tables
-- ============================================

-- Stock Basic Information Table
CREATE TABLE IF NOT EXISTS stock_basic (
    id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL UNIQUE COMMENT 'Stock code',
    name VARCHAR(100) NOT NULL COMMENT 'Stock name',
    full_name VARCHAR(200) COMMENT 'Full name',
    market VARCHAR(20) NOT NULL COMMENT 'Market (A/H/US)',
    industry VARCHAR(50) COMMENT 'Industry',
    listing_date DATE COMMENT 'Listing date',
    delisting_date DATE COMMENT 'Delisting date',
    status ENUM('正常', 'ST', '*ST', '退市') DEFAULT '正常' COMMENT 'Stock status',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_symbol (symbol),
    INDEX idx_industry (industry)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Stock basic information';

-- Stock Realtime Quote Table
CREATE TABLE IF NOT EXISTS stock_realtime (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL COMMENT 'Stock code',
    price DECIMAL(10, 2) NOT NULL COMMENT 'Current price',
    change_amount DECIMAL(10, 2) NOT NULL COMMENT 'Change amount',
    change_pct DECIMAL(5, 2) NOT NULL COMMENT 'Change percentage',
    open DECIMAL(10, 2) NOT NULL COMMENT 'Open price',
    high DECIMAL(10, 2) NOT NULL COMMENT 'High price',
    low DECIMAL(10, 2) NOT NULL COMMENT 'Low price',
    close_yest DECIMAL(10, 2) NOT NULL COMMENT 'Yesterday close',
    volume BIGINT NOT NULL COMMENT 'Volume',
    amount DECIMAL(15, 2) NOT NULL COMMENT 'Amount',
    turnover DECIMAL(5, 2) NOT NULL COMMENT 'Turnover rate',
    pe DECIMAL(10, 2) COMMENT 'P/E ratio',
    pb DECIMAL(10, 2) COMMENT 'P/B ratio',
    datetime DATETIME NOT NULL COMMENT 'Quote time',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_symbol_datetime (symbol, datetime),
    FOREIGN KEY (symbol) REFERENCES stock_basic(symbol) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Stock realtime quotes';

-- Stock History Table
CREATE TABLE IF NOT EXISTS stock_history (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL COMMENT 'Stock code',
    trade_date DATE NOT NULL COMMENT 'Trade date',
    open DECIMAL(10, 2) NOT NULL COMMENT 'Open price',
    high DECIMAL(10, 2) NOT NULL COMMENT 'High price',
    low DECIMAL(10, 2) NOT NULL COMMENT 'Low price',
    close DECIMAL(10, 2) NOT NULL COMMENT 'Close price',
    volume BIGINT NOT NULL COMMENT 'Volume',
    amount DECIMAL(15, 2) NOT NULL COMMENT 'Amount',
    adj_close DECIMAL(10, 2) COMMENT 'Adjusted close',
    change_pct DECIMAL(5, 2) COMMENT 'Change percentage',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_symbol_date (symbol, trade_date),
    INDEX idx_symbol (symbol),
    INDEX idx_date (trade_date),
    FOREIGN KEY (symbol) REFERENCES stock_basic(symbol) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Stock history quotes';

-- ============================================
-- News Tables (MongoDB recommended)
-- ============================================

-- News Collection (use MongoDB)
-- {
--     "title": "News title",
--     "content": "News content",
--     "publish_time": "2024-01-01 10:00:00",
--     "source": "Source",
--     "url": "URL",
--     "sentiment": 0.5,
--     "related_stocks": ["600519", "000001"]
-- }

-- Announcement Collection (use MongoDB)
-- {
--     "title": "Announcement title",
--     "content": "Announcement content",
--     "publish_time": "2024-01-01 10:00:00",
--     "announcement_type": "Type",
--     "company_code": "600519",
--     "url": "URL"
-- }

-- ============================================
-- User Token/Session Table
-- ============================================

CREATE TABLE IF NOT EXISTS user_tokens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT 'User ID',
    token VARCHAR(255) NOT NULL COMMENT 'Token',
    token_data VARCHAR(500) COMMENT 'Token data',
    expires_at DATETIME NOT NULL COMMENT 'Expiration time',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_token (token),
    FOREIGN KEY (user_id) REFERENCES user_info(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='User tokens';
