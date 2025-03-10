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


# In[40]:

def question3_plot2():
       print("hello2")
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
              toolbar_location=None)

       p.line(x='date', y='daily crashes', source=crashsource, legend_label="Crashes", line_width=2, color="blue")
       p.xaxis.major_label_orientation = "vertical"

       p.extra_y_ranges = {"ratings": Range1d(start=.5, end=5.5)}

       p.add_layout(LinearAxis(y_range_name="ratings", axis_label="Ratings"), 'right')

       p.circle(x='date', y='rating', source=ratings_source, legend_label="Mean Daily Ratings", 
              size=8, color="green", alpha=0.7, y_range_name="ratings")

       df_clean = sdf.dropna(subset=['daily average rating'])

       dates_numeric = (df_clean['date'] - df_clean['date'].min()).dt.days

       slope, intercept, r_value, p_value, std_err = stats.linregress(dates_numeric, df_clean['daily average rating'])
       print(f"Slope: {slope}, Intercept: {intercept}, P-value: {p_value}, Std Err: {std_err}")

       regression_line = slope * dates_numeric + intercept
       p.line(df_clean['date'], regression_line, line_width=2, color="red", 
              legend_label="Ratings Trend (Stats)", y_range_name="ratings")

       p.legend.location = "top_left"
       p.legend.click_policy = "hide"

       return p

# p = figure(title="Daily Crashes Over time", x_axis_label='Date', x_axis_type='datetime', y_axis_label="Daily Crashes")
# p.line(x='date', y='daily crashes', source=crashsource, legend_label="Crashes", line_width=2, color="blue")
# p.xaxis.major_label_orientation = "vertical"

# # Add a secondary y-axis for ratings (1 to 5)
# p.extra_y_ranges = {"ratings": Range1d(start=0, end=5.5)}
# p.add_layout(Range1d(start=1, end=5), 'right')
# p.yaxis[1].axis_label = "Ratings"
# # p.line(x='date', y='daily anrs', source=crashsource, legend_label="Crashes", line_width=2)
# # p.line(x='date', y='daily average rating', source=statssource, legend_label="Crashes", line_width=2)
# # p.circle(sdf['date'], sdf['daily average rating']*10, size=10, color="red", alpha=0.5)

# print(reviewdf)
# p.circle(x='date', y='rating', source=reviewdf, legend_label="Review Ratings", 
#          size=8, color="green", alpha=0.7, y_range_name="ratings")
# df_clean = sdf.dropna(subset=['daily average rating'])

# # Convert the dates to numerical values for regression calculation
# dates_numeric = (df_clean['date'] - df_clean['date'].min()).dt.days

# # Perform linear regression on the cleaned data (without NaNs)
# slope, intercept, r_value, p_value, std_err = stats.linregress(dates_numeric, df_clean['daily average rating'])
# print(slope, intercept, p_value, std_err)
# # Generate the regression line for the cleaned data
# regression_line = slope * dates_numeric + intercept
# p.line(df_clean['date'], regression_line, line_width=2, color="red", legend_label="Ratings", y_range_name="ratings")

# show(p)


# In[56]:

def question3_plot1():
       print("hello")
       sales_csv = pd.read_csv(f"./sales_df.csv")
       salesdf = pd.DataFrame(sales_csv)
       crash_csv = pd.read_csv(f"./crashesdf.csv")
       cdf = pd.DataFrame(crash_csv)
       crashsource = ColumnDataSource(cdf)
       salesdf['transaction date'] = pd.to_datetime(salesdf['transaction date'])
       sales_per_date = salesdf.groupby('transaction date')['amount (merchant currency)'].sum().reset_index()
       sales_per_date = sales_per_date.rename(columns={'transaction date': 'date'})

       sales_source = ColumnDataSource(sales_per_date)

       p = figure(title="Daily Crashes and Ratings Over Time",
              x_axis_label='Date',
              x_axis_type='datetime',
              y_axis_label='Daily Crashes',
              toolbar_location=None)

       p.extra_y_ranges = {"Sales": Range1d(start=0, end=sales_per_date["amount (merchant currency)"].max() * 1.1)}
       p.add_layout(LinearAxis(y_range_name="Sales", axis_label="Sales Amount"), 'right')

       dates_numeric = (sales_per_date['date'] - sales_per_date['date'].min()).dt.days
       slope, intercept, r_value, p_value, std_err = stats.linregress(dates_numeric, sales_per_date['amount (merchant currency)'])
       print(f"Slope: {slope}, Intercept: {intercept}, P-value: {p_value}, Std Err: {std_err}")

       regression_line = slope * dates_numeric + intercept

       regression_data = pd.DataFrame({
       'date': sales_per_date['date'],
       'regression': regression_line
       })
       regression_source = ColumnDataSource(regression_data)

       p.line(x='date', y='daily crashes', source=crashsource,
              legend_label="Crashes", line_width=2, color="blue")

       p.line(x='date', y='amount (merchant currency)', source=sales_source,
              legend_label="Sales", line_width=2, color="red", y_range_name="Sales")

       p.line(x='date', y='regression', source=regression_source,
              legend_label="Sales Trend", line_width=2, color="purple", y_range_name="Sales")

       p.xaxis.major_label_orientation = "vertical"
       p.legend.location = "top_left"


       p.legend.click_policy = "hide"

       return p

