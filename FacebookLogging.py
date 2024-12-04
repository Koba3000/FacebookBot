import tkinter as tk
from tkinter import ttk, messagebox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time


def start_bot(username, password, message_text, group_url):
    try:
        # Automatyczne zarządzanie ChromeDriverem
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)

        # Otwórz Facebook
        driver.get("https://www.facebook.com/")
        time.sleep(1)

        # Logowanie
        username_field = driver.find_element(By.ID, "email")
        password_field = driver.find_element(By.ID, "pass")
        username_field.send_keys(username)
        password_field.send_keys(password)

        # Zaloguj się
        password_field.send_keys(Keys.RETURN)
        time.sleep(2)

        print("Zalogowano pomyślnie!")

        # Przejście do grupy
        driver.get(group_url)
        time.sleep(5)

        # Wyciągnięcie ID grupy z URL
        group_id = group_url.split('/')[4]
        print(f"ID grupy: {group_id}")

        # Dynamiczne przewijanie strony
        members_set = set()
        previous_count = 0
        while True:
            members_elements = driver.find_elements(By.XPATH, f"//a[contains(@href, '/groups/{group_id}/user/')]")
            for member in members_elements:
                member_href = member.get_attribute("href")
                if member_href not in members_set:
                    members_set.add(member_href)

            if len(members_set) == previous_count:
                break

            previous_count = len(members_set)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

        print("Znaleziono unikalnych członków grupy.")
        for member_id in list(members_set):
            try:
                driver.get(member_id)
                time.sleep(1)

                message_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Wyślij wiadomość')]"))
                )
                message_button.click()
                time.sleep(1)

                message_box = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@aria-placeholder='Aa']//p"))
                )
                message_box.send_keys(message_text)
                message_box.send_keys(Keys.RETURN)

                close_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Zamknij czat']"))
                )
                close_button.click()

                print(f"Wiadomość wysłana do: {member_id}")
                time.sleep(3)
            except Exception as e:
                print(f"Nie udało się wysłać wiadomości do: {member_id}, błąd: {e}")

        driver.quit()
        messagebox.showinfo("Success", "Bot zakończył pracę pomyślnie!")
    except Exception as e:
        messagebox.showerror("Error", f"Błąd podczas działania bota: {e}")


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
