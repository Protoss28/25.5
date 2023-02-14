import pytest
from selenium import webdriver
from settings import valid_email, valid_password

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@pytest.fixture(autouse=True)
def authorization():
    pytest.driver = webdriver.Chrome('./webdriver/chromedriver.exe')
    # Переход на страницу авторизации
    pytest.driver.get('http://petfriends.skillfactory.ru/login')
    # Ввести email
    pytest.driver.find_element('id', 'email').send_keys(valid_email)
    # Ввести пароль
    pytest.driver.find_element('id', 'pass').send_keys(valid_password)
    # Нажимаем на кнопку входа в аккаунт
    pytest.driver.find_element('css selector', 'button[type="submit"]').click()
    # Проверка, что мы на главной (/all_pets) странице
    assert pytest.driver.find_element('tag name', 'h1').text == "PetFriends"

    yield

    pytest.driver.quit()

# Проверка страницы /all_pets
def test_cards_all_pets():
    # Настройка на неявное ожидание
    pytest.driver.implicitly_wait(10)

    # Собирается информацию о питомцах
    images = pytest.driver.find_elements('css selector', '.card-deck .card-img-top')
    names = pytest.driver.find_elements('css selector', '.card-deck .card-title')
    descriptions = pytest.driver.find_elements('css selector', '.card-deck .card-text')

    # Проверка найденной информации о питомцах на не пустоту
    for i in range(len(names)):
        assert images[i].get_attribute('src') != ''
        assert names[i].text != ''
        assert descriptions[i].text != ''
        assert ', ' in descriptions[i].text
        parts = descriptions[i].text.split(", ")
        assert len(parts[0]) > 0
        assert len(parts[1]) > 0

# Проверка страницы /my_pets
def test_list_my_pets():
    # Настройка на явное ожидание
    waiter = WebDriverWait(pytest.driver, 10)

    # Переход на страницу пользователя (/my_pets)
    pytest.driver.find_element('link text', 'Мои питомцы').click()
    # Ожидание перехода на личную страницу (/my_pets)
    assert waiter.until(EC.title_is('PetFriends: My Pets'))

    # Вытаскивание оглавления из верхнего левого угла (с ником)
    title = waiter.until(EC.presence_of_element_located((By.XPATH, '// *[ @ class = ".col-sm-4 left"]')))
    # Оглавление делиться на строки, и вытаскивание общего числа питомцев
    title_pets_number = int(title.text.split('\n')[1][10:])

    # Расчитываем количество строк в таблице питомцев
    table_of_pets = waiter.until(EC.presence_of_all_elements_located((By.XPATH, '// *[ @ id = "all_my_pets"] / table / tbody / tr')))
    pets_in_table_number = len(table_of_pets)

    # Составляется список питомцев и расчитываем количество питомцев с фотографиями
    list_of_my_pets = []
    pets_with_photo_number = 0
    # Обращение за каждым элементом на сайт
    for i in range(pets_in_table_number):
        photo = pytest.driver.find_element('xpath', f'// *[ @ id = "all_my_pets"] / table / tbody / tr[{i+1}] / th / img')
        name = pytest.driver.find_element('xpath', f'// *[ @ id = "all_my_pets"] / table / tbody / tr[{i+1}] / td[1]').text
        pet_type = pytest.driver.find_element('xpath', f'// *[ @ id = "all_my_pets"] / table / tbody / tr[{i+1}] / td[2]').text
        age = pytest.driver.find_element('xpath', f'// *[ @ id = "all_my_pets"] / table / tbody / tr[{i+1}] / td[3]').text
        list_of_my_pets.append([name, pet_type, age])
        if photo.get_attribute('src') != '':
            pets_with_photo_number += 1

    # Проверка каждого питомца на Имя, Породу и Возраст что не пустые
    all_pets_valid = True
    for pet in list_of_my_pets:
        if not ( pet[0] and pet[1] and pet[2] ):
            all_pets_valid = False
            break

    # Проверка питомцев на разные имена.
    list_of_my_pets_names = []
    for pet in list_of_my_pets:
        list_of_my_pets_names.append(pet[0])
    all_pets_have_different_names = True
    if len(list_of_my_pets_names) != len(set(list_of_my_pets_names)):
        all_pets_have_different_names = False

    # Проверка на не повторяющихся питомцев.
    all_pets_different = True
    for i in range(len(list_of_my_pets)):
        for j in range(i+1, len(list_of_my_pets)):
            if list_of_my_pets[i] == list_of_my_pets[j]:
                all_pets_different = False
                break
        if not all_pets_different:
            break

