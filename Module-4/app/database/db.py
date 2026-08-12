import os
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ----------------------------------
# FIND PROJECT ROOT
# ----------------------------------

CURRENT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

APP_DIR = os.path.dirname(CURRENT_DIR)

MODULE4_DIR = os.path.dirname(APP_DIR)

PROJECT_ROOT = os.path.dirname(MODULE4_DIR)

MODULE1_DIR = os.path.join(
    PROJECT_ROOT,
    "Module-1"
)

# ----------------------------------
# ADD MODULE-1 TO PYTHON PATH
# ----------------------------------

if MODULE1_DIR not in sys.path:
    sys.path.append(MODULE1_DIR)

# ----------------------------------
# IMPORT DATABASE URL
# ----------------------------------

from models.database import DATABASE_URL

# ----------------------------------
# DATABASE ENGINE
# ----------------------------------

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)