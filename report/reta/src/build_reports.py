"""builds pdf reports for each local station"""

from datetime import datetime
from io import StringIO
import re
import jinja2
import pandas as pd
import yaml


def get_data(df, column, index_col=None, single_value=True, **kwargs):
    """filters a dataframe based on kwargs and returns column from the resulting row

    Args:
        df (_type_): _description_

    Returns:
        _type_: _description_
    """
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
        return res.iloc[0][column]
    return res[column]


def format_pct(pct):
    """formats percentage values"""
    if not isinstance(pct, (int, float)):
        raise TypeError(f"cannot format {type(pct)} value {pct}")

    return round(pct * 100, 1)


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

run_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

national_clearance_rate = format_pct(get_data(national, "clearance_rate", year=2020))


class Report:
    """builds an HTML report for a given market"""

    def __init__(self, market_name):
        env = jinja2.Environment(loader=jinja2.FileSystemLoader("./templates/"))
        self.template = env.get_template("reta_local.html.j2")

        self.market_name = market_name
        self.market_name_snake_case = re.sub(
            r"\s{2,}", "_", self.market_name.lower().strip()
        )

        self.market_data = markets[self.market_name]
        self.data = {"national_clearance_rate": national_clearance_rate}
        self.get_data()

    def get_data(self):
        """populates data for a report"""

        self.data.update(
            {
                "market_name": self.market_name,
                "generated_date": run_timestamp,
                "state": {
                    "state_abbr": self.market_data["state_abbr"],
                    "clearance_rate_2020": format_pct(
                        get_data(
                            df=state_2020,
                            column="clearance_rate",
                            state_abbr=self.market_data["state_abbr"],
                        )
                    ),
                    "plot_svg": get_plot_svg(
                        get_data(
                            df=state,
                            column="clearance_rate",
                            index_col="year",
                            single_value=False,
                            state_abbr=self.market_data["state_abbr"],
                        )
                        * 100,
                        title=f"{self.market_data['state_abbr']} "
                        "statewide homicide clearance rate",
                    ),
                },
                "core_agencies": [],
            }
        )

        self.data["state"]["compared_to_national"] = compare_to_national(
            self.data["state"]["clearance_rate_2020"]
        )

        # core agencies
        for agency_info in self.market_data["core_agencies"]:
            adata = {
                "agency_name": agency_info["agency_name"],
                "clearance_rate_2020": format_pct(
                    get_data(
                        df=agency_2020,
                        column="clearance_rate",
                        ori_code=agency_info["ori_code"],
                        agency_name=agency_info["agency_name"],
                    )
                ),
                "clearance_rate_2020_change": format_pct(
                    get_data(
                        df=agency_5yr,
                        column="change",
                        ori_code=agency_info["ori_code"],
                        agency_name=agency_info["agency_name"],
                    )
                ),
            }
            adata["compared_to_national"] = format_pct(
                (adata["clearance_rate_2020"] - national_clearance_rate)
                / national_clearance_rate
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


def compare_to_national(num):
    """gets percentage difference compared to national value"""
    return format_pct((num - national_clearance_rate) / national_clearance_rate)


def get_plot_svg(df, **kwargs):
    """runs dataframe.plot with styling and gets the svg text"""
    string_io = StringIO()
    df.plot(
        figsize=kwargs.pop("figsize", (7, 4.5)),
        legend=kwargs.pop("legend", True),
        xlabel=kwargs.pop("xlabel", "Year"),
        ylabel=kwargs.pop("ylabel", "Clearance rate"),
        **kwargs,
    ).get_figure().savefig(string_io, format="svg", dpi=1200)
    return string_io.getvalue()


if __name__ == "__main__":
    for market in markets:
        report = Report(market)
        report.build_html_report()
