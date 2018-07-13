#!/usr/bin/env bash

#
# LICENSE:
#-----------------------------------------------------------------------------------------------------------------------
#
# Copyright 2018 Jesse McLaughlin <nzjess(at)gmail.com>
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
#    disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the
#    following disclaimer in the documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
# USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

#
# MOTIVATION
#-----------------------------------------------------------------------------------------------------------------------
# The CSV export feature in Kibana 6 is not very scriptable: https://www.elastic.co/blog/kibana-6-0-0-released
#

#
# PRE-REQS:
#-----------------------------------------------------------------------------------------------------------------------
#
# jq: https://stedolan.github.io/jq/
# json2csv: https://www.npmjs.com/package/json2csv
#

#
# QUICK START:
#-----------------------------------------------------------------------------------------------------------------------
#
# 1. Print help:
# $ ./es-export-csv.sh
#
# 2. Export absolute time window:
# $ ./es-export-csv.sh -c example-query.conf -h "http://localhost:9200" \
#     -f "2018-01-29 11:00 GMT" -t "2018-01-29 11:10 GMT" -d tmp -o output -v
#
# 3. Export time window relative to now:
# $ ./es-export-csv.sh -c example-query.conf -h "http://localhost:9200" \
#     -w "1 hour" -d tmp -o output -v
#
# 4. Export time window relative to previously marked window end time:
# $ ./es-export-csv.sh -c example-query.conf -h "http://localhost:9200" \
#     -w "1 hour" -d tmp -o output -m -v
#
# 5. Export time window relative to absolute window end time:
# $ ./es-export-csv.sh -c example-query.conf -h "http://localhost:9200" \
#     -t "2018-01-29 11:00 GMT" -w "1 hour" -d work -o output -v
#

DATE=date
if [ "$(uname)" == "Darwin" ]; then
    # On Mac:  $ brew install coreutils
    DATE=gdate
fi

function usage {
    if [ ! -z "$1" ]; then
      echo "$1"
      echo
    fi

    echo "\
Usage: $0 <args>

Arguments:
    --conf-file|-c <filename>
    --host|-h <host:port>
    [--user|-u <username:password>]
    [--query-file|-q <filename>]
    [--work-dir|-d <dirname>]
    [--output-dir|-o <dirname>]
    [--window|-w <duration>]
    [--window-max|-x <duration>]
    [--time-from|-f <date time>]
    [--time-to|-t <date time>]
    [--scroll-size|-s <count>]
    [--scroll-keep-alive|-k <duration>]
    [--no-header|-n]
    [--mark|-m]
    [--gzip|-z]
    [--verbose|-v]
    [--help|-h]"

    exit 1
}

[[ $# != 0 ]] || usage "Missing arguments"

CONF_FILE=""
HOST_PORT=""
USER_PASS=""
INDEX_QUERY_FILE=""
WORK_DIR="."
OUTPUT_DIR="."
TIME_WINDOW="1 hour"
TIME_WINDOW_MAX=""
TIME_FROM=""
TIME_TO=""
SCROLL_SIZE="10000"
SCROLL_KEEP_ALIVE="1m"
NO_HEADER=
MARK=
GZIP=
VERBOSE=
HELP=

while [[ $# -gt 0 ]]; do
    case $1 in
        -c | --conf-file )            shift
                                      CONF_FILE=$1
                                      ;;
        -h | --host )                 shift
                                      HOST_PORT=$1
                                      ;;
        -u | --user )                 shift
                                      USER_PASS=$1
                                      ;;
        -q | --query-file )           shift
                                      INDEX_QUERY_FILE=$1
                                      ;;
        -o | --output-dir )           shift
                                      OUTPUT_DIR=$1
                                      ;;
        -d | --work-dir )             shift
                                      WORK_DIR=$1
                                      ;;
        -w | --window )               shift
                                      TIME_WINDOW=$1
                                      ;;
        -x | --window-max )           shift
                                      TIME_WINDOW_MAX=$1
                                      ;;
        -f | --time-from )            shift
                                      TIME_FROM=$1
                                      ;;
        -t | --time-to )              shift
                                      TIME_TO=$1
                                      ;;
        -s | --scroll-size)           shift
                                      SCROLL_SIZE=$1
                                      ;;
        -k | --scroll-keep-alive )    shift
                                      SCROLL_KEEP_ALIVE=$1
                                      ;;
        -n | --no-header )            NO_HEADER=true
                                      ;;
        -m | --mark )                 MARK=true
                                      ;;
        -z | --gzip )                 GZIP=true
                                      ;;
        -v | --verbose )              VERBOSE=true
                                      ;;
        -h | --help )                 HELP=true
                                      ;;
        * )                           usage "Unrecognized argument: $1"
    esac
    shift
