import numpy as np
import pandas as pd
import datetime as dt
import geopandas
import bokeh
import json
from bokeh.models import CustomJS, ColumnDataSource, Button, FactorRange, Tabs, TabPanel, HoverTool, CheckboxGroup, CDSView, GroupFilter
from bokeh.palettes import Blues
from bokeh.plotting import figure, show
from bokeh.layouts import column, gridplot
from bokeh.models.ranges import FactorRange
from bokeh.transform import factor_cmap,dodge
from bokeh.colors import RGB

from datetime import timedelta

from bokeh.layouts import column

def question1_1():
    #importing the dataframe
    df = pd.read_csv("./sales_df.csv")
    df['transaction date'] = pd.to_datetime(df['transaction date'])#make this column a datetime column
    df.rename(columns={ df.columns[0]: "index" }, inplace = True)
    df = df.set_index("index")
    #month relevant data
    month_map = {
        "Jun": 6,"Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
    }
    months = list(month_map.keys())
    daily_data = {#days of each relevant month
        "Jun": [str(i) for i in range(1, 31)],
        "Jul": [str(i) for i in range(1, 32)],
        "Aug": [str(i) for i in range(1, 32)],
        "Sep": [str(i) for i in range(1, 31)],
        "Oct": [str(i) for i in range(1, 32)],
        "Nov": [str(i) for i in range(1, 31)],
        "Dec": [str(i) for i in range(1, 32)]
    }
    #day relevant data
    days_map = {
        "Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5,
        "Sun": 6
    }
    days = list(days_map.keys())

    #the initial plot can use dictionary input: we will process that here
    #first plot with sale amounts:
    daily_sales_amounts = {}#will contain for every month a list of length days of that month, all daily values
    monthly_sums_amounts = []#will contain the bar data we need later
    #second plot with sales volumes:
    daily_sales_volumes = {}#will contain for every month a list of length days of that months, all daily volumes
    monthly_sums_volumes = []#will contain the bar data we need later
    for month in months:
        #the entire dataframe for just this month:
        month_df = df.loc[df['transaction date'].dt.month == month_map[month]]

        #month bar data for first plot:
        monthly_sums_amounts.append(month_df['amount (merchant currency)'].sum())#sum the series to get that months total
        #month bar data for second plot:
        monthly_sums_volumes.append(len(month_df))

        #now for the daily values of both plots:
        day_list_amounts = []
        day_list_volumes = []
        for i in daily_data[month]:
            day_list_amounts.append(sum(month_df.loc[month_df['transaction date'].dt.day==int(i)]['amount (merchant currency)']))#plot 1
            day_list_volumes.append(len(month_df.loc[month_df['transaction date'].dt.day==int(i)]))#plot 2
        #now we need the daily values as a list to append to the daily values dictionary
        daily_sales_amounts[month] = day_list_amounts#plot 1
        daily_sales_volumes[month] = day_list_volumes#plot 2
    
    #The customJS script unfortunately can't process dictionaries. So we have to make a flattend list and 
    #get the data through smart indexing
    all_days = [] #flat days of month list
    all_values_sales = []#flat amounts list for first plot
    all_values_volumes = []#flat amounts list for second plot
    month_indices = {}  #start & end indices for each month

    #now we do the same process above, but now with flat lists
    current_index = 0
    for month in months:
        days = daily_data[month]
        sales_values = daily_sales_amounts[month]
        sales_volumes = daily_sales_volumes[month]
        month_indices[month] = (current_index, current_index + len(days))  # Store index range
        all_days.extend(days)
        all_values_sales.extend(sales_values)
        all_values_volumes.extend(sales_volumes)
        current_index += len(days)  # Update starting index for next month

    #We convert lists to JSON for JavaScript
    all_days_json = json.dumps(all_days)
    month_indices_json = json.dumps(month_indices)  # Will be parsed into an object
    #now we need the values for the two plots:
    all_values_sales_json = json.dumps(all_values_sales)#first plot
    all_values_volumes_json = json.dumps(all_values_volumes)#second plot

    # Bokeh data source for the main plot
    cds = ColumnDataSource(data={"x": months, "y": monthly_sums_amounts})

    fig1 = figure(x_range=FactorRange(*months), height=400, title="Monthly Sales Data, click on bar to get daily info", tools="tap", toolbar_location=None)
    fig1.vbar(x="x", top="y", width=0.5, source=cds)

    button1 = Button(label="Back to Month Overview", button_type="success", visible=False)

    fig1.yaxis.axis_label = "euros"
    # Pass this max value to the JavaScript callback
    callback = CustomJS(args=dict(source=cds, p=fig1, button=button1,
                                all_days_json=all_days_json,
                                all_values_json=all_values_sales_json,
                                month_indices_json=month_indices_json),
                        code="""
        var selected = source.selected.indices[0]; 
        if (selected === undefined) return;

        // Parse JSON data into arrays
        var all_days = JSON.parse(all_days_json);
        var all_values = JSON.parse(all_values_json);
        var month_indices = JSON.parse(month_indices_json);

        var month = source.data['x'][selected];

        if (!(month in month_indices)) return;

        var start_idx = month_indices[month][0];
        var end_idx = month_indices[month][1];

        var days = all_days.slice(start_idx, end_idx);
        var values = all_values.slice(start_idx, end_idx);

        source.data['x'] = days;
        source.data['y'] = values;
        source.change.emit();

        // Update x-axis dynamically
        p.x_range.factors = days;
        p.title.text = "Daily Sales Data of " + month;

        source.selected.indices = [];
        button.visible = true;
    """)
    # JavaScript for resetting the plot to monthly view
    reset_callback = CustomJS(args=dict(source=cds, p=fig1, button=button1, 
                                        months=months, monthly_sums=monthly_sums_amounts), 
                            code="""
        // Restore the original monthly data
        source.data['x'] = months;  // Use the months list directly
        source.data['y'] = monthly_sums;  // Use the original monthly sums
        source.change.emit();
        // Reset x-axis to show months
        p.x_range.factors = months;
        // Reset title
        p.title.text = "Monthly Sales Data, click on bar to get daily info";
        // Deselect any selected bars
        source.selected.indices = [];
        // Hide back button again
        button.visible = false;
    """)
    # Attach the callback to the button
    button1.js_on_event("button_click", reset_callback)
    cds.selected.js_on_change('indices', callback)

    # Bokeh data source for the main plot
    cds = ColumnDataSource(data={"x": months, "y": monthly_sums_volumes})

    fig2 = figure(x_range=FactorRange(*months), height=400, title="Monthly Sale amounts, click on bar to get daily info", tools="tap", toolbar_location=None)
    fig2.vbar(x="x", top="y", width=0.5, source=cds)

    button2 = Button(label="Back to Month Overview", button_type="success", visible=False)
    # Find the global max for daily values
    global_max_y = max(all_values_volumes) * 1.1  # Add 10% buffer for visual clarity

    fig2.yaxis.axis_label = "amount of sales"
    # Pass this max value to the JavaScript callback
    callback = CustomJS(args=dict(source=cds, p=fig2, button=button2,
                                all_days_json=all_days_json,
                                all_values_json=all_values_volumes_json,
                                month_indices_json=month_indices_json,
                                global_max_y=global_max_y),
                        code="""
        var selected = source.selected.indices[0]; 
        if (selected === undefined) return;

        // Parse JSON data into arrays
        var all_days = JSON.parse(all_days_json);
        var all_values = JSON.parse(all_values_json);
        var month_indices = JSON.parse(month_indices_json);

        var month = source.data['x'][selected];

        if (!(month in month_indices)) return;

        var start_idx = month_indices[month][0];
        var end_idx = month_indices[month][1];

        var days = all_days.slice(start_idx, end_idx);
        var values = all_values.slice(start_idx, end_idx);

        source.data['x'] = days;
        source.data['y'] = values;
        source.change.emit();

        // Set consistent y-axis range
        p.y_range.start = 0;
        p.y_range.end = global_max_y;  
        p.change.emit();
        
        // Update x-axis dynamically
        p.x_range.factors = days;
        p.title.text = "Daily Sale amounts of " + month;

        source.selected.indices = [];
        button.visible = true;
    """)
    # JavaScript for resetting the plot to monthly view
    reset_callback = CustomJS(args=dict(source=cds, p=fig2, button=button2, 
                                        months=months, monthly_sums=monthly_sums_volumes), 
                            code="""
        // Restore the original monthly data
        source.data['x'] = months;  // Use the months list directly
        source.data['y'] = monthly_sums;  // Use the original monthly sums
        source.change.emit();
        // Reset x-axis to show months
        p.x_range.factors = months;
        // Reset title
        p.title.text = "Monthly Sale amounts, click on bar to get daily info";
        // Deselect any selected bars
        source.selected.indices = [];
        // Hide back button again
        button.visible = false;
    """)

    # Attach the callback to the button
    button2.js_on_event("button_click", reset_callback)

    cds.selected.js_on_change('indices', callback)

    # Assume fig1 and fig2 are created following your original logic
    panel1 = TabPanel(child=column(button1, fig1),title="Sales Volume (euros)")
    panel2 = TabPanel(child=column(button2, fig2),title="Sales Volume (amounts)")

    tabs = Tabs(tabs=[panel1, panel2])

    return(tabs)

