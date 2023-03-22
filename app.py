import streamlit as st
import pandas as pd
from datetime import datetime

# Store the CSV file path as a secret
csv_path = st.secrets["csvurl"]


# Load the data from the CSV file into a Pandas DataFrame
df = pd.read_csv(csv_path)

# Setting up download button arguments
download_status = True
csv = ''
file_name = ''

# Preprocessing the DataFrame
df.rename(columns={'Timestamp': 'Time signed'}, inplace=True)
df.rename(columns={'Please enter your TZ number.': 'TZ Number'}, inplace=True)

mandatory_items = ['Breadboard', 'D18B20 (Digital Temperature Sensor)',
       'FireBeetle-ESP32 (MCU)', 'LEDs (small lights)',
       'OLED Display (screen)', 'Plastic Box', 'Resistors Set',
       'SHT3X (Temperature / Humidity Sensor)', 'Thermistor (10K)',
       'USB type-C cable']

def check_admin(user,password):
    if user == st.secrets["adminuser"]:
        if password == st.secrets["password"]:
            download_status = True
            missing_items_but = st.button('Missing Items Per User')
            missing_items_but2 = st.button('Users Per Missing Items')
            
            if missing_items_but: # If the form has been submitted, this block of code is executed.         
                missing_items_per_user(df, mandatory_items)
            if missing_items_but2: # If the form has been submitted, this block of code is executed.    
                users_per_missing_items(df, mandatory_items)
                
def users_per_missing_items(df, mandatory_items):

  def filter_and_check(df):
      # Create an empty dictionary to store filtered DataFrames and sensor values
      filtered_dict = {}
      values_dict = {sensor: [] for sensor in mandatory_items}

      # Iterate over unique email addresses in the DataFrame
      for email in df['Email Address'].unique():
          # Create a filtered DataFrame for each email
          filtered_df = df[df['Email Address'] == email]

          # Add filtered DataFrame to dictionary
          filtered_dict[email] = filtered_df

          # Check which sensor values are not in filtered DataFrame
          for sensor in values_dict:
              if sensor not in filtered_df['Sensor Name / Model Number'].values:
                  # Extract the text before the @ sign
                  username = email.split("@")[0]
                  # Split the username into first and last name
                  first_name = username.split(".")[0].capitalize()
                  last_name = username.split(".")[1].capitalize()

                  values_dict[sensor].append(f'{first_name} {last_name}')

      # Return filtered dictionary and values dictionary
      return filtered_dict, values_dict

  # Call the filter_and_check function to create filtered DataFrames and sensor value lists
  filtered_dict, values_dict = filter_and_check(df)


  # Print sensor value lists
  for sensor, values in values_dict.items():
      st.markdown(f'**{sensor}:**')
      st.text(values)
      st.text('')        

def missing_items_per_user(df, mandatory_items):
  def filter_and_check(df):
      # Create an empty dictionary to store filtered DataFrames and missing items for each email address
      filtered_dict = {}
      missing_items_dict = {}

      # Iterate over unique email addresses in the DataFrame
      for email in df['Email Address'].unique():
          # Create a filtered DataFrame for each email
          filtered_df = df[df['Email Address'] == email]

          # Add filtered DataFrame to dictionary
          filtered_dict[email] = filtered_df

          # Check which sensor values are not in filtered DataFrame
          missing_items = []
          for sensor in mandatory_items:
              if sensor not in filtered_df['Sensor Name / Model Number'].values:
                  missing_items.append(sensor)

          # Add missing items list to dictionary for this email address
          missing_items_dict[email] = missing_items

      # Return filtered dictionary and missing items dictionary
      return filtered_dict, missing_items_dict


  # Call the filter_and_check function to create filtered DataFrames and missing item lists
  filtered_dict, missing_items_dict = filter_and_check(df)

  # Print missing items for each email
  for email, missing_items in missing_items_dict.items():
    if len(missing_items) >0:
      # Extract the text before the @ sign
      username = email.split("@")[0]
      # Split the username into first and last name
      first_name = username.split(".")[0].capitalize()
      last_name = username.split(".")[1].capitalize()


      st.markdown(f'**{first_name} {last_name}:**')
      st.text(missing_items)
      st.text('')



# streamlit app
# Setting up Streamlit page configuration
favicon = 'favicon.png'
st.set_page_config(page_title="AgTech Personal Equipment", page_icon=favicon, layout="centered")
st.title("AgTech Personal Equipment List")
st.markdown('''
            <div style="text-align: justify;">
            Welcome to the AgTech (71252) Personal Equipment List app!\n 
            This handy tool allows you to easily view the sensors and equipment that you have signed up for on the pickup form. 
            Simply enter your email address and Teudat Zehut (TZ) number, and the app will display a list of the items assigned to you.
            Keep track of your assigned equipment throughout the course and ensure that you have everything you need to succeed.  
            Don't forget to write your name and phone number on the equipment box, and remember to return the items at the end of the course.\n 
            Let's get started!
            </div>''', unsafe_allow_html=True)
            
st.markdown('Yedidya @ https://agrotech-lab.github.io')

def load_items (email, tz_number, capitalized_name):
    # Filtering data based on user inputs
    if email and tz_number:
        filtered_df = df[(df["Email Address"] == email) & (df["TZ Number"] == tz_number)]
        filtered_df = filtered_df.reset_index(drop=True)
        filtered_df['Returned'] = filtered_df['Returned'].fillna('No')

        
        if not filtered_df.empty:
            st.markdown(f"**{capitalized_name}, Here's a list of your equipment:**")
            st.dataframe(filtered_df[['Time signed','Sensor Name / Model Number','Quantity', 'Returned']])
        else:
            st.warning(f"{capitalized_name}, No data found for the entered email address and TZ number.")
        return filtered_df

def convert_df(df):
    # Converting filtered data to CSV format
    return df.to_csv(index=False).encode('utf-8')


# Setting up input fields for email address and TZ number
st.markdown("#### Enter your email address and Teudat Zehut (TZ) number:")

with st.form("my_form"):

    email = st.text_input("Email address").strip()
    tz_number = st.number_input("TZ number", value=1)
    name = email.split(".")[0]
    capitalized_name = name.title()
    
    # Every form must have a submit button.
    submitted = st.form_submit_button("Submit")
    if submitted: # If the form has been submitted, this block of code is executed.
        
        filtered_df = load_items (email, tz_number, capitalized_name)  
        csv = convert_df(filtered_df)     
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        download_status = False
        file_name = f'Agtech_Equipment_{capitalized_name}_{timestamp}.csv'

# This line creates a download button that allows the user to download the CSV file.
st.download_button(
   "Download As CSV",
   csv,
   file_name,
   "text/csv",
   key='download-csv',
   disabled=download_status
)

# admin buttons, just if admin and password were inserted
check_admin(email,tz_number)



        



