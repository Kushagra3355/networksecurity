# Network Security: Phishing Data Classification System

## Project Overview

The Network Security Phishing Data Classification System is an enterprise-grade, end-to-end Machine Learning Operations (MLOps) pipeline designed to detect phishing web pages and malicious network activity. The project implements automated data extraction from MongoDB Atlas, schema validation, statistical data drift detection using Kolmogorov-Smirnov tests, feature preprocessing with KNN imputation, hyperparameter optimization across multiple machine learning models, experiment tracking using MLflow and DagsHub, cloud artifact persistence on AWS S3, and RESTful web service API deployment using FastAPI and Docker. Continuous Integration and Continuous Deployment (CI/CD) pipelines are established through GitHub Actions to automate container builds, Amazon ECR repository pushes, and deployment onto Amazon EC2 instances.

---

## Key Features

* **Automated Data ETL & Storage:** Extract raw dataset records from MongoDB Atlas and ingest into local feature stores with automated train-test splitting.
* **Schema Validation & Drift Detection:** Validate feature schema against structured YAML definitions and run two-sample Kolmogorov-Smirnov tests to flag dataset drift between training and testing data splits.
* **Automated Data Transformation:** Handle missing value imputation using KNN Imputer, encode target variables, and save preprocessing pipeline objects.
* **Multi-Model Evaluation & Hyperparameter Tuning:** Train and compare Logistic Regression, Decision Trees, Random Forests, Gradient Boosting, and AdaBoost classifiers using GridSearchCV cross-validation.
* **MLflow & DagsHub Tracking:** Log model metrics (F1 score, precision, recall), hyperparameters, and model binaries to remote MLflow servers hosted on DagsHub.
* **AWS Cloud Synchronization:** Automatically upload training artifacts and model checkpoints to AWS S3 buckets.
* **RESTful FastAPI Service:** Expose endpoints for automated model training (`/train`) and interactive batch prediction via CSV upload (`/predict`) rendering HTML results tables.
* **Docker Containerization:** Package application runtime environment into lightweight Linux Docker images.
* **CI/CD Deployment:** Automate workflow integration, container image creation, Amazon ECR pushing, and Amazon EC2 self-hosted runner deployment via GitHub Actions.

---

## Technology Stack

* **Programming Language:** Python 3.10
* **Web Framework:** FastAPI, Uvicorn, Jinja2 Templates
* **Database Management:** MongoDB Atlas, PyMongo API
* **Data Processing & Machine Learning:** Pandas, NumPy, Scikit-Learn, SciPy
* **Experiment Tracking:** MLflow, DagsHub
* **Cloud Infrastructure:** AWS S3 (Artifact Storage), AWS ECR (Container Registry), AWS EC2 (Hosting Environment)
* **Containerization:** Docker
* **CI/CD Automation:** GitHub Actions
* **Package Packaging:** Setuptools (`setup.py`)

---

## Data Pipeline Architecture

```
+------------------+
| MongoDB Atlas    |
| (NetworkData)    |
+--------+---------+
         |
         v
+------------------+     Export Feature Store
| Data Ingestion   +---------------------------> Train/Test Split (CSV)
+--------+---------+
         |
         v
+------------------+     Validation & Drift Detection
| Data Validation  +---------------------------> Drift Report (YAML)
+--------+---------+                             (KS-2Samp Test)
         |
         v
+------------------+     KNN Imputer & Mapping
| Transformation   +---------------------------> Transformed Arrays (.npy)
+--------+---------+                             Preprocessor (.pkl)
         |
         v
+------------------+     GridSearchCV & Hyperparameter Tuning
| Model Trainer    +---------------------------> MLflow Tracking / DagsHub
+--------+---------+                             Best Model (.pkl)
         |
         v
+------------------+     Cloud Artifact Sync
| AWS S3 & ECR     +---------------------------> S3 Bucket Persistence
+--------+---------+
         |
         v
+------------------+
| FastAPI Server   | <--- Client Request (/predict)
+------------------+
```

---

## Directory Structure

