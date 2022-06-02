"""builds pdf reports for each local station"""

from datetime import datetime
from io import StringIO
import re
from textwrap import wrap
import hvplot
import jinja2
import numpy as np
import pandas as pd
import yaml


def get_data(df, column=None, index_col=None, single_value=True, **kwargs):
    """filters a dataframe based on kwargs and returns column from the resulting row"""
    query_string = []
    for kwarg, val in kwargs.items():
        if isinstance(val, str):
            val_str = f'"{val}"'
        else:
            val_str = f"{val}"
        query_string.append(f"({kwarg} == {val_str})")

    if len(query_string) == 0:
        res = df
    else:
        res = df.query("&".join(query_string))

        if index_col is not None:
            res = res.set_index(index_col)

        if single_value is True:
            assert (
                len(res) == 1
            ), f"query result should have 1 row, got {len(res)}. params were {kwargs}"
            assert column is not None, "must pass a column to obtain a single value"
            return res.iloc[0][column]

    if column is None:
        return res
    return res[column]


def format_pct(pct):
    """formats percentage values"""
    if not isinstance(pct, (int, float)):
        raise TypeError(f"cannot format {type(pct)} value {pct}")

    return round(pct * 100, 1)


def word_wrap_title(title):
    """accomodates long titles by breaking at 60 characters"""
    return "\n".join(wrap(title, 60))


agencies = pd.read_csv("input/agencies.csv").query("data_year == 2020")[
    ["ori", "state_abbr"]
]
agency = pd.read_csv("input/agency.csv")
agency_latest = pd.read_csv("input/agency_latest.csv")
agency_5yr = pd.read_csv("input/agency_5yr.csv")
msa = pd.read_csv("input/msa.csv")
msa_latest = pd.read_csv("input/msa_latest.csv")
msa_5yr = pd.read_csv("input/msa_5yr.csv")
national = pd.read_csv("input/national.csv")
state = pd.read_csv("input/state.csv")
state_latest = pd.read_csv("input/state_latest.csv")
state_5yr = pd.read_csv("input/state_5yr.csv")

with open("hand/markets.yaml", "r", encoding="utf-8") as file:
    markets = yaml.load(file, Loader=yaml.CLoader)

run_timestamp = datetime.now().strftime("%Y-%m-%d at %H:%M %p")

national_clearance_rate = format_pct(get_data(national, "clearance_rate", year=2020))

national = national.set_index("year")


class Report:
    """builds an HTML report for a given market"""

    def __init__(self, market_name):
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader("./templates/"),
            undefined=jinja2.StrictUndefined,
        )
        self.template = env.get_template("base.j2")

        self.market_name = market_name
        self.market_name_snake_case = re.sub(
            r"\s{1,}", "_", self.market_name.lower().strip()
        )

        self.report_info = markets[self.market_name]
        self.data = {
            "national_clearance_rate": national_clearance_rate,
            "nosummary": self.report_info.pop("nosummary", False),
        }
        self.get_data()

    def __enter__(self):
        self.get_data()
        return self

    def __exit__(self, *args, **kwargs):
        pass

    def get_data(self):
        """populates data for a report"""

        self.data.update(
            {
                "market_name": self.market_name,
                "generated_date": run_timestamp,
                "national": get_single_data("national", "National", annual_only=True),
                "agencies": [],
            }
        )

        if "state_abbr" in self.report_info:
            self.data.update(
                {
                    "state": get_single_data(
                        "state",
                        self.report_info["state_abbr"],
                        state_abbr=self.report_info["state_abbr"],
                    )
                }
            )

        if "msa_name" in self.report_info:
            self.data.update(
                {
                    "msa": get_single_data(
                        "msa",
                        self.report_info["msa_name"],
                        msa_name=self.report_info["msa_name"],
                    )
                }
            )

        # agencies
        for agency_info in self.report_info["agencies"]:
            adata = get_single_data(
                "agency",
                agency_info["ncic_agency_name"].title(),
                ori_code=agency_info["ori_code"],
                ncic_agency_name=agency_info["ncic_agency_name"],
            )
            self.data["agencies"].append(adata)

        # optional agency comparison table
        if (
            "agency_comparison" in self.report_info
            and self.report_info["agency_comparison"] is True
        ):
            cols = {
                "ncic_agency_name": "Agency Name",
                "state_abbr": "State",
                "5_year_avg": "2015-2019 Average",
                "latest": "2020",
            }
            self.data.update(
                {
                    "agency_comparison": {
                        "interactive_table_html": get_hvplot_html(
                            agency_5yr.merge(
                                agencies,
                                how="left",
                                left_on="ori_code",
                                right_on="ori",
                                validate="1:1",
                            )[list(cols.keys())]
                            .set_index(["ncic_agency_name", "state_abbr"])
                            .multiply(100)
                            .round(1)
                            .replace((np.inf, -np.inf), np.NaN)
                            .dropna(subset=["5_year_avg"])
                            .reset_index()
                            .sort_values("latest")
                            .rename(columns=cols)
                            .plot(kind="table", height=500, backend="hvplot")
                        )
                    }
                }
            )

    def build_html_report(self):
        """builds an html report"""

        html = self.template.render(report=self.data)
        with open(
            f"output/clearance_rate_{self.market_name_snake_case}.html",
            "w",
            encoding="utf-8",
        ) as outfile:
            outfile.write(html)


