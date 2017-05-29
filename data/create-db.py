import sys 
import os
sys.path.insert(0, os.path.abspath(os.path.join(__file__, os.path.pardir, os.path.pardir)))

from data.models import Base, Feature
from data.db import engine


if __name__ == '__main__':
    Base.metadata.create_all(engine)
