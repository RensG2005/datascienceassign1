#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import datetime as dt
from bokeh.plotting import figure, show
from bokeh.io import output_notebook
from bokeh.models import ColumnDataSource, Range1d, LinearAxis
from bokeh.models import Range1d
from scipy import stats
from bokeh.colors import RGB


# In[40]:

def question3_plot2():
       crash_csv = pd.read_csv(f"./crashesdf.csv")
       stats_csv = pd.read_csv(f"./statsoverviewdf.csv")
       review_csv = pd.read_csv(f"./reviewdf.csv")

       output_notebook()
       cdf = pd.DataFrame(crash_csv)
       sdf = pd.DataFrame(stats_csv)
       reviewdf = pd.DataFrame(review_csv)
       cdf['date'] = pd.to_datetime(cdf['date'])
       sdf['date'] = pd.to_datetime(sdf['date'])
       reviewdf['date'] = pd.to_datetime(reviewdf['date'])


       crashsource = ColumnDataSource(cdf)
       statssource = ColumnDataSource(sdf)
       mean_ratings_per_day = reviewdf.groupby('date')['rating'].mean().reset_index()
       ratings_source = ColumnDataSource(mean_ratings_per_day) 


       p = figure(title="Daily Crashes and Ratings Over Time", 
              x_axis_label='Date', 
              x_axis_type='datetime', 
              y_axis_label='Daily Crashes',
              width=750,
              toolbar_location=None)

       p.line(x='date', y='daily crashes', source=crashsource, legend_label="Crashes", line_width=2, color=RGB(173, 216, 230))
       p.xaxis.major_label_orientation = "vertical"

       p.extra_y_ranges = {"ratings": Range1d(start=.5, end=5.5)}

       p.add_layout(LinearAxis(y_range_name="ratings", axis_label="Ratings"), 'right')

       p.circle(x='date', y='rating', source=ratings_source, legend_label="Mean Daily Ratings", 
              size=8, color=RGB(250,150,0), alpha=0.7, y_range_name="ratings")

       df_clean = sdf.dropna(subset=['daily average rating'])

       dates_numeric = (df_clean['date'] - df_clean['date'].min()).dt.days

       merged_df = pd.merge(cdf, df_clean, on='date', how='inner')
       correlation = np.corrcoef(merged_df["daily crashes"], merged_df["daily average rating"])[0, 1]
       print(f"Correlation between crashes and sales: {correlation:.4f}")

       slope, intercept, r_value, p_value, std_err = stats.linregress(dates_numeric, df_clean['daily average rating'])

       regression_line = slope * dates_numeric + intercept
       p.line(df_clean['date'], regression_line, line_width=2, color="orange", 
              legend_label="Ratings Trend", y_range_name="ratings")

       p.legend.location = "top_left"
       p.legend.click_policy = "hide"

       return p

def question3_plot1():
    sales_csv = pd.read_csv(f"./sales_df.csv")
    salesdf = pd.DataFrame(sales_csv)
    crash_csv = pd.read_csv(f"./crashesdf.csv")
    cdf = pd.DataFrame(crash_csv)
    cdf['date'] = pd.to_datetime(cdf['date'])
    
    print("Crash dataframe columns:", cdf.columns.tolist())
    
    crashsource = ColumnDataSource(cdf)
    
    salesdf['transaction date'] = pd.to_datetime(salesdf['transaction date'])
    sales_per_date = salesdf.groupby('transaction date')['amount (merchant currency)'].sum().reset_index()
    sales_per_date = sales_per_date.rename(columns={'transaction date': 'date'})
    sales_per_date['sales_diff'] = sales_per_date['amount (merchant currency)'].diff()
    sales_source = ColumnDataSource(sales_per_date)
    
    merged_df = pd.merge(cdf, sales_per_date, on='date', how='inner')

    correlation = np.corrcoef(merged_df["daily crashes"], merged_df["amount (merchant currency)"])[0, 1]
    print(f"Correlation between crashes and sales: {correlation:.4f}")


    p = figure(title="Daily Crashes and Sales Over Time",
              x_axis_label='Date',
              x_axis_type='datetime',
              y_axis_label='Daily Crashes',
              width=750,
              toolbar_location=None)
    
    p.extra_y_ranges = {"Sales": Range1d(start=0, end=sales_per_date["amount (merchant currency)"].max() * 1.1)}
    p.add_layout(LinearAxis(y_range_name="Sales", axis_label="Sales Amount"), 'right')
    
    dates_numeric = (sales_per_date['date'] - sales_per_date['date'].min()).dt.days
    slope, intercept, r_value, p_value, std_err = stats.linregress(dates_numeric, sales_per_date['amount (merchant currency)'])
    regression_line = slope * dates_numeric + intercept
    regression_data = pd.DataFrame({
        'date': sales_per_date['date'],
        'regression': regression_line
    })
    regression_source = ColumnDataSource(regression_data)
    
    crash_column = 'daily crashes'
    if crash_column not in cdf.columns:
        crash_column = cdf.columns[1]
        print(f"Using '{crash_column}' as crash column")
        
    p.line(x='date', y=crash_column, source=crashsource,
          legend_label="Crashes", line_width=2, color=RGB(173, 216, 230))
    
    p.line(x='date', y='amount (merchant currency)', source=sales_source,
          legend_label="Sales", line_width=2, color=RGB(255, 200, 150), y_range_name="Sales")
    
    p.line(x='date', y='regression', source=regression_source,
          legend_label="Sales Trend", line_width=2, color="orange", y_range_name="Sales")
    
    p.xaxis.major_label_orientation = "vertical"
    p.legend.location = "top_left"
    p.legend.click_policy = "hide"
    
    return p