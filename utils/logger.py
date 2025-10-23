import logging
import os
from datetime import datetime

# Setup logger
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"assistant_{datetime.now().strftime('%Y%m%d')}.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def log_step(step_name: str, details: str):
    """Log a specific step for debugging."""
    logger.info(f"[STEP: {step_name}] {details}")