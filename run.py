import logging
import pathlib
import schedule
import subprocess
import time

from scrape import process_files

logging.basicConfig(
    format="%(asctime)s - %(levelname)s : %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    level=logging.INFO,
    handlers=[logging.FileHandler("debug.log"), logging.StreamHandler()],
)


def main():
    logging.info("Scheduled scraping started.")

    logging.info("Cloning data repository.")

    data_dir = pathlib.Path("./COVID-19/")

    if data_dir.exists():
        stdout = subprocess.run(
            ["git", "-C", "./COVID-19/", "pull", "--depth", "1"], capture_output=True
        ).stdout.decode("utf-8")

        if stdout == "Already up to date.\n":
            logging.info("No new data to update.")
            return 0

    else:
        repository_url = "https://github.com/CSSEGISandData/COVID-19.git"
        subprocess.run(["git", "clone", "--depth", "1", f"{repository_url}"])

    try:
        latest_date = process_files()
        logging.info(f"Dataset updated to {latest_date}")
    except:
        logging.critical("Failed to process file.")
        return 0

    logging.info("Pushing to COVID19-Nepal repository.")

    data_dir = pathlib.Path("./COVID19-Nepal/")

    if not data_dir.exists():
        logging.info("Directory doesn't exists. Cloning the repository")

        repository_url = "git@github.com:divyamani1/COVID19-Nepal.git"
        subprocess.run(["git", "clone", f"{repository_url}"])

    logging.info("Committing the updated dataset.")

    subprocess.run(["mv", "covid19-nepal.csv", "./COVID19-Nepal/"])
    subprocess.run(["git", "-C", "./COVID19-Nepal/", "add", "covid19-nepal.csv"])
    subprocess.run(
        [
            "git",
            "-C",
            "./COVID19-Nepal/",
            "commit",
            "-m",
            f"Update dataset ({latest_date})",
        ]
    )
    subprocess.run(["git", "-C", "./COVID19-Nepal/", "push"])


if __name__ == "__main__":
    schedule.every(12).hours.do(main)
    while True:
        schedule.run_pending()
        time.sleep(1)
