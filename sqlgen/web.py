#!/usr/bin/python
# -*- coding: utf8

from pathlib import Path

from pywebio import config
from pywebio import start_server
from pywebio.input import file_upload, input, input_group
from pywebio.output import put_buttons, put_code, put_error, put_markdown, put_warning
from pywebio.session import download, set_env

from sqlgen import ddlgenerator, reader
from sqlgen.cli import parse_sheets

cache_dir = Path(__file__).parent.parent.joinpath(".cache")
if not cache_dir.exists():
    cache_dir.mkdir(parents=True, exist_ok=True)


@config(theme="minty")
def main():
    set_env(auto_scroll_bottom=True)

    put_markdown(
        """
    # sqlgen
    Infers SQL DDL (Data Definition Language) from template file.
    
    details: http://git.patsnap.com/wangzhiwei/sqlgen
    """
    )

    data = input_group(
        "Generate DDL SQL",
        [
            file_upload("Upload document:", name="doc", accept=".xlsx", multiple=False),
            input(
                "Select sheets:",
                name="sheets",
                type="text",
                placeholder="eg: 1/1,3/1-5 default 0",
            ),
        ],
    )
    sheets = data["sheets"]
    doc = data["doc"]
    if not doc:
        put_warning("No file or upload failed!")
        return

    template = cache_dir.joinpath(doc["filename"])
    with open(template, "wb") as f:
        f.write(doc["content"])

    clauses = list()
    try:
        for sheet in parse_sheets(sheets):
            template_data = reader.parse(template, index=sheet)
            table = ddlgenerator.parse(template_data)
            sql = table.clause()
            clauses.append(sql)

        clauses = "\n".join(clauses)
    except Exception as e:
        put_error(e)
        return

    put_markdown(
        f"""
    **document:** {doc["filename"]}
    **sheets:** {sheets}
    """
    )
    put_code(f"{clauses}", language="sql")
    put_buttons(
        ["Download SQL"],
        lambda _: download("ddl.sql", clauses.encode("utf8")),
        small=True,
    )


if __name__ == "__main__":
    start_server(main, port=8080)
