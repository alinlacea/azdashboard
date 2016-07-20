Azurelib - Library for Azure Storage Services
=============================================

# Contents
* Flow
* Entities
	* Queue messages
	* Table entities
* Error handling

* * *

# Flow
Prerequisites:

* `from azurelib.core.connection import AzConnection`
* packages:
	* Azure
	* Wrapt

## Queues
Main steps:

```python
	connection = AzConnection('username', 'azure_key')
	queue = connection.queue() # or queue = connection.queue('queue_name')
	queue.select('queue_name') # if name not provided above
	messages = queue.pop()
	for msg in messages:
			print msg
			queue.delete_message(msg)
	queue.purge()
```

## Tables
Main steps:

```python
	connection = AzConnection('username', 'azure_key')
	table = connection.table() # or table = connection.table('table_name')
	table.select('table_name') # if name not provided above
	table.set_partition('partition_key')
	entity = {
		"RowKey": 'row_key',
		"column_1" 1
	}
	table.insert(entity)
```

* * *

# Entities
## Queue messages
## Table entities

* * *

# Error handling
