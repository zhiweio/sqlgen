#!/usr/bin/python
# -*- coding: utf8

import logging

from sqlgen import reserved
from sqlgen.exceptions import InValidReservedWords
from sqlgen.reserved import is_reserved_words

logger = logging.getLogger(__name__)


class Field:
    def __init__(self, name, data_type, length=None, extra_attributes=None, null=True, default=None, comment=None,
                 key=None):
        self.Name = name
        self.Type = data_type
        self.Length = length
        self.Extra = extra_attributes
        self.Null = null
        self.Default = default
        self.Comment = comment
        self.Key = key
        self._judge()

    def __hash__(self):
        return hash(self.Name)

    def __eq__(self, other):
        if type(self) == type(other):
            return self.Name == other.Name
        return False

    def __repr__(self):
        return f"Field(" \
               f"name={self.Name!r}," \
               f"data_type={self.Type!r}," \
               f"length={self.Length!r}," \
               f"extra_attributes={self.Extra!r}," \
               f"null={self.Null!r}," \
               f"comment={self.Comment!r}," \
               f"key={self.Key!r}" \
               f")"

    def clause(self):
        if isinstance(self.Length, int):
            dtype = f"{self.Type}({self.Length})"
        elif isinstance(self.Length, tuple):
            dtype = f"{self.Type}{self.Length!r}"
        else:
            dtype = self.Type

        null = "NOT NULL" if not self.Null else ""

        if isinstance(self.Default, (int, float)) \
                or is_reserved_words(self.Default) \
                or isinstance(self.Default, str):
            default = f"DEFAULT {self.Default}"
        else:
            default = ""

        extra = " ".join(self.Extra or list())
        comment = f"COMMENT \"{self.Comment}\"" if self.Comment else ""

        sql_str = f"`{self.Name}` {dtype} {null} {default} {extra} {comment}"
        return sql_str

    def _judge(self):
        self._judge_default()
        self._judge_length()
        self._judge_reserved_words(self.Type)
        for word in [self.Extra, self.Key]:
            if word:
                self._judge_reserved_words(word)

    @staticmethod
    def _judge_reserved_words(words):
        if not is_reserved_words(words):
            raise InValidReservedWords(f"invalid sql reserverd words: {words}")

    def _judge_default(self):
        if not self.Default:
            if self.Type in reserved.DEFAULT_EMPTY_STRING:
                self.Default = "\"\""
            else:
                self.Default = None
        else:
            if isinstance(self.Default, float) and (self.Default % 1) == 0.0:
                self.Default = int(self.Default)
                # 转换数值单元格式中的数字字符串
                if self.Type in reserved.DEFAULT_EMPTY_STRING:
                    self.Default = str(self.Default)
            if isinstance(self.Default, str):
                self.Default = f"\"{self.Default}\""

    def _judge_length(self):
        if self.Type in reserved.DATE_AND_TIME:
            self.Length = None

    def is_primary(self):
        return self.Key == "PRIMARY"

    def is_index(self):
        return self.Key == "INDEX"

    def is_unique(self):
        return self.Key == "UNIQUE"


class Table:
    def __init__(self, name, columns, engine="InnoDB", auto_increment=0, charset="utf8mb4", row_format="DYNAMIC"):
        self.name = name
        self.pk = self.find_pk(columns)
        self.uk = self.find_uk(columns)
        self.idx = self.find_index(columns)
        self.columns = columns
        self.engine = engine
        self.charset = charset
        self.row_format = row_format
        self.auto_increment = auto_increment

    @staticmethod
    def find_pk(columns):
        for _ in columns:
            if _.is_primary():
                return _
        return

    @staticmethod
    def find_uk(columns):
        uk = list()
        for _ in columns:
            if _.is_unique():
                uk.append(_)
        return uk

    @staticmethod
    def find_index(columns):
        idx = list()
        for _ in columns:
            if _.is_index():
                idx.append(_)
        return idx

    def clause(self):
        columns = "\t\t, ".join([f"{c.clause()}\n" for c in self.columns])
        keys = list()
        if self.pk:
            keys.append(f"PRIMARY KEY (`{self.pk.Name}`)")
        if self.idx:
            for x in self.idx:
                keys.append(f"INDEX `{x.Name}_index` USING BTREE(`{x.Name}`)")
        if self.uk:
            uk = ",".join([f"`{_.Name}`" for _ in self.uk])
            keys.append(f"UNIQUE KEY ({uk})")
        keys = "\t, ".join([f"{k}\n" for k in keys])
        engine = f"ENGINE={self.engine}" if self.engine else ""
        auto_increment = f"AUTO_INCREMENT={self.auto_increment}" if isinstance(self.auto_increment, int) else ""
        charset = f"DEFAULT CHARSET={self.charset}" if self.charset else ""
        row_format = f"ROW_FORMAT={self.row_format}" if self.row_format else ""
        sql_str = f"""
CREATE TABLE 
    IF NOT EXISTS `{self.name}`
    (
      \t\t{columns}
      \t, {keys}
    )
    {engine} {auto_increment} {charset} {row_format}
;
"""
        return sql_str


def parse(template):
    table_name = template["Table"]
    columns = list()
    for c in template["Fields"]:
        field = Field(
            name=c["Name"],
            data_type=c["Type"],
            length=c["Length"],
            extra_attributes=c["Extra"],
            null=c["Null"],
            comment=c["Comment"],
            default=c["Default"],
            key=c['Key']
        )
        columns.append(field)

    engine = template.get("ENGINE") or "InnoDB"
    charset = template.get("CHARSET") or "utf8mb4"
    auto_increment = template.get("AUTO_INCREMENT") or 0
    row_format = template.get("ROW_FORMAT") or "DYNAMIC"

    table = Table(
        table_name,
        columns,
        engine=engine,
        charset=charset,
        auto_increment=auto_increment,
        row_format=row_format
    )
    return table
