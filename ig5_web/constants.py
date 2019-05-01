import os

from dotenv import load_dotenv


here = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(here, "data")
summary_img_dir = os.path.join("img", "summary")
summary_photos_dir = os.path.join(here, "static", summary_img_dir)


load_dotenv(os.path.join(os.path.dirname(here), ".env"))
gmaps_api_key = os.environ["GMAPS_API_KEY"]
