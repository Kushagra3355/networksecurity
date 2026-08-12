import os
import sys
import pandas as pd
import numpy as np

"""
define common cosntant variables for training pipeline 
"""

TARGET_COLUMN = "Result"
PIPELINE_NAME: str = "NetworkSecurity"
ARTIFACT_DIR: str = "Artifacts"
FILE_NAME: str = "phisingData.csv"

TRAIN_FILE_NAME: str = "train.csv"
TEST_FILE_NAME: str = "test.csv"



"""
    Data Ingestion  realted constants, with DATA_INGESTION VAR name
"""

DATA_INGESTION_COLLECTION_NAME : str = "NetworkData" 
DATA_INGESTION_DATABSE_NAME: str = 'KUSHU'
DATA_INGESTION_DIR_NAME: str = "data_ingestion"
DATA_INGESTION_FEATURE_STORE_NAME: str = "feature_store"
DATA_INGESTION_INGESTED_DIR: str = "ingested"
DATA_INGESTION_TRAIN_TEST_SPLIT_RATION: float = 0.2