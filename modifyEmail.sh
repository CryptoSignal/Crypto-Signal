#!/usr/bin/bash

export emails=$2
if [ "$1" = "easy" ]
then
    rm -rf easy/*
    cd origin_yml
    for fullname in *.yml; do
        filename=$(echo $fullname | sed 's/\.[^.]*$//')
        easyFileName=$filename"_easy.yml"
        cp -r $fullname ../easy/$easyFileName
        touch ../easy/$filename".log"
    done
    cd ..

    for easyFileName in easy/*.yml; do
      sed  -i '$easyFileName' '/destination_emails/s/.*/      destination_emails : ['$emails']/g' $easyFileName
    done

rm -rf easy/*easyFileName
echo "easy mode yml email update complete."
fi

if [ "$1" = "custom" ]
then
    rm -rf custom/*
    cd origin_yml
    for fullname in *.yml; do
        filename=$(echo $fullname | sed 's/\.[^.]*$//')
        customFileName=$filename"_custom.yml"
        cp -r $fullname ../custom/$customFileName
        touch ../custom/$filename".log"
    done
    cd ..

    for customFileName in custom/*.yml; do
      sed  -i '$customFileName' '/destination_emails/s/.*/      destination_emails : ['$emails']/g' $customFileName
    done

rm -rf custom/*customFileName
echo "custom mode yml email update complete."
fi
