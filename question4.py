#!/usr/bin/env python
# coding: utf-8

# In[3]:


import pandas as pd

import geopandas as gpd
import json

from bokeh.io import output_notebook
from bokeh.models import ColumnDataSource, GeoJSONDataSource, LogColorMapper, LinearColorMapper, ColorBar, HoverTool, LabelSet,  NumeralTickFormatter,HoverTool
from bokeh.palettes import brewer
from bokeh.plotting import figure
from bokeh.layouts import row

import pycountry

def get_country_name(iso2_code):
        try:
            country = pycountry.countries.get(alpha_2=iso2_code)
            return country.name if country else iso2_code
        except AttributeError:
            return iso2_code

def question4_plot1():
    sales_csv = pd.read_csv(f"./sales_df.csv")
    salesdf = pd.DataFrame(sales_csv)
    countrydf = salesdf.groupby("buyer country")["amount (merchant currency)"].sum().reset_index()
    countrydf.columns = ["country", "total_sales"]

    countrydf["country_code"] = countrydf["country"].apply(get_country_name)
    countrydf = countrydf[["country_code", "total_sales"]]

    shapefile = "./countriesshapes/ne_110m_admin_0_countries.shp"
    gdf = gpd.read_file(shapefile)[["ADMIN", "ADM0_A3", "geometry"]]
    gdf.columns = ["country_name", "country_code", "geometry"]
    gdf = gdf.drop(gdf.index[159])

    key = "total_sales"
    merged = gdf.merge(countrydf, left_on="country_code", right_on="country_code", how="left")
    merged[key] = merged[key].fillna(0)

    def get_geodatasource(gdf):
        json_data = json.dumps(json.loads(gdf.to_json()))
        return GeoJSONDataSource(geojson=json_data)

    def bokeh_plot_map(gdf, column, title=""):
        geosource = get_geodatasource(gdf)
        palette = brewer["Blues"][9][::-1]
        
        vals = gdf[column]
        low_val = 0.1 if vals.min() == 0 else vals.min()
        color_mapper = LogColorMapper(palette=palette, low=low_val, high=vals.max())
        color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8, width=500, height=20,
                            location=(0,0), orientation="horizontal", title="Total Sales (log scale)")
        
        p = figure(title=title, height=400, width=850, tools="hover")
        p.xgrid.grid_line_color = None
        p.ygrid.grid_line_color = None
        
        patches = p.patches("xs", "ys", source=geosource, fill_alpha=1, line_width=0.5, line_color="black",  
                            fill_color={"field": column, "transform": color_mapper})
        
        hover = p.select_one(HoverTool)
        hover.tooltips = [("Country", "@country_name"), ("Sales", f"@{column}")]
        
        p.add_layout(color_bar, "below")
        return p

    output_notebook()
    p = bokeh_plot_map(merged, column=key, title="Map of Total Sales by Country (Log Scale)")
    p.xaxis.visible = False
    p.yaxis.visible = False
    return p

def question4_plot2():
    rating_csv = pd.read_csv(f"./statscountrydf.csv")
    rating_df = pd.DataFrame(rating_csv)
    countrydf = rating_df.groupby("country")["total average rating"].mean().reset_index()
    countrydf.columns = ["country", "avg_rating"]

    countrydf["country_code"] = countrydf["country"].apply(get_country_name)
    countrydf = countrydf[["country_code", "avg_rating"]]

    shapefile = "./countriesshapes/ne_110m_admin_0_countries.shp"
    gdf = gpd.read_file(shapefile)[["ADMIN", "ADM0_A3", "geometry"]]
    gdf.columns = ["country_name", "country_code", "geometry"]
    gdf = gdf.drop(gdf.index[159])

    key = "avg_rating"
    merged = gdf.merge(countrydf, left_on="country_code", right_on="country_code", how="left")
    merged[key] = merged[key].fillna(0)

    def get_geodatasource(gdf):
        json_data = json.dumps(json.loads(gdf.to_json()))
        return GeoJSONDataSource(geojson=json_data)

    def bokeh_plot_map(gdf, column, title=""):
        geosource = get_geodatasource(gdf)
        palette = brewer["Blues"][9][::-1]
        vals = gdf[column]
        
        low_val = 0.1 if vals.min() == 0 else vals.min()
        color_mapper = LinearColorMapper(palette=palette, low=low_val, high=vals.max())
        color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8, width=500, height=20,
                            location=(0,0), orientation="horizontal", title="Average Rating")
        
        p = figure(title=title, height=400, width=850, tools="hover")
        p.xgrid.grid_line_color = None
        p.ygrid.grid_line_color = None
        
        p.xaxis.visible = False
        p.yaxis.visible = False
        
        patches = p.patches("xs", "ys", source=geosource, fill_alpha=1, line_width=0.5, line_color="black",  
                            fill_color={"field": column, "transform": color_mapper})
        
        
        hover = p.select_one(HoverTool)
        hover.tooltips = [("Country", "@country_name"), ("Avg Rating", f"@{column}")]
        
        p.add_layout(color_bar, "below")
        return p
    p = bokeh_plot_map(merged, column=key)
    return p
def question4_plot3():
    sales_csv = pd.read_csv("./sales_df.csv")
    salesdf = pd.DataFrame(sales_csv)
    country_sales = salesdf.groupby("buyer country")["amount (merchant currency)"].sum().reset_index()
    country_sales.columns = ["country", "total_sales"]
    rating_csv = pd.read_csv("./statscountrydf.csv")
    rating_df = pd.DataFrame(rating_csv)
    country_ratings = rating_df.groupby("country")["total average rating"].mean().reset_index()
    country_ratings.columns = ["country", "avg_rating"]
    
    country_sales["country_name"] = country_sales["country"].apply(get_country_name)
    country_ratings["country_name"] = country_ratings["country"].apply(get_country_name)
    
    country_sales = country_sales[country_sales["total_sales"] > 0]
    country_ratings = country_ratings[country_ratings["avg_rating"] > 0]
    
    top_sales = country_sales.nlargest(5, "total_sales")
    
    bottom_ratings = country_ratings.nsmallest(5, "avg_rating")
    
    top_sales["category"] = "Top 5 Sales"
    top_sales["color"] = "#4682B4"
    
    bottom_ratings["category"] = "Bottom 5 Ratings"
    bottom_ratings["color"] = "#FFA500"    

    
    sales_source = ColumnDataSource(data=dict(
        countries=list(top_sales["country_name"]),
        sales=top_sales["total_sales"],
        category=top_sales["category"],
        color=top_sales["color"]
    ))
    
    ratings_source = ColumnDataSource(data=dict(
        countries=list(bottom_ratings["country_name"]),
        ratings=bottom_ratings["avg_rating"],
        category=bottom_ratings["category"],
        color=bottom_ratings["color"]
    ))
    p_sales = figure(
        width=850,
        height=500,
        title="Top 5 Countries by Sales",
        x_range=sales_source.data["countries"],
        toolbar_location=None,
        tools="hover"
    )
    
    hover_sales = p_sales.select(dict(type=HoverTool))
    hover_sales.tooltips = [
        ("Country", "@countries"),
        ("Sales", "@sales{0,0}")
    ]
    
    bars_sales = p_sales.vbar(
        x="countries",
        top="sales",
        width=0.7,
        source=sales_source,
        line_color=None,
        fill_color="color"
    )
    
    labels_sales = LabelSet(
        x="countries",
        y="sales",
        text="sales",
        text_font_size="9pt",
        text_color="black",
        text_align="center",
        text_baseline="bottom",
        source=sales_source,
        x_offset=0,
        y_offset=5,
    )
    p_sales.add_layout(labels_sales)
    
    p_sales.xaxis.major_label_orientation = 45
    p_sales.xgrid.grid_line_color = None
    p_sales.y_range.start = 0
    p_sales.yaxis.formatter = NumeralTickFormatter(format="0,0")
    p_sales.yaxis.axis_label = "Total Sales"
    p_sales.title.text_font_size = "14pt"
    
    p_ratings = figure(
        width=850,
        height=500,
        title="Bottom 5 Countries by Average Rating",
        x_range=ratings_source.data["countries"],
        toolbar_location=None,
        tools="hover"
    )
    
    hover_ratings = p_ratings.select(dict(type=HoverTool))
    hover_ratings.tooltips = [
        ("Country", "@countries"),
        ("Rating", "@ratings{0.00}")
    ]
    
    bars_ratings = p_ratings.vbar(
        x="countries",
        top="ratings",
        width=0.7,
        source=ratings_source,
        line_color=None,
        fill_color="color"
    )
    
    labels_ratings = LabelSet(
        x="countries",
        y="ratings",
        text="ratings",
        text_font_size="9pt",
        text_color="black",
        text_align="center",
        text_baseline="bottom",
        source=ratings_source,
        x_offset=0,
        y_offset=5,
    )
    p_ratings.add_layout(labels_ratings)
    p_ratings.xaxis.major_label_orientation = 45
    p_ratings.xgrid.grid_line_color = None
    p_ratings.y_range.start = 0
    p_ratings.yaxis.formatter = NumeralTickFormatter(format="0.00")
    p_ratings.yaxis.axis_label = "Average Rating"
    layout = row(p_sales, p_ratings)
    
    return layout