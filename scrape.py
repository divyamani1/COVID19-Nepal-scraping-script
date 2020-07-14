import glob
import logging
import re

import pandas as pd

datadir = "./csse_covid_19_daily_reports/"
date_re = "\d+-\d+-\d+"

reg = re.compile(date_re)


datelist = []


def process_files():
    all_files = glob.glob(datadir + "/*.csv")
    final_data = pd.DataFrame(
        columns=[
            "FIPS",
            "Admin2",
            "Province_State",
            "Country_Region",
            "Last_Update",
            "Lat",
            "Long_",
            "Confirmed",
            "Deaths",
            "Recovered",
            "Active",
            "Combined_Key",
        ]
    )
    logging.info("Created empty dataframe.")

    logging.info("Looping over all files.")
    for filename in all_files:
        data = pd.read_csv(filename)

        if hasattr(data, "Country_Region"):
            record = data[data.Country_Region == "Nepal"]
        elif hasattr(data, "Combined_Key"):
            record = data[data.Combined_Key == "Nepal"]
        elif hasattr(data, "Country/Region"):
            record = data[data["Country/Region"] == "Nepal"]

        if len(record):
            final_data = final_data.append(record, sort=False)
        else:
            final_data = final_data.append(pd.Series(), ignore_index=True, sort=False)

        datelist.append(reg.findall(filename)[0])

    logging.info("Cleaning scraped data.")
    final_data = final_data.loc[
        :,
        [
            "Active",
            "Case-Fatality_Ratio",
            "Confirmed",
            "Deaths",
            "Incidence_Rate",
            "Recovered",
        ],
    ]

    final_data["date"] = pd.to_datetime(datelist, infer_datetime_format=True)

    final_data = final_data.sort_values("date")

    logging.info("Saving new data to CSV.")
    final_data.to_csv("covid19-nepal.csv", index=False)

    return max(datelist)
