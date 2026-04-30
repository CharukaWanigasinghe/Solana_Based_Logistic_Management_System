"""
Application configuration with Solana blockchain integration
"""

import os
import logging
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class Config:
    """Base application configuration"""

    # Application
    APP_NAME = "Solana Logistics Management System"
    APP_VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"

    # Server
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))

    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./logistics.db")

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    loggers = [
        logging.getLogger("app"),
        logging.getLogger("blockchain"),
        logging.getLogger("solana")
    ]

    # CORS
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

    # ============================================
    # Blockchain Configuration
    # ============================================

    # Use blockchain for operations
    USE_BLOCKCHAIN = os.getenv("USE_BLOCKCHAIN", "true").lower() == "true"

    # Blockchain Features
    BLOCKCHAIN_GPS_TRACKING = os.getenv("BLOCKCHAIN_GPS_TRACKING", "true").lower() == "true"
    BLOCKCHAIN_DELIVERY_CONFIRMATION = os.getenv("BLOCKCHAIN_DELIVERY_CONFIRMATION", "true").lower() == "true"
    BLOCKCHAIN_OWNERSHIP_TRANSFER = os.getenv("BLOCKCHAIN_OWNERSHIP_TRANSFER", "true").lower() == "true"

    @classmethod
    def init_logging(cls):
        """Initialize logging configuration"""
        log_level = getattr(logging, cls.LOG_LEVEL.upper(), logging.INFO)

        # Configure root logger
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Configure specific loggers
        for logger in cls.loggers:
            logger.setLevel(log_level)


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = "WARNING"
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",")


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    DATABASE_URL = "sqlite:///:memory:"
    TESTING = True
    LOG_LEVEL = "DEBUG"


# Get configuration based on environment
ENV = os.getenv("ENVIRONMENT", "development").lower()

if ENV == "production":
    config = ProductionConfig()
elif ENV == "testing":
    config = TestingConfig()
else:
    config = DevelopmentConfig()

# Initialize logging
config.init_logging()