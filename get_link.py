from pyngrok import ngrok
import time

# Open a tunnel to port 8502 (Streamlit)
print("Starting ngrok tunnel...")
public_url = ngrok.connect(8502)
print("\n" + "="*50)
print("YOUR PUBLIC LINK IS READY!")
print("="*50)
print(f"\nShare this link with your friend:\n\n   {public_url}\n")
print("="*50)
print("\nKeep this window open -- closing it will stop the link.")
print("Press Ctrl+C to stop.\n")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    ngrok.disconnect(public_url)
    print("\nTunnel closed.")
