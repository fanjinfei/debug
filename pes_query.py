'''
{
  "from" : 30000,
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
