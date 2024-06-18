#!/usr/bin/env python3
""" """
import time
import os
import requests
import sys
import music_tag
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


class LBookDownload:
    """ """

    def __init__(self):
        """ """
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        scriptpath = os.path.abspath(os.path.dirname(sys.argv[0]))
        chrome_options.add_argument(f"user-data-dir={scriptpath}/.chrome")
        # chrome_options.add_argument("--headless=new")
        self.driver = webdriver.Chrome(options=chrome_options)

    def teardown(self):
        """ """
        self.driver.quit()

    def login(self):
        """ """
        self.driver.find_element(By.ID, "username").send_keys("your_username")
        self.driver.find_element(By.ID, "password").send_keys("your_password")
        self.driver.find_element(
            By.CSS_SELECTOR, "#loginFormUsernameAndPasswordButton > .MuiButton-label-56"
        ).click()
        time.sleep(10)

    def download(self, title):
        """ """
        self.driver.get("https://www.onlinebibliotheek.nl/account/boekenplank.html")
        time.sleep(1)

        try:
            self.driver.find_element(
                By.XPATH,
                f"//h2[contains(., 'Mijn boekenplank')]",
            )
        except:
            self.login()

        self.driver.find_element(
            By.XPATH,
            f"//a[.//span[contains(., '{title}')]]",
        ).click()
        self.driver.find_element(By.ID, "download").click()
        time.sleep(1)

        self.driver.find_element(
            By.XPATH,
            "//vg-chapter-list-button/button",
        ).click()
        time.sleep(1)

        chapter_total = len(
            self.driver.find_elements(By.XPATH, "//md-list/md-list-item")
        )
        print(f"Found {chapter_total} chapters total")
        self.driver.find_element(By.XPATH, "//md-list/md-list-item[1]/button").click()
        time.sleep(1)

        audio = self.driver.find_element(
            By.XPATH,
            "//audio",
        )

        chapter_ptr = 1
        file_list = []
        while chapter_ptr <= chapter_total:
            file = f"./{title} - Chapter {chapter_ptr:03}.mp3"
            chapter_ptr += 1

            mp3_url = audio.get_attribute("src")
            if os.path.isfile(file):
                print(f"File exists: {file}")
            else:
                print(f"Downloading: {file}")
                download = requests.get(mp3_url)
                if download.status_code == 200:
                    with open(file, "wb") as file_:
                        file_.write(download.content)
                        file_.close()
                        file_list.append(file)
                else:
                    print("Error: unable to download")
                    sys.exit(1)

            self.driver.find_element(By.CSS_SELECTOR, ".next").click()
            time.sleep(1)   
        time.sleep(10)
        return file_list


def setFileTitle(file_list):
    """Set the title of the file based on its title tag. If no tag present, then return nothing"""
    for file in file_list:
        f = music_tag.load_file(file) # dict access returns a MetadataItem
        if f['title']:
            file_new = file.split("-")[0] + "- " + str(f['title']) + ".mp3"
            print("Post processing tags: renaming " + file + " to " + file_new)
            os.rename(file, file_new)


def main():
    """Main program"""
    book_title = sys.argv[1]
    bookdl = LBookDownload()
    file_list = bookdl.download(book_title)
    bookdl.teardown()
    setFileTitle(file_list)


if __name__ == "__main__":
    main()
