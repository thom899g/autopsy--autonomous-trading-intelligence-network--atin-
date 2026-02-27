"""
ATIN Configuration Manager
Handles environment variables with validation and type conversion.
Critical for preventing NameError by ensuring all variables are initialized.
"""
import os
import logging
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

@dataclass
class TradingConfig:
    """Validated trading configuration"""
    symbol: str
    interval_seconds: int
    risk_percentage: float
    
    @classmethod
    def from_env(cls) -> 'TradingConfig':
        """Initialize from environment with defaults"""
        return cls(
            symbol=os.getenv('TRADING_SYMBOL', 'BTC/USDT'),
            interval_seconds=int(os.getenv('CHECK_INTERVAL_SECONDS', '60')),
            risk_percentage=float(os.getenv('RISK_PERCENTAGE', '2.0'))
        )

@dataclass
class LLMConfig:
    """Validated LLM configuration with retry logic"""
    base_url: str
    model: str
    timeout: int
    max_retries: int
    
    @classmethod
    def from_env(cls) -> 'LLMConfig':
        """Initialize from environment with validation"""
        base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        if not base_url.startswith(('http://', 'https://')):
            raise ValueError(f"Invalid OLLAMA_BASE_URL: {base_url}")
            
        return cls(
            base_url=base_url,
            model=os.getenv('OLLAMA_MODEL', 'llama2'),
            timeout=int(os.getenv('OLLAMA_TIMEOUT', '30')),
            max_retries=int(os.getenv('OLLAMA_MAX_RETRIES', '3'))
        )

@dataclass
class AlertConfig:
    """Validated alert configuration"""
    telegram_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> 'AlertConfig':
        """Initialize from environment"""
        return cls(
            telegram_token=os.getenv('TELEGRAM_BOT_TOKEN'),
            telegram_chat_id=os.getenv('TELEGRAM_CHAT_ID')
        )

class Config:
    """Master configuration singleton"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize all configurations"""
        self.trading = TradingConfig.from_env()
        self.llm = LLMConfig.from_env()
        self.alerts = AlertConfig.from_env()
        self.exchange_api_key = os.getenv('EXCHANGE_API_KEY')
        self.exchange_secret = os.getenv('EXCHANGE_SECRET_KEY')
        
        # Validate critical configurations
        if not self.exchange_api_key or not self.exchange_secret:
            logging.warning("Exchange API credentials not found. Running in analysis-only mode.")
    
    @property
    def firebase_credentials_path(self) -> str:
        """Get Firebase credentials path with existence check"""
        path = os.getenv('FIREBASE_CREDENTIALS_PATH', './firebase-credentials.json')
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"Firebase