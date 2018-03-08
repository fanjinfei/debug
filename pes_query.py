
import sys
import json

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from elasticsearch_dsl import DocType, Date, Integer, Keyword, Text, connections

#use Elastic search query builder
''' Put this inside the "functions" list
{
  "gauss": {
     "date": {
        "origin": "2013-09-17",  #current date
        "scale": "10d",
        "offset": "5d", 
        "decay" : 0.5 
     }
  }
},
'''
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

body='''
{
  "from" : 0,
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
  "gauss": {
     "timestamp": {
        "origin": "2018-03-08",
        "scale": "60d",
        "offset": "10d", 
        "decay" : 0.5 
     }
  }
},
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

class Result():
    def __init__(self, txt):
        self.d = txt #json.loads(txt)

    def test(self):
        print 'total', self.d['hits']['total']
        r = self.d['hits']['hits']
        for item in r:
            doc = item['_source']
            print doc['timestamp'], item['_score'], doc['title'].encode('utf-8')

#dsl_search()
#sys.exit(0)

body = json.loads(body)
s = Search.from_dict(body)
body = s.to_dict()

client = Elasticsearch('localhost:'+sys.argv[1])

es = Elasticsearch([{'host': 'localhost', 'port': int(sys.argv[1])}])
r = es.search(index="fess.20180125", body=body)
#print (r)
r= Result(r)
r.test()


# "dGltZXN0YW1wOltub3ctN2QvZCBUTyAqXQ==" base64 decode to "timestamp:[now-7d/d TO *]"
'''
{
  "from": 30,
  "size": 1,
  "timeout": "10000ms",
  "query": {
    "bool": {
      "must": [
        {
          "function_score": {
            "query": {
              "bool": {
                "should": [
                  {
                    "match_phrase": {
                      "title": {
                        "query": "consumer+price+index",
                        "slop": 0,
                        "boost": 0.2
                      }
                    }
                  },
                  {
                    "match_phrase": {
                      "content": {
                        "query": "consumer+price+index",
                        "slop": 0,
                        "boost": 0.1
                      }
                    }
                  },
                  {
                    "match_phrase": {
                      "title_en": {
                        "query": "consumer+price+index",
                        "slop": 0,
                        "boost": 1
                      }
                    }
                  },
                  {
                    "match_phrase": {
                      "content_en": {
                        "query": "consumer+price+index",
                        "slop": 0,
                        "boost": 0.5
                      }
                    }
                  }
                ],
                "disable_coord": false,
                "adjust_pure_negative": true,
                "boost": 1
              }
            },
            "functions": [
              {
                "filter": {
                  "match_all": {
                    "boost": 1
                  }
                },
                "field_value_factor": {
                  "field": "boost",
                  "factor": 1,
                  "modifier": "none"
                }
              }
            ],
            "score_mode": "multiply",
            "max_boost": 3.4028235e+38,
            "boost": 1
          }
        }
      ],
      "filter": [
        {
          "bool": {
            "should": [
              {
                "term": {
                  "role": {
                    "value": "1guest",
                    "boost": 1
                  }
                }
              },
              {
                "term": {
                  "role": {
                    "value": "Rguest",
                    "boost": 1
                  }
                }
              }
            ],
            "disable_coord": false,
            "adjust_pure_negative": true,
            "boost": 1
          }
        }
      ],
      "disable_coord": false,
      "adjust_pure_negative": true,
      "boost": 1
    }
  },
  "_source": {
    "includes": [
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
    "excludes": [
      
    ]
  },
  "aggregations": {
    "query:dGltZXN0YW1wOltub3ctN2QvZCBUTyAqXQ==": { 
      "filter": {
        "range": {
          "timestamp": {
            "from": "now-7d\/d",
            "to": null,
            "include_lower": true,
            "include_upper": true,
            "boost": 1
          }
        }
      }
    },
    "query:dGltZXN0YW1wOltub3ctMXkvZCBUTyAqXQ==": {
      "filter": {
        "range": {
          "timestamp": {
            "from": "now-1y\/d",
            "to": null,
            "include_lower": true,
            "include_upper": true,
            "boost": 1
          }
        }
      }
    },
    "query:dGltZXN0YW1wOltub3ctMWQvZCBUTyAqXQ==": {
      "filter": {
        "range": {
          "timestamp": {
            "from": "now-1d\/d",
            "to": null,
            "include_lower": true,
            "include_upper": true,
            "boost": 1
          }
        }
      }
    },
    "query:dGltZXN0YW1wOltub3ctMzBkL2QgVE8gKl0=": {
      "filter": {
        "range": {
          "timestamp": {
            "from": "now-30d\/d",
            "to": null,
            "include_lower": true,
            "include_upper": true,
            "boost": 1
          }
        }
      }
    },
    "query:dGltZXN0YW1wOlsqIFRPIG5vdy0xeS0xZC9kXQ==": {
      "filter": {
        "range": {
          "timestamp": {
            "from": null,
            "to": "now-1y-1d\/d",
            "include_lower": true,
            "include_upper": true,
            "boost": 1
          }
        }
      }
    }
  },
  "highlight": {
    "fields": {
      "content": {
        "fragment_size": 50,
        "number_of_fragments": 5,
        "type": "fvh"
      }
    }
  }
}
'''
