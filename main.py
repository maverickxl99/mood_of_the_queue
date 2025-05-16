import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import plotly.express as px
from datetime import datetime
import pytz
import json

# Set page config
st.set_page_config(
    page_title="Mood of the Queue",
    page_icon="😊",
    layout="centered"
)

# Initialize Google Sheets connection
def init_gsheets():
    try:
        # Get credentials from Streamlit secrets
        creds_dict = st.secrets["gcp_service_account"]
        
        # Create credentials object
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        # Try to open the sheet to verify access
        sheet = client.open("Mood of the Queue").sheet1
        
        # Initialize headers if sheet is empty
        if not sheet.get_all_values():
            sheet.append_row(['timestamp', 'mood', 'note'])
            
        return client, sheet
    except Exception as e:
        st.error(f"Error connecting to Google Sheets: {str(e)}")
        st.stop()

# Initialize session state
if 'moods' not in st.session_state:
    st.session_state.moods = {
        '😊': 'Happy',
        '😠': 'Frustrated',
        '😕': 'Confused',
        '🎉': 'Excited'
    }

# Main app
def main():
    st.title("Mood of the Queue")
    
    try:
        # Initialize Google Sheets
        client, sheet = init_gsheets()
        
        # Sidebar for mood logging
        with st.sidebar:
            st.header("Log a Mood")
            
            # Mood selection
            selected_mood = st.radio(
                "How's the queue feeling?",
                options=list(st.session_state.moods.keys()),
                horizontal=True
            )
            
            # Note input
            note = st.text_area("Add a note (optional)", height=100)
            
            # Submit button
            if st.button("Submit Mood"):
                # Get current timestamp in PST
                pst = pytz.timezone('America/Los_Angeles')
                timestamp = datetime.now(pst).strftime("%Y-%m-%d %H:%M:%S")
                
                # Append to Google Sheet
                sheet.append_row([timestamp, selected_mood, note])
                st.success("Mood logged successfully!")
                st.rerun()
        
        # Main content area for visualization
        st.header("Today's Mood Distribution")
        
        try:
            # Get data from Google Sheet
            all_values = sheet.get_all_values()
            
            if len(all_values) <= 1:  # Only header row or empty
                st.info("No data available yet!")
                return
                
            # Create DataFrame with explicit column names
            df = pd.DataFrame(all_values[1:], columns=all_values[0])
            
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
            
            # Filter for today's entries
            today = pd.Timestamp.now(pytz.timezone('America/Los_Angeles')).date()
            df_today = df[df['timestamp'].dt.date == today]
            
            if not df_today.empty:
                # Create mood count visualization
                mood_counts = df_today['mood'].value_counts()
                
                # Create a more visually appealing bar chart
                fig = px.bar(
                    x=mood_counts.index,
                    y=mood_counts.values,
                    labels={'x': 'Mood', 'y': 'Count'},
                    title="Mood Distribution Today",
                    color=mood_counts.index,  # Color bars by mood
                    color_discrete_sequence=px.colors.qualitative.Set3,  # Use a nice color palette
                    text=mood_counts.values,  # Show count on bars
                )
                
                # Update layout for better appearance
                fig.update_layout(
                    showlegend=False,
                    plot_bgcolor='white',
                    title_x=0.5,  # Center the title
                    title_font_size=24,
                    xaxis_title_font_size=16,
                    yaxis_title_font_size=16,
                    margin=dict(t=50, l=50, r=50, b=50),
                )
                
                # Update traces for better bar appearance
                fig.update_traces(
                    textposition='outside',
                    textfont_size=14,
                    marker_line_color='rgb(8,48,107)',
                    marker_line_width=1.5,
                    opacity=0.8
                )
                
                # Show the chart
                st.plotly_chart(fig, use_container_width=True)
                
                # Show mood statistics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Entries", len(df_today))
                with col2:
                    st.metric("Most Common Mood", mood_counts.index[0])
                with col3:
                    st.metric("Unique Moods", len(mood_counts))
                
                # Show recent entries
                st.subheader("Recent Entries")
                recent_entries = df_today.sort_values('timestamp', ascending=False).head(5)
                for _, row in recent_entries.iterrows():
                    st.write(f"{row['timestamp'].strftime('%I:%M %p')} - {row['mood']} - {row['note']}")
            else:
                st.info("No moods logged today yet!")
                
        except Exception as e:
            st.error(f"Error processing data: {str(e)}")
            st.write("Debug - Raw data from sheet:")
            st.write(all_values)
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.info("Please make sure you have the correct Google Sheets credentials and the sheet is properly set up.")

if __name__ == "__main__":
    main()
