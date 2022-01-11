#!/usr/bin/python
# -*- coding: utf8

from pathlib import Path

from pywebio import config
from pywebio import start_server
from pywebio.input import *
from pywebio.output import *
from pywebio.session import download, run_js, set_env

from sqlgen import ddlgenerator, reader
from sqlgen.cli import parse_sheets

cache_dir = Path(__file__).parent.parent.joinpath(".cache")
if not cache_dir.exists():
    cache_dir.mkdir(parents=True, exist_ok=True)


def get_existing_docs():
    return list(cache_dir.glob("*.xlsx"))


def btn_back():
    run_js("window.location.reload()")


def click_back():
    put_button("Back", color="dark", onclick=btn_back, small=True)


@config(theme="minty")
def main():
    set_env(title="sqlgen", auto_scroll_bottom=True)

    put_markdown(
        """
    # sqlgen
    Infers SQL DDL (Data Definition Language) from template file.
    
    details: http://git.patsnap.com/wangzhiwei/sqlgen
    """
    )
    inputs = [
        file_upload(
            "Upload new document:",
            name="doc",
            accept=".xlsx",
            multiple=False,
            required=False,
        ),
        input(
            "Select sheets:",
            name="sheets",
            type="text",
            placeholder="eg: 1/1,3/1-5 default 0",
        ),
    ]
    existing_docs = get_existing_docs()
    if existing_docs:
        doc_options = [
            {
                "label": _.name,
                "value": str(_),
            }
            for _ in existing_docs
        ]
        doc_input = radio(
            "Existing documents",
            name="existing_docs",
            options=doc_options,
            multiple=False,
        )
        inputs.insert(
            0,
            doc_input,
        )

    data = input_group(
        "Generate DDL SQL",
        inputs,
    )
    sheets = data["sheets"]
    if not sheets:
        sheets = "0"

    if data.get("existing_docs") is not None:
        template = data["existing_docs"]
        doc_name = Path(template).name
        if not Path(template).exists():
            put_warning(f"missing file: {template}!")
            click_back()
            return
    else:
        doc = data["doc"]
        if not doc:
            put_warning("No file selected or uploaded!")
            click_back()
            return
        template = cache_dir.joinpath(doc["filename"])
        doc_name = doc["filename"]
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
        click_back()
        return

    put_markdown(
        f"""
    **document:** {doc_name}
    **sheets:** {sheets}
    """
    )
    put_code(f"{clauses}", language="sql")

    def btn_download():
        download("ddl.sql", clauses.encode("utf8"))

    put_buttons(
        buttons=[
            dict(label="Download", value="download", color="primary"),
            dict(label="Back", value="back", color="dark"),
        ],
        onclick=[btn_download, btn_back],
        small=True,
    )


if __name__ == "__main__":
    start_server(main, port=8080)
