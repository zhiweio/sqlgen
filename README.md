# SQLGEN

sqlgen 是一个从 Excel 文档模板自动生成建表 SQL 语句的小工具，支持命令行和 WebUI 使用，适用于经常进行数据库设计建表的场景。

### 安装

```bash
$ https://github.com/zhiweio/sqlgen.git  && cd sqlgen/
$ python3 setup.py install --user
```

### Excel 建表模板

Excel 文档模板及规范说明见：[数据产品建表需求文档模板v2.1.xlsx](doc/数据产品建表需求文档模板v2.1.xlsx)

![](./doc/template.png)

### Web 使用

```shell
$ python sqlgen/web.py
Running on all addresses.
Use http://127.0.0.1:8080/ to access the application

```

从 docker 运行
```shell
$ docker build -t sqlgen:1.0 .
$ docker run -d -p 8080:8080 sqlgen:1.0
```

从 dock-compose 运行
```shell
$ docker-compose up -d
```

input
![](./doc/run_on_web_input.png)

output
![](./doc/run_on_web_output.png)



### 命令行使用

```bash
$ sqlgen -h
Usage: sqlgen [OPTIONS]

Options:
  -V, --version        Show the version and exit.
  -t, --template PATH  file template
  -s, --sheets TEXT    index of excel sheets, eg: 1-6  [default: 0]
  -o, --output PATH    Save task template into file
  --debug-file PATH    File to be used as a stream for DEBUG logging
  -v, --verbose        Print debug information
  -h, --help           Show this message and exit.

```

读取 Excel 模板生成 SQL
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

从指定的工作簿生成 SQL
```bash
$ sqlgen -t tests/excel_template.xlsx --sheets 0
CREATE TABLE
    IF NOT EXISTS `t_sz_ipoguidancestate`

...
```

生成 SQL 并输出到指定文件
```bash
$ sqlgen -t tests/excel_template.xlsx -o tmp.sql
```

打印详细信息
```bash
$ sqlgen -t tests/excel_template.xlsx -v
2020-08-20 18:08:50,872 DEBUG reader.py[line:93] sqlgen.reader: The number of worksheets is 1
2020-08-20 18:08:50,873 DEBUG reader.py[line:94] sqlgen.reader: Worksheet name(s): ['Template']
2020-08-20 18:08:50,873 DEBUG reader.py[line:97] sqlgen.reader: Template rows: 37 columns: 16

2020-08-20 18:08:50,873 DEBUG reader.py[line:161] sqlgen.reader: Database: db_finance   Table: t_sz_ipoguidancestate    Fields: ['id', 'credit_no', 'name', 'eid', 'updatedate', 'type', 'csrc', 'guidanceagency', 'u
rl', 'recorddate', 'submissiondate', 'reportdate', 'progressreportdate', 'changesponsordate', 'summaryreportdate', 'terminationdate', 'signdate', 'otherdate', 'status', 'accountingfirm', 'legaladvisor', 'source',
'u_tags', 'create_time', 'row_update_time']

CREATE TABLE
    IF NOT EXISTS `t_sz_ipoguidancestate`

...
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
