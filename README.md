# YouTube Comments Sentiment Analysis

 ## 1. Data Collection and Dataset Construction

The dataset was created by collecting YouTube comments using the YouTube Data API. This process is handled by the following script:

📄 00_Python_YouTube_Comments_Scraper.py

This script retrieves comments from selected YouTube videos and formats them for further analysis.

🗃️ The resulting dataset is available on Kaggle:
Kanye West YouTube Comments Sentiment Analysis
https://www.kaggle.com/datasets/sphacode/kanye-west-youtube-comments-sentiment-analysis

-----

 3. Data Preprocessing and EDA (Exported Data Analysis)
 
 4. Build Baseline Model
 
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
       
  9. Add to Model Registry
  10. Implement Chrome plugin
  11. Prepare CI/CD workflow
  12. Dockerization
  13. Deployment - AWS
  14. Github upload
