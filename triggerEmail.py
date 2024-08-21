import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# Set Email credentials
sender_email = "techstar.valuehack@gmail.com"
app_password = "eded azds yemv whlc"  # Use the app-specific password
# Set Supervision email
receiver_email = "sahilgupta.312000@gmail.com"

# Set up the server
smtp_server = "smtp.gmail.com"
port = 587

# Create Email content
subject = "Urgent: Potential Safety Breach Reported at Site"
body = "Dear Security Supervisor, This is an automated email triggered to report potential safety breach that occurred at site on [date and time]."

def getEmailBody():
    # Get the current date and time
    now = datetime.now()
    return "Dear Security Supervisor, This is an automated email triggered to report potential safety breach that occurred at site on "+now.strftime("%Y-%m-%d %H:%M:%S")

def sendEmail():
    # Create the MIME structure
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.attach(MIMEText(getEmailBody(), "plain"))
    try:
        # Connect to the server and send the email
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()  # Upgrade the connection to secure
        server.login(sender_email, app_password)
        server.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        server.quit()