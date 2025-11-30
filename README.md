# Wellness Forever – Customer Segmentation Using RFM Analysis in Python  
Data Analytics | Python | Power BI | Retail Pharmacy

## Project Summary
This project applies Recency–Frequency–Monetary (RFM) analysis to one year of transactional data from Wellness Forever Pharmacy (Apr 2022 – Mar 2023).  
The objective is to segment customers based on purchasing behavior and generate data-driven recommendations to improve retention, loyalty, and revenue.

## Business Problem
Wellness Forever receives a high volume of retail transactions across multiple stores.  
However, the organization lacked a systematic approach to:
- Identify high-value customers  
- Detect customers at risk of churn  
- Personalize marketing strategies  

This project introduces a structured RFM segmentation framework to convert raw transaction data into actionable insights.

## Objectives
- Clean, preprocess, and standardize raw POS data  
- Compute customer-level RFM metrics  
- Build RFM scoring and segmentation rules  
- Develop insights and recommendations based on customer behavior  

## Dataset Overview
**Source:** Internal POS/ERP system export (Excel workbook with monthly sheets)

**Record counts:**
- Total raw records: ~250,000  
- Records after data cleaning: ~227,000  
- Valid customers after mobile validation: ~30,000  

Invalid mobile numbers, duplicate records, and missing values were removed during preprocessing.

## Technology Stack
- Python  
- Pandas, NumPy  
- Jupyter Notebook  
- Power BI  
- Excel  

## Approach
- Combined 12 monthly transaction sheets into a unified dataset and performed comprehensive preprocessing, including handling missing values and removing invalid or duplicate records.  
- Transformed line-level POS data into invoice-level aggregates to ensure accurate computation of customer-level metrics.  
- Calculated Recency, Frequency, and Monetary indicators for each customer and applied quintile-based scoring to construct the RFM model.  
- Implemented a rule-based segmentation framework to classify customers into behavioral groups such as Champions, Loyal, At Risk, Lost, New, and Promising.

## What I Delivered
- A fully cleaned and standardized customer dataset suitable for analytics and business decision-making.  
- An end-to-end Python pipeline for RFM analysis, including data cleaning, invoice aggregation, scoring, and customer segmentation.  
- A final RFM output file and an executive summary outlining key insights and recommended strategic actions.  
- A Power BI dashboard providing an interactive view of customer segments, RFM distributions, and segment-level performance.

## Visual Overview

### Customer Count by Segment

![Customer Count by RFM Segment](images/segment_counts_improved.png)

### Recency Distribution

![Distribution of Recency](images/recency_improved.png)

### Frequency vs Monetary by Segment

![Frequency vs Monetary by Segment](images/freq_monetary_improved.png)

