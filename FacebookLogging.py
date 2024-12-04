from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Dane wejściowe dla programu
message_text = "Strach i presja, idzie Bestia!"
group_url = "https://www.facebook.com/groups/1096010835465202/people"

# Ścieżka do WebDrivera
driver_path = r"C:\webdriver\chromedriver.exe"
service = Service(driver_path)
driver = webdriver.Chrome(service=service)

# Otwórz Facebook
driver.get("https://www.facebook.com/")
time.sleep(2)

# Logowanie
username = driver.find_element(By.ID, "email")
password = driver.find_element(By.ID, "pass")

username.send_keys("login")
password.send_keys("pass")  # Zamień na swoje prawdziwe hasło

# Zaloguj się
password.send_keys(Keys.RETURN)
time.sleep(5)  # Poczekaj na załadowanie strony

print("Zalogowano pomyślnie!")

# Przejście do grupy
driver.get(group_url)
time.sleep(7)  # Poczekaj na załadowanie

# Przewijanie strony, aby załadować więcej członków
for _ in range(10):  # Przewiń 10 razy
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

# Wyciągnięcie ID grupy z URL
group_id = group_url.split('/')[4]
print(f"ID grupy: {group_id}")

# Znajdź członków grupy i dodaj do unikalnego zbioru
members_set = set()  # Zbiór przechowujący unikalne linki do profili
members_elements = driver.find_elements(By.XPATH, f"//a[contains(@href, '/groups/{group_id}/user/')]")

for member in members_elements:
    member_href = member.get_attribute("href")
    if member_href not in members_set:
        members_set.add(member_href)

print("Znaleziono unikalnych członków grupy:")
for member_id in members_set:
    print(member_id)

# Iteracja po unikalnych członkach
for member_id in list(members_set)[:5]:  # Ograniczenie do pierwszych 5 członków dla testów
    try:
        # Przejdź do profilu użytkownika
        driver.get(member_id)
        time.sleep(3)

        # Kliknij "Wiadomość" (oczekiwanie na element)
        message_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Wyślij wiadomość')]"))
        )
        message_button.click()
        time.sleep(3)

        message_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@aria-placeholder='Aa']//p"))
        )
        message_box.send_keys(message_text)
        message_box.send_keys(Keys.RETURN)

        print(f"Wiadomość wysłana do: {member_id}")
        time.sleep(5)
    except Exception as e:
        print(f"Nie udało się wysłać wiadomości do: {member_id}, błąd: {e}")

driver.quit()
