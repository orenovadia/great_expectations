import altair as alt
import json
import pandas as pd
from string import Template

from .renderer import Renderer
from .content_block import ValueListContentBlockRenderer
from .content_block import TableContentBlockRenderer
from .content_block import PrescriptiveBulletListContentBlockRenderer


class ColumnSectionRenderer(Renderer):
    @classmethod
    def _get_column_name(cls, ge_object):
        # This is broken out for ease of locating future validation here
        if isinstance(ge_object, list):
            candidate_object = ge_object[0]
        else:
            candidate_object = ge_object
        try:
            if "kwargs" in candidate_object:
                # This is an expectation (prescriptive)
                return candidate_object["kwargs"]["column"]
            elif "expectation_config" in candidate_object:
                # This is a validation (descriptive)
                return candidate_object["expectation_config"]["kwargs"]["column"]
            else:
                raise ValueError(
                    "Provide a column section renderer an expectation, list of expectations, evr, or list of evrs.")
        except KeyError:
            return None


class DescriptiveColumnSectionRenderer(ColumnSectionRenderer):

    @classmethod
    def render(cls, evrs, section_name=None, column_type=None):
        if section_name is None:
            column = cls._get_column_name(evrs)
        else:
            column = section_name

        content_blocks = []
        cls._render_header(evrs, content_blocks, column_type)
        # cls._render_column_type(evrs, content_blocks)
        cls._render_overview_table(evrs, content_blocks)
        cls._render_quantile_table(evrs, content_blocks)
        cls._render_stats_table(evrs, content_blocks)

        cls._render_histogram(evrs, content_blocks)
        cls._render_values_set(evrs, content_blocks)
        cls._render_bar_chart_table(evrs, content_blocks)

        # cls._render_statistics(evrs, content_blocks)
        # cls._render_common_values(evrs, content_blocks)
        # cls._render_extreme_values(evrs, content_blocks)

        # cls._render_frequency(evrs, content_blocks)
        # cls._render_composition(evrs, content_blocks)

        cls._render_expectation_types(evrs, content_blocks)
        # cls._render_unrecognized(evrs, content_blocks)

        return {
            "section_name": column,
            "content_blocks": content_blocks
        }

    @classmethod
    def _render_header(cls, evrs, content_blocks, column_type=None):

        # NOTE: This logic is brittle
        try:
            column_name = evrs[0]["expectation_config"]["kwargs"]["column"]
        except KeyError:
            column_name = "Table-level expectations"

        try:
            column_type_list = cls._find_evr_by_type(
                evrs, "expect_column_values_to_be_in_type_list"
            )["expectation_config"]["kwargs"]["type_list"]
            column_types = ", ".join(column_type_list)

        except TypeError:
            column_types = "None"

        # assert False

        content_blocks.append({
            "content_block_type": "header",
            "header": "{column_name} (type: {column_type})".format(column_name=column_name, column_type=column_type) if column_type else column_name,
            "sub_header": column_types,
            # {
            #     "template": column_type,
            # },
            "styling": {
                "classes": ["col-12"],
                "header": {
                    "classes": ["alert", "alert-secondary"]
                }
            }
        })

    @classmethod
    def _render_expectation_types(cls, evrs, content_blocks):
        # NOTE: The evr-fetching function is an kinda similar to the code other_section_renderer.DescriptiveOverviewSectionRenderer._render_expectation_types

        # type_counts = defaultdict(int)

        # for evr in evrs:
        #     type_counts[evr["expectation_config"]["expectation_type"]] += 1

        # bullet_list = sorted(type_counts.items(), key=lambda kv: -1*kv[1])

        bullet_list = [{
            "template": "$expectation_type $is_passing",
            "params": {
                "expectation_type": evr["expectation_config"]["expectation_type"],
                "is_passing": str(evr["success"]),
            },
            "styling": {
                "classes": ["list-group-item", "d-flex", "justify-content-between", "align-items-center"],
                "params": {
                    "is_passing": {
                        "classes": ["badge", "badge-secondary", "badge-pill"],
                    }
                },
                # TODO: Adding popovers was a nice idea, but didn't pan out well in the first experiment.
                # "attributes": {
                #     "data-toggle": "popover",
                #     "data-trigger": "hover",
                #     "data-placement": "top",
                #     # "data-content": jinja2.utils.htmlsafe_json_dumps(evr["expectation_config"], indent=2),
                #     # TODO: This is a hack to get around the fact that `data-content` doesn't like arguments bracketed by {}.
                #     "data-content": "<pre>"+html.escape(json.dumps(evr["expectation_config"], indent=2))[1:-1]+"</pre>",
                #     "container": "body",
                # }
            }
        } for evr in evrs]

        content_blocks.append({
            "content_block_type": "bullet_list",
            "header": 'Expectation types <span class="mr-3 triangle"></span>',
            "bullet_list": bullet_list,
            "styling": {
                "classes": ["col-12"],
                "styles": {
                    "margin-top": "20px"
                },
                "header": {
                    # "classes": ["alert", "alert-secondary"],
                    "classes": ["collapsed"],
                    "attributes": {
                        "data-toggle": "collapse",
                        "href": "#{{content_block_id}}-body",
                        "role": "button",
                        "aria-expanded": "true",
                        "aria-controls": "collapseExample",
                    },
                    "styles": {
                        "cursor": "pointer",
                    }
                },
                "body": {
                    "classes": ["list-group", "collapse"],
                },
            },
        })

    @classmethod
    def _render_overview_table(cls, evrs, content_blocks):
        unique_n = cls._find_evr_by_type(
            evrs,
            "expect_column_unique_value_count_to_be_between"
        )
        unique_proportion = cls._find_evr_by_type(
            evrs,
            "expect_column_proportion_of_unique_values_to_be_between"
        )
        null_evr = cls._find_evr_by_type(
            evrs,
            "expect_column_values_to_not_be_null"
        )
        evrs = [evr for evr in [
            unique_n, unique_proportion, null_evr] if evr is not None]

        if len(evrs) > 0:
            new_content_block = TableContentBlockRenderer.render(evrs)
            new_content_block["header"] = "Properties"
            new_content_block["styling"] = {
                "classes": ["col-4", ],
                "styles": {
                    "margin-top": "20px"
                },
                "body": {
                    "classes": ["table", "table-sm", "table-unbordered"],
                    "styles": {
                        "width": "100%"
                    },
                }

            }
            content_blocks.append(new_content_block)

    @classmethod
    def _render_quantile_table(cls, evrs, content_blocks):
        table_rows = []

        quantile_evr = cls._find_evr_by_type(
            evrs,
            "expect_column_quantile_values_to_be_between"
        )

        if not quantile_evr:
            return

        quantiles = quantile_evr["result"]["observed_value"]["quantiles"]
        quantile_ranges = quantile_evr["result"]["observed_value"]["values"]

        quantile_strings = {
            .25: "Q1",
            .75: "Q3",
            .50: "Median"
        }

        for idx, quantile in enumerate(quantiles):
            quantile_string = quantile_strings.get(quantile)
            table_rows.append([
                quantile_string if quantile_string else "{:3.2f}".format(quantile),
                quantile_ranges[idx]
            ])

        content_blocks.append({
            "content_block_type": "table",
            "header": "Quantiles",
            "table_rows": table_rows,
            "styling": {
                "classes": ["col-4"],
                "styles": {
                    "margin-top": "20px"
                },
                "body": {
                    "classes": ["table", "table-sm", "table-unbordered"],
                }
            },
        })

    @classmethod
    def _render_stats_table(cls, evrs, content_blocks):
        table_rows = []

        mean_evr = cls._find_evr_by_type(
            evrs,
            "expect_column_mean_to_be_between"
        )
        mean_value = "{:.2f}".format(
            mean_evr['result']['observed_value']) if mean_evr else None
        if mean_value:
            table_rows.append(["Mean", mean_value])

        min_evr = cls._find_evr_by_type(
            evrs,
            "expect_column_min_to_be_between"
        )
        min_value = "{:.2f}".format(
            min_evr['result']['observed_value']) if min_evr else None
        if min_value:
            table_rows.append(["Minimum", min_value])

        max_evr = cls._find_evr_by_type(
            evrs,
            "expect_column_max_to_be_between"
        )
        max_value = "{:.2f}".format(
            max_evr['result']['observed_value']) if max_evr else None
        if max_value:
            table_rows.append(["Maximum", max_value])

        if len(table_rows) > 0:
            content_blocks.append({
                "content_block_type": "table",
                "header": "Statistics",
                "table_rows": table_rows,
                "styling": {
                    "classes": ["col-4"],
                    "styles": {
                        "margin-top": "20px"
                    },
                    "body": {
                        "classes": ["table", "table-sm", "table-unbordered"],
                    }
                },
            })
        else:
            return

    @classmethod
    def _render_values_set(cls, evrs, content_blocks):
        set_evr = cls._find_evr_by_type(
            evrs,
            "expect_column_values_to_be_in_set"
        )

        if set_evr and "partial_unexpected_counts" in set_evr["result"]:
            partial_unexpected_counts = set_evr["result"]["partial_unexpected_counts"]
            values = [str(v["value"]) for v in partial_unexpected_counts]
        elif set_evr and "partial_unexpected_list" in set_evr["result"]:
            values = [str(item) for item in set_evr["result"]["partial_unexpected_list"]]
        else:
            return

        if len(" ".join(values)) > 100:
            classes = ["col-12"]
        else:
            classes = ["col-4"]

        new_block = {
            "content_block_type": "value_list",
            "header": "Example values",
            "value_list": [{
                "template": "$value",
                "params": {
                    "value": value
                },
                "styling": {
                    "default": {
                        "classes": ["badge", "badge-info"]
                    }
                }
            } for value in values],
            "styling": {
                "classes": classes,
                "styles": {
                    "margin-top": "20px",
                }
            }
        }

        content_blocks.append(new_block)

    @classmethod
    def _render_histogram(cls, evrs, content_blocks):
        # NOTE: This code is very brittle
        kl_divergence_evr = cls._find_evr_by_type(
            evrs,
            "expect_column_kl_divergence_to_be_less_than"
        )
        # print(json.dumps(kl_divergence_evr, indent=2))
        if kl_divergence_evr == None:
            return

        bins = kl_divergence_evr["result"]["details"]["observed_partition"]["bins"]
        # bin_medians = [round((v+bins[i+1])/2, 1)
        #                for i, v in enumerate(bins[:-1])]
        # bin_medians = [(round(bins[i], 1), round(bins[i+1], 1)) for i, v in enumerate(bins[:-1])]
        bins_x1 = [round(value, 1) for value in bins[:-1]]
        bins_x2 = [round(value, 1) for value in bins[1:]]

        df = pd.DataFrame({
            "bin_min": bins_x1,
            "bin_max": bins_x2,
            "weights": kl_divergence_evr["result"]["details"]["observed_partition"]["weights"],
        })
        df.weights *= 100

        bars = alt.Chart(df).mark_bar().encode(
            x='bin_min:O',
            x2='bin_max:O',
            y="weights:Q"
        ).properties(width=200, height=200, autosize="fit")

        chart = bars.to_json()

        new_block = {
            "content_block_type": "graph",
            "header": "Histogram",
            "graph": chart,
            "styling": {
                "classes": ["col-4"],
                "styles": {
                    "margin-top": "20px",
                }
            }
        }

        content_blocks.append(new_block)

    @classmethod
    def _render_bar_chart_table(cls, evrs, content_blocks):
        distinct_values_set_evr = cls._find_evr_by_type(
            evrs,
            "expect_column_distinct_values_to_be_in_set"
        )
        # print(json.dumps(kl_divergence_evr, indent=2))
        if distinct_values_set_evr == None:
            return

        value_count_dicts = distinct_values_set_evr['result']['details']['value_counts']
        values = [value_count_dict['value']
                  for value_count_dict in value_count_dicts]
        counts = [value_count_dict['count']
                  for value_count_dict in value_count_dicts]

        df = pd.DataFrame({
            "value": values,
            "count": counts,
        })

        bars = alt.Chart(df).mark_bar(size=20).encode(
            x='count:Q',
            y="value:O"
        ).properties(width=200, autosize="fit")

        chart = bars.to_json()

        new_block = {
            "content_block_type": "graph",
            "header": "Value Counts",
            "graph": chart,
            "styling": {
                "classes": ["col-4"],
                "styles": {
                    "margin-top": "20px",
                }
            }
        }

        content_blocks.append(new_block)

    @classmethod
    def _render_unrecognized(cls, evrs, content_blocks):
        unrendered_blocks = []
        new_block = None
        for evr in evrs:
            if evr["expectation_config"]["expectation_type"] not in [
                "expect_column_to_exist",
                "expect_column_values_to_be_of_type",
                "expect_column_values_to_be_in_set",
                "expect_column_unique_value_count_to_be_between",
                "expect_column_proportion_of_unique_values_to_be_between",
                "expect_column_values_to_not_be_null",
                "expect_column_max_to_be_between",
                "expect_column_mean_to_be_between",
                "expect_column_min_to_be_between"
            ]:
                new_block = {
                    "content_block_type": "text",
                    "content": []
                }
                new_block["content"].append("""
    <div class="alert alert-primary" role="alert">
        Warning! Unrendered EVR:<br/>
    <pre>"""+json.dumps(evr, indent=2)+"""</pre>
    </div>
                """)

        if new_block is not None:
            unrendered_blocks.append(new_block)

        # print(unrendered_blocks)
        content_blocks += unrendered_blocks


class PrescriptiveColumnSectionRenderer(ColumnSectionRenderer):

    @classmethod
    def _render_header(cls, expectations, content_blocks):
        column = cls._get_column_name(expectations)

        content_blocks.append({
            "content_block_type": "header",
            "header": column
        })

        return expectations, content_blocks

    @classmethod
    def _render_bullet_list(cls, expectations, content_blocks):
        content = PrescriptiveBulletListContentBlockRenderer.render(
            expectations,
            include_column_name=False,
        )
        content_blocks.append(content)

        return [], content_blocks

    @classmethod
    def render(cls, expectations):
        column = cls._get_column_name(expectations)

        remaining_expectations, content_blocks = cls._render_header(
            expectations, [])
        # remaining_expectations, content_blocks = cls._render_column_type(
        # remaining_expectations, content_blocks)
        remaining_expectations, content_blocks = cls._render_bullet_list(
            remaining_expectations, content_blocks)

        return {
            "section_name": column,
            "content_blocks": content_blocks
        }