def question2_1():
    #importing the dataframe
    df = pd.read_csv("./sales_df.csv")
    df['transaction date'] = pd.to_datetime(df['transaction date'])#make this column a datetime column
    df.rename(columns={ df.columns[0]: "index" }, inplace = True)
    df = df.set_index("index")

    #month relevant data
    month_map = {
        "Jun": 6,"Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
    }
    months = list(month_map.keys())
    daily_data = {#days of each relevant month
        "Jun": [str(i) for i in range(1, 31)],
        "Jul": [str(i) for i in range(1, 32)],
        "Aug": [str(i) for i in range(1, 32)],
        "Sep": [str(i) for i in range(1, 31)],
        "Oct": [str(i) for i in range(1, 32)],
        "Nov": [str(i) for i in range(1, 31)],
        "Dec": [str(i) for i in range(1, 32)]
    }

    #day relevant data
    days_map = {
        "Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5,
        "Sun": 6
    }
    days = list(days_map.keys())
    #we will do the month loop again to keep things clear (a bit inefficient but it doesn't take long)
    monthly_sums = []
    #the initial plot can use dictionary input: we will process that here
    daily_values_premium = {}
    daily_values_unlock = {}
    for month in months:
        #get all the dates of this month 
        month_values = df.loc[df['transaction date'].dt.month == month_map[month]]
        #get values for premium and unlock separately
        prem_values = month_values.loc[month_values['sku id'] == "premium"]
        unlock_values = month_values.loc[month_values['sku id'] == "unlockcharactermanager"]
        #now we iterate over the days and append the length of a series of only that day
        prem_day_value_list = []
        unlock_day_value_list = []
        for i in daily_data[month]:
            prem_day_value_list.append(len(prem_values.loc[prem_values['transaction date'].dt.day==int(i)]))
            unlock_day_value_list.append(len(unlock_values.loc[unlock_values['transaction date'].dt.day==int(i)]))
        #now we need the daily values as a list to append to the daily values dictionary
        daily_values_premium[month] = prem_day_value_list
        daily_values_unlock[month] = unlock_day_value_list

    #now we have a dictionary with all the daily values. Now we need to combine this with an x-axis that's
    #all the dates between the start and end of our data set
    flat_daily_values_premium = [value for month in months for value in daily_values_premium[month]] #will be our y-axis
    flat_daily_values_unlock = [value for month in months for value in daily_values_unlock[month]] #will be our y-axis
    dates_list = [df['transaction date'][0] + timedelta(days=i) for i in range(len(flat_daily_values_premium))]#we can choose 1 of the 2

    # Create a figure with a datetime type x-axis
    fig = figure(title='Cumulative sales volume of premium and character unlock',
                height=400, width=700,
                x_axis_label='Day Number', y_axis_label='Cumulative sales amount',
                toolbar_location=None)

    # The cumulative sum will be a trend line
    fig.line(x=dates_list, y=np.cumsum(flat_daily_values_premium),
            color='gray', line_width=2,legend_label="Premium Sales")
    fig.line(x=dates_list, y=np.cumsum(flat_daily_values_unlock),
            color='#E6E6FA', line_width=2,legend_label="Unlock Sales")

    #We add a legend
    fig.legend.title = "Sales Type"
    fig.legend.location = "top_left"
    return(fig)

