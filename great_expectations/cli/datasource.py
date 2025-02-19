import os
import click

from .util import cli_message
from great_expectations.render import DefaultJinjaPageView
from great_expectations.version import __version__ as __version__


def add_datasource(context):
    cli_message(
        """
========== Datasources ==========

See <blue>https://docs.greatexpectations.io/en/latest/core_concepts/datasource.html?utm_source=cli&utm_medium=init&utm_campaign={0:s}</blue> for more information about datasources.
""".format(__version__.replace(".", "_"))
    )
    data_source_selection = click.prompt(
        msg_prompt_choose_data_source,
        type=click.Choice(["1", "2", "3", "4"]),
        show_choices=False
    )

    cli_message(data_source_selection)

    if data_source_selection == "1":  # pandas
        path = click.prompt(
            msg_prompt_filesys_enter_base_path,
            # default='/data/',
            type=click.Path(
                exists=False,
                file_okay=False,
                dir_okay=True,
                readable=True
            ),
            show_default=True
        )
        if path.startswith("./"):
            path = path[2:]

        if path.endswith("/"):
            basenamepath = path[:-1]
        else:
            basenamepath = path

        default_data_source_name = os.path.basename(basenamepath) + "__dir"
        data_source_name = click.prompt(
            msg_prompt_datasource_name,
            default=default_data_source_name,
            show_default=True
        )

        context.add_datasource(data_source_name, "pandas",
                               base_directory=os.path.join("..", path))

    elif data_source_selection == "2":  # sqlalchemy
        data_source_name = click.prompt(
            msg_prompt_datasource_name, default="mydb", show_default=True)

        cli_message(msg_sqlalchemy_config_connection.format(
            data_source_name))

        drivername = click.prompt("What is the driver for the sqlalchemy connection?", default="postgres",
                                  show_default=True)
        host = click.prompt("What is the host for the sqlalchemy connection?", default="localhost",
                            show_default=True)
        port = click.prompt("What is the port for the sqlalchemy connection?", default="5432",
                            show_default=True)
        username = click.prompt("What is the username for the sqlalchemy connection?", default="postgres",
                                show_default=True)
        password = click.prompt("What is the password for the sqlalchemy connection?", default="",
                                show_default=False, hide_input=True)
        database = click.prompt("What is the database name for the sqlalchemy connection?", default="postgres",
                                show_default=True)

        credentials = {
            "drivername": drivername,
            "host": host,
            "port": port,
            "username": username,
            "password": password,
            "database": database
        }
        context.add_profile_credentials(data_source_name, **credentials)

        context.add_datasource(
            data_source_name, "sqlalchemy", profile=data_source_name)

    elif data_source_selection == "3":  # Spark
        path = click.prompt(
            msg_prompt_filesys_enter_base_path,
            default='/data/',
            type=click.Path(
                exists=True,
                file_okay=False,
                dir_okay=True,
                readable=True
            ),
            show_default=True
        )
        if path.startswith("./"):
            path = path[2:]

        if path.endswith("/"):
            basenamepath = path[:-1]
        default_data_source_name = os.path.basename(basenamepath)
        data_source_name = click.prompt(
            msg_prompt_datasource_name, default=default_data_source_name, show_default=True)

        context.add_datasource(data_source_name, "spark", base_directory=path)

    # if data_source_selection == "5": # dbt
    #     dbt_profile = click.prompt(msg_prompt_dbt_choose_profile)
    #     log_message(msg_dbt_go_to_notebook, color="blue")
    #     context.add_datasource("dbt", "dbt", profile=dbt_profile)
    if data_source_selection == "4":  # None of the above
        cli_message(msg_unknown_data_source)
        print("Skipping datasource configuration. You can add a datasource later by editing the great_expectations.yml file.")
        return None

    if data_source_name != None:

        cli_message(
            """
========== Profiling ==========

Would you like to profile '{0:s}' to create candidate expectations and documentation?

Please note: As of v0.7.0, profiling is still a beta feature in Great Expectations.  
This generation of profilers will evaluate the entire data source (without sampling) and may be very time consuming. 
As a rule of thumb, we recommend starting with data smaller than 100MB.

To learn more about profiling, visit <blue>https://docs.greatexpectations.io/en/latest/guides/profiling.html?utm_source=cli&utm_medium=init&utm_campaign={1:s}</blue>.
            """.format(data_source_name, __version__.replace(".", "_"))
        )
        if click.confirm("Proceed?",
                         default=True
                         ):
            profiling_results = context.profile_datasource(
                data_source_name,
                max_data_assets=20
            )

            print("\nDone.\n\nProfiling results are saved here:")
            for profiling_result in profiling_results:
                data_asset_name = profiling_result[1]['meta']['data_asset_name']
                expectation_suite_name = profiling_result[1]['meta']['expectation_suite_name']
                run_id = profiling_result[1]['meta']['run_id']

                print("  {0:s}".format(context.get_validation_location(
                    data_asset_name, expectation_suite_name, run_id)['filepath']))

            cli_message(
                """
========== Data Documentation ==========

To generate documentation from the data you just profiled, the profiling results should be moved from 
great_expectations/uncommitted (ignored by git) to great_expectations/fixtures.

Before committing, please make sure that this data does not contain sensitive information!

To learn more: <blue>https://docs.greatexpectations.io/en/latest/guides/data_documentation.html?utm_source=cli&utm_medium=init&utm_campaign={0:s}</blue>
""".format(__version__.replace(".", "_"))
            )
            if click.confirm("Move the profiled data and build HTML documentation?",
                             default=True
                             ):
                cli_message("\nMoving files...")

                for profiling_result in profiling_results:
                    data_asset_name = profiling_result[1]['meta']['data_asset_name']
                    expectation_suite_name = profiling_result[1]['meta']['expectation_suite_name']
                    run_id = profiling_result[1]['meta']['run_id']
                    context.move_validation_to_fixtures(
                        data_asset_name, expectation_suite_name, run_id)

                cli_message("\nDone.")

                cli_message("\nBuilding documentation...")

                context.render_full_static_site()
                cli_message(
                    """
To view the generated data documentation, open this file in a web browser:
    <green>great_expectations/uncommitted/documentation/index.html</green>
""")
            else:
                cli_message(
                    "Okay, skipping HTML documentation for now.`."
                )

        else:
            cli_message(
                "Okay, skipping profiling for now. You can always do this later by running `great_expectations profile`."
            )

    if data_source_selection == "1":  # Pandas
        cli_message(msg_filesys_go_to_notebook)

    elif data_source_selection == "2":  # SQL
        cli_message(msg_sqlalchemy_go_to_notebook)

    elif data_source_selection == "3":  # Spark
        cli_message(msg_spark_go_to_notebook)


