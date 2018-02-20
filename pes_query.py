
import sys
import json

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from elasticsearch_dsl import DocType, Date, Integer, Keyword, Text, connections

#modify following es query to support decay function
def dsl_search():
    client = Elasticsearch('localhost:9200')

    s = Search(using=client, index="my-index") \
        .filter("term", category="search") \
        .query("match", title="python")   \
        .exclude("match", description="beta")

#override connection
#s = s.using(Elasticsearch('otherhost:9200'))

    s.aggs.bucket('per_tag', 'terms', field='tags') \
        .metric('max_lines', 'max', field='lines')

    body = s.to_dict()
    print (body)
    return

    response = s.execute()

    for hit in response:
        print(hit.meta.score, hit.title)

    for tag in response.aggregations.per_tag.buckets:
        print(tag.key, tag.max_lines.value)

dsl_search()
sys.exit(0)

body='''
{
  "from" : 1000,
  "size" : 20,
  "timeout" : "10000ms",
  "query" : {
    "bool" : {
      "must" : [
        {
          "function_score" : {
            "query" : {
              "bool" : {
                "must" : [
                  {
                    "bool" : {
                      "should" : [
                        {
                          "wildcard" : {
                            "title" : {
                              "wildcard" : "*",
                              "boost" : 0.2
                            }
                          }
                        },
                        {
                          "wildcard" : {
                            "content" : {
                              "wildcard" : "*",
                              "boost" : 0.1
                            }
                          }
                        }
                      ],
                      "disable_coord" : false,
                      "adjust_pure_negative" : true,
                      "boost" : 1.0
                    }
                  },
                  {
                    "bool" : {
                      "should" : [
                        {
                          "term" : {
                            "label" : {
                              "value" : "daily_archive",
                              "boost" : 1.0
                            }
                          }
                        },
                        {
                          "term" : {
                            "label" : {
                              "value" : "daily",
                              "boost" : 1.0
                            }
                          }
                        },
                        {
                          "term" : {
                            "label" : {
                              "value" : "daily_latest",
                              "boost" : 1.0
                            }
                          }
                        }
                      ],
                      "disable_coord" : false,
                      "adjust_pure_negative" : true,
                      "boost" : 1.0
                    }
                  }
                ],
                "disable_coord" : false,
                "adjust_pure_negative" : true,
                "boost" : 1.0
              }
            },
            "functions" : [
              {
                "filter" : {
                  "match_all" : {
                    "boost" : 1.0
                  }
                },
                "field_value_factor" : {
                  "field" : "boost",
                  "factor" : 1.0,
                  "modifier" : "none"
                }
              }
            ],
            "score_mode" : "multiply",
            "max_boost" : 3.4028235E38,
            "boost" : 1.0
          }
        }
      ],
      "filter" : [
        {
          "bool" : {
            "should" : [
              {
                "term" : {
                  "role" : {
                    "value" : "1guest",
                    "boost" : 1.0
                  }
                }
              },
              {
                "term" : {
                  "role" : {
                    "value" : "Rguest",
                    "boost" : 1.0
                  }
                }
              }
            ],
            "disable_coord" : false,
            "adjust_pure_negative" : true,
            "boost" : 1.0
          }
        }
      ],
      "disable_coord" : false,
      "adjust_pure_negative" : true,
      "boost" : 1.0
    }
  },
  "_source" : {
    "includes" : [
      "score",
      "_id",
      "doc_id",
      "boost",
      "content_length",
      "host",
      "site",
      "last_modified",
      "timestamp",
      "mimetype",
      "filetype",
      "filename",
      "created",
      "title",
      "digest",
      "url",
      "thumbnail",
      "click_count",
      "favorite_count",
      "config_id",
      "lang",
      "has_cache",
      "lang"
    ],
    "excludes" : [ ]
  },
  "highlight" : {
    "fields" : {
      "content" : {
        "fragment_size" : 50,
        "number_of_fragments" : 5,
        "type" : "fvh"
      }
    }
  }
}
'''
body = json.loads(body)
s = Search.from_dict(body)
body = s.to_dict()

client = Elasticsearch('localhost:'+sys.argv[1])

es = Elasticsearch([{'host': 'localhost', 'port': int(sys.argv[1])}])
r = es.search(index="fess.20180125", body=body)
print (r)

