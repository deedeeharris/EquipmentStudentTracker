import streamlit as st
import pandas as pd
from datetime import datetime

# Store the CSV file path as a secret
csv_path = st.secrets["csvurl"]

# Load the data from the CSV file into a Pandas DataFrame
df = pd.read_csv(csv_path)

# download button args
download_status = True
csv = ''
file_name = ''

# preprocessing
df.rename(columns={'Timestamp': 'Time signed'}, inplace=True)
df.rename(columns={'Please enter your TZ number.': 'TZ Number'}, inplace=True)



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
   return df.to_csv(index=False).encode('utf-8')


#col1, col2, col3 = st.columns(3)
#with col1:
st.markdown("#### Enter your email address and Teudat Zehut (TZ) number:")

with st.form("my_form"):

    email = st.text_input("Email address").strip()
    tz_number = st.number_input("TZ number", value=1)
    name = email.split(".")[0]
    capitalized_name = name.title()
    
    # Every form must have a submit button.
    submitted = st.form_submit_button("Submit")
    if submitted:
        filtered_df = load_items (email, tz_number, capitalized_name)  
        
        csv = convert_df(filtered_df)     
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        download_status = False
        file_name = f'Agtech_Equipment_{capitalized_name}_{timestamp}.csv'

# download csv button
st.download_button(
   "Download As CSV",
   csv,
   file_name,
   "text/csv",
   key='download-csv',
   disabled=download_status
)


        



