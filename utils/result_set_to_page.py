import api

class ArrayResultSetToPage:
    def __init__(self, result_set, page_number = api.DEFAULT_PAGE_NUMBER, page_size = api.DEFAULT_PAGE_SIZE):
        self.result_set = result_set
        self.page_number = page_number
        self.page_size = page_size
        self.row_count = len(result_set)
        self.last_page = (self.row_count + self.page_size - 1) // self.page_size
        self.has_more_pages = page_number < self.last_page
        
        self.rows = self._get_rows_for_page()
    
    def _get_rows_for_page(self):
        start_index = (self.page_number - 1) * self.page_size
        end_index = start_index + self.page_size
        return self.result_set[start_index:end_index]
    
    def to_json(self):
        json_data = {
            'objetoJson' : {
                #'row_count': self.row_count,
                'page_size': self.page_size,
                'page_number': self.page_number,
                #'last_page': self.last_page,
                'has_more_pages': self.has_more_pages
            },
            'arrayJson' : 
                {'rows': self.rows}
            
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
        WHERE rnum BETWEEN (({page_number} - 1) * {page_size} + 1) AND ({page_number} * {page_size}) 
        """
        return query