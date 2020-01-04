import requests
from requests.exceptions import HTTPError
from requests.exceptions import ConnectionError
from requests.exceptions import TooManyRedirects
from requests.exceptions import InvalidSchema
from requests.exceptions import ReadTimeout
import shutil
import os

import argparse

class ImageDownloader:

    def __init__(self , url):
        self.links = self.get_links(url)

        if len(self.links) == 0:
            exit(1)

        print("Total links : {}".format(len(self.links)))

    def get_starting_index(self , path):

        files = os.listdir(path)
        indexes = [int(file_.split(".")[0]) for file_ in files]

        return max(indexes) + 1

    def start(self , save_dir ,  image_count):

        if os.path.isdir(save_dir) == False:
            os.mkdir(save_dir)
            print("Directory {} created.".format(save_dir))
            link_tested_count = 0
        else:
            link_tested_count = self.get_starting_index(save_dir)

        if image_count > len(self.links):
            print("there are less image found than required")
            image_count = len(self.links)
            print("Setting max image count to : {}".format(image_count))



        for _ in self.links:
            link = self.links[link_tested_count]
            path = os.path.join(save_dir , str(link_tested_count) + "." + self.get_ext(link) )

            if self.download(link , path):

                print("{}.downloaded => {}".format(link_tested_count , link))
                if link_tested_count >= image_count:
                    break
            else:
                print("Could not download : {}".format(link))

            link_tested_count += 1

    def download(self , url , save_path):

        res = None

        try:
            res = requests.get(url , timeout = 25 ,  stream = True)
        except HTTPError :
            return False
        except ConnectionError:
            return False
        except TooManyRedirects:
            return False
        except InvalidSchema:
            return False
        except ReadTimeout:
            print("timed out.")
            return False


        with open(save_path, "wb") as f:
            res.raw.decode_content = True
            shutil.copyfileobj(res.raw , f)
        return True



    def get_ext(self , url):
        parts = url.split('.')
        ext = parts[-1]

        if ext in ["jpg" , "jpeg"  , "gif" , "tiff" , "png"]:
            return ext
        return "jpg"


    def get_links(self , url):

        res = None

        try:
            res = requests.get(url)
        except  HTTPError:
            print("Error downloading links")
            return []

        text = res.text
        urls = text.split("\n")

        return urls



def tested():
    image_downloader = ImageDownloader(url = "http://www.image-net.org/api/text/imagenet.synset.geturls?wnid=n03791235")
    image_downloader.start("./cars" , 150)


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--url', dest = "url" , required = True ,   type = str ,  help='imagenet url')
    parser.add_argument('--save_dir', dest = "save_dir" , required = True ,   type = str ,  help='save dir')
    parser.add_argument('--count', dest = "count" ,  type = int , required = True ,   help='image count')
    args = parser.parse_args()


    image_downloader = ImageDownloader(args.url)
    image_downloader.start(args.save_dir  , args.count)


if __name__ == "__main__":
    main()
