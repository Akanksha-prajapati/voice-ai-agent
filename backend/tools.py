from langchain_core.tools import tool
import sqlite3
import smtplib
from email.message import EmailMessage
import requests

# 1. Database Tool
@tool
def query_database(query: str) -> str:
    """Executes a SQL query on the local SQLite database and returns the result. 
    Use this to fetch records from our 'users' table or insert data.
    Never run destructive queries (drop/delete) without caution.
    Args:
        query: The raw SQL string to execute. (e.g., "INSERT INTO users (name) VALUES ('John')")
    """
    try:
        # Connect to a simple local sqlite file
        conn = sqlite3.connect("local_data.db")
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # If no result or simple string
        if not rows:
            return "No results found or action completed successfully."
            
        result = "\n".join([str(row) for row in rows])
        conn.commit()
        conn.close()
        return result
    except Exception as e:
        return f"Database error: {str(e)}"

# 2. Email Tool
@tool
def send_email(to_address: str, subject: str, message_body: str) -> str:
    """Sends an email to the specified address. Use this when the user asks to email someone."""
    # Simulation block for safety (so we don't accidentally spam without configuring)
    print(f"--- Simulating sending email ---\nTo: {to_address}\nSubject: {subject}\nBody: {message_body}")
    return f"Successfully sent the email to {to_address} (Simulated)"
    
    '''
    # Real sending block - Uncomment and configure to use
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    SENDER_EMAIL = "your_email@gmail.com"
    SENDER_APP_PASSWORD = "your_app_password"
    
    try:
        msg = EmailMessage()
        msg.set_content(message_body)
        msg['Subject'] = subject
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_address
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return f"Successfully sent the email to {to_address}"
    except Exception as e:
        return f"Failed to send email: {str(e)}"
    '''

# 3. Third party API Tool
@tool
def fetch_weather(city: str) -> str:
    """Fetches the current weather for a specific city using a free public API. Use this when the user asks about the weather."""
    try:
        url = f"https://wttr.in/{city}?format=%C+%t"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return f"The weather in {city} is {response.text.strip()}."
        return f"Failed to fetch weather for {city}."
    except Exception as e:
        return f"API Error: {str(e)}"

def get_tools():
    """Returns the list of tools available to the LangChain Agent."""
    return [query_database, send_email, fetch_weather]
