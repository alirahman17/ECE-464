import scrapy
from ..items import AmcItem

class AmcSpider(scrapy.Spider):
    name = "AMC"
    allowed_domains = ["amctheatres.com"]
    start_urls = ["https://www.amctheatres.com/movies/frozen-2-49085/showtimes/all/2019-11-25/amc-empire-25/all"]
    start_date = 24;
    place = "amc-empire-25"
    count = 0

    def parse(self, response):
        new_loc = response.css('select.Showtimes-Action-Dropdown#showtimes-theatre-filter option:nth-child(4)::attr(value)').get()
        location = response.css('select.Showtimes-Action-Dropdown#showtimes-theatre-filter option:nth-child(1)::text').getall()
        location = location[0]
        date = response.css('select.Showtimes-Action-Dropdown#showtimes-date-filter option:checked::text').get()
        movies = response.css('div.ShowtimesByTheatre-film')
        for movie in movies:
            name = movie.css('a.MovieTitleHeader-title h2::text').get()
            first_theatre = movie.css('div.Showtimes-Section-Wrapper-First')
            for theatre in first_theatre:
                type = theatre.css('div.Showtimes-Section--PremiumFormat-Heading-Title h4::text').get()
                showtimes = theatre.css('div.Showtime')
                for showtime in showtimes:
                    AmcSpider.count += 1
                    item = AmcItem()
                    time = showtime.css('::text').get()
                    item['movie_name'] = name
                    item['theater_name'] = location
                    item['date'] = date
                    item['time'] = time
                    item['type'] = type
                    yield item
            theatres = movie.css('div.Showtimes-Section-Wrapper')
            for theatre in theatres:
                type = theatre.css('div.Showtimes-Section--PremiumFormat-Heading-Title h4::text').get()
                showtimes = theatre.css('div.Showtime')
                for showtime in showtimes:
                    AmcSpider.count += 1
                    item = AmcItem()
                    time = showtime.css('::text').get()
                    item['movie_name'] = name
                    item['theater_name'] = location
                    item['date'] = date
                    item['time'] = time
                    item['type'] = type
                    yield item
        if AmcSpider.start_date <= 29:
            AmcSpider.start_date += 1
            next_page = "https://www.amctheatres.com/movies/frozen-2-49085/showtimes/all/2019-11-" + str(AmcSpider.start_date) + "/" + str(AmcSpider.place) + "/all"
            yield response.follow(next_page, callback = self.parse)
        else:
            AmcSpider.start_date = 24
            AmcSpider.place = new_loc
            next_page = "https://www.amctheatres.com/movies/frozen-2-49085/showtimes/all/2019-11-" + str(AmcSpider.start_date) + "/" + str(AmcSpider.place) + "/all"
            yield response.follow(next_page, callback = self.parse)
