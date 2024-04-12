import pandas as pd
import datetime as dt
try:
    data_frame = pd.read_csv('filename.csv')
except FileNotFoundError:
    data_frame = pd.DataFrame({'year': [], 'month': [], 'day': [], 'hour': [], 'minute': [], 'second': []})

current_time = dt.datetime.now()
new_row = pd.DataFrame({
    'year': [current_time.year], 
    'month': [current_time.month], 
    'day': [current_time.day], 
    'hour': [current_time.hour], 
    'minute': [current_time.minute], 
    'second': [current_time.second]
})
data_frame = pd.concat([data_frame, new_row], ignore_index=True)
data_frame.to_csv("filename.csv", index=False)
print(data_frame)
