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
 
 5. Setup MLflow server locally for Experiment Tracking

 
 
 6. Improve Baseline Model
     - TFIDF
     - Max Feature
     - Handling Imbalanced Data
     - Hyperparameter tuning
     - Multiple Model
     - Stacking Model
       
  7. ML Pipeline using DVC

     git init, dvc init
     
     - Data Ingestion
     - Data PreProcessing
     - Model Building
     - Model Evaluation with MLflow
     - Model Register in MLflow
       
  8. Add to Model Registry
  9. Implement Chrome plugin
  10. Prepare CI/CD workflow
  11. Dockerization
  12. Deployment - AWS
  13. Github upload
