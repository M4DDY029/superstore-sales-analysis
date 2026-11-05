# Superstore Sales Performance Analysis

A beginner-friendly data analyst portfolio project that cleans and analyzes the public Global Superstore dataset, then presents the results in a Jupyter notebook and an interactive Streamlit dashboard.

## Objective

Understand what drives sales and profit across products, customer segments, regions, discounts, and shipping modes. The analysis uses the provided sales and profit units; the source spans multiple markets and does not specify a common currency.

## Business questions answered

1. What are total sales, profit, orders, customers, and overall profit margin?
2. How have sales and profit changed by month and year?
3. Which products generate the most and least profit?
4. Which categories and sub-categories are profitable or loss-making?
5. Which regions and states/provinces perform best or worst?
6. How are discount levels associated with order-line profit?
7. Which customer segments and customers contribute the most sales?
8. How many days does shipping take for each shipping mode?

## Dataset

- **Source:** [Global Superstore on Kaggle](https://www.kaggle.com/datasets/anandaramg/global-superstore)
- **Kaggle handle:** `anandaramg/global-superstore`
- **Original file:** `Global Superstore.txt` (tab-separated, UTF-8)
- **Project raw file:** `data/raw/Superstore.csv` (generated from the original text file)
- **Date range:** 2011–2014
- **Rows and columns:** 51,290 rows and 27 source columns

The raw dataset is excluded from Git because it is a large input file. The cleaned CSV is included so the dashboard works immediately after cloning, including on Streamlit Community Cloud. To recreate the data locally, run the download and cleaning scripts below.

## Tools used

Python, pandas, NumPy, Matplotlib, Seaborn, Plotly, Streamlit, Jupyter, KaggleHub, and openpyxl.

## Project structure

```text
.
├── app.py
├── data
│   ├── raw/                         # Downloaded source data (ignored by Git)
│   └── processed
│       └── superstore_cleaned.csv   # Analysis-ready data used by the app
├── notebooks
│   └── analysis.ipynb
├── src
│   ├── clean_data.py
│   └── download_data.py
├── .gitignore
└── requirements.txt
```

## Setup and run

The steps below use Windows PowerShell and Python 3.11.

### 1. Create and activate the environment

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m ipykernel install --user --name superstore-sales --display-name "Python (Superstore Sales)"
```

If PowerShell blocks activation, allow it for the current terminal only:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 2. Download and clean the dataset

```powershell
python src\download_data.py
python src\clean_data.py
```

The download script uses KaggleHub to fetch the public dataset and converts its tab-separated file into `data/raw/Superstore.csv`. The cleaning script saves `data/processed/superstore_cleaned.csv` and reports its row, duplicate, and missing-value counts.

The cleaner standardizes columns to lowercase snake case, parses order and ship dates, removes duplicate rows, handles missing required and text values, and adds `order_year`, `order_month`, `order_month_name`, `profit_margin`, and `shipping_days`. A profit margin is undefined for the one row with zero sales, so it remains missing rather than being reported as zero.

### 3. Run the analysis notebook

Open `notebooks/analysis.ipynb` in VS Code or Jupyter and select the **Python (Superstore Sales)** kernel. To open JupyterLab from the project folder:

```powershell
jupyter lab notebooks\analysis.ipynb
```

The notebook has been run from top to bottom and contains the analysis, charts, and data-backed insights.

### 4. Run the Streamlit dashboard

```powershell
streamlit run app.py
```

Use the sidebar to filter by year, region, category, and customer segment. The KPIs and charts update to reflect the selected rows.

## Key findings from the real dataset

- **Overall:** 12,642,905 total sales, 1,467,457.29 total profit, 25,035 distinct orders, and 4,873 customers. The weighted profit margin is **11.61%**.
- **Yearly trend:** Sales grew from 2,259,511 in 2011 to 4,300,041 in 2014; profit rose from 248,940.81 to 504,165.97.
- **Products:** Canon imageCLASS 2200 Advanced Copier had the highest product profit at 25,199.93. Cubify CubeX 3D Printer Double Head Print had the lowest at -8,879.97.
- **Category:** Technology led with 663,778.73 profit. Tables was the only loss-making sub-category, at -64,083.39.
- **Region and state/province:** The Central region led at 311,403.98 profit. Istanbul had the largest state/province loss at -29,033.70.
- **Discounts:** Average row-level profit was 61.04 with no discount and -76.07 in the 40%+ bucket (including exactly 40%). The row-level discount-profit correlation was -0.316; this is an association, not proof of causation.
- **Customers:** Consumer customers contributed 6,508,141 sales and 749,239.78 profit. Tom Ashbrook was the top customer by sales at 40,489.
- **Shipping:** Same Day averaged 0.04 elapsed calendar days; Standard Class averaged 5.00 days.

## Recommendations

1. Review pricing, shipping, and cost drivers for Tables and the lowest-profit products before offering additional discounts.
2. Introduce approval thresholds for discounts at or above 40%, and monitor profit per order line as well as sales.
3. Investigate product mix and fulfillment costs in loss-making states/provinces, starting with Istanbul, Lagos, and Texas.

## Dashboard screenshot and live link

- **Dashboard screenshot:** Add a screenshot here after deployment.
- **Streamlit Community Cloud link:** `https://<your-app-name>.streamlit.app`

## Publish to GitHub

1. Create an empty GitHub repository named `superstore-sales-analysis` (do not initialize it with a README or license).
2. From this project folder, add the remote and push:

```powershell
git branch -M main
git remote add origin https://github.com/<YOUR-USERNAME>/superstore-sales-analysis.git
git push -u origin main
```

## Deploy on Streamlit Community Cloud

1. Push the project to GitHub using the commands above.
2. Sign in at [share.streamlit.io](https://share.streamlit.io/) and select **Create app**.
3. Choose the repository, `main` branch, and `app.py` as the main file path.
4. Deploy. Streamlit Cloud installs `requirements.txt`; the cleaned dataset is included in the repository so the app can load it.
5. Copy the generated app URL into the live-link placeholder above.
