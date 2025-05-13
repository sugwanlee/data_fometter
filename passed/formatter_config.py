import os

# 기본값 매핑 설정
DEFAULT_VALUE_MAPPING = {
    # label_formatted로 변환되는 필드들
    'label': '0000000000000x000000000000000001',
    
    # ownershiplabel_formatted로 변환되는 필드들
    'ownershiplabel': '0000000000000x000000000000000001',

    # ownershipshared_formatted로 변환되는 필드들
    'ownershipshared': '0000000000000x000000000000000002',
    
    # [lstn] scheduled 컬럼을 위한 기본값
    '[lstn] scheduled': '0000000000000x000000000000000003',
    
    # istnplus 컬럼을 위한 기본값
    'lstnplus': '0000000000000x000000000000000004',
    
    # playlist channel 컬럼을 위한 기본값
    'playlist channel': '0000000000000x000000000000000005',
    
    # playlist creator 컬럼을 위한 기본값
    'playlist creator': '0000000000000x000000000000000006',
    
    # contract_formatted로 변환되는 필드들
    'contract': '0000000000000x000000000000000007',

    # ownershipuser_formatted로 변환되는 필드들
    'ownershipuser': '0000000000000x000000000000000008',
}

# 테이블 타입별 설정
TABLE_CONFIGS = {
    'user': {
        'required_columns': ['unique id'],
        'uuid_columns': {
            'unique_id': 'unique id',
        },
        'default_values': {
        }
    },
    'label': {
        'required_columns': ['unique id'],
        'uuid_columns': {
            'unique_id': 'unique id'
        },
        'default_values': {
        }
    },
    'musician': {
        'required_columns': ['unique id', 'label'],
        'uuid_columns': {
            'unique_id': 'unique id',
            'label_formatted': 'label'
        },
        'default_values': {
            'label': DEFAULT_VALUE_MAPPING['label']
        }
    },
    'album': {
        'required_columns': ['unique id', 'label'],
        'uuid_columns': {
            'unique_id': 'unique id',
            'label_formatted': 'label',
        },
        'default_values': {
            'label': DEFAULT_VALUE_MAPPING['label']
        }
    },
    'track': {
        'required_columns': ['unique id', 'ownershipshared'],
        'uuid_columns': {
            'unique_id': 'unique id',
            'ownership_shared': 'ownershipshared'
        },
        'default_values': {
            'ownershipshared': DEFAULT_VALUE_MAPPING['ownershipshared']
        }
    },
    'ownership': {
        'required_columns': ['unique id', 'ownershiplabel'],
        'uuid_columns': {
            'unique_id': 'unique id',
            'ownership_label': 'ownershiplabel',
            # 'ownershipuser_formatted': 'ownershipuser',
        },
        'default_values': {
            'ownershiplabel': DEFAULT_VALUE_MAPPING['ownershiplabel'],
            # 'ownershipuser': DEFAULT_VALUE_MAPPING['ownershipuser'],
        }
    },
    'settlement_melon': {
        'required_columns': ['unique id', 'ownershipuser'],
        'uuid_columns': {
            'unique_id': 'unique id',
            'ownership_user': 'ownershipuser',
        },
        'default_values': {
            'ownershipuser': DEFAULT_VALUE_MAPPING['ownershipuser']
        }
    },
    'settlement_vibe': {
        'required_columns': ['unique id'],
        'uuid_columns': {
            'unique_id': 'unique id'
        },
        'default_values': {
        }
    },
    'settlement_genie': {
        'required_columns': ['unique id'],
        'uuid_columns': {
            'unique_id': 'unique id',
        },
        'default_values': {
        }
    },
    'settlement_flo': {
        'required_columns': ['unique id'],
        'uuid_columns': {
            'unique_id': 'unique id',
        },
        'default_values': {
        }
    },
    'settlement_youtube': {
        'required_columns': ['unique id'],
        'uuid_columns': {
            'unique_id': 'unique id'
        },
        'default_values': {
        }
    },
    'settlement_global': {
        'required_columns': ['unique id'],
        'uuid_columns': {
            'unique_id': 'unique id'
        },
        'default_values': {
        }
    },
    'payout_buyer': {
        'required_columns': ['unique id'],
        'uuid_columns': {
            'unique_id': 'unique id'
        },
        'default_values': {
        }
    },
    'payout_creator': {
        'required_columns': ['unique id', '[lstn] scheduled', 'lstnplus', 'playlist channel', 'playlist creator'],
        'uuid_columns': {
            'unique_id': 'unique id',
            'lstn_scheduled': '[lstn] scheduled',
            'lstnplus_formatted': 'lstnplus',
            'playlist_channel': 'playlist channel',
            'playlist_creator': 'playlist creator'
            # 'partneruser_formatted': 'partneruser'
        },
        'default_values': {
            # 'partneruser': DEFAULT_VALUE_MAPPING['partneruser']
            '[lstn] scheduled': DEFAULT_VALUE_MAPPING['[lstn] scheduled'],
            'lstnplus': DEFAULT_VALUE_MAPPING['lstnplus'],
            'playlist channel': DEFAULT_VALUE_MAPPING['playlist channel'],
            'playlist creator': DEFAULT_VALUE_MAPPING['playlist creator']
        }
    },
    'shorts_channels': {
        'required_columns': ['unique id', 'contract'],
        'uuid_columns': {
            'unique_id': 'unique id',
            'contract_formatted': 'contract',
        },
        'default_values': {
            'contract': DEFAULT_VALUE_MAPPING['contract'],
        }
    },
    'shorts_contracts': {
        'required_columns': ['unique id'],
        'uuid_columns': {
            'unique_id': 'unique id',
        },
        'default_values': {
        }
    },
    'shorts_licensed_video': {
        'required_columns': ['unique id'],
        'uuid_columns': {
            'unique_id': 'unique id',
        },
        'default_values': {
        }
    },
    'shorts_permissionvideo': {
        'required_columns': ['unique id'],
        'uuid_columns': {
            'unique_id': 'unique id'
        },
        'default_values': {
        }
    },
    # 'shorts_profits_per_video': {
    #     'required_columns': ['unique id', 'channel', 'contract', 'contractor', 'partner'],
    #     'uuid_columns': {
    #         'unique_id': 'unique id',
    #         'channel_formatted': 'channel',
    #         'contract_formatted': 'contract',
    #         'contractor_formatted': 'contractor',
    #         'partner_formatted': 'partner'
    #     },
    #     'default_values': {
    #         'channel': DEFAULT_VALUE_MAPPING['channel'],
    #         'contract': DEFAULT_VALUE_MAPPING['contract'],
    #         'contractor': DEFAULT_VALUE_MAPPING['contractor'],
    #         'partner': DEFAULT_VALUE_MAPPING['partner']
    #     }
    # },
}

BUCKET_CONFIGS = {
    'album': {
        'cover': {
            'name': 'image', 
            'path': 'album',
            'filename_pattern': lambda row: f"{row.get('codealbum', '')}_IMG.jpg"
        }
    },
    'label': {
        'logo': {'name': 'image', 'path': 'label'},
    },
    'musician': {
        'imageprofile': {'name': 'image', 'path': 'musician'},
        'imageverification': {'name': 'image', 'path': 'musician'},
    },
    'shorts_channels': {
        'thumbnails': {'name': 'image', 'path': 'shorts-channel'},
    },
    'shorts_contracts': {
        'contractfile': {'name': 'contract', 'path': 'contract'},
    },
    'shorts_licensed_video': {
        'thumbnails': {'name': 'image', 'path': 'shorts-video'},
    },
    'track': {
        'mp3 (ar)': {
            'name': 'track', 
            'path': 'mp3',
            'filename_pattern': lambda row: f"{row.get('trackcode', '')}-{row.get('tracknumber', '')}.mp3"
        },
        'wav (ar)': {
            'name': 'track', 
            'path': 'wav',
            'filename_pattern': lambda row: f"{row.get('trackcode', '')}-{row.get('tracknumber', '')}.wav"
        },
    },
    'user': {
        'imgprofile': {'name': 'profile-image', 'path': 'profile-image'},
        'businessbankaccountfile': {'name': 'business', 'path': 'business'},
        'businessreg-document': {'name': 'business', 'path': 'business'},
    }
}