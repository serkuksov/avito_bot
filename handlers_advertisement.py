from avito_parser import Advertisement


def checking_filter(advertisement: Advertisement):
    if 10000 <= advertisement.price <= 400000 and 'металлический' not in advertisement.parameters:
        return True

