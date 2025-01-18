#!/bin/bash

# Start SSH service
service ssh start

# Apply SQLite configuration
sqlite3 <<EOF
.load /usr/lib/sqlite3/pcompress
.load /usr/lib/sqlite3/pjson1
.load /usr/lib/sqlite3/pdbstat
.load /usr/lib/sqlite3/psqlite_db_config
EOF

# Run the main application
python src/main.py