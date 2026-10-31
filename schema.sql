-- =======================================================
-- Database Schema for Farmer Market Price Assistant
-- Target Districts: Coimbatore, Tiruppur, Erode (Tamil Nadu)
-- =======================================================

CREATE DATABASE IF NOT EXISTS `farmer_market_db` 
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE `farmer_market_db`;

-- 1. Districts
CREATE TABLE IF NOT EXISTS `districts` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL UNIQUE,
    `state` VARCHAR(100) NOT NULL DEFAULT 'Tamil Nadu',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Markets (Mandis)
CREATE TABLE IF NOT EXISTS `markets` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `district_id` INT NOT NULL,
    `district_name` VARCHAR(100) NOT NULL,
    `market_name` VARCHAR(100) NOT NULL UNIQUE,
    `latitude` DECIMAL(10, 6) NOT NULL,
    `longitude` DECIMAL(10, 6) NOT NULL,
    `contact_info` VARCHAR(255) DEFAULT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`district_id`) REFERENCES `districts`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Crops / Commodities
CREATE TABLE IF NOT EXISTS `crops` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL UNIQUE,
    `tamil_name` VARCHAR(100) DEFAULT NULL,
    `category` VARCHAR(50) DEFAULT 'General',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Daily Market Prices (Official AGMARKNET / data.gov.in records)
