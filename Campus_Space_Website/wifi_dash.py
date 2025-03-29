import matplotlib.pyplot as plt
import pandas as pd
import ipywidgets as widgets
from IPython.display import display, HTML
import math
from datetime import datetime

# Widgets for user input
start_date_picker = widgets.DatePicker(description='Start Date', value=datetime(2024, 6, 11))
start_time_picker = widgets.TimePicker(description='Start Time', value=datetime.strptime('10:00', '%H:%M').time())
end_date_picker = widgets.DatePicker(description='End Date', value=datetime(2024, 6, 15))
end_time_picker = widgets.TimePicker(description='End Time', value=datetime.strptime('10:00', '%H:%M').time())
interval_slider = widgets.FloatSlider(description='Interval (hrs)', min=0.25, max=24, step=0.25, value=1)
generate_button = widgets.Button(description='Generate Graph', button_style='success')
generate_button.style.button_color = '#00539B'

output = widgets.Output()

def display_wifi_options():
    generate_button.on_click(on_generate_button_clicked)
    display(start_date_picker, start_time_picker, end_date_picker,
            end_time_picker, interval_slider, generate_button, output)

def generate_predictions(filtered_df, start_datetime, end_datetime, interval):
    interval_timedelta = pd.Timedelta(hours=interval)
    timestamps = pd.date_range(start=start_datetime, end=end_datetime, freq=interval_timedelta)
    
    data = {
        'datetime': [],
        'total_entries_prediction': [],
        'unique_users_prediction': []
    }
    
    for timestamp in timestamps:
        window_start = timestamp - pd.Timedelta(minutes=20)
        window_end = timestamp + pd.Timedelta(minutes=20)
        window_df = filtered_df[(filtered_df['_time'] >= window_start) & (filtered_df['_time'] <= window_end)]
        
        total_entries = len(window_df)
        unique_users = window_df['user'].nunique()
        
        total_entries_prediction = math.floor(total_entries * 0.0347073234431158 + 0.44464825912121597)
        unique_users_prediction = math.floor(unique_users * 0.8437650730600083)
        
        data['datetime'].append(timestamp)
        data['total_entries_prediction'].append(total_entries_prediction)
        data['unique_users_prediction'].append(unique_users_prediction)
    
    prediction_df = pd.DataFrame(data)
    return prediction_df

def display_linear_graph(start_date, start_time, end_date, end_time, interval):
    # Convert input to datetime
    try:
        start_datetime = pd.Timestamp.combine(pd.to_datetime(start_date), start_time)
        end_datetime = pd.Timestamp.combine(pd.to_datetime(end_date), end_time)
    except ValueError:
        with output:
            print("Invalid date or time format. Please use 'YYYY-MM-DD' for date and 'HH:MM' for time.")
        return


    # Make sure that times are formatted correctly
    interval_timedelta = pd.Timedelta(hours=interval)
    if end_datetime <= start_datetime + interval_timedelta:
        with output:
            print("End date and time must be at least one interval after start date and time.")
        return

    if start_datetime < pd.to_datetime('2024-06-11') or end_datetime > pd.to_datetime('2024-07-03'):
        with output:
            print("Error: Date is outside the allowed range of available data. Please select a date between June 11 and July 3.")
        return

    
    # Read the data
    df = pd.read_csv('./resources/june11_july3_bostock.csv')
    df['_time'] = pd.to_datetime(df['_time']).dt.tz_localize(None)
    df = df.sort_values(by='_time')
    
    # Filter DataFrame for entries within the selected time range
    filtered_df = df[(df['_time'] >= start_datetime) & (df['_time'] <= end_datetime)]
    
    if filtered_df.empty:
        with output:
            print("No data available for the selected time range.")
        return
    
    # Generate predictions
    prediction_df = generate_predictions(filtered_df, start_datetime, end_datetime, interval)
    
    # Plot the data
    plt.figure(figsize=(12, 6))
    plt.plot(prediction_df['datetime'], prediction_df['total_entries_prediction'], marker='o', linestyle='-', label='Total Entries Prediction')
    plt.plot(prediction_df['datetime'], prediction_df['unique_users_prediction'], marker='o', linestyle='-', label='Unique Users Prediction')
    plt.xlabel('Time')
    plt.ylabel('Predicted Count')
    plt.title('Predicted People Count Over Time')
    plt.legend()
    plt.grid(True)
    plt.show()
    
    # Display the prediction dataframe
    with output:
        display(HTML(prediction_df.to_html(index=True)))
        
        # Generate CSV file for download
        csv_filename = 'predictions.csv'
        prediction_df.to_csv(csv_filename, index=True)
        
        # Create a download link
        download_link = f'''
            <a href="{csv_filename}" download="{csv_filename}" 
            style="
            display: inline-block;
            padding: 10px 20px;
            font-size: 16px;
            color: #fff;
            background-color: #00539B;
            text-align: center;
            text-decoration: none;
            border-radius: 5px;
            margin-top: 10px;
            ">
            Click here to download the dataset
            </a>
        '''
        display(HTML(download_link))

def on_generate_button_clicked(b):
    with output:
        output.clear_output()
        start_date = start_date_picker.value
        start_time = start_time_picker.value
        end_date = end_date_picker.value
        end_time = end_time_picker.value
        interval = interval_slider.value
        if start_date and start_time and end_date and end_time and interval:
            display_linear_graph(start_date, start_time, end_date, end_time, interval)
        else:
            print("Please select all the required inputs.")

# generate_button.on_click(on_generate_button_clicked)