def get_single_data(geography, title, annual_only=False, **selectors):
    """gets a dictionary containing the data needed to populate the template

    Args:
        geography (str): type of geography to use
        title (str): title of data

    Returns:
        dict: dict of template data
    """
    df_annual = globals()[geography]
    if not annual_only:
        df_latest = globals()[f"{geography}_latest"]
        df_5yr = globals()[f"{geography}_5yr"]

    data = {
        "title": title,
        "annual_chart_svg": get_chart_html(
            get_data(
                df=df_annual,
                index_col="year",
                single_value=False,
                **selectors,
            ),
            title=f"{title} Homicide Clearance Rate",
            label=title,
            national_compare=not annual_only,
        ),
        "annual_table_html": get_table_html(
            get_data(df=df_annual, index_col="year", single_value=False, **selectors),
            columns=["Actual", "Cleared", "Clearance Rate"],
        ),
    }

    if not annual_only:
        data.update(
            {
                "annual_only": False,
                "max_complete_year": get_data(
                    df_latest, column="latest_year", single_value=True, **selectors
                ),
                "clearance_rate_latest": format_pct(
                    get_data(df=df_latest, column="clearance_rate", **selectors)
                ),
                "clearance_rate_latest_change": format_pct(
                    get_data(df=df_5yr, column="change", **selectors)
                ),
            }
        )
        data["compared_to_national"] = compare_to_national(
            data["clearance_rate_latest"]
        )
        data["comparison_chart_html"] = get_table_html(
            get_data(
                df=df_5yr.rename(columns={"5_year_avg": "5-Year Average"}),
                index_col=list(selectors.keys()),
                single_value=False,
                **selectors,
            )
        )
    else:
        data.update({"max_complete_year": 2020, "annual_only": True})

    return data


def compare_to_national(num):
    """gets percentage difference compared to national value"""
    return format_pct((num - national_clearance_rate) / national_clearance_rate)


def get_chart_html(df, title, label, national_compare=True):
    """runs dataframe.plot with styling and gets the svg text"""
    chart_df = df[["clearance_rate"]].rename(columns={"clearance_rate": label})

    if national_compare is True:
        chart_df = chart_df.join(
            national[["clearance_rate"]].rename(columns={"clearance_rate": "national"})
        )

    chart = chart_df.multiply(100).plot(
        title=word_wrap_title(title),
        height=500,
        legend="top",
        xlabel="Year",
        ylabel="Clearance rate",
        backend="hvplot",
        rot=90,
    )
    return get_hvplot_html(chart)


def get_hvplot_html(plot_output):
    """returns the html output pandas.plot with backend='hvplot' as str"""
    string_io = StringIO()
    hvplot.save(plot_output, string_io)
    return string_io.getvalue()


def get_table_html(df, **kwargs):
    """runs dataframe.to_html with styling and returns the html"""
    df = df.copy()
    pct_cols = ["5-Year Average", "clearance_rate", "latest", "change"]
    for col in pct_cols:
        if col in df.columns:
            df[col] = df[col].multiply(100).round(1).astype(str) + "%"

    df.columns = (
        df.columns.str.replace("_", " ")
        .str.replace("cleared arrest", "cleared")
        .str.title()
    )
    return df.to_html(**kwargs)


if __name__ == "__main__":
    for market in markets:
        with Report(market) as report:
            report.build_html_report()
