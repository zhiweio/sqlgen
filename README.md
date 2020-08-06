# SQLGEN

Infers SQL DDL (Data Definition Language) from template file

### Install

```bash
$ git clone http://git.qixin007.com/zhiwei/sqlgen  && cd sqlgen/
$ python setup install --user
```

### Usage

```bash
$ sqlgen -h
Usage: sqlgen [OPTIONS]

Options:
  -V, --version        Show the version and exit.
  -t, --template PATH  file template
  --index INTEGER      index of excel sheets  [default: 0]
  -o, --output PATH    Save task template into file
  --debug-file PATH    File to be used as a stream for DEBUG logging
  -v, --verbose        Print debug information
  -h, --help           Show this message and exit.
```

```bash
$ sqlgen -t tests/excel_template.xlsx

CREATE TABLE
    IF NOT EXISTS `t_sz_ipoguidancestate`
    (
                `id` BIGINT(20) NOT NULL  AUTO_INCREMENT COMMENT "自增主键"
                , `credit_no` VARCHAR(255) NOT NULL   COMMENT "社会信用代码"
                , `name` VARCHAR(255)    COMMENT "企业名称"
                , `eid` CHAR(36)    COMMENT "企业ID"
                , `updatedate` DATETIME    COMMENT "最新变更日期"
                , `type` VARCHAR(200)    COMMENT "辅导企业公司类型"
                , `csrc` VARCHAR(20)    COMMENT "所属证监局"
                , `guidanceagency` VARCHAR(200)    COMMENT "辅导机构"
                , `url` VARCHAR(1000)    COMMENT "公告网址"
                , `recorddate` DATETIME    COMMENT "辅导备案日"
                , `submissiondate` DATETIME    COMMENT "报送备案登记材料日"
                , `reportdate` DATETIME    COMMENT "出具辅导监管报告日期"
                , `progressreportdate` DATETIME    COMMENT "最近一期递交辅导进展报告日期"
                , `changesponsordate` DATETIME    COMMENT "更换保荐机构日"
                , `summaryreportdate` DATETIME    COMMENT "IPO辅导总结报告日期"
                , `terminationdate` DATETIME    COMMENT "终止辅导日期"
                , `signdate` DATETIME    COMMENT "签署辅导协议日"
                , `otherdate` DATETIME    COMMENT "其他重要日期"
                , `status` VARCHAR(255)    COMMENT "当前辅导状态"
                , `accountingfirm` VARCHAR(255)    COMMENT "会计师事务所"
                , `legaladvisor` VARCHAR(255)    COMMENT "律师事务所"
                , `source` CHAR(20)    COMMENT "数据来源"
                , `u_tags` TINYINT(3)    COMMENT "是否隐藏"
                , `create_time` BIGINT(20)    COMMENT "记录创建时间"
                , `row_update_time` DATETIME   ON UPDATE CURRENT_TIMESTAMP COMMENT "记录更新时间"

        , PRIMARY KEY (`id`)
        , INDEX `credit_no_index` USING btree(`credit_no`)
        , INDEX `eid_index` USING btree(`eid`)

    )
    ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC
;
```

## Design

### Key Words

**Field:** str

**Type(Data Types):**

1. Numeric Data Types
   * INTEGER, INT, SMALLINT, TINYINT, MEDIUMINT, BIGINT
   * DECIMAL, NUMERIC
   * FLOAT, DOUBLE
   * BIT
2. Date and Time Data Types
   * DATE, DATETIME, TIMESTAMP
   * TIME
   * YEAR
3. String Data Types
   * CHAR, VARCHAR, BINARY, VARBINARY, BLOB, TEXT, ENUM, SET
4. Spatial Data Types
5. The JSON Data Types

**Length**: int

**Extra:**

- BINARY
- UNSIGNED
- UNSIGNED ZEROFILL
- AUTO_INCREMENT
- ON UPDATE CURRENT_TIMESTAMP

**Default:**

- NULL
- CURRENT_TIMESTAMP
- Customize

**Null:**

- Y
- N

**Comment:** str

**Key:**

- PRIMARY
- INDEX
- UNIQUE
- FULLTEXT
- SPATIAL

### JSON Template

```json
{
    "Table": "t_test",
    "Fields": [
        {
            "Name": "id",
            "Type": "BIGINT",
            "Length": 20,
            "Extra": ["UNSIGNED", "AUTO_INCREMENT"],
            "Null": false,
            "Comment": "自增主键",
            "Key": "PRIMARY"
        },
        {
            "Name": "credit_no",
            "Type": "VARCHAR",
            "Length": 255,
            "Default": "",
            "Null": false,
            "Comment": "社会信用代码",
            "Key": "INDEX"
        },
        {
            "Name": "name",
            "Type": "VARCHAR",
            "Length": 255,
            "Default": "",
            "Null": true,
            "Comment": "企业名称"
        },
        {
            "Name": "updatedate",
            "Type": "DATETIME",
            "Null": true,
            "Comment": "最新变更日期"
        },
        {
            "Name": "row_update_time",
            "Type": "DATETIME",
            "Extra": ["ON UPDATE CURRENT_TIMESTAMP"],
            "Default": "CURRENT_TIMESTAMP",
            "Comment": "记录更新时间"
        }
    ],
    "ENGINE": "InnoDB",
    "AUTO_INCREMENT": 0,
    "CHARSET": "utf8mb4",
    "ROW_FORMAT": "DYNAMIC"
}
```

### API

```python
from sqlgen import ddlgenerator

# template.json 内容格式见 `JSON Template`
with open('template.json') as f:
    template =  json.load(f)
    table = ddlgenerator.parse(template)
    sql = table.clause()

```
