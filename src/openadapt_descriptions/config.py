from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import logging
import yaml

logger = logging.getLogger(__name__)

class ConfigError(Exception):
    """Configuration related errors"""
    pass

@dataclass(frozen=True)  # Make config immutable
class Config:
    """Application configuration.
    
    Attributes:
        output_dir: Directory for saving description files
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        max_events: Maximum number of events to process without confirmation
        max_file_size: Maximum output file size in bytes
        db_timeout: Database operation timeout in seconds
    """
    output_dir: Path = field(default=Path('prompts'))
    log_level: str = field(default='INFO')
    max_events: int = field(default=100)  # Require confirmation above this
    max_file_size: int = field(default=10_000_000)  # 10MB
    db_timeout: int = field(default=60)  # 60 seconds

    def validate(self) -> None:
        """Validate configuration values."""
        if not isinstance(self.output_dir, Path):
            raise ConfigError("output_dir must be a Path object")
        
        if self.log_level not in ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'):
            raise ConfigError(f"Invalid log_level: {self.log_level}")
            
        if self.max_events < 1:
            raise ConfigError("max_events must be positive")
            
        if self.max_file_size < 1:
            raise ConfigError("max_file_size must be positive")
            
        if self.db_timeout < 1:
            raise ConfigError("db_timeout must be positive")

def load_config(config_path: Optional[Path] = None) -> Config:
    """Load configuration from file or use defaults.
    
    Args:
        config_path: Optional path to config file
        
    Returns:
        Validated Config object
        
    Raises:
        ConfigError: If configuration is invalid
    """
    try:
        if config_path and config_path.exists():
            with config_path.open() as f:
                config = yaml.safe_load(f)
                if not isinstance(config, dict):
                    raise ConfigError("Invalid config format")
                
                # Convert output_dir to Path
                config['output_dir'] = Path(config.get('output_dir', 'prompts'))
                
                # Use defaults for missing values
                config.setdefault('log_level', 'INFO')
                config.setdefault('max_events', 100)
                config.setdefault('max_file_size', 10_000_000)
                config.setdefault('db_timeout', 60)
                
                logger.info(f"Using config from {config_path}")
                cfg = Config(**config)
                cfg.validate()
                return cfg
        
        # Use default config if no file provided
        logger.info("Using default configuration")
        return Config()
        
    except yaml.YAMLError as e:
        raise ConfigError(f"Error parsing config file: {e}")
    except Exception as e:
        raise ConfigError(f"Error loading config: {e}") 