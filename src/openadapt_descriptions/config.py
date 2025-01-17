from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import logging
import yaml

logger = logging.getLogger(__name__)

class ConfigError(Exception):
    """Configuration related errors"""
    pass

@dataclass
class Config:
    output_dir: Path
    log_level: str

    def validate(self) -> None:
        """Validate configuration values"""
        if not isinstance(self.output_dir, Path):
            raise ConfigError("output_dir must be a Path object")
        if self.log_level not in ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'):
            raise ConfigError(f"Invalid log level: {self.log_level}")

def load_config(config_path: Optional[Path] = None) -> Config:
    try:
        if config_path and config_path.exists():
            with config_path.open() as f:
                config = yaml.safe_load(f)
                if not isinstance(config, dict):
                    raise ConfigError("Invalid config format")
                config['output_dir'] = Path(config.get('output_dir', 'prompts'))
                logger.info(f"Using config from {config_path}: {config}")
                cfg = Config(**config)
                cfg.validate()
                return cfg
        
        default_config_path = Path(__file__).parent.parent.parent / 'configs' / 'default_config.yaml'
        if default_config_path.exists():
            with default_config_path.open() as f:
                config = yaml.safe_load(f)
                if not isinstance(config, dict):
                    raise ConfigError("Invalid default config format")
                config['output_dir'] = Path(config.get('output_dir', 'prompts'))
                logger.info(f"Using default config: {config}")
                cfg = Config(**config)
                cfg.validate()
                return cfg
        
        logger.info("No config file found, using hardcoded defaults")
        cfg = Config(
            output_dir=Path('prompts'),
            log_level='INFO'
        )
        cfg.validate()
        return cfg
    except yaml.YAMLError as e:
        raise ConfigError(f"Error parsing config file: {e}")
    except Exception as e:
        raise ConfigError(f"Error loading config: {e}") 