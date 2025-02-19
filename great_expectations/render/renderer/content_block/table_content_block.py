from .content_block import ContentBlockRenderer


class TableContentBlockRenderer(ContentBlockRenderer):

    @classmethod
    def render(cls, ge_object, header_row=[]):
        """Each expectation method should return a list of rows"""
        if isinstance(ge_object, list):
            table_entries = []
            for sub_object in ge_object:
                expectation_type = cls._get_expectation_type(sub_object)
                extra_rows_fn = getattr(cls, expectation_type, None)
                if extra_rows_fn is not None:
                    rows = extra_rows_fn(sub_object)
                    table_entries.extend(rows)
        else:
            table_entries = []
            expectation_type = cls._get_expectation_type(ge_object)
            extra_rows_fn = getattr(cls, expectation_type, None)
            if extra_rows_fn is not None:
                rows = extra_rows_fn(ge_object)
                table_entries.extend(rows)

        return {
            "content_block_type": "table",
            "header_row": header_row,
            "table_rows": table_entries
        }

    @classmethod
    def expect_column_values_to_not_match_regex(cls, ge_object):
        regex = ge_object["expectation_config"]["kwargs"]["regex"]
        unexpected_count = ge_object["result"]["unexpected_count"]
        if regex == '^\\s+|\\s+$':
            return [["Leading or trailing whitespace (n)", unexpected_count]]
        else:
            return [["Regex: %s" % regex, unexpected_count]]

    @classmethod
    def expect_column_unique_value_count_to_be_between(cls, ge_object):
        observed_value = ge_object["result"]["observed_value"]
        return [["Distinct (n)", observed_value]]

    @classmethod
    def expect_column_proportion_of_unique_values_to_be_between(cls, ge_object):
        observed_value = ge_object["result"]["observed_value"]
        if not observed_value:
            return [["Distinct (%)", "--"]]
        else:
            return [["Distinct (%)", "%.1f%%" % (100*observed_value)]]

    @classmethod
    def expect_column_max_to_be_between(cls, ge_object):
        observed_value = ge_object["result"]["observed_value"]
        return [["Max", observed_value]]

    @classmethod
    def expect_column_mean_to_be_between(cls, ge_object):
        observed_value = ge_object["result"]["observed_value"]
        return [["Mean", observed_value]]

    @classmethod
    def expect_column_values_to_not_be_null(cls, ge_object):
        return [
            ["Missing (n)", ge_object["result"]["unexpected_count"]],
            ["Missing (%)", "%.1f%%" %
             (ge_object["result"]["unexpected_percent"] * 100.0)]
        ]

    @classmethod
    def expect_column_values_to_be_null(cls, ge_object):
        return [
            ["Populated (n)", ge_object["result"]["unexpected_count"]],
            ["Populated (%)", "%.1f%%" %
             ge_object["result"]["unexpected_percent"]]
        ]