done

[[   -z "${HELP}" ]]              || usage

[[ ! -z "${CONF_FILE}" ]]         || usage "Missing config file"
[[ ! -z "${HOST_PORT}" ]]         || usage "Missing host:port"
[[ ! -z "${WORK_DIR}" ]]          || usage "Missing working dir"
[[ ! -z "${OUTPUT_DIR}" ]]        || usage "Missing output dir"
[[ ! -z "${TIME_WINDOW}" ]]       || usage "Missing time window"
[[ ! -z "${SCROLL_SIZE}" ]]       || usage "Missing scroll size"
[[ ! -z "${SCROLL_KEEP_ALIVE}" ]] || usage "Missing scroll keep alize"

function error {
    echo "$1"
    exit 1
}

[[ -f "${CONF_FILE}" ]]       || error "Missing config file"

INDEX_PATTERN=""
INDEX_QUERY=""
CSV_FIELDS=""
JQ_FIELDS=""
source ${CONF_FILE}

[[ ! -z "${INDEX_PATTERN}" ]] || error "Missing config setting: INDEX_PATTERN"
[[ ! -z "${CSV_FIELDS}" ]]    || error "Missing config setting: CSV_FIELDS"
[[ ! -z "${JQ_FIELDS}" ]]     || error "Missing config setting: JQ_FIELDS"

BASE_NAME=${CONF_FILE}
if [[ -z "${INDEX_QUERY}" && -f "${INDEX_QUERY_FILE}" ]]; then
  INDEX_QUERY=$(cat ${INDEX_QUERY_FILE})
  BASE_NAME=${INDEX_QUERY_FILE}
fi

[[ ! -z "${INDEX_QUERY}" ]]   || error "Missing config setting: INDEX_QUERY or INDEX_QUERY_FILE"

mkdir -p "${WORK_DIR}"
[[ $? == 0 ]] || error "Error creating work dir"

mkdir -p "${OUTPUT_DIR}"
[[ $? == 0 ]] || error "Error creating output dir"

BASE_FILE=$(basename "${BASE_NAME}")
BASE_NAME="${BASE_FILE%.*}"

TMP_FILE="${WORK_DIR}/${BASE_NAME}.tmp"
CSV_FILE="${WORK_DIR}/${BASE_NAME}.csv"
if [ ! -z "${MARK}" ]; then
    MARKER_FILE="${WORK_DIR}/${BASE_NAME}.marker"
fi

if [ -z "${TIME_FROM}" ]; then
    if [ -f "${MARKER_FILE}" ]; then
        TIME_FROM=$(cat ${MARKER_FILE})
        if [ ! -z "${TIME_WINDOW_MAX}" ]; then
            TIME_MIN=$($DATE -d "${TIME_TO}-${TIME_WINDOW_MAX}" +%s%3N)
            if [[ ! -z "${TIME_FROM}" && ${TIME_FROM} -lt ${TIME_MIN} ]]; then
                TIME_FROM=""
            fi
        fi
    fi
    if [ -z "${TIME_FROM}" ]; then
        TIME_FROM=$($DATE -d "${TIME_TO}-${TIME_WINDOW}" +%s%3N)
    fi
else
    TIME_FROM=$($DATE -d "${TIME_FROM}" "+%s%3N")
fi

if [ -z "${TIME_TO}" ]; then
    TIME_TO=$($DATE +%s%3N)
else
    TIME_TO=$($DATE -d "${TIME_TO}" "+%s%3N")
fi

if [ ! -z "${USER_PASS}" ]; then
    USER_PASS="-u ${USER_PASS}"