CREATE TABLE IF NOT EXISTS `daily_prices` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `market_id` INT DEFAULT NULL,
    `market_name` VARCHAR(100) NOT NULL,
    `district_name` VARCHAR(100) NOT NULL,
    `crop_name` VARCHAR(100) NOT NULL,
    `variety` VARCHAR(100) DEFAULT 'Standard',
    `arrival_date` DATE NOT NULL,
    `min_price` DECIMAL(10, 2) NOT NULL COMMENT 'Price in INR per Quintal',
    `max_price` DECIMAL(10, 2) NOT NULL COMMENT 'Price in INR per Quintal',
    `modal_price` DECIMAL(10, 2) NOT NULL COMMENT 'Price in INR per Quintal',
    `source` VARCHAR(50) DEFAULT 'AGMARKNET_API',
    `raw_payload` JSON DEFAULT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY `uniq_mkt_crop_date` (`market_name`, `crop_name`, `arrival_date`),
    INDEX `idx_crop_date` (`crop_name`, `arrival_date`),
    INDEX `idx_district_crop` (`district_name`, `crop_name`),
    INDEX `idx_arrival_date` (`arrival_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Farmers Information
CREATE TABLE IF NOT EXISTS `farmers` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(120) NOT NULL,
    `phone` VARCHAR(20) DEFAULT NULL,
    `location` VARCHAR(150) NOT NULL,
    `district` VARCHAR(100) NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. Search History
CREATE TABLE IF NOT EXISTS `search_history` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `farmer_id` INT DEFAULT NULL,
    `farmer_name` VARCHAR(120) DEFAULT 'Farmer',
    `crop_name` VARCHAR(100) NOT NULL,
    `district_name` VARCHAR(100) NOT NULL,
    `market_name` VARCHAR(100) NOT NULL,
    `quantity_kg` DECIMAL(10, 2) NOT NULL,
    `farmer_location` VARCHAR(150) NOT NULL,
    `search_date` DATE NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`farmer_id`) REFERENCES `farmers`(`id`) ON DELETE SET NULL,
    INDEX `idx_search_date` (`search_date`),
    INDEX `idx_crop` (`crop_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7. Profit Calculations & Best Market Recommendations
CREATE TABLE IF NOT EXISTS `profit_calculations` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `search_id` INT DEFAULT NULL,
    `crop_name` VARCHAR(100) NOT NULL,
    `quantity_kg` DECIMAL(10, 2) NOT NULL,
    `farmer_location` VARCHAR(150) NOT NULL,
    `market_name` VARCHAR(100) NOT NULL,
    `district_name` VARCHAR(100) NOT NULL,
    `modal_price_quintal` DECIMAL(10, 2) NOT NULL,
    `price_per_kg` DECIMAL(10, 2) NOT NULL,
    `selling_value` DECIMAL(12, 2) NOT NULL,
    `distance_km` DECIMAL(8, 2) DEFAULT 0.00,
    `transport_cost` DECIMAL(10, 2) NOT NULL,
    `other_expenses` DECIMAL(10, 2) NOT NULL,
    `net_profit` DECIMAL(12, 2) NOT NULL,
    `is_recommended` TINYINT(1) DEFAULT 0,
    `calculation_date` DATE NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`search_id`) REFERENCES `search_history`(`id`) ON DELETE CASCADE,
    INDEX `idx_crop_calc` (`crop_name`, `calculation_date`),
    INDEX `idx_market_profit` (`market_name`, `net_profit`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 8. API Sync Logs
CREATE TABLE IF NOT EXISTS `api_sync_logs` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `source` VARCHAR(50) DEFAULT 'data.gov.in',
    `status` VARCHAR(20) NOT NULL, -- SUCCESS, FAILED, NO_DATA
    `records_fetched` INT DEFAULT 0,
    `records_inserted` INT DEFAULT 0,
    `records_updated` INT DEFAULT 0,
    `error_message` TEXT DEFAULT NULL,
    `synced_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 9. App Settings / API Key Store
CREATE TABLE IF NOT EXISTS `app_settings` (
    `setting_key` VARCHAR(50) PRIMARY KEY,
    `setting_value` TEXT,
    `description` VARCHAR(255) DEFAULT NULL,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 10. Buyer & Seller Connection Marketplace
CREATE TABLE IF NOT EXISTS `marketplace_listings` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `listing_type` ENUM('SELL', 'BUY') NOT NULL,
    `user_name` VARCHAR(120) NOT NULL,
    `user_phone` VARCHAR(25) NOT NULL,
    `user_role` VARCHAR(50) NOT NULL DEFAULT 'Farmer',
    `district` VARCHAR(100) NOT NULL,
    `location` VARCHAR(150) NOT NULL,
    `crop_name` VARCHAR(100) NOT NULL,
    `variety` VARCHAR(100) DEFAULT 'Standard',
    `quantity_kg` DECIMAL(10, 2) NOT NULL,
    `price_per_kg` DECIMAL(10, 2) NOT NULL,
    `notes` TEXT DEFAULT NULL,
    `status` VARCHAR(20) DEFAULT 'ACTIVE',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_market_crop` (`crop_name`, `district`),
    INDEX `idx_market_type` (`listing_type`, `status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 11. Automatic Price Alerts
CREATE TABLE IF NOT EXISTS `price_alerts` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `farmer_name` VARCHAR(120) NOT NULL,
    `contact` VARCHAR(100) NOT NULL,
    `crop_name` VARCHAR(100) NOT NULL,
    `market_name` VARCHAR(100) NOT NULL,
    `condition_type` ENUM('ABOVE', 'BELOW') NOT NULL,
    `target_price_per_kg` DECIMAL(10, 2) NOT NULL,
    `is_active` TINYINT(1) DEFAULT 1,
    `last_triggered_at` TIMESTAMP NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_alert_crop` (`crop_name`, `market_name`, `is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 12. Farmer Income & Expense Management (Farm Ledger)
CREATE TABLE IF NOT EXISTS `farm_ledger` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `entry_type` ENUM('INCOME', 'EXPENSE') NOT NULL,
    `category` VARCHAR(100) NOT NULL,
    `title` VARCHAR(200) NOT NULL,
    `amount` DECIMAL(12, 2) NOT NULL,
    `crop_name` VARCHAR(100) DEFAULT NULL,
    `entry_date` DATE NOT NULL,
    `notes` TEXT DEFAULT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_ledger_date` (`entry_date`),
    INDEX `idx_ledger_type` (`entry_type`, `category`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 13. AI-Based Crop Price Predictions
CREATE TABLE IF NOT EXISTS `ai_price_forecasts` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `crop_name` VARCHAR(100) NOT NULL,
    `market_name` VARCHAR(100) NOT NULL,
    `forecast_date` DATE NOT NULL,
    `predicted_modal_price` DECIMAL(10, 2) NOT NULL,
    `lower_bound` DECIMAL(10, 2) NOT NULL,
    `upper_bound` DECIMAL(10, 2) NOT NULL,
    `confidence_pct` DECIMAL(5, 2) NOT NULL DEFAULT 92.50,
    `trend_direction` VARCHAR(20) NOT NULL,
    `advisory_action` TEXT DEFAULT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY `uniq_forecast` (`crop_name`, `market_name`, `forecast_date`),
    INDEX `idx_forecast_date` (`forecast_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
