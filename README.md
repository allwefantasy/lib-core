# lib-core

For Ray 0.8.0：

```
pip install Cython
pip install pyarrow==0.10.0
pip install ray==0.8.0
pip install aiohttp psutil setproctitle grpcio pandas xlsxwriter==1.2.0 xlrd==1.2.0
pip install watchdog requests click uuid sfcli
pip install pyjava==0.2.8.3
```

For Ray 1.3.0：

```
pip install Cython
pip install ray==1.3.0
pip install aiohttp psutil setproctitle grpcio pandas xlsxwriter==1.2.0 xlrd==1.2.0
pip install watchdog requests click uuid sfcli
pip install pyjava==0.2.8.5
```

Conda recommended.

## dataset.vega_datasets

Make sure python lib vega_datasets installed.  
Then you can save the vega_datasets to any path with
following code:

```sql
-- if you are in china, please replace github.com with gitee.com.
include lib.`github.com/allwefantasy/lib-core` where 
alias="libCore";

-- set pythonEnv="source activate dev";
-- once vega_datasets.mlsql is inclued then you
-- you have `!dumpData` command available.
include local.`libCore.dataset.vega_datasets`;

-- dump data to object store
!dumpData /tmp/veca_datasets;

-- Check the data
load parquet.`/tmp/veca_datasets` as output;
```

### dataset.vega_datasets_visual

Visualize vega_datasets.

```sql
load parquet.`/tmp/veca_datasets` as data;

set inputTable="data";
include local.`libCore.dataset.vega_datasets_visual`;
```
