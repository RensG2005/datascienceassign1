#!/usr/bin/env python
# coding: utf-8

# In[3]:


import pandas as pd

import geopandas as gpd
import json
import matplotlib as mpl
import pylab as plt

from bokeh.io import show, output_notebook
from bokeh.models import ColumnDataSource, GeoJSONDataSource, LogColorMapper, LinearColorMapper, ColorBar, HoverTool
from bokeh.palettes import brewer
from bokeh.plotting import figure, show

import panel as pn
import panel.widgets as pnw

import pycountry


# In[4]:

def question4_plot1():
    sales_csv = pd.read_csv(f"./sales_df.csv")
    salesdf = pd.DataFrame(sales_csv)
    countrydf = salesdf.groupby("buyer country")["amount (merchant currency)"].sum().reset_index()
    countrydf.columns = ["country", "total_sales"]

    def get_iso3_code(iso2_code):
        try:
            country = pycountry.countries.get(alpha_2=iso2_code)
            return country.alpha_3 if country else iso2_code
        except AttributeError:
            return iso2_code

    countrydf["country_code"] = countrydf["country"].apply(get_iso3_code)
    countrydf = countrydf[["country_code", "total_sales"]]

    # Load the shapefile
    shapefile = './countriesshapes/ne_110m_admin_0_countries.shp'
    gdf = gpd.read_file(shapefile)[['ADMIN', 'ADM0_A3', 'geometry']]
    gdf.columns = ['country_name', 'country_code', 'geometry']
    gdf = gdf.drop(gdf.index[159])

    # Merge with country sales data
    key = "total_sales"
    merged = gdf.merge(countrydf, left_on="country_code", right_on="country_code", how="left")
    merged[key] = merged[key].fillna(0)  # Fill NaN with 0

    def get_geodatasource(gdf):
        json_data = json.dumps(json.loads(gdf.to_json()))
        return GeoJSONDataSource(geojson=json_data)

    def bokeh_plot_map(gdf, column, title=''):
        geosource = get_geodatasource(gdf)
        palette = brewer['Blues'][9][::-1]
        
        if column not in gdf.columns:
            raise ValueError(f"Column '{column}' not found in the GeoDataFrame")
        
        vals = gdf[column]
        low_val = 0.1 if vals.min() == 0 else vals.min()  # Avoid log(0), use 0.1 as base for zeros
        color_mapper = LogColorMapper(palette=palette, low=low_val, high=vals.max())
        color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8, width=500, height=20,
                            location=(0,0), orientation='horizontal', title="Total Sales (log scale)")
        
        p = figure(title=title, height=400, width=850, tools="hover")
        p.xgrid.grid_line_color = None
        p.ygrid.grid_line_color = None
        
        patches = p.patches('xs', 'ys', source=geosource, fill_alpha=1, line_width=0.5, line_color='black',  
                            fill_color={'field': column, 'transform': color_mapper})
        
        hover = p.select_one(HoverTool)
        hover.tooltips = [("Country", "@country_name"), ("Sales", f"@{column}")]
        
        p.add_layout(color_bar, 'below')
        return p

    output_notebook()
    p = bokeh_plot_map(merged, column=key, title="Map of Total Sales by Country (Log Scale)")
    p.xaxis.visible = False
    p.yaxis.visible = False
    return p


# In[ ]:

def question4_plot2():
    rating_csv = pd.read_csv(f"./statscountrydf.csv")
    rating_df = pd.DataFrame(rating_csv)
    countrydf = rating_df.groupby("country")["total average rating"].mean().reset_index()
    countrydf.columns = ["country", "avg_rating"]

    # Convert two-letter country codes to three-letter ISO A3 codes
    def get_iso3_code(iso2_code):
        try:
            country = pycountry.countries.get(alpha_2=iso2_code)
            return country.alpha_3 if country else iso2_code
        except AttributeError:
            return iso2_code

    countrydf["country_code"] = countrydf["country"].apply(get_iso3_code)
    countrydf = countrydf[["country_code", "avg_rating"]]

    shapefile = './countriesshapes/ne_110m_admin_0_countries.shp'
    gdf = gpd.read_file(shapefile)[['ADMIN', 'ADM0_A3', 'geometry']]
    gdf.columns = ['country_name', 'country_code', 'geometry']
    gdf = gdf.drop(gdf.index[159])  # Assuming this is still needed

    key = "avg_rating"
    merged = gdf.merge(countrydf, left_on="country_code", right_on="country_code", how="left")
    merged[key] = merged[key].fillna(0)  # Fill NaN with 0 for countries with no ratings

    def get_geodatasource(gdf):
        json_data = json.dumps(json.loads(gdf.to_json()))
        return GeoJSONDataSource(geojson=json_data)

    def bokeh_plot_map(gdf, column, title=''):
        geosource = get_geodatasource(gdf)
        palette = brewer['Blues'][9][::-1]
        
        if column not in gdf.columns:
            raise ValueError(f"Column '{column}' not found in the GeoDataFrame")
        
        vals = gdf[column]
        
        low_val = 0.1 if vals.min() == 0 else vals.min()  # Avoid log(0), use 0.1 as base for zeros
        color_mapper = LinearColorMapper(palette=palette, low=low_val, high=vals.max())
        color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8, width=500, height=20,
                            location=(0,0), orientation='horizontal', title="Average Rating")
        
        p = figure(title=title, height=400, width=850, tools='hover')
        p.xgrid.grid_line_color = None
        p.ygrid.grid_line_color = None
        
        p.xaxis.visible = False
        p.yaxis.visible = False
        
        patches = p.patches('xs', 'ys', source=geosource, fill_alpha=1, line_width=0.5, line_color='black',  
                            fill_color={'field': column, 'transform': color_mapper})
        
        
        hover = p.select_one(HoverTool)
        hover.tooltips = [("Country", "@country_name"), ("Avg Rating", f"@{column}")]
        
        p.add_layout(color_bar, 'below')
        return p

    # Create and display the map
    output_notebook()  # If in a Jupyter notebook
    p = bokeh_plot_map(merged, column=key)
    return p