```
network_security_main/
├── .github/
│   └── workflows/
│       └── main.yml               # GitHub Actions CI/CD pipeline configuration
├── data_schema/
│   └── schema.yaml                # Feature schema definitions and data types
├── final_model/
│   ├── model.pkl                  # Serialized best-performing classification model
│   └── preprocessor.pkl           # Serialized preprocessor transformation object
├── Network_Data/
│   └── phisingData.csv            # Raw sample dataset
├── networksecurity/
│   ├── cloud/
│   │   └── s3_syncer.py           # AWS S3 synchronization utility
│   ├── components/
│   │   ├── data_ingestion.py      # MongoDB data extraction and split logic
│   │   ├── data_validation.py     # Schema validation and statistical drift detection
│   │   ├── data_transformation.py # Missing value KNN imputation and preprocessing
│   │   └── model_trainer.py       # Model training, hyperparameter tuning, MLflow logging
│   ├── constant/
│   │   └── training_pipeline/     # Pipeline constants and configurable parameters
│   ├── entity/
│   │   ├── artifact_entity.py     # Data container classes for pipeline artifacts
│   │   └── config_entity.py       # Configuration dataclasses for pipeline modules
│   ├── exception/
│   │   └── exception.py           # Detailed custom exception handling module
│   ├── logging/
│   │   └── logger.py              # Log directory and timestamped logger configuration
│   ├── pipeline/
│   │   ├── batch_prediction.py    # Batch inference logic
│   │   └── training_pipeline.py   # Master pipeline orchestrator controller
│   └── utils/
│       ├── main_utils/
│       │   └── utils.py           # File I/O, YAML reader/writer, model evaluation
│       └── ml_utils/
│           ├── metric/            # Classification evaluation metric estimators
│           └── model/             # Estimator wrapper class (NetworkModel)
├── templates/
│   └── table.html                 # HTML layout template for prediction tabular UI
├── app.py                         # FastAPI RESTful web service implementation
├── Dockerfile                     # Docker build specification
├── main.py                        # Pipeline standalone execution script
├── push_data.py                   # Data loader script for pushing CSV data to MongoDB Atlas
├── requirements.txt               # Dependency library requirements
├── setup.py                       # Packaging setup script
└── test_mongodb.py                # Database connection testing utility
```

---

## Pipeline Components Breakdown

### 1. Data Ingestion (`networksecurity/components/data_ingestion.py`)
* Establishes TLS-secured connections to MongoDB Atlas via PyMongo and `certifi`.
* Queries database `KRISHAI` and collection `NetworkData`.
* Converts raw BSON query results into Pandas DataFrames and drops the default `_id` field.
* Replaces string missing markers (`na`) with `np.nan`.
* Exports raw feature data to `Artifacts/<timestamp>/data_ingestion/feature_store/phisingData.csv`.
* Splits data into 80% training set (`train.csv`) and 20% testing set (`test.csv`).

### 2. Data Validation & Drift Detection (`networksecurity/components/data_validation.py`)
* Validates dataframe columns against the official schema file (`data_schema/schema.yaml`).
* Verifies feature column count consistency.
* Evaluates data drift between training and test sets using the two-sample Kolmogorov-Smirnov test (`ks_2samp`) at a significance threshold of 0.05.
* Generates a YAML drift report (`report.yaml`) detailing column p-values and drift status flags.
* Outputs validated train/test files to `Artifacts/<timestamp>/data_validation/validated/`.

### 3. Data Transformation (`networksecurity/components/data_transformation.py`)
* Separates input features from the target column (`Result`).
* Converts original binary label encodings (-1 and 1) into standard binary values (0 and 1).
* Constructs a transformation pipeline employing `KNNImputer` (3 nearest neighbors) for missing value resolution.
* Fits preprocessor transformations on training features and applies transformations to test features.
* Combines transformed feature vectors with target vectors into NumPy array files (`train.npy` and `test.npy`).
* Saves preprocessor objects to artifact storage and to `final_model/preprocessor.pkl`.

### 4. Model Training & MLflow Tracking (`networksecurity/components/model_trainer.py`)
* Evaluates five machine learning algorithms:
  * Random Forest Classifier
  * Decision Tree Classifier
  * Gradient Boosting Classifier
  * Logistic Regression
  * AdaBoost Classifier
