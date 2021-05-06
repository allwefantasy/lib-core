# lib-core

## dataset

### vega_datasets

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

### vega_datasets_visual

Visualize vega_datasets.

```sql
load parquet.`/tmp/veca_datasets` as data;

set inputTable="data";
include local.`libCore.dataset.vega_datasets_visual`;
```
