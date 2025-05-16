import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import pytz
import json

# Set page config
st.set_page_config(
    page_title="Mood of the Queue",
    layout="centered"
)

EMOJIS = ['🤣', '😊', '😉', '😅', '😭', '🫠']

def init_gsheets():
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    
    # streamline secrets
    creds_dict = dict(st.secrets["gcp_service_account"])
    
    # credentials object
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    
    # open the sheet to verify access
    sheet = client.open("Mood of the Queue").sheet1
    
    # empty data sheet
    if not sheet.get_all_values():
        sheet.append_row(['timestamp', 'mood', 'note'])
        
    return client, sheet

if 'moods' not in st.session_state:
    st.session_state.moods = EMOJIS

def main():
    st.title("Mood of the Queue")
    
    # initialize google sheets
    client, sheet = init_gsheets()
    
    # mood logging
    with st.sidebar:
        st.header("Log a Mood")
        
        # mood selection
        selected_mood = st.radio(
            "Select a mood from below",
            options=EMOJIS,
            horizontal=True
        )
        
        # note input
        note = st.text_area("Add a note (optional)", height=100)
        
        # submit button
        if st.button("Submit Mood"):
            # add timestamp
            pst = pytz.timezone('America/Los_Angeles')
            timestamp = datetime.now(pst).strftime("%Y-%m-%d %H:%M:%S")
            sheet.append_row([timestamp, selected_mood, note])
            st.success("Mood logged successfully")
            st.rerun()
    
    # visualization
    st.header("Mood Distribution")
    
    # extract data
    all_values = sheet.get_all_values()
    
    if len(all_values) <= 1:  # empty
        st.info("No data available yet")
        return
        
    # df to store data
    df = pd.DataFrame(all_values[1:], columns=all_values[0])
    
    # timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
    
    # group by today
    today = pd.Timestamp.now(pytz.timezone('America/Los_Angeles')).date()
    df_today = df[df['timestamp'].dt.date == today]
    
    if not df_today.empty:
        # mood count visualization
        mood_counts = df_today['mood'].value_counts()
        
        plt.figure(figsize=(10, 6))
        bars = plt.bar(mood_counts.index, mood_counts.values)
        plt.title("Mood Distribution Today", fontsize=20, pad=20)
        plt.xlabel("Mood", fontsize=14)
        plt.ylabel("Count", fontsize=14)
        
        # labels
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontsize=12)
        
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.xticks(fontsize=20)
        plt.yticks(fontsize=12)
        
        plt.tight_layout()
        st.pyplot(plt)
        
        # statistics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Entries", len(df_today))
        with col2:
            st.metric("Most Common Mood", mood_counts.index[0])
        
        # recent entries
        st.subheader("Recent Entries")
        recent_entries = df_today.sort_values('timestamp', ascending=False).head(5)
        for _, row in recent_entries.iterrows():
            st.write(f"{row['timestamp'].strftime('%I:%M %p')} - {row['mood']} - {row['note']}")
    else:
        st.info("No moods logged yet!")

if __name__ == "__main__":
    main()
