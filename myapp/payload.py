
class _TopLevel:
    def __init__(self, data):
        self.event:str = data.get('event', '')
        self.user:bool = data.get('user', None)
        self.owner:bool = data.get('owner', None)


class _Account:
    def __init__(self, data):
        self.id:int = data.get('id', None)
        self.thumb:str = data.get('thumb', '')
        self.title:str = data.get('title', '')


class _Server:
    def __init__(self, data):
        self.title:str = data.get('title', '')
        self.uuid:str = data.get('uuid', '')


class _Player:
    def __init__(self, data):
        self.local:bool = data.get('local', None)
        self.publicAddress:str = data.get('publicAddress', '')
        self.title:str = data.get('title', '')
        self.uuid:str = data.get('uuid', '')


class _Metadata:
    def __init__(self, data):
        self.ratingKey:str = data.get('ratingKey', '')
        self.key:str = data.get('key', '')
        self.guid:str = data.get('guid', '')
        self.studio:str = data.get('studio', '')
        self.type:str = data.get('type', '')
        self.title:str = data.get('title', '')
        self.titleSort:str = data.get('titleSort', '')

        self.librarySectionTitle:str = data.get('librarySectionTitle', '')
        self.librarySectionType:str = data.get('librarySectionType', '')
        self.librarySectionID:int = data.get('librarySectionID', None)
        self.librarySectionKey:str = data.get('librarySectionKey', '')

        self.originalTitle:str = data.get('originalTitle', '')
        self.contentRating:str = data.get('contentRating', '')
        self.summary:str = data.get('summary', '')
        self.rating:float = data.get('rating', None)
        self.audienceRating:float = data.get('audienceRating', None)
        self.userRating:float = data.get('userRating', None)
        self.lastRatedAt:int = data.get('lastRatedAt', None)
        self.year:int = data.get('year', None)
        self.tagline:str = data.get('tagline', '')
        self.thumb:str = data.get('thumb', '')
        self.art:str = data.get('art', '')
        self.duration:int = data.get('duration', None)
        self.originallyAvailableAt:str = data.get('originallyAvailableAt', '')
        self.addedAt:int = data.get('addedAt', None)
        self.updatedAt:int = data.get('updatedAt', None)
        self.audienceRatingImage:str = data.get('audienceRatingImage', '')
        self.chapterSource:str = data.get('chapterSource', '')
        self.primaryExtraKey:str = data.get('primaryExtraKey', '')
        self.ratingImage:str = data.get('ratingImage', '')
        self.rottentomatoes:str = data.get('rottentomatoes', '')
        self.Genres:list[Tag] = [Tag(item) for item in data.get('Genre', [])]
        self.Countrys:list[Tag] = [Tag(item) for item in data.get('Country', [])]
        self.Guids:list[dict] = data.get('Guid', [])
        self.Ratings:list[Rating] = [Rating(item) for item in data.get('Rating', [])]
        self.Directors:list[Tag] = [Tag(item) for item in data.get('Director', [])]
        self.Writers:list[Tag] = [Tag(item) for item in data.get('Writer', [])]
        self.Roles:list[Tag] = [Tag(item) for item in data.get('Role', [])]
        self.Producers:list[Tag] = [Tag(item) for item in data.get('Producer', [])]
        self.Fields:list[dict] = data.get('Field', [])


class Tag:
    def __init__(self, data):
        self.id:int = data.get('id')
        self.filter:str = data.get('filter')
        self.tag:str = data.get('tag')
        self.tagKey:str = data.get('tagKey')
        self.count:int = data.get('count')
        self.role:str = data.get('role')
        self.thumb:str = data.get('thumb')


class Rating:
    def __init__(self, data):
        self.image:str = data.get('image')
        self.value:float = data.get('value')
        self.type:str = data.get('type')
        self.count:str = data.get('count')


class Payload:
    def __init__(self, data):
        self.TopLevel = _TopLevel(data)
        self.Account = _Account(data.get('Account', {}))
        self.Server = _Server(data.get('Server', {}))
        self.Player = _Player(data.get('Player', {}))
        self.Metadata = _Metadata(data.get('Metadata', {}))
