import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import ipywidgets as widgets
from IPython.display import display, clear_output
import os
from datetime import datetime

# Function to process CSV files
def process_files(file_list, timestamp_col, date_format=None):
    data_frames = []
    for file in file_list:
        try:
            df = pd.read_csv(file)
            if date_format:
                df[timestamp_col] = pd.to_datetime(df[timestamp_col], format=date_format, errors='coerce')
            else:
                df[timestamp_col] = pd.to_datetime(df[timestamp_col], errors='coerce')
            df = df.dropna(subset=[timestamp_col])
            data_frames.append(df)
        except Exception as e:
            print(f"Error processing file {file}: {str(e)}")
    if not data_frames:
        raise ValueError("No valid data frames were created. Check your input files.")
    combined_df = pd.concat(data_frames, ignore_index=True)
    return combined_df.sort_values(by=timestamp_col)

# Function to create visualizations
def create_visualizations(date, room, room_volume):
    # Lists of file paths and date formats
    room_files = {
        'Room 133': {
            'occupancy_files': [
                ('./resources/CO2_occupancy_data/Room_133/20th_CO2_occupancy_data.csv', '%m/%d/%Y %H:%M'),
                ('./resources/CO2_occupancy_data/Room_133/24th_occupancy_data - Sheet1.csv', '%m-%d-%Y %H:%M:%S'),
                ('./resources/CO2_occupancy_data/Room_133/25th_Co2_occupancy_data - Sheet1.csv', '%m-%d-%Y %H:%M:%S'),
                ('./resources/CO2_occupancy_data/Room_133/26th_Co2_occupancy_data - Sheet1.csv', '%m-%d-%Y %H:%M:%S')
            ],
            'co2_pi1_files': [
                './resources/CO2_data/Room_133/co2_data_24th_pi1.csv',
                './resources/CO2_data/Room_133/co2_data_25th_pi1.csv',
                './resources/CO2_data/Room_133/co2_data_pi1.csv',
                './resources/CO2_data/Room_133/co2_data_26th_pi1.csv'
            ],
            'co2_pi2_files': [
                './resources/CO2_data/Room_133/co2_data_24th_pi2.csv',
                './resources/CO2_data/Room_133/co2_data_25th_pi2.csv',
                './resources/CO2_data/Room_133/co2_data.csv',
                './resources/CO2_data/Room_133/co2_data_26th_pi2.csv'
            ]
        },
        'Room 127': {
            'occupancy_files': [
                # Add the 127 files
                ('./resources/CO2_occupancy_data/Room_127/Rm_127_09th_July_occupancy.csv', '%m-%d-%Y %H:%M:%S'),
                ('./resources/CO2_occupancy_data/Room_127/Rm_127_16th_July_occupancy.csv', '%m-%d-%Y %H:%M:%S'),
                ('./resources/CO2_occupancy_data/Room_127/Rm_127_17th_July_occupancy.csv', '%m-%d-%Y %H:%M:%S')
            ],
            'co2_pi1_files': [
                './resources/CO2_data/Room_127/co2_data_2024-07-09-pi1.csv',
                './resources/CO2_data/Room_127/co2_data_2024-07-16-pi1.csv',
                './resources/CO2_data/Room_127/co2_data_2024-07-17-pi1.csv'
            ],
            'co2_pi2_files': [
                './resources/CO2_data/Room_127/co2_data_2024-07-09-pi2.csv',
                './resources/CO2_data/Room_127/co2_data_2024-07-16-pi2.csv',
                './resources/CO2_data/Room_127/co2_data_2024-07-17-pi2.csv'
            ]
        }
    }

    files = room_files[room]

    # Process occupancy files with their respective date formats
    occupancy_data = []
    for file, fmt in files['occupancy_files']:
        occupancy_data.append(process_files([file], 'Time', fmt))
    occupancy = pd.concat(occupancy_data, ignore_index=True).sort_values(by='Time')

    # Process CO2 files
    co2_pi1 = process_files(files['co2_pi1_files'], 'timestamp')
    co2_pi2 = process_files(files['co2_pi2_files'], 'timestamp')

    # Merge data
    co2_data = pd.merge_asof(co2_pi1, co2_pi2, on='timestamp', suffixes=('_pi1', '_pi2'))
    merged_data = pd.merge_asof(co2_data, occupancy, left_on='timestamp', right_on='Time')

    # Calculate average CO2 and CO2 per volume
    merged_data['co2_avg'] = (merged_data['co2_pi1'] + merged_data['co2_pi2']) / 2
    merged_data['co2_avg_per_volume'] = merged_data['co2_avg'] / room_volume

    # Boxplot of CO2 concentration distribution by occupancy (using all data)
    plt.figure(figsize=(12, 6))
    sns.boxplot(x='count', y='co2_avg_per_volume', data=merged_data)
    plt.ylabel('Average CO2 per Volume (ppm/m^3)')
    plt.xlabel('Occupancy')
    plt.title('CO2 Concentration Distribution by Occupancy')
    plt.tight_layout()
    plt.show()

    # Check if there is data for the selected date
    selected_date = pd.to_datetime(date).date()
    if not any(merged_data['timestamp'].dt.date == selected_date):
        print(f"Selected date is not available: (Room 133) Select either 06/14, 06/24-25, or 06/26. (Room 127) Select either 07/09, 07/16, or 07/17.")
        return

    # Filter for the selected date for heatmap
    filtered_data = merged_data[merged_data['timestamp'].dt.date == selected_date]

    # CO2 Heatmap (for the specified date)
    pivot_data = filtered_data.pivot_table(
        values='co2_avg_per_volume', 
        index=filtered_data['timestamp'].dt.floor('15min').dt.time, 
        columns=filtered_data['timestamp'].dt.hour,
        aggfunc='mean'
    )
    plt.figure(figsize=(12, 8))
    sns.heatmap(pivot_data, cmap='YlOrRd', cbar_kws={'label': 'Average CO2 per Volume (ppm/m^3)'})
    plt.xlabel('Hour of Day')
    plt.ylabel('15-Minute Interval')
    plt.title(f'CO2 Levels Heatmap on {date}')
    plt.tight_layout()
    plt.show()

# Widgets for user input
room_selector = widgets.ToggleButtons(
    options=[('Room 133', 33.6475), ('Room 127', 334.40298596)],
    description='Select Room:',
    layout=widgets.Layout(width='auto', min_width='1000px'),
)
date_picker = widgets.DatePicker(description='Select Date', value=datetime(2024, 6, 24))
generate_button = widgets.Button(description='Generate Graph', button_style='success')
generate_button.style.button_color = '#00539B'
output = widgets.Output()

def display_co2_options():
    generate_button.on_click(on_generate_button_clicked)
    display(room_selector, date_picker, generate_button, output)

def on_generate_button_clicked(b):
    with output:
        output.clear_output()
        selected_room_volume = room_selector.value
        selected_room = room_selector.label
        selected_date = date_picker.value
        if selected_room_volume and selected_date:
            create_visualizations(selected_date.strftime('%Y-%m-%d'), selected_room, selected_room_volume)
        else:
            print("Please select both a room and a date.")

# Display the widgets for user interaction
# display_co2_options()

