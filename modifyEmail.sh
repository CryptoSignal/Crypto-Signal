#!/usr/bin/bash

export emails=$1
for filename in ./*.yml; do
  sed  -i '$filename' '/destination_emails/s/.*/      destination_emails : ['$emails']/g' $filename
done
