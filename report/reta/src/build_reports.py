"""builds pdf reports for each local station"""

from datetime import datetime
from io import StringIO
import re
from textwrap import wrap
import jinja2
import matplotlib.pyplot as plt
import pandas as pd
import yaml


def get_data(df, column=None, index_col=None, single_value=True, **kwargs):
    """filters a dataframe based on kwargs and returns column from the resulting row"""
    query_string = []
    for kwarg, val in kwargs.items():
        if isinstance(val, str):
            val_str = f"'{val}'"
        else:
            val_str = f"{val}"
        query_string.append(f"({kwarg} == {val_str})")

    res = df.query("&".join(query_string))

    if index_col is not None:
        res = res.set_index(index_col)

    if single_value is True:
        assert len(res) == 1, f"query result should have 1 row, got {len(res)}"
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


agency = pd.read_csv("input/agency.csv")
agency_2020 = pd.read_csv("input/agency_2020.csv")
agency_5yr = pd.read_csv("input/agency_5yr.csv")
msa = pd.read_csv("input/msa.csv")
msa_2020 = pd.read_csv("input/msa_2020.csv")
msa_5yr = pd.read_csv("input/msa_5yr.csv")
national = pd.read_csv("input/national.csv")
state = pd.read_csv("input/state.csv")
state_2020 = pd.read_csv("input/state_2020.csv")
state_5yr = pd.read_csv("input/state_5yr.csv")

with open("hand/markets.yaml", "r", encoding="utf-8") as file:
    markets = yaml.load(file, Loader=yaml.CLoader)

run_timestamp = datetime.now().strftime("%Y-%m-%d at %H:%M %p")

national_clearance_rate = format_pct(get_data(national, "clearance_rate", year=2020))


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
            r"\s{2,}", "_", self.market_name.lower().strip()
        )

        self.market_data = markets[self.market_name]
        self.data = {"national_clearance_rate": national_clearance_rate}
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
                "state": get_single_data(
                    "state",
                    self.market_data["state_abbr"],
                    state_abbr=self.market_data["state_abbr"],
                ),
                "msa": get_single_data(
                    "msa",
                    self.market_data["msa_name"],
                    msa_name=self.market_data["msa_name"],
                ),
                "core_agencies": [],
            }
        )

        # core agencies
        for agency_info in self.market_data["core_agencies"]:
            adata = get_single_data(
                "agency",
                agency_info["agency_name"].title(),
                ori_code=agency_info["ori_code"],
                agency_name=agency_info["agency_name"],
            )
            self.data["core_agencies"].append(adata)

    def build_html_report(self):
        """builds an html report"""

        html = self.template.render(report=self.data)
        with open(
            f"output/reta_{self.market_name_snake_case}.html",
            "w",
            encoding="utf-8",
        ) as outfile:
            outfile.write(html)


def get_single_data(geography, title, **selectors):
    """gets a dictionary containing the data needed to populate the template

    Args:
        geography (str): type of geography to use
        title (str): title of data

    Returns:
        dict: dict of template data
    """
    df_annual = globals()[geography]
    df_2020 = globals()[f"{geography}_2020"]
    df_5yr = globals()[f"{geography}_5yr"]

    data = {
        "title": title,
        "clearance_rate_2020": format_pct(
            get_data(df=df_2020, column="clearance_rate", **selectors)
        ),
        "clearance_rate_2020_change": format_pct(
            get_data(df=df_5yr, column="change", **selectors)
        ),
        "annual_chart_svg": get_chart_svg(
            get_data(
                df=df_annual,
                column="clearance_rate",
                index_col="year",
                single_value=False,
                **selectors,
            )
            * 100,
            title=f"{title} homicide clearance rate",
        ),
        "annual_table_html": get_table_html(
            get_data(df=df_annual, index_col="year", single_value=False, **selectors),
            columns=["Actual", "Cleared", "Clearance Rate"],
        ),
    }
    data["compared_to_national"] = compare_to_national(data["clearance_rate_2020"])
    data["comparison_chart_html"] = get_table_html(
        get_data(
            df=df_5yr.rename(columns={"2015_2019_avg": "2015-2019 Average"}),
            index_col=list(selectors.keys()),
            single_value=False,
            **selectors,
        )
    )
    return data


def compare_to_national(num):
    """gets percentage difference compared to national value"""
    return format_pct((num - national_clearance_rate) / national_clearance_rate)


def get_chart_svg(df, **kwargs):
    """runs dataframe.plot with styling and gets the svg text"""
    string_io = StringIO()
    df.plot(
        title=word_wrap_title(kwargs.pop("title", None)),
        figsize=kwargs.pop("figsize", (7, 4.5)),
        legend=kwargs.pop("legend", True),
        xlabel=kwargs.pop("xlabel", "Year"),
        ylabel=kwargs.pop("ylabel", "Clearance rate"),
        **kwargs,
    ).get_figure().savefig(string_io, format="svg", dpi=1200)
    plt.clf()
    return string_io.getvalue()


def get_table_html(df, **kwargs):
    """runs dataframe.to_html with styling and returns the html"""
    pct_cols = ["2015-2019 Average", "clearance_rate", "2020", "change"]
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
