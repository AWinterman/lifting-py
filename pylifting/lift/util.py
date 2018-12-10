from datetime import datetime

duration_formats = ('%H:%M:%S', '%M:%S')
day_format = '%Y-%m-%d'
listing_query_date_formats = ('%Y', '%Y-%m', day_format)
rpe_range = (1, 10)


def validate_date(value):
    if not value:
        return value
    for f in listing_query_date_formats:
        try:
            dt = datetime.strptime(value, f)
            return dt
        except ValueError:
            pass