* Conducts hyperparameter tuning via `GridSearchCV` using 3-fold cross-validation.
* Computes metrics including F1 score, Precision, and Recall using `get_classification_score`.
* Logs parameters, evaluation metrics, and model binaries to MLflow hosted on DagsHub.
* Packages best-performing model with its preprocessor into a unified estimator instance (`NetworkModel`).
* Serializes winning model artifacts to `final_model/model.pkl`.

### 5. Training Pipeline Orchestrator (`networksecurity/pipeline/training_pipeline.py`)
* Manages linear execution across Ingestion, Validation, Transformation, and Model Training steps.
* Triggers AWS CLI `s3 sync` operations to push artifacts to `s3://netwworksecurity/artifact/` and `s3://netwworksecurity/final_model/`.

---

## Dataset Features Definition

The dataset evaluates 30 predictive features associated with domain characteristics, network protocols, and page content, targeting the `Result` classification label:

| Feature Name | Data Type | Description |
| :--- | :--- | :--- |
| `having_IP_Address` | Integer | Indicates if an IP address is used in place of a domain name |
| `URL_Length` | Integer | Classification of URL character length |
| `Shortining_Service` | Integer | Detects usage of domain shortening services |
| `having_At_Symbol` | Integer | Checks presence of the '@' symbol in the URL |
| `double_slash_redirecting` | Integer | Identifies redirecting double slashes in URL paths |
| `Prefix_Suffix` | Integer | Evaluates domain prefix/suffix separation using hyphens |
| `having_Sub_Domain` | Integer | Subdomain count assessment |
| `SSLfinal_State` | Integer | SSL/TLS certificate authority trust verification |
| `Domain_registeration_length` | Integer | Domain registration renewal period remaining |
| `Favicon` | Integer | Evaluates whether favicon is loaded from an external domain |
| `port` | Integer | Monitors standard vs non-standard port traffic |
| `HTTPS_token` | Integer | Checks for HTTPS token presence in domain hostnames |
| `Request_URL` | Integer | Percentage of external objects loaded within the webpage |
| `URL_of_Anchor` | Integer | Percentage of anchor links pointing to external domains |
| `Links_in_tags` | Integer | Percentage of links within Meta, Script, or Link elements |
| `SFH` | Integer | Server Form Handler status check |
| `Submitting_to_email` | Integer | Presence of client-side mail submission functions |
| `Abnormal_URL` | Integer | Hostname matching verification against server responses |
| `Redirect` | Integer | Count of HTTP redirect hops |
| `on_mouseover` | Integer | Status bar alteration via mouseover events |
| `RightClick` | Integer | Detection of right-click disabling scripts |
| `popUpWidnow` | Integer | Presence of form input pop-up windows |
| `Iframe` | Integer | Usage of invisible frame elements |
| `age_of_domain` | Integer | Domain registration age check |
| `DNSRecord` | Integer | DNS record availability check |
| `web_traffic` | Integer | Web traffic popularity rank |
| `Page_Rank` | Integer | PageRank score assessment |
| `Google_Index` | Integer | Google search indexing status |
| `Links_pointing_to_page` | Integer | Backlink count analysis |
| `Statistical_report` | Integer | Presence of IP/host on known threat intelligence databases |
| `Result` (Target) | Integer | Classification outcome (1: Legitimate / 0: Phishing) |

---

## FastAPI REST API Specification

The REST API application defined in `app.py` provides execution interfaces for prediction and model training:

### API Endpoints

#### 1. Swagger UI Redirect
* **HTTP Method:** `GET`
* **Route:** `/`
* **Response:** Redirects client to interactive OpenAPI documentation at `/docs`.

#### 2. Trigger Pipeline Execution
* **HTTP Method:** `GET`
* **Route:** `/train`
* **Description:** Instantiates `TrainingPipeline` and executes end-to-end data ingestion, validation, transformation, model training, and cloud synchronization.
* **Response:** Text message confirming successful pipeline completion.

