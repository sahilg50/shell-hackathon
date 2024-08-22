import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# Set Email credentials
sender_email = "techstar.valuehack@gmail.com"
app_password = "eded azds yemv whlc"  # Use the app-specific password here

# Set Supervision email
receiver_email = "rohit.rajan2@shell.com"

# Set up the server
smtp_server = "smtp.gmail.com"
port = 587

# Create Email content
subject = "Urgent: Potential Safety Breach Reported at Site"

def getEmailBody(date_time, zone, voilation):
    body = f"""
    <html>
    <body>
        Hi,<br><br>
        This is a automated email alert for a safety breach. Please find the details below.<br>
        <b>Date:</b> {date_time.strftime("%d-%m-%Y at %H:%M:%S")} <br>
        <b>Zone Triggered:</b> {zone} <br>
        <b>Violations:</b> {', '.join(map(str,voilation))} <br><br>
        Thank You!<br>
    </body>
    </html>
    """
    return body

def sendEmail(date_time, zone, voilation):
    # Create the MIME structure
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.attach(MIMEText(getEmailBody(date_time, zone, voilation), "html"))
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