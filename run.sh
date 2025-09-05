#!/bin/bash

if [ -z "$SLACK_URL" ]; then
    echo "Provide SLACK_URL in env"
    exit 1
fi

mkdir -p builds var 2>/dev/null

while true; do
    echo -ne "\n\n"
    date

    rm -f var/msg.txt

    curTS="$(date -u +%Y-%m-%d-%H-%M-%S)"
    cur="builds/$curTS.json"

    prevTS="$(head -n 1 var/prev.txt)"
    prev="builds/$prevTS.json"

    az pipelines build list --definition-ids 428766 428757 428756 428764 428767 428763 > $cur && \
    test -s $cur && \
    ./compare.py $prev $cur > var/msg.txt

    if [ -s var/msg.txt ]; then
        cat var/msg.txt && \
        jq -Rsa --raw-input '{"msg": .}' var/msg.txt > var/msg.json && \
        curl -X POST -H "Content-Type: application/json" -d "@var/msg.json" "$SLACK_URL" && \
        echo $curTS > var/prev.txt && \
        rm -f $prev
    else
        rm -rf $cur
    fi


    sleep 300
done
