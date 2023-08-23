import api

class ArrayResultSetToPage:
    def __init__(self, result_set, has_more_pages, page_number = api.DEFAULT_PAGE_NUMBER, page_size = api.DEFAULT_PAGE_SIZE):
        self.result_set = result_set
        self.page_number = page_number
        self.page_size = page_size
        self.row_count = len(result_set)
        self.last_page = (self.row_count + self.page_size - 1) // self.page_size
        self.has_more_pages = has_more_pages
    
    def to_json(self):
        json_data = {
            'objetoJson' : {
                'page_size': self.row_count,
                'page_number': self.page_number,
                'has_more_pages': self.has_more_pages
            },
            'arrayJson' : 
                {
                    'rows': self.result_set
                }
            
        }
        return json_data
    
    def convert_query_to_page(query_, page_number = api.DEFAULT_PAGE_NUMBER, page_size = api.DEFAULT_PAGE_SIZE):
        query = f"""
        SELECT *
        FROM (
                SELECT a.*, ROWNUM AS rnum
                FROM (
                    {query_}
                    ORDER BY 1
                    ) a 
            ) 
        WHERE rnum BETWEEN (({page_number} - 1) * {page_size} + 1) AND ({page_number} * {page_size} + 1) 
        """ # offset en oracle versiones menores a 12c
        return query