def question2_2():
    #importing the dataframe
    df = pd.read_csv("./sales_df.csv")
    df['transaction date'] = pd.to_datetime(df['transaction date'])#make this column a datetime column
    df.rename(columns={ df.columns[0]: "index" }, inplace = True)
    df = df.set_index("index")
    #make a new column with the date of the week, we need this in part 2
    df['day of week'] = df['transaction date'].dt.weekday #monday is 0

    #month relevant data
    month_map = {
        "Jun": 6,"Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
    }
    months = list(month_map.keys())
    daily_data = {#days of each relevant month
        "Jun": [str(i) for i in range(1, 31)],
        "Jul": [str(i) for i in range(1, 32)],
        "Aug": [str(i) for i in range(1, 32)],
        "Sep": [str(i) for i in range(1, 31)],
        "Oct": [str(i) for i in range(1, 32)],
        "Nov": [str(i) for i in range(1, 31)],
        "Dec": [str(i) for i in range(1, 32)]
    }

    #day relevant data
    days_map = {
        "Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5,
        "Sun": 6
    }
    days = list(days_map.keys())
    #we will do the month loop again to keep things clear (a bit inefficient but it doesn't take long)
    monthly_sums = []
    #first, we need to get a list of average amount of sales per weekday
    days_sales_volume_total = {}
    days_sales_volume_premium = {}
    days_sales_volume_unlock = {}
    for day in days_map.keys():
        #get the mean amount of sales for that day
        day_df = df.loc[df['day of week'] == days_map[day]]
        total_sales_vol = len(day_df)
        premium_sales_vol = len(day_df.loc[day_df['sku id'] == "premium"])
        unlock_sales_vol = len(day_df.loc[day_df['sku id'] == "unlockcharactermanager"])
        days_sales_volume_total[day] = total_sales_vol/7 #average over all week days
        days_sales_volume_premium[day] = premium_sales_vol/7 #average over all week days
        days_sales_volume_unlock[day] = unlock_sales_vol/7 #average over all week days
    
    ###################TOTAL FIGURE###############

    # Extract x and y values from the dictionary
    x_values = list(days_sales_volume_total.keys())  # ["Mon", "Tue", ...]
    y_values = list(days_sales_volume_total.values())  # Corresponding sales amounts

    # Create a Bokeh data source
    source = ColumnDataSource(data=dict(days=x_values, sales=y_values))

    # Create a figure
    fig1 = figure(title='Average Sales Volume per Weekday',
                height=400, width=700,
                x_axis_label='Day of Week', y_axis_label='Sales Volume',
                x_range=x_values,  # Ensure correct categorical axis
                toolbar_location=None)

    # Add bars to the figure
    fig1.vbar(x='days', top='sales', width=0.5, source=source, 
            fill_color=factor_cmap('days', palette="Blues7", factors=x_values))
    
    ##############PREMIUM+UNLOCK FIGURE################
    # Extract x-axis labels (weekdays)
    x_values = list(days_sales_volume_premium.keys())  # ["Mon", "Tue", "Wed", ...]

    # Extract y-axis values (sales volume) for both categories
    premium_sales = list(days_sales_volume_premium.values())
    unlock_sales = list(days_sales_volume_unlock.values())

    # Create a Bokeh data source
    source = ColumnDataSource(data=dict(days=x_values, premium=premium_sales, unlock=unlock_sales))

    # Create figure
    fig2 = figure(title='Average Sales Volume per Weekday (Premium vs Unlock)',
                height=400, width=700,
                x_axis_label='Day of Week', y_axis_label='Sales Volume',
                x_range=x_values,  # Ensures categorical axis
                toolbar_location=None)

    # Bar width and dodge distance
    bar_width = 0.4  # Adjust width for better spacing
    dodge_dist = 0.2  # Moves one bar left and the other right

    # Add bars for Premium Sales
    fig2.vbar(x=dodge('days', -dodge_dist, range=fig2.x_range), 
            top='premium', width=bar_width, source=source, 
            color="royalblue", legend_label="Premium Sales")

    # Add bars for Unlock Sales
    fig2.vbar(x=dodge('days', dodge_dist, range=fig2.x_range), 
            top='unlock', width=bar_width, source=source, 
            color=RGB(12,12,12), legend_label="Unlock Sales")

    # Customize legend
    fig2.legend.title = "Sales Type"
    fig2.legend.location = "top_left"
    # Configure the gridplot
    gridplotje = gridplot([[fig1],[fig2]],toolbar_location=None)
    return [fig1, fig2]
    # return(gridplotje)