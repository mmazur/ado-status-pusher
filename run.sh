#!/bin/bash

if [ -z "$SLACK_URL" ]; then
    echo "Provide SLACK_URL in env"
    exit 1
fi

while true; do
    echo -ne "\n\n"
    date

    curTS="$(date -u +%Y-%m-%d-%H-%M-%S)"
    cur="builds/$curTS.json"

    [ ! -f "prev.txt" ] && echo "$curTS" > prev.txt
    prevTS="$(head -n 1 prev.txt)"
    prev="builds/$prevTS.json"

    az pipelines build list --definition-ids 428766 428757 428756 > $cur && \
    ./compare.py $prev $cur > msg.txt

    if [ -s msg.txt ]; then
        cat msg.txt && \
        jq -Rsa --raw-input '{"msg": .}' msg.txt > msg.json && \
        curl -X POST -H "Content-Type: application/json" -d "@msg.json" "$SLACK_URL" && \
        echo $curTS > prev.txt && \
        rm -f $prev
    else
        rm -rf $cur
    fi


    sleep 300
done