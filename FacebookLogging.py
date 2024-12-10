import tkinter as tk
from tkinter import ttk, messagebox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

import time


def validate_input(username, password, group_url):
    """Validate user input."""
    if not username or not password or not group_url:
        raise ValueError("Wszystkie pola (email, hasło, URL grupy) muszą być wypełnione.")

    if "facebook.com/groups/" not in group_url:
        raise ValueError("Podany URL grupy jest nieprawidłowy. Upewnij się, że jest to URL do grupy na Facebooku.")


def setup_driver():
    """Set up and return a configured WebDriver instance."""
    chrome_options = Options()
    chrome_options.add_argument("--disable-notifications")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

def login(driver, username, password):
    """Login to Facebook."""
    try:
        driver.get("https://www.facebook.com/")
        time.sleep(1)
    except Exception as e:
        raise RuntimeError(f"Nie udało się otworzyć strony Facebooka: {e}")

    # Logowanie
    username_field = driver.find_element(By.ID, "email")
    password_field = driver.find_element(By.ID, "pass")
    username_field.send_keys(username)
    password_field.send_keys(password)

    # Zaloguj się
    password_field.send_keys(Keys.RETURN)
    time.sleep(3)

    if "login" in driver.current_url:
        raise RuntimeError("Nie udało się zalogować. Sprawdź poprawność danych logowania.")

def check_authentication(driver):
    """Check if authentication is required."""
    if "authentication" in driver.current_url:
        print("Weryfikacja wykryta. Zamrażanie bota na minutę...")
        time.sleep(60)

def navigate_to_group(driver, group_url):
    # Przejście do grupy
    try:
        driver.get(group_url)
        time.sleep(3)
    except Exception as e:
        raise RuntimeError(f"Nie udało się otworzyć URL grupy: {e}")

    # Wyciągnięcie ID grupy z URL
    try:
        group_id = group_url.split('/')[4]
    except IndexError:
        raise ValueError("Nie udało się wyciągnąć ID grupy z podanego URL.")

    print(f"ID grupy: {group_id}")

    # Przejście do zakładki z listą osób w grupie
    try:
        members_tab_url = f"https://www.facebook.com/groups/{group_id}/members/"
        driver.get(members_tab_url)
        time.sleep(5)
        print(f"Przeszedł do zakładki z członkami grupy: {members_tab_url}")

    except Exception as e:
        raise RuntimeError(f"Nie udało się przejść do zakładki członków grupy: {e}")

    return group_id

def fetch_members(driver, group_id):
    # Dynamiczne przewijanie strony
    members_set = set()
    previous_count = 0
    scroll_attempts = 0  # Licznik przewinięć bez nowych członków
    max_scroll_attempts = 5  # Maksymalna liczba prób przewinięcia bez znalezienia nowych członków

    while scroll_attempts < max_scroll_attempts:
        try:
            members_elements = driver.find_elements(By.XPATH, f"//a[contains(@href, '/groups/{group_id}/user/')]")
            for member in members_elements:
                member_href = member.get_attribute("href")
                if member_href not in members_set:
                    # Usunięcie dodatkowych parametrów w URL
                    cleaned_url = member_href.split('?')[0]
                    members_set.add(cleaned_url)

            # Sprawdzenie, czy liczba unikalnych członków wzrosła
            if len(members_set) == previous_count:
                scroll_attempts += 1  # Zwiększ licznik przewinięć bez nowych członków
            else:
                scroll_attempts = 0  # Resetuj licznik, jeśli dodano nowych członków

            previous_count = len(members_set)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)
        except Exception as e:
            print(f"Błąd podczas przewijania strony lub pobierania członków: {e}")
            break

    print(f"Znaleziono unikalnych członków grupy: {len(members_set)}.")

    return members_set

def send_message_to_member(driver, member_url, message_text):
    """Send a message to a single group member."""
    driver.get(member_url)
    time.sleep(1)
    try:
        message_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Wyślij wiadomość')]"))
        )
        message_button.click()
        message_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@aria-placeholder='Aa']//p"))
        )
        message_box.send_keys(message_text)
        message_box.send_keys(Keys.RETURN)
        close_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Zamknij czat']"))
        )
        close_button.click()
        print(f"Wiadomość wysłana do: {member_url}")
        return True  # Wiadomość została wysłana
    except Exception as e:
        print(f"Nie udało się wysłać wiadomości do: {member_url}. Błąd: {e}")
        return False # Wiadomość nie została wysłana




def start_bot(username, password, message_text, group_url):
    """Main function to start the bot."""
    try:
        # Weryfikacja danych wejściowych
        validate_input(username, password, group_url)

        # Konfiguracja przeglądarki
        driver = setup_driver()

        # Logowanie do Facebooka
        login(driver, username, password)

        # Sprawdzenie dwuetapowej weryfikacji
        check_authentication(driver)

        # Przejście do grupy i pobranie ID grupy
        group_id = navigate_to_group(driver, group_url)

        # Pobranie członków grupy
        members = fetch_members(driver, group_id)

        # Słownik do przechowywania wyników wysyłania wiadomości
        members_status = {}

        print(f"\nRozpoczynam wysyłanie wiadomości do {len(members)} członków...")

        # Iteracja po członkach grupy i wysyłanie wiadomości
        for member_url in members:
            members_status[member_url] = send_message_to_member(driver, member_url, message_text)  # Klucz: URL, Wartość: True/False

        # Wyświetlenie podsumowania
        print("\nPodsumowanie wysyłania wiadomości:")
        for member_url, status in members_status.items():
            print(f"{member_url}: {'Wysłano' if status else 'Nie wysłano'}")

        # Zamknięcie przeglądarki
        driver.quit()

        print("\nBot zakończył pracę pomyślnie.")
        return members_status  # Zwrócenie słownika wyników
    except Exception as e:
        print(f"Błąd: {e}")



# Tworzenie GUI
root = tk.Tk()
root.title("Facebook Messenger Bot")

# Domyślne credentiale

default_username = "example@gmail.com"
default_password = "MySecurePassword"
default_message_text = "Hello, this is a test message."
default_url = "https://www.facebook.com/groups/123456789/people"

# Etykiety i pola tekstowe
ttk.Label(root, text="Email:").grid(row=0, column=0, padx=10, pady=5)
email_entry = ttk.Entry(root, width=40)
email_entry.insert(0, default_username)
email_entry.grid(row=0, column=1, padx=10, pady=5)

ttk.Label(root, text="Password:").grid(row=1, column=0, padx=10, pady=5)
password_entry = ttk.Entry(root, width=40, show="*")
password_entry.insert(0, default_password)
password_entry.grid(row=1, column=1, padx=10, pady=5)

ttk.Label(root, text="Message:").grid(row=2, column=0, padx=10, pady=5)
message_entry = ttk.Entry(root, width=40)
message_entry.insert(0, default_message_text)
message_entry.grid(row=2, column=1, padx=10, pady=5)

ttk.Label(root, text="Group URL:").grid(row=3, column=0, padx=10, pady=5)
url_entry = ttk.Entry(root, width=40)
url_entry.insert(0, default_url)
url_entry.grid(row=3, column=1, padx=10, pady=5)


# Przycisk do uruchamiania bota
def run_bot():
    email = email_entry.get()
    password = password_entry.get()
    message = message_entry.get()
    group_url = url_entry.get()
    start_bot(email, password, message, group_url)


run_button = ttk.Button(root, text="Start Bot", command=run_bot)
run_button.grid(row=4, column=0, columnspan=2, pady=20)

# Uruchomienie GUI
root.mainloop()
