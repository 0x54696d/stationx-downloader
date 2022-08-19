import requests
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from awesome_progress_bar import ProgressBar


class Lecture:
    def __init__(self, title, link):
        self.title = title
        self.link = link

    def download(self, driver, path):
        driver.get(self.link)
        try:
            download_link = driver.find_element(by=By.CLASS_NAME, value='download').get_property('href')
        except NoSuchElementException:
            print('No downloadable video file found!')
            return

        r = requests.get(download_link, stream=True)
        if r.ok:
            with open(path, 'wb') as f:
                total_length = r.headers.get('content-length')

                if total_length is None:  # no content length header
                    f.write(r.content)
                else:
                    dl = 0
                    total_length = int(total_length)
                    bar = ProgressBar(100, bar_length=50)
                    prev_done = 0
                    for data in r.iter_content(chunk_size=4096):
                        dl += len(data)
                        f.write(data)
                        done = int(100 * dl / total_length)
                        if done > prev_done:
                            bar.iter()
                        prev_done = done
                    bar.wait()
        else:  # HTTP status code 4XX/5XX
            print(f'Download failed: status code {r.status_code}\n{r.text}')
