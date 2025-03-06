@app.route('/recommend_ntd', methods=["POST", "GET"])
def recommend_ntd():
    try:
        data_body = dict(request.form)
        id_tin = data_body.get('new_id')
        update = data_body.get('update')
        print(f"tin đang gợi ý {id_tin}")
        # keyword = data_body.get('keyword')
        if 'pagination' in data_body:
            pagination = data_body.get('pagination')
        else:
            pagination = '1'
        if 'size' in data_body:
            num_tin = data_body.get('size')
        else:
            num_tin = '6'

        try:
            # else:
            try:
                data = client.get(index="tin_timviec365_5", id=id_tin)
                keyword = data['_source']['new_title']
                cat_tin_main = data['_source']['new_cat_id']
                city_tin_main = data['_source']['new_city']
                # keyword = data['data']['data']['new_title']

                print(keyword)
            except Exception as err:
                print('err check id tin:', err)
                data = client.get(index="tin_timviec365", id=id_tin)
                keyword = data['_source']['new_title']
                cat_tin_main = data['_source']['new_cat_id']
                city_tin_main = data['_source']['new_city']
                # keyword = data['data']['data']['new_title']

            # key_word = clean_keyword(keyword,search_stopword, search_acronyms)[0]
            # print(key_wo
            query_vector = data['_source']['new_title_vector_new']
            key_word = clean_title_ntd(keyword)
            print('========================================')
            print(key_word)

            # thêm từ 15/10/2024
            ss_exp = []
            new_exp = data['_source']['new_exp']
            if new_exp != '0' and new_exp != '1':
                ss_exp.append({"wildcard": {"cv_exp": new_exp}})
            ss_bang_cap = []
            new_bang_cap = data['_source']['new_bang_cap']
            if new_bang_cap != '0':
                for bang_cap in range(int(new_bang_cap), 19):
                    ss_bang_cap.append({"wildcard": {"cv_hocvan": str(bang_cap)}})
                ss_bang_cap.append({"wildcard": {"cv_hocvan": "0"}})
            print('ss_bang_cap:', ss_bang_cap)

            # kết thúc thêm

            ss_regions = []

            new_north_id = data['_source']['new_north_id']
            new_centeral_id = data['_source']['new_centeral_id']

            new_south_id = data['_source']['new_south_id']

            if 'cv_all_php' in data['_source']:
                new_content = data['_source']['new_title'] + ' ' + data['_source']['cv_all_php']
            else:
                new_content = data['_source']['new_title']
            if int(new_north_id) == 1:
                ss_regions.append({"wildcard": {"cv_north_id": new_north_id}})
            elif int(new_centeral_id) == 1:
                ss_regions.append({"wildcard": {"cv_centeral_id": new_centeral_id}})
            elif int(new_south_id) == 1:
                ss_regions.append({"wildcard": {"cv_south_id": new_south_id}})
            elif int(new_north_id) == 1 and int(new_centeral_id) == 1 and int(new_south_id) == 1:
                ss_regions = []

            print('ss_regions:', ss_regions)

            # print(keyword)

            ss = split_cat_id(cat_tin_main)
            # nganh nghe
            ssmd = []
            for i in ss:
                ssmd.append({"wildcard": {"cv_cate_id": i}})
                # ssmd.append({"wildcard": {"cv_cate_id" : city}})

            print('ssmd:', ssmd)

            ssmd_city = []
            print('------------------------------------------------')
            # tinh thanh
            print('city_tin_main:', city_tin_main)
            if city_tin_main != '0' and city_tin_main != 'toàn quốc' and city_tin_main != '1000' and city_tin_main != '1001' and city_tin_main != '1002' and city_tin_main != '':
                ss_city = split_cat_id(city_tin_main)
                # ssmd_city.append({"wildcard": {"cv_city_id" : ""}})
                # ssmd_city.append({"wildcard": {"cv_city_id" : 0}})
                for i in ss_city:
                    ssmd_city.append({"wildcard": {"cv_city_id": i}})

            # print(city_tin_main)
            if city_tin_main == '1000':
                ssmd_city.append({"term": {"cv_north_id": "1"}})
            if city_tin_main == '1001':
                ssmd_city.append({"term": {"cv_centeral_id": "1"}})
            if city_tin_main == '1002':
                ssmd_city.append({"term": {"cv_south_id": "1"}})

            print('ssmd_city:', ssmd_city)

            new_gioi_tinh = data['_source']['new_gioi_tinh']
            print('new_gioi_tinh:', new_gioi_tinh)
            ssmd_gioi_tinh = []
            if new_gioi_tinh == 'Nam' or new_gioi_tinh == '1':
                ssmd_gioi_tinh.append({"term": {"use_gioi_tinh": 2}})
            elif new_gioi_tinh == 'Nữ' or new_gioi_tinh == '2':
                ssmd_gioi_tinh.append({"term": {"use_gioi_tinh": 1}})
            print('ssmd_gioi_tinh:', ssmd_gioi_tinh)
            # query_vector_mota = convert_to_vector (keyword_mota)

            # if "nhân viên" in key_word:
            #      key_word = key_word.replace("nhân viên","")
            # if "chuyên viên" in key_word:
            #      key_word = key_word.replace("chuyên viên","")
            # cùng title và tỉnh thành 3 ngày (tìm kiếm)
            #    words = key_word.split()
            phrase_search = pharse_word(key_word)
            query_0_0 = {
                "query": {
                    "bool": {
                        "must": [

                            {

                                "bool": {

                                    "should": [
                                        {
                                            "multi_match": {

                                                "query": keyword,
                                                "fields": ["cv_title"],
                                                "type": "phrase"

                                            }

                                        },

                                    ]
                                },

                            },
                            {
                                "bool": {
                                    "should": ssmd
                                }
                            },
                            {
                                "bool": {"should": ss_exp}
                            },
                            {
                                "bool": {"should": ss_bang_cap}
                            },
                            {
                                "bool": {"should": ssmd_city}
                            },
                            {
                                "bool": {"must_not": ssmd_gioi_tinh}
                            },
                            {
                                "bool": {"must": {
                                    "range": {
                                        "use_update_time_new": {'gte': int(round(datetime.now().timestamp())) - 86400}
                                    }
                                }}
                            },
                            {
                                "bool": {"must": {
                                    "range": {
                                        "use_show": {'gte': 1}
                                    }
                                }}
                            },
                            {
                                "bool": {"must": {
                                    "range": {
                                        "percents": {'gte': 45}
                                    }
                                }}
                            }

                        ],

                    }
                }
            }

            query_0_1 = {
                "query": {
                    "bool": {
                        "must": [

                            {

                                "bool": {

                                    "should": [
                                        {
                                            "match_phrase": {
                                                "cv_title": word,

                                            }

                                        } for word in phrase_search

                                    ], "minimum_should_match": 1
                                },

                            },
                            # {
                            #     "bool":{
                            #         "should":ssmd
                            #     }
                            # },
                            {
                                "bool": {"should": ss_exp}
                            },
                            {
                                "bool": {"should": ss_bang_cap}
                            },
                            {
                                "bool": {"should": ssmd_city}
                            },
                            {
                                "bool": {"must_not": ssmd_gioi_tinh}
                            },
                            {
                                "bool": {"must": {
                                    "range": {
                                        "use_update_time_new": {'gte': int(round(datetime.now().timestamp())) - 86400}
                                    }
                                }}
                            },
                            {
                                "bool": {"must": {
                                    "range": {
                                        "use_show": {'gte': 1}
                                    }
                                }}
                            },
                            {
                                "bool": {"must": {
                                    "range": {
                                        "percents": {'gte': 45}
                                    }
                                }}
                            }

                        ],

                    }
                }
            }

            query_0_2 = {
                "query": {
                    "bool": {
                        "must": [

                            {

                                "bool": {

                                    "should": [
                                        {
                                            "multi_match": {

                                                "query": key_word,
                                                "fields": ["cv_title"],
                                                "type": "phrase"

                                            }

                                        },

                                    ]
                                },

                            },
                            {
                                "bool": {
                                    "should": ssmd
                                }
                            },
                            {
                                "bool": {"should": ss_exp}
                            },
                            {
                                "bool": {"should": ss_bang_cap}
                            },
                            {
                                "bool": {"should": ssmd_city}
                            },
                            {
                                "bool": {"must_not": ssmd_gioi_tinh}
                            },
                            {
                                "bool": {"must": {
                                    "range": {
                                        "use_update_time_new": {'gte': int(round(datetime.now().timestamp())) - 86400}
                                    }
                                }}
                            },
                            {
                                "bool": {"must": {
                                    "range": {
                                        "use_show": {'gte': 1}
                                    }
                                }}
                            },
                            {
                                "bool": {"must": {
                                    "range": {
                                        "percents": {'gte': 45}
                                    }
                                }}
                            }

                        ],

                    }
                }
            }

            query_0_3 = {
                "query": {
                    "script_score": {
                        "query": {
                            "bool": {
                                "must": [
                                    {
                                        "bool": {
                                            "should": ssmd
                                        }
                                    },
                                    {
                                        "bool": {"should": ss_exp}
                                    },
                                    {
                                        "bool": {"should": ss_bang_cap}
                                    },
                                    {
                                        "bool": {
                                            "should": ssmd_city
                                        }
                                    },
                                    {
                                        "bool": {"must": {
                                            "range": {
                                                "use_show": {'gte': 1}
                                            }
                                        }}
                                    },
                                    {
                                        "bool": {"must": {
                                            "range": {
                                                "percents": {'gte': 45}
                                            }
                                        }}
                                    },
                                    {
                                        "bool": {"must_not": ssmd_gioi_tinh}
                                    },
                                    {
                                        "bool": {
                                            "must": {
                                                "exists": {
                                                    "field": "cv_title_vector_new"
                                                }
                                            }
                                        }
                                    },
                                    {
                                        "bool": {
                                            "must": [
                                                {
                                                    "range": {
                                                        "use_create_time_new": {
                                                            'gte': int(round(datetime.now().timestamp())) - 86400
                                                            # 'gte': int(round(datetime.now().timestamp())) - 259200
                                                        }
                                                    }
                                                }
                                            ]
                                        }
                                    }
                                ]

                            },

                        },
                        "min_score": 1.75,
                        "script": {
                            "source": "cosineSimilarity(params.query_vector, 'cv_title_vector_new') + 1.0",
                            "params": {
                                "query_vector": query_vector,

                            }
                        }
                    },

                }

            }
            query_1_0 = {
                "query": {
                    "bool": {
                        "must": [

                            {

                                "bool": {

                                    "should": [
                                        {
                                            "multi_match": {

                                                "query": key_word,
                                                "fields": ["cv_title"],
                                                "type": "phrase"

                                            }

                                        },

                                    ]
                                },

                            },
                            {
                                "bool": {
                                    "should": ssmd
                                }
                            },
                            {
                                "bool": {"should": ss_exp}
                            },
                            {
                                "bool": {"should": ss_bang_cap}
                            },
                            {
                                "bool": {"should": ssmd_city}
                            },
                            {
                                "bool": {"must_not": ssmd_gioi_tinh}
                            },
                            {
                                "bool": {"must": {
                                    "range": {
                                        "use_update_time_new": {'gte': int(round(datetime.now().timestamp())) - 259200}
                                    }
                                }}
                            },
                            {
                                "bool": {"must": {
                                    "range": {
                                        "use_show": {'gte': 1}
                                    }
                                }}
                            },
                            {
                                "bool": {"must": {
                                    "range": {
                                        "percents": {'gte': 45}
                                    }
                                }}
                            }

                        ],

                    }
                }
            }

            query_1_1 = {
                "query": {
                    "bool": {
                        "must": [

                            {

                                "bool": {

                                    "should": [
                                        {
                                            "match_phrase": {
                                                "cv_title": word,

                                            }

                                        } for word in phrase_search

                                    ], "minimum_should_match": 1
                                },

                            },
                            {
                                "bool": {
                                    "should": ssmd
                                }
                            },
                            {
                                "bool": {"should": ss_exp}
                            },
                            {
                                "bool": {"should": ss_bang_cap}
                            },
                            {
                                "bool": {"should": ssmd_city}
                            },
                            {
                                "bool": {"must_not": ssmd_gioi_tinh}
                            },
                            {
                                "bool": {"must": {
                                    "range": {
                                        "use_update_time_new": {'gte': int(round(datetime.now().timestamp())) - 259200}
                                    }
                                }}
                            },
                            {
                                "bool": {"must": {
                                    "range": {
                                        "use_show": {'gte': 1}
                                    }
                                }}
                            },
                            {
                                "bool": {"must": {
                                    "range": {
                                        "percents": {'gte': 45}
                                    }
                                }}
                            }

                        ],

                    }
                }
            }

            query_1_2 = {
                "query": {
                    "bool": {
                        "must": [

                            {

                                "bool": {

                                    "should": [
                                        {
                                            "multi_match": {

                                                "query": key_word,
                                                "fields": ["cv_all_php"],
                                                "type": "phrase"

                                            }

                                        },

                                    ]
                                },

                            },
                            {
                                "bool": {
                                    "should": ssmd
                                }
                            },
                            {
                                "bool": {"should": ss_exp}
                            },
                            {
                                "bool": {"should": ss_bang_cap}
                            },
                            {
                                "bool": {"should": ssmd_city}
                            },
                            {
                                "bool": {"must_not": ssmd_gioi_tinh}
                            },
                            {
                                "bool": {"must": {
                                    "range": {
                                        "use_update_time_new": {'gte': int(round(datetime.now().timestamp())) - 259200}
                                    }
                                }}
                            },
                            {
                                "bool": {"must": {
                                    "range": {
                                        "use_show": {'gte': 1}
                                    }
                                }}
                            },
                            {
                                "bool": {"must": {
                                    "range": {
                                        "percents": {'gte': 45}
                                    }
                                }}
                            }

                        ],

                    }
                }
            }

            query_1_3 = {
                "query": {
                    "script_score": {
                        "query": {
                            "bool": {
                                "must": [
                                    {
                                        "bool": {
                                            "should": ssmd
                                        }
                                    },
                                    {
                                        "bool": {"should": ss_exp}
                                    },
                                    {
                                        "bool": {"should": ss_bang_cap}
                                    },
                                    {
                                        "bool": {
                                            "should": ssmd_city
                                        }
                                    },
                                    {
                                        "bool": {"must": {
                                            "range": {
                                                "use_show": {'gte': 1}
                                            }
                                        }}
                                    },
                                    {
                                        "bool": {"must": {
                                            "range": {
                                                "percents": {'gte': 45}
                                            }
                                        }}
                                    },
                                    {
                                        "bool": {"must_not": ssmd_gioi_tinh}
                                    },
                                    {
                                        "bool": {
                                            "must": {
                                                "exists": {
                                                    "field": "cv_title_vector_new"
                                                }
                                            }
                                        }
                                    },
                                    {
                                        "bool": {
                                            "must": [
                                                {
                                                    "range": {
                                                        "use_create_time_new": {
                                                            'gte': int(round(datetime.now().timestamp())) - 10259200
                                                            # 'gte': int(round(datetime.now().timestamp())) - 259200
                                                        }
                                                    }
                                                }
                                            ]
                                        }
                                    }
                                ]

                            },

                        },
                        "min_score": 1.05,
                        "script": {
                            "source": "cosineSimilarity(params.query_vector, 'cv_title_vector_new') + 1.0",
                            "params": {
                                "query_vector": query_vector,

                            }
                        }
                    },

                }

            }
            # tương tự cùng ngành nghề + tỉnh thành 3 ngày, title cùng ngữ nghĩa, yêu câu cùng ngữ nghĩa với kỹ năng
            query_1 = {
                "query": {
                    "script_score": {
                        "query": {
                            "bool": {
                                "must": [
                                    {
                                        "bool": {
                                            "should": ssmd
                                        }
                                    },
                                    {
                                        "bool": {"should": ss_exp}
                                    },
                                    {
                                        "bool": {"should": ss_bang_cap}
                                    },
                                    {
                                        "bool": {
                                            "should": ssmd_city
                                        }
                                    },
                                    {
                                        "bool": {"must": {
                                            "range": {
                                                "use_show": {'gte': 1}
                                            }
                                        }}
                                    },
                                    {
                                        "bool": {"must": {
                                            "range": {
                                                "percents": {'gte': 45}
                                            }
                                        }}
                                    },
                                    {
                                        "bool": {"must_not": ssmd_gioi_tinh}
                                    },
                                    {
                                        "bool": {
                                            "must": {
                                                "exists": {
                                                    "field": "cv_title_vector_new"
                                                }
                                            }
                                        }
                                    },
                                    {
                                        "bool": {
                                            "must": [
                                                {
                                                    "range": {
                                                        "use_create_time_new": {
                                                            'gte': int(round(datetime.now().timestamp())) - 5184000
                                                            # 'gte': int(round(datetime.now().timestamp())) - 259200
                                                        }
                                                    }
                                                }
                                            ]
                                        }
                                    }
                                ]

                            }

                        },
                        "min_score": 1.65,
                        "script": {
                            "source": "cosineSimilarity(params.query_vector, 'cv_title_vector_new') + 1.0",
                            "params": {
                                "query_vector": query_vector,

                            }
                        }
                    }

                }

            }

            # tương tự cùng  + ngành nghề + tỉnh thành 2 thasng
            query_2 = {
                "query": {
                    "script_score": {
                        "query": {
                            "bool": {
                                "must": [
                                    {
                                        "bool": {
                                            "should": ssmd
                                        }
                                    },
                                    {
                                        "bool": {"should": ss_exp}
                                    },
                                    {
                                        "bool": {"should": ss_bang_cap}
                                    },
                                    {
                                        "bool": {
                                            "should": ssmd_city
                                        }
                                    },
                                    {
                                        "bool": {"must": {
                                            "range": {
                                                "use_show": {'gte': 1}
                                            }
                                        }}
                                    },
                                    {
                                        "bool": {"must": {
                                            "range": {
                                                "percents": {'gte': 45}
                                            }
                                        }}
                                    },
                                    {
                                        "bool": {"must_not": ssmd_gioi_tinh}
                                    },
                                    {
                                        "bool": {
                                            "must": {
                                                "exists": {
                                                    "field": "cv_title_vector_new"
                                                }
                                            }
                                        }
                                    },
                                    {
                                        "bool": {
                                            "must": [
                                                {
                                                    "range": {
                                                        "use_create_time_new": {
                                                            'gte': int(round(datetime.now().timestamp())) - 518400
                                                            # 'gte': int(round(datetime.now().timestamp())) - 259200
                                                        }
                                                    }
                                                }
                                            ]
                                        }
                                    }
                                ]

                            },

                        },
                        "min_score": 1.65,
                        "script": {
                            "source": "cosineSimilarity(params.query_vector, 'cv_title_vector_new') + 1.0",
                            "params": {
                                "query_vector": query_vector,

                            }
                        }
                    },

                }

            }

            query_3 = {

                "bool": {
                    "must": [

                        {

                            "bool": {

                                "should": [
                                    {
                                        "multi_match": {

                                            "query": key_word,
                                            "fields": ["cv_title"],
                                            "type": "phrase"

                                        }

                                    },

                                ]
                            },

                        },
                        {
                            "bool": {
                                "should": ssmd
                            }
                        },
                        {
                            "bool": {"should": ss_exp}
                        },
                        {
                            "bool": {"should": ss_bang_cap}
                        },
                        {
                            "bool": {"should": ssmd_city}
                        },
                        {
                            "bool": {"must_not": ssmd_gioi_tinh}
                        },
                        {
                            "bool": {"must": {
                                "range": {
                                    "use_update_time_new": {'gte': int(round(datetime.now().timestamp())) - 259200}
                                }
                            }}
                        },
                        {
                            "bool": {"must": {
                                "range": {
                                    "use_show": {'gte': 1}
                                }
                            }}
                        },
                        {
                            "bool": {"must": {
                                "range": {
                                    "percents": {'gte': 45}
                                }
                            }}
                        }

                    ],

                }
            }
            # cùng title cùng khu vực 3 ngày ( tìm kiếm)

            # tương tự cùng ngành nghề + tỉnh thành 3 ngày, title cùng ngữ nghĩa, yêu câu cùng ngữ nghĩa với kỹ năng
            query_4 = {
                "query": {
                    "script_score": {
                        "query": {
                            "bool": {
                                "must": [
                                    {
                                        "bool": {
                                            "should": ssmd
                                        }
                                    },
                                    {
                                        "bool": {"should": ss_exp}
                                    },
                                    {
                                        "bool": {"should": ss_bang_cap}
                                    },
                                    {
                                        "bool": {"should": ssmd_city}
                                    },
                                    {
                                        "bool": {
                                            "must": {
                                                "exists": {
                                                    "field": "cv_title_vector_new"
                                                }
                                            }
                                        }
                                    },
                                    {
                                        "bool": {"must": {
                                            "range": {
                                                "use_show": {'gte': 1}
                                            }
                                        }}
                                    },
                                    {
                                        "bool": {"must": {
                                            "range": {
                                                "percents": {'gte': 45}
                                            }
                                        }}
                                    },
                                    {
                                        "bool": {"must_not": ssmd_gioi_tinh}
                                    },
                                    {
                                        "bool": {
                                            "must": [
                                                {
                                                    "range": {
                                                        "use_update_time_new": {
                                                            # 'gte': int(round(datetime.now().timestamp())) - 5184000
                                                            'gte': int(round(datetime.now().timestamp())) - 259200
                                                        }
                                                    }
                                                }
                                            ]
                                        }
                                    }
                                ]

                            },

                        },
                        "min_score": 1.75,
                        "script": {
                            "source": "cosineSimilarity(params.query_vector, 'cv_title_vector_new') + 1.0",
                            "params": {
                                "query_vector": query_vector,

                            }
                        }
                    },

                }

            }
            # tương tự cùng  + ngành nghề + tỉnh thành 2 thasng
            query_5 = {
                "query": {
                    "script_score": {
                        "query": {
                            "bool": {
                                "must": [
                                    {
                                        "bool": {
                                            "should": ssmd
                                        }
                                    },
                                    {
                                        "bool": {"should": ss_exp}
                                    },
                                    {
                                        "bool": {"should": ss_bang_cap}
                                    },
                                    {
                                        "bool": {
                                            "should": ssmd_city
                                        }
                                    },
                                    {
                                        "bool": {"must": {
                                            "range": {
                                                "use_show": {'gte': 1}
                                            }
                                        }}
                                    },
                                    {
                                        "bool": {"must": {
                                            "range": {
                                                "percents": {'gte': 45}
                                            }
                                        }}
                                    },
                                    {
                                        "bool": {"must_not": ssmd_gioi_tinh}
                                    },
                                    {
                                        "bool": {
                                            "must": {
                                                "exists": {
                                                    "field": "cv_title_vector_new"
                                                }
                                            }
                                        }
                                    }
                                    #  {
                                    #      "bool":{
                                    #      "must":[
                                    #      {
                                    #          "range": {
                                    #              "use_create_time_new":{
                                    #                  'gte': int(round(datetime.now().timestamp())) - 518400
                                    #                  # 'gte': int(round(datetime.now().timestamp())) - 259200
                                    #              }
                                    #          }
                                    #      }
                                    #      ]
                                    #      }
                                    #  }
                                ]

                            },

                        },
                        "min_score": 1.05,
                        "script": {
                            "source": "cosineSimilarity(params.query_vector, 'cv_title_vector_new') + 1.0",
                            "params": {
                                "query_vector": query_vector,

                            }
                        }
                    },

                }

            }

            sort_1 = [{"use_update_time_new": {"order": "desc", }}]

            if 'vàaaaaaaaaaa' in key_word:
                key_word = key_word.split('và')
                multi_text_query = []
                for key_word in key_word:
                    if "nhân viên" in key_word:
                        key_word = key_word.replace("nhân viên", "")
                    if "chuyên viên" in key_word:
                        key_word = key_word.replace("chuyên viên", "")
                    multi_text_query.append({
                        "multi_match": {

                            "query": key_word,
                            "fields": ["cv_title"],
                            "type": "phrase",
                            # "analyzer": "synonym",

                        }

                    })
                query = {

                    "bool": {
                        "must": [

                            {

                                "bool": {

                                    "should": multi_text_query
                                },

                            },
                            {
                                "bool": {
                                    "should": ssmd
                                }
                            },
                            {
                                "bool": {"should": ssmd_city}
                            },
                            {
                                "bool": {"must": {
                                    "range": {
                                        "use_update_time_new": {'gte': int(round(datetime.now().timestamp())) - 259200}
                                    }
                                }}
                            }

                        ],

                    }
                }
                query_1 = {

                    "bool": {
                        "must": [

                            {

                                "bool": {

                                    "should": multi_text_query
                                },

                            },
                            {
                                "bool": {
                                    "should": ssmd
                                }
                            },
                            {
                                "bool": {"should": ss_regions}
                            },
                            # {
                            #     "bool":{"must":{
                            #         "range":{
                            #             "use_update_time_new":{'gte': int(round(datetime.now().timestamp())) - 259200}
                            #         }
                            #     }}
                            # }

                        ],

                    }
                }

            ss = []
            list_id = []
            list_id_cat_city = []
            list_id_cat_not_city = []

            # print('query:', query)
            list_query = [query_0_0, query_0_1, query_0_2, query_0_3, query_1_0, query_1_1, query_1_2, query_1_3]

            def query_uv():
                list_id = []
                ss = []
                for query_id in list_query:
                    print('index:', list_query.index(query_id))
                    print('query:', query_id)
                    res_1 = client.search(index="tin_uvtimviec365_5", body=query_id, size=100)
                    res_1 = res_1['hits']
                    for i in res_1['hits']:
                        a = i['_source']['use_id']
                        print('a:', a)
                        if a not in list_id:
                            ss.append({'use_id': i['_source']['use_id'], 'cv_title': i['_source']['cv_title'],
                                       'cv_content': i['_source']['cv_all_php']})
                            list_id.append(i['_source']['use_id'])
                            print('len ss:', len(ss))
                # try:
                #      # print('len ss:', len(ss))
                #      if len(ss) > 5:
                #           ss_5 = ss[:5]
                #           ss_5_sorted = sorted_result(ss_5, new_content, 'false')
                #           ss_sorted = ss_5_sorted + ss[5:]
                #      else:
                #           ss_sorted = sorted_result(ss, new_content, 'false') if len(ss) > 2 else ss
                #      # list_id = [s['new_id'] for s in ss_sorted]
                # except Exception as err:
                #      print('err:', err)
                ss_sorted = ss
                return ss_sorted

            if _SERVER_.check_document_index("suggest_uv", id_tin) == False:
                ss_sorted = query_uv()
                if ss_sorted:
                    doc = {"suggest": ss_sorted[:10]} if len(ss_sorted) > 10 else {"suggest": ss_sorted}
                    _SERVER_.create_document("suggest_uv", id_tin, doc)
            else:
                if update == 'false':
                    result = _SERVER_.get_document("suggest_uv", id_tin)
                    ss_sorted = result['_source']['suggest']
                else:
                    ss_sorted = query_uv()
                    doc = {"suggest": ss_sorted[:10]} if len(ss_sorted) > 10 else {"suggest": ss_sorted}
                    _SERVER_.create_document("suggest_uv", id_tin, doc)
            list_id = [uv['use_id'] for uv in ss_sorted]
            return ({'list': ss_sorted, 'list_id': list_id, 'total': len(list_id)})

        # return ({'list':ss})
        except Exception as err:
            print('err:', err)
            traceback.print_exc()
            return ({"error": f'Không lấy được gợi ý, {err}'})
    except Exception as err:
        print('êrrrrr:', err)