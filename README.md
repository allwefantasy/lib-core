# lib-core

## Demo Data From Python

### vega_datasets

Make sure python lib vega_datasets installed.  
Then you can save the vega_datasets to any path with
following code:

```sql
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

### 

