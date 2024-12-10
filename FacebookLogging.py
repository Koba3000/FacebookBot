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

# Globalna tablica na credentials
bot_accounts = []

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
                    user_index = member_href.find("/user/")
                    if user_index != -1:
                        cleaned_url = member_href[:member_href.find("/", user_index + 6) + 1]  # Do drugiego slasha włącznie
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




def start_bot(username, password, message_text):
    """Main function to start the bot for a single account."""
    global members_status  # Słownik wyników wysyłania wiadomości
    try:
        # Konfiguracja przeglądarki
        driver = setup_driver()

        # Logowanie do Facebooka
        login(driver, username, password)
        check_authentication(driver)

        all_sent = True
        for member_url, status in members_status.items():
            if not status:  # Wysyłaj tylko do członków, którzy jeszcze nie otrzymali wiadomości
                print(f"Wysyłanie wiadomości do: {member_url}")
                success = send_message_to_member(driver, member_url, message_text)
                members_status[member_url] = success  # Zaktualizuj status
                if not success:
                    all_sent = False
                    break  # Przerwij, jeśli nie udało się wysłać wiadomości

        driver.quit()
        return all_sent  # Zwróć True, jeśli wszystkie wiadomości zostały wysłane
    except Exception as e:
        print(f"Błąd podczas pracy z kontem {username}: {e}")
        return False



def add_account_frame(default_email=None, default_password=None):
    """Dodaje nowe pola do wprowadzania loginu i hasła."""
    new_frame = ttk.Frame(dynamic_accounts_frame)
    new_frame.pack(fill="x", pady=5)

    ttk.Label(new_frame, text="Email:").grid(row=0, column=0, padx=5, pady=5)
    email_entry = ttk.Entry(new_frame, width=30)
    if default_email:
        email_entry.insert(0, default_email)
    email_entry.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(new_frame, text="Password:").grid(row=0, column=2, padx=5, pady=5)
    password_entry = ttk.Entry(new_frame, width=30, show="*")
    if default_password:
        password_entry.insert(0, default_password)
    password_entry.grid(row=0, column=3, padx=5, pady=5)

    def save_account():
        """Zapisuje dane konta do globalnej tablicy."""
        email = email_entry.get()
        password = password_entry.get()
        if email and password:
            bot_accounts.append({'email': email, 'password': password})
            email_entry.config(state="disabled")
            password_entry.config(state="disabled")
            save_button.config(state="disabled")
        else:
            messagebox.showwarning("Błąd", "Wprowadź zarówno email, jak i hasło.")

    save_button = ttk.Button(new_frame, text="Zapisz konto", command=save_account)
    save_button.grid(row=0, column=4, padx=5, pady=5)


# GUI główne
root = tk.Tk()
root.title("Facebook Messenger Bot")

# Domyślne dane logowania
default_username = "example@gmail.com"
default_password = "MySecurePassword"
default_message_text = "Hello, this is a test message."
default_url = "https://www.facebook.com/groups/123456789/people"

# Główna ramka
main_frame = ttk.Frame(root, padding=10)
main_frame.pack(fill="both", expand=True)

# Etykiety i pola tekstowe dla wiadomości i URL
ttk.Label(main_frame, text="Group URL:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
url_entry = ttk.Entry(main_frame, width=60)
url_entry.insert(0, default_url)
url_entry.grid(row=0, column=1, padx=10, pady=5)

ttk.Label(main_frame, text="Message:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
message_entry = ttk.Entry(main_frame, width=60)
message_entry.insert(0, default_message_text)
message_entry.grid(row=1, column=1, padx=10, pady=5)

# Przyciski na górze
buttons_frame = ttk.Frame(main_frame)
buttons_frame.grid(row=2, column=0, columnspan=2, pady=10)

def run_bot():
    """Uruchomienie bota dla wszystkich kont."""
    global members_status
    message_text = message_entry.get()
    group_url = url_entry.get()

    # Pobierz członków grupy tylko raz przy użyciu pierwszego konta
    first_account = bot_accounts[0]
    print(f"Uruchamiam bota dla pierwszego konta: {first_account['email']}")

    driver = setup_driver()
    login(driver, first_account['email'], first_account['password'])
    check_authentication(driver)
    group_id = navigate_to_group(driver, group_url)
    members = fetch_members(driver, group_id)

    # Inicjalizacja statusów wiadomości
    members_status = {member: False for member in members}

    driver.quit()

    # Próbuj wysyłać wiadomości przy użyciu kolejnych kont, aż wszystkie zostaną wysłane
    for account in bot_accounts:
        print(f"Próba wysyłania wiadomości z konta: {account['email']}")
        all_sent = start_bot(account['email'], account['password'], message_text)
        if all_sent:  # Jeśli wszystkie wiadomości zostały wysłane, przerwij pętlę
            print("Wszystkie wiadomości zostały wysłane.")
            break
    else:
        print("Nie udało się wysłać wszystkich wiadomości.")


run_button = ttk.Button(buttons_frame, text="Start Bot", command=run_bot)
run_button.pack(side="left", padx=10)

add_account_button = ttk.Button(buttons_frame, text="Dodaj konto", command=lambda: add_account_frame())
add_account_button.pack(side="left", padx=10)

# Dynamiczne pola na konta
dynamic_accounts_frame = ttk.Frame(main_frame)
dynamic_accounts_frame.grid(row=3, column=0, columnspan=2, pady=20, sticky="nsew")

# Dodaj pierwsze konto z domyślnymi wartościami (nie zapisuje ich automatycznie)
add_account_frame(default_email=default_username, default_password=default_password)

# Uruchomienie GUI
root.mainloop()
