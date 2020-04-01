#!/bin/bash
CURRENT_DATE_UTC=`date -u +%FT%T+00:00`
while true; do
echo "logs since ${CURRENT_DATE_UTC}"
sleep 60
gcloud logging read "resource.type=\"container\"
resource.labels.namespace_id=\"kubernetes-runner-namespace\"
timestamp>=\"${CURRENT_DATE_UTC}\"
" --limit 1000000000000 --order asc --format 'value(resource.labels.pod_id, jsonPayload.message, textPayload)' > logfile.txt
cat logfile.txt | sed '/^$/d'
if [[ $(cat logfile.txt | head -n 5 | wc -l) -ne 0 ]]; then
    CURRENT_DATE_UTC=`date -u +%FT%T+00:00`;
else
    kubectl get events --sort-by=.metadata.creationTimestamp | tail -n 2
fi

done