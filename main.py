import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from awesome_progress_bar import ProgressBar
from getpass import getpass

from section import Section
from lecture import Lecture

WINDOW_SIZE = '1920,1080'

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--window-size=%s' % WINDOW_SIZE)

driver = webdriver.Chrome(options=chrome_options)


def login(username, password):
    driver.get('https://sso.teachable.com/secure/58751/identity/login/password')
    driver.find_element(value='email').send_keys(username)
    driver.find_element(value='password').send_keys(password)
    driver.find_element(by=By.NAME, value='commit').click()

    if driver.current_url == 'https://sso.teachable.com/secure/58751/identity/login/password':
        print('Login failed!')
        exit()
    else:
        print('Login succeeded!')


def validate_course(course_id):
    driver.get('https://courses.stationx.net/courses/' + course_id)
    if course_id not in driver.current_url:
        print('Invalid course specified!')
        exit()


def get_course_title(course_id):
    driver.get('https://courses.stationx.net/courses/' + course_id)
    return driver.find_element(by=By.CLASS_NAME, value='course-sidebar').find_element(by=By.TAG_NAME, value='h2').text


def get_lectures(course_id):
    driver.get('https://courses.stationx.net/courses/' + course_id)
    sections = []

    # Looping through each section
    for section_item in driver.find_elements(by=By.CLASS_NAME, value='row'):
        # List holding all lectures for each section
        lectures = []

        # Looping through each lecture
        for lecture_item in section_item.find_elements(by=By.CLASS_NAME, value='item'):
            lectures.append(Lecture(
                lecture_item.find_element(by=By.CLASS_NAME, value='lecture-name').text,
                lecture_item.get_property('href')
            ))

        sections.append(Section(
            section_item.find_element(by=By.CLASS_NAME, value='section-title').text,
            lectures
        ))
    return sections


def main():
    print('Please enter your StationX credentials.')
    mail = input('Mail: ')
    password = getpass()

    print(f'\nSigning in to {mail}...')

    login(mail, password)

    course_id = input('\nPlease enter the course ID you wish to download: ')

    validate_course(course_id)
    course_name = get_course_title(course_id)
    print(f'Proceeding with "{course_name}".\n')
    os.makedirs(course_name, exist_ok=True)

    bar = ProgressBar(1, bar_length=50, use_eta=False)
    try:
        sections = get_lectures(course_id)
        bar.iter(' scanned!')
    except:
        bar.stop()
    bar.wait()

    sections_amount = len(sections)
    print(f'Sections found: {sections_amount}')

    lectures_amount = 0
    for section in sections:
        lectures_amount += section.get_lectures_amount()
    print(f'Lectures found: {lectures_amount}')

    lecture_index = 0
    for section in sections:
        print(f'\nCreating directory for section "{section.title}"')
        os.makedirs(os.path.join(course_name, section.title.replace(":", "-")), exist_ok=True)
        for lecture in section.lectures:

            # Path to save the video in
            lecture_path = os.path.join(course_name,
                                        section.title.replace(":", "-"),
                                        f'{lecture_index}_{lecture.title.replace(":", "-")}.mp4')

            print(f'\nDownloading lecture "{lecture.title}"')
            if os.path.exists(lecture_path):
                print('Skipped because file already exists...')
            else:
                lecture_index += 1
                lecture.download(driver, lecture_path)

    driver.close()
    print(f'\nSuccessfully downloaded "{course_name}"!')


main()
