# YouTube Comments Sentiment Analysis

 ### 1. Data Collection and Dataset Construction

The dataset Kanye West YouTube Comments Sentiment Analysis was created by collecting YouTube comments using the YouTube Data API. This process is handled by the following script:

📄 [00_Python_YouTube_Comments_Scraper.py](https://github.com/spha-code/YouTube-Comments-Sentiment-Analysis-MLOps/blob/main/00_YouTube_Comments_Scraper.py)

This script retrieves comments from selected YouTube videos and formats them for further analysis.

The resulting dataset is available on Kaggle:
Kanye West YouTube Comments Sentiment Analysis

🗃️ https://www.kaggle.com/datasets/sphacode/kanye-west-youtube-comments-sentiment-analysis

-----

 ### 2. Data Preprocessing and EDA (Exported Data Analysis)

 https://github.com/spha-code/YouTube-Comments-Sentiment-Analysis-MLOps/blob/main/02_experiment_1_MLflow_Baseline_Model.ipynb

-----

 ### 3. Starting with a Baseline Model

https://github.com/spha-code/YouTube-Comments-Sentiment-Analysis-MLOps/blob/main/02_MLflow_2_baseline_model.ipynb

-----
 
### 4. Setup MLflow server locally for Experiment Tracking

 
 
### 5. Improve Baseline Model
     - TFIDF
     - Max Feature
     - Handling Imbalanced Data
     - Hyperparameter tuning
     - Multiple Model
     - Stacking Model
       
### 6. ML Pipeline using DVC

     git init, dvc init
     
     - Data Ingestion
     - Data PreProcessing
     - Model Building
     - Model Evaluation with MLflow
     - Model Register in MLflow
       
### 7. Add to Model Registry
### 8. Implement Chrome plugin
### 9. Prepare CI/CD workflow

https://github.com/spha-code/YouTube-Comments-Sentiment-Analysis-MLOps/blob/main/.github/workflows/cicd.yaml
  
### 10. Dockerization
### 11. Deployment - AWS
### 12. Github upload