msg_prompt_choose_data_source = """
Configure a datasource:
    1. Pandas DataFrame
    2. Relational database (SQL)
    3. Spark DataFrame
    4. Skip datasource configuration
"""

#     msg_prompt_dbt_choose_profile = """
# Please specify the name of the dbt profile (from your ~/.dbt/profiles.yml file Great Expectations \
# should use to connect to the database
#     """

#     msg_dbt_go_to_notebook = """
# To create expectations for your dbt models start Jupyter and open notebook
# great_expectations/notebooks/using_great_expectations_with_dbt.ipynb -
# it will walk you through next steps.
#     """

msg_prompt_filesys_enter_base_path = """
Enter the path of the root directory where the data files are stored.
(The path may be either absolute or relative to current directory.)
"""

msg_prompt_datasource_name = """
Give your new data source a short name.
"""

msg_sqlalchemy_config_connection = """
Great Expectations relies on sqlalchemy to connect to relational databases.
Please make sure that you have it installed.

Next, we will configure database credentials and store them in the "{0:s}" section
of this config file: great_expectations/uncommitted/credentials/profiles.yml:
"""

msg_unknown_data_source = """
We are looking for more types of data types to support.
Please create a GitHub issue here:
https://github.com/great-expectations/great_expectations/issues/new
In the meantime you can see what Great Expectations can do on CSV files.
To create expectations for your CSV files start Jupyter and open notebook
great_expectations/notebooks/using_great_expectations_with_pandas.ipynb -
it will walk you through configuring the database connection and next steps.
"""

msg_filesys_go_to_notebook = """
To create expectations for your data, start Jupyter and open a tutorial notebook:

To launch with jupyter notebooks:
    <green>jupyter notebook great_expectations/notebooks/create_expectations.ipynb</green>

To launch with jupyter lab:
    <green>jupyter lab great_expectations/notebooks/create_expectations.ipynb</green>
"""

msg_sqlalchemy_go_to_notebook = """
To create expectations for your data start Jupyter and open the notebook
that will walk you through next steps.

To launch with jupyter notebooks:
    <green>jupyter notebook great_expectations/notebooks/create_expectations.ipynb</green>

To launch with jupyter lab:
    <green>jupyter lab great_expectations/notebooks/create_expectations.ipynb</green>
"""

msg_spark_go_to_notebook = """
To create expectations for your data start Jupyter and open the notebook
that will walk you through next steps.

To launch with jupyter notebooks:
    <green>jupyter notebook great_expectations/notebooks/create_expectations.ipynb</green>

To launch with jupyter lab:
    <green>jupyter lab great_expectations/notebooks/create_expectations.ipynb</green>
"""