fi

echo ${INDEX_QUERY} | \
sed -E "s/Q_TIME_FROM/${TIME_FROM}/;s/Q_TIME_TO/${TIME_TO}/;s/Q_SCROLL_SIZE/${SCROLL_SIZE}/" | \
curl -sf ${USER_PASS} \
  -H "Content-Type: application/json" \
  "${HOST_PORT}/${INDEX_PATTERN}/_search?scroll=${SCROLL_KEEP_ALIVE}" \
  --data @- \
  > ${TMP_FILE}

[[ $? == 0 ]] || error "Error initiating Elasticsearch query"

if [ ! -z "${VERBOSE}" ]; then
    echo "Exporting from ${TIME_FROM} to ${TIME_TO}:"
fi

if [ -z "${NO_HEADER}" ]; then
    echo ${CSV_FIELDS} > ${CSV_FILE}
else
    echo -n > ${CSV_FILE}
fi

COUNT=0
while true ; do
    SCROLL_ID=""
    HIT_COUNT=0

    eval $(jq --raw-output \
      '{ "scroll_id": ._scroll_id, "hit_count" : .hits.hits|length } |
       "SCROLL_ID=\"\(.scroll_id)\"\nHIT_COUNT=\(.hit_count)"' \
      ${TMP_FILE})

    if [[ -z "${SCROLL_ID}" || ${HIT_COUNT} == 0 ]]; then
        break
    fi

    jq "[ .hits.hits[]._source | { ${JQ_FIELDS} } ]" ${TMP_FILE} | \
      json2csv --no-header --fields "${CSV_FIELDS}" \
      >> ${CSV_FILE}

    curl -sf ${USER_PASS} \
      -H "Content-Type: application/json" \
      "${HOST_PORT}/_search/scroll" \
      --data "{\"scroll\": \"${SCROLL_KEEP_ALIVE}\", \"scroll_id\": \"${SCROLL_ID}\"}" \
      > ${TMP_FILE}

    [[ $? == 0 ]] || error "Error continuing Elasticsearch query"

    if [ ! -z "${VERBOSE}" ]; then
        if [[ ${COUNT} -ge 80 ]]; then
            echo "."
            COUNT=0
        else
            echo -n "."
            COUNT=$((COUNT+1))
        fi
    fi
done

if [ ! -z "${VERBOSE}" ]; then
    [[ ${COUNT} == 0 ]] || echo
    echo "Done."
fi

rm -f ${TMP_FILE}

if [ ! -z "${MARKER_FILE}" ]; then
    echo -n "${TIME_TO}" > ${MARKER_FILE}
fi

if [ ! -z "${GZIP}" ]; then
    gzip ${CSV_FILE}
    CSV_FILE="${CSV_FILE}.gz"
fi

if [ "${OUTPUT_DIR}" != "${WORK_DIR}" ]; then
    mv ${CSV_FILE} ${OUTPUT_DIR}
fi

echo before comment
: <<'END'
#sample config
INDEX_PATTERN="http-access-logs-*"

INDEX_QUERY='{
  "query": {
    "bool": {
      "must": [
        { "wildcard": {
          "requestpath" : "/blog/*" }
        }
      ],
      "filter": [
        { "range": {
          "@timestamp": {
                "gt": "Q_TIME_FROM",
               "lte": "Q_TIME_TO",
            "format": "epoch_millis" }
          }
        }
      ]
    }
  },
  "sort": [
    { "@timestamp": {
      "order": "asc" }
    }
  ],
  "_source": [
    "@timestamp",
    "useragent",
    "referrer",
    "requestpath",
    "requestargs",
    "response",
    "bytes_body"
  ],
  "size": Q_SCROLL_SIZE
}
'

CSV_FIELDS="\
timestamp,\
useragent,\
referrer,\
request,\
response,\
bytes"

JQ_FIELDS="\
\"timestamp\":.[\"@timestamp\"],\
\"useragent\":.useragent,\
\"referrer\":.referrer,\
\"request\":\"\(.requestpath)\(if(.requestargs) != null then .requestargs else \"\" end)\",\
\"response\":.response,\
\"bytes\":.bytes_body"
END
echo after comment
