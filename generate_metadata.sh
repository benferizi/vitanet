#!/bin/bash

# Target folder and log destination
PROJECT="vitanet"
LOG="$PROJECT/METADATA.txt"

# Start fresh
echo "Archive Name: vitanet_bundle.zip" > $LOG
echo "Created On: $(date)" >> $LOG
echo "Created By: Ben-A" >> $LOG
echo "" >> $LOG

# Version notes
echo "Version Notes: VitaNet v1.0 — July 2025" >> $LOG
echo "" >> $LOG

# Included files
echo "Included Files:" >> $LOG
find $PROJECT -type f \
  ! -path "$PROJECT/vnet-env/*" \
  ! -path "$PROJECT/__pycache__/*" \
  ! -name "*.pyc" >> $LOG
echo "" >> $LOG

# Excluded paths
echo "Excluded Paths:" >> $LOG
echo "- vnet-env/" >> $LOG
echo "- __pycache__/" >> $LOG
echo "- *.pyc temporary files" >> $LOG
echo "" >> $LOG

# Confirmation
echo "✅ Metadata log created at: $LOG"

