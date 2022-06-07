"""builds pdf reports for each local station"""

from datetime import datetime
from io import StringIO
import os
import re
from textwrap import wrap
import hvplot
import jinja2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml


def query_dataframe(df, column=None, index_col=None, single_value=True, **kwargs):
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


def format_excel_sheet(df, writer, sheet_index):
    """sets excel percent format for shr outputs and auto-fits columns"""
    pct_format = writer.book.add_format({"num_format": "0.0%"})
    sheet = writer.book.worksheets()[sheet_index]
    for i in range(len(df.columns)):
        if i < 2:
            continue

        col_width = len(df.columns[i]) + 3
        sheet.set_column(i, i, col_width, pct_format)


def word_wrap_title(title):
    """accomodates long titles by breaking at 60 characters"""
    return "\n".join(wrap(title, 60))


with open("hand/markets.yaml", "r", encoding="utf-8") as file:
    markets = yaml.load(file, Loader=yaml.CLoader)


class Report:
    """builds an HTML report for a given market"""

    def __init__(self, market_name):
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader("./templates/"),
            undefined=jinja2.StrictUndefined,
        )
        self.template = env.get_template("base.j2")

        self.run_timestamp = datetime.now().strftime("%Y-%m-%d at %H:%M %p")

        self.load_csv_files()

        self.national_clearance_rate = format_pct(
            query_dataframe(self.reta_national, "clearance_rate", year=2020)
        )
        self.reta_national = self.reta_national.set_index("year")

        self.market_name = market_name
        self.market_name_snake_case = re.sub(
            r"\s{1,}", "_", self.market_name.lower().strip()
        )

        self.report_info = markets[self.market_name]
        self.data = {
            "national_clearance_rate": self.national_clearance_rate,
            "nosummary": self.report_info.pop("nosummary", False),
        }
        self.get_data()

    def __enter__(self):
        self.get_data()
        return self

    def __exit__(self, *args, **kwargs):
        pass

    def load_csv_files(self):
        """reads csv files and attaches to self"""

        for filename in os.listdir("input"):
            attrname = os.path.basename(filename).split(".")[0]
            self.__dict__[attrname] = pd.read_csv(f"input/{filename}", low_memory=False)

        # do this manually
        self.agencies = pd.read_csv("input/agencies.csv").query("data_year == 2020")[
            ["ori", "state_abbr"]
        ]

    def write_local_shr_data(self):
        write_args = {"index": False}
        sheet_index = 0

        if "state_abbr" not in self.report_info:
            return

        with pd.ExcelWriter(
            f"output/shr/clearance_demographics_{self.market_name}.xlsx",
            engine="xlsxwriter",
        ) as writer:
            self.shr_state.pipe(
                query_dataframe,
                single_value=False,
                state_abbr=self.report_info["state_abbr"],
            ).to_excel(
                writer,
                sheet_name=self.report_info["state_abbr"]
                if len(self.report_info["state_abbr"]) < 31
                else self.report_info["state_abbr"][:31],
                **write_args,
            )

            format_excel_sheet(self.shr_state, writer, sheet_index)
            sheet_index += 1

            for agency_info in self.report_info["agencies"]:
                self.shr_agency.pipe(
                    query_dataframe,
                    single_value=False,
                    ori_code=agency_info["ori_code"],
                ).to_excel(
                    writer,
                    sheet_name=agency_info["ncic_agency_name"]
                    if len(agency_info["ncic_agency_name"]) < 31
                    else agency_info["ncic_agency_name"][:31],
                    **write_args,
                )
                format_excel_sheet(self.shr_agency, writer, sheet_index)
                sheet_index += 1

    def get_data(self):
        """populates data for a report"""

        self.data.update(
            {
                "market_name": self.market_name,
                "generated_date": self.run_timestamp,
                "reta": {
                    "national": self.get_single_data(
                        "reta_national", "National", annual_only=True
                    ),
                    "agencies": [],
                },
            }
        )

        if "state_abbr" in self.report_info:
            self.data["reta"].update(
                {
                    "state": self.get_single_data(
                        "reta_state",
                        self.report_info["state_abbr"],
                        state_abbr=self.report_info["state_abbr"],
                    )
                }
            )

        if "msa_name" in self.report_info:
            self.data["reta"].update(
                {
                    "msa": self.get_single_data(
                        "reta_msa",
                        self.report_info["msa_name"],
                        msa_name=self.report_info["msa_name"],
                    )
                }
            )

        # agencies
        for agency_info in self.report_info["agencies"]:
            adata = self.get_single_data(
                "reta_agency",
                agency_info["ncic_agency_name"].title(),
                ori_code=agency_info["ori_code"],
                ncic_agency_name=agency_info["ncic_agency_name"],
            )
            self.data["reta"]["agencies"].append(adata)

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
            self.data["reta"].update(
                {
                    "agency_comparison": {
                        "interactive_table_html": get_hvplot_html(
                            self.reta_agency_5yr.merge(
                                self.agencies,
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

        self.write_local_shr_data()

        html = self.template.render(report=self.data)
        with open(
            f"output/reta/clearance_rate_{self.market_name_snake_case}.html",
            "w",
            encoding="utf-8",
        ) as outfile:
            outfile.write(html)

    def get_single_data(self, geography, title, annual_only=False, **selectors):
        """gets a dictionary containing the data needed to populate the template

        Args:
            geography (str): type of geography to use
            title (str): title of data

        Returns:
            dict: dict of template data
        """
        df_annual = getattr(self, geography)
        if not annual_only:
            df_latest = getattr(self, f"{geography}_latest")
            df_5yr = getattr(self, f"{geography}_5yr")

        data = {
            "title": title,
            "annual_chart_html": self.get_chart_html(
                query_dataframe(
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
                query_dataframe(
                    df=df_annual, index_col="year", single_value=False, **selectors
                ),
                columns=["Actual", "Cleared", "Clearance Rate"],
            ),
        }

        if not annual_only:
            data.update(
                {
                    "annual_only": False,
                    "max_complete_year": query_dataframe(
                        df_latest, column="latest_year", single_value=True, **selectors
                    ),
                    "clearance_rate_latest": format_pct(
                        query_dataframe(
                            df=df_latest, column="clearance_rate", **selectors
                        )
                    ),
                    "clearance_rate_latest_change": format_pct(
                        query_dataframe(df=df_5yr, column="change", **selectors)
                    ),
                }
            )
            data["compared_to_national"] = compare_to_national(
                data["clearance_rate_latest"], self.national_clearance_rate
            )
            data["comparison_chart_html"] = get_table_html(
                query_dataframe(
                    df=df_5yr.rename(columns={"5_year_avg": "5-Year Average"}),
                    index_col=list(selectors.keys()),
                    single_value=False,
                    **selectors,
                )
            )
        else:
            data.update({"max_complete_year": 2020, "annual_only": True})

        return data

    def get_chart_html(self, df, title, label, national_compare=True):
        """runs dataframe.plot with styling and gets the html"""
        chart_df = df[["clearance_rate"]].rename(columns={"clearance_rate": label})

        if national_compare is True:
            chart_df = chart_df.join(
                self.reta_national[["clearance_rate"]].rename(
                    columns={"clearance_rate": "national"}
                )
            )

        chart_df = chart_df.multiply(100)

        # shared arguments used for svg and html chart generation
        chart_args = {
            "title": word_wrap_title(title),
            "legend": "top",
            "xlabel": "Year",
            "ylabel": "Clearance rate",
            "rot": 90,
        }

        chart = chart_df.plot(height=500, backend="hvplot", **chart_args)
        # also output as svg
        chart_df.plot(
            figsize=(15, 12),
            ylim=(0, 100),
            **chart_args,
        ).get_figure().savefig(f"output/svgs/{title}.svg")
        plt.close("all")
        return get_hvplot_html(chart)


def compare_to_national(num, national):
    """gets percentage difference compared to national value"""
    return format_pct((num - national) / national)


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