#### 3. Batch Dataset Prediction
* **HTTP Method:** `POST`
* **Route:** `/predict`
* **Content-Type:** `multipart/form-data`
* **Parameters:** `file` (CSV file containing input features matching `schema.yaml`)
* **Description:** Loads preprocessor and model artifacts, generates target predictions, attaches predictions as `predicted_column`, exports `prediction_output/output.csv`, and renders an HTML prediction preview using `templates/table.html`.
* **Response:** HTML output displaying formatted prediction table.

---

## Continuous Integration & Deployment (CI/CD)

Automated build and deployment processes are defined in `.github/workflows/main.yml`:

```
           Push to main Branch
                    |
                    v
       +-------------------------+
       | Continuous Integration  |
       |  - Code Checkout        |
       |  - Linting & Unit Tests |
       +------------+------------+
                    |
                    v
       +-------------------------+
       | Continuous Delivery     |
       |  - AWS Authentication   |
       |  - Docker Image Build   |
       |  - Push Image to ECR    |
       +------------+------------+
                    |
                    v
       +-------------------------+
       | Continuous Deployment   |
       |  - Self-Hosted Runner   |
       |  - Docker Pull & Run    |
       |  - Port 8080 Exposure   |
       +-------------------------+
```

### GitHub Actions Secrets Configuration

Configure the following secrets in GitHub Repository Settings -> Secrets and variables -> Actions:

| Secret Name | Description |
| :--- | :--- |
| `AWS_ACCESS_KEY_ID` | AWS Security Credentials IAM Access Key ID |
| `AWS_SECRET_ACCESS_KEY` | AWS Security Credentials IAM Secret Access Key |
| `AWS_REGION` | AWS Region (e.g., `us-east-1`) |
| `AWS_ECR_LOGIN_URI` | Registry URI (e.g., `788614365622.dkr.ecr.us-east-1.amazonaws.com`) |
| `ECR_REPOSITORY_NAME` | ECR Repository Identifier (`networkssecurity`) |

---

## Installation & Operating Guide

### Prerequisites
* Python 3.10 or higher
* MongoDB Atlas database cluster
* AWS CLI installed and configured (for cloud storage features)
* Docker Desktop / Docker Engine (for container deployments)

### Local Environment Setup

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/your-username/network_security_main.git
   cd network_security_main
   ```

2. **Create and Activate Virtual Environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

4. **Configure Environment Variables:**
   Create a `.env` file in the root directory:
   ```env
   MONGO_DB_URL=mongodb+srv://<username>:<password>@cluster.mongodb.net/?retryWrites=true&w=majority
   MONGODB_URL_KEY=mongodb+srv://<username>:<password>@cluster.mongodb.net/?retryWrites=true&w=majority
   ```

5. **Upload Sample Data to MongoDB:**
   Execute `push_data.py` to convert `Network_Data/phisingData.csv` to JSON format and populate the MongoDB Atlas collection:
   ```bash
   python push_data.py
   ```

6. **Execute Pipeline locally:**
   Run the local execution script to complete ingestion, validation, transformation, and model training:
   ```bash
   python main.py
   ```

7. **Launch API Server:**
   Start the FastAPI service using Uvicorn:
   ```bash
   python app.py
   ```
   Navigate to `http://localhost:8000/docs` in your browser to interact with the API endpoints.

---

## AWS Deployment Guide

### Deployment on Amazon EC2 Instance

1. **Launch EC2 Instance:**
   Launch an Ubuntu Server 22.04 LTS instance on AWS EC2. Configure security group rules to allow inbound traffic on ports `22` (SSH) and `8080` (FastAPI Server).

2. **Install Docker Engine on EC2:**
   Connect to the instance via SSH and run:
   ```bash
   sudo apt-get update -y
   sudo apt-get upgrade -y
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker ubuntu
   newgrp docker
   ```

3. **Set Up Self-Hosted GitHub Runner:**
   Navigate to repository settings in GitHub: Settings -> Actions -> Runners -> New self-hosted runner. Execute the provided runner installation commands on the EC2 server to enable automated deployment via GitHub Actions.

---

## License & Package Metadata

* **Package Name:** NetworkSecurity
* **Version:** 0.0.1
* **Author:** Kushagra Omar
* **Author Email:** kushagra3355@gmail.com
* **License:** Open Source