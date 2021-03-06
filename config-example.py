class PRODUCTION:
    def __init__(self) -> None:
        self.id = "PRODUCTION ID"
        self.token = "PRODUCTION TOKEN"
        self = BOTH(self)

class DEV:
    def __init__(self) -> None:
        self.id = "DEV ID"
        self.token = "DEV TOKEN"
        self = BOTH(self)

class BOTH:
    def __init__(self, other_class) -> None:
        other_class.gif_token = "GIPHY TOKEN"
        other_class.serpapi_key = "SERP API KEY"