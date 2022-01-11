#!/usr/bin/python
# -*- coding: utf8
import time
from pathlib import Path

from pywebio import config
from pywebio import start_server
from pywebio.input import *
from pywebio.output import *
from pywebio.pin import *
from pywebio.session import download, go_app, run_js, set_env

from sqlgen import ddlgenerator, reader
from sqlgen.cli import parse_sheets

cache_dir = Path(__file__).parent.parent.joinpath(".cache")
if not cache_dir.exists():
    cache_dir.mkdir(parents=True, exist_ok=True)

toast_duration = 2


def get_existing_docs():
    return list(cache_dir.glob("*.xlsx"))


def refresh_page():
    run_js("window.location.reload()")


def go_back(callback=refresh_page):
    put_button("Back", color="dark", onclick=callback, small=True)


def page_header():
    set_env(title="sqlgen", auto_scroll_bottom=True)
    put_link("Home\t\t", app="main")
    put_link("Documents", app="documents")
    put_markdown(
        """
    # sqlgen
    Infers SQL DDL (Data Definition Language) from template file.
    
    details: http://git.patsnap.com/wangzhiwei/sqlgen
    
    """
    )


def delete_file(file: Path):
    if isinstance(file, str):
        file = Path(file)
    file.unlink(missing_ok=True)
    return file


def delete(selected):
    if not selected:
        toast("No documents selected", duration=toast_duration, color="warning")
        return
    deleted = list()
    for doc in selected:
        ret = delete_file(doc)
        deleted.append(ret.name)
    toast(f"{','.join(deleted)} deleted", duration=toast_duration, color="success")
    time.sleep(toast_duration)
    refresh_page()


@config(theme="minty")
def documents():
    page_header()
    put_markdown(
        f"""
        ## documents manage
    """
    )
    options = [{"label": _.name, "value": str(_)} for _ in get_existing_docs()]
    if options:
        put_checkbox(name="selected", options=options, label="Select documents")
        put_button("Delete", onclick=lambda: delete(pin.selected), small=True)
    else:
        put_text("No documents exist")
        go_back(lambda: go_app("home"))


@config(theme="minty")
def main():
    page_header()
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
            go_back()
            return
    else:
        doc = data["doc"]
        if not doc:
            put_warning("No file selected or uploaded!")
            go_back()
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
        go_back()
        return

    put_markdown(
        f"""
    **document:** {doc_name}
    **sheets:** {sheets}
    """
    )
    put_collapse(
        "ddl.sql",
        [
            put_code(f"{clauses}", language="sql"),
        ],
        open=True,
    )

    def btn_download():
        download("ddl.sql", clauses.encode("utf8"))

    put_buttons(
        buttons=[
            dict(label="Download", value="download", color="primary"),
            dict(label="Back", value="back", color="dark"),
        ],
        onclick=[btn_download, refresh_page],
        small=True,
    )


@config(theme="minty")
def index():
    main()


if __name__ == "__main__":
    start_server([index, main, documents], port=8080)
