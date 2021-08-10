#!/usr/bin/python
# -*- coding: utf8

import logging
import re

import xlrd

from sqlgen.exceptions import InValidReservedWords, InValidTemplate
from sqlgen.reserved import is_reserved_words

logger = logging.getLogger(__name__)


def parse(file_path, read_type="excel", **kwargs):
    if read_type == "excel":
        return Excel.parse(file_path, **kwargs)
    return


def _convert_key(key):
    if not key:
        return

    keys = {
        '主键': 'PRIMARY',
        'PRI': 'PRIMARY',
        '索引': 'INDEX',
        'MUL': 'INDEX',
        '普通索引': 'INDEX',
        '唯一索引': 'UNIQUE',
        '唯一键': 'UNIQUE',
        'UNI': 'UNIQUE',
    }
    key = keys[key]
    if not is_reserved_words(key):
        raise InValidReservedWords(f"invalid sql reserverd words: {key}")
    return key


def _convert_extra(attributes):
    if not isinstance(attributes, str):
        raise InValidTemplate(f"Invalid template value: {attributes}")
    attr = [_.strip().upper() for _ in attributes.split(",") if _]
    return attr or None


def _convert_length(length):
    if not length:
        return

    if isinstance(length, str):
        # 全角转半角
        length = length.replace("，", ",")
        if "," in length:
            length = tuple(int(_.strip()) for _ in length.split(",") if re.match(r'\d+', _.strip()))
        elif re.match(r'\d+', length):
            length = int(length)
        else:
            raise InValidTemplate(f"Invalid template Length: {length!r}")
    elif isinstance(length, (int, float)):
        length = int(length)

    if isinstance(length, (int, tuple)):
        return length

    return


def _convert(field):
    ret = dict()
    ret["Name"] = field["Field"].strip()
    ret["Type"] = field["Type"].upper()
    ret["Length"] = _convert_length(field["Length"])
    ret["Null"] = False if field["Null"].upper() == "N" else True
    ret["Default"] = field["Default"].strip() if isinstance(field["Default"], str) else field["Default"]
    ret["Key"] = _convert_key(field["Key"].strip().upper())
    ret["Extra"] = _convert_extra(field["Extra"].strip())
    ret["Comment"] = field["Comment"].strip()

    return ret


class Excel:
    @staticmethod
    def read(file_path, index=0):
        """read MS Excel and return dicts form of generator
        @param: xls_file: name of excel file
        @param: index: index of Excel worksheets
        """

        book = xlrd.open_workbook(file_path)
        logger.debug("The number of worksheets is {0}".format(book.nsheets))
        logger.debug("Worksheet name(s): {0}".format(book.sheet_names()))

        sheet = book.sheet_by_index(index)
        logger.debug("{0} rows: {1} columns: {2}\n".format(sheet.name, sheet.nrows, sheet.ncols))

        rows = [sheet.row_values(rx) for rx in range(sheet.nrows)]
        return rows

    @staticmethod
    def _is_seq(seq):
        if isinstance(seq, (float, int)):
            return True
        elif isinstance(seq, str) and seq.isdigit():
            return True
        return False

    @staticmethod
    def _is_header(word):
        if isinstance(word, str):
            if word == "序号" or word.lower() == "seq":
                return True
        return False

    @staticmethod
    def _convert_header(row):
        header = {
            "字段名称": "Field",
            "字段中文名": "Comment",
            "字段类型": "Type",
            "字段长度": "Length",
            "能否为空": "Null",
            "默认值": "Default",
            "字段属性": "Key",
            "附加属性": "Extra",
        }
        if len(set(row) & set(header.values())) == len(header):
            return row
        elif len(set(row) & set(header.keys())) == len(header):
            return [header[_] if _ in header else _ for _ in row]
        else:
            raise InValidTemplate(f"Invalid template header: {row}")

    @staticmethod
    def parse(file_path, index=0):
        rows = Excel.read(file_path, index)
        db_name = ""
        table_name = ""
        table_name_zh = ""
        header = list()
        values = list()
        seq = 1
        for row in rows:
            if row[0] == '库名':
                db_name = row[1]
            elif row[0] == '表名':
                table_name = row[1]
            elif row[0] == '表中文名':
                table_name_zh = row[1]
            elif Excel._is_header(row[0]):
                header = Excel._convert_header(row)
            elif Excel._is_seq(row[0]):
                if int(row[0]) == seq:
                    values.append(row)
                    seq += 1

        header = [_.title() for _ in header]
        fields = [_convert(dict(zip(header, val))) for val in values]
        if not table_name or not header or not fields:
            raise InValidTemplate(f"Invalid template, please check file: {file_path}")

        logger.debug(f"Database: {db_name}\tTable: {table_name}\tFields: {[x['Name'] for x in fields]}")
        template = dict()
        template["Table"] = table_name
        template["Table_zh"] = table_name_zh
        template["Fields"] = fields
        # template["ENGINE"] = ""
        # template["AUTO_INCREMENT"] = ""
        # template["CHARSET"] = ""
        # template["ROW_FORMAT"] = ""
        return template
