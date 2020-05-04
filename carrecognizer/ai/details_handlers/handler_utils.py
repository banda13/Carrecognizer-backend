def most_common(lst):
    return max(set(lst), key=lst.count)


def averaged_list_of_json(source):
    temp_response = {}
    averaged_response = {}
    for item in source:
        if 'error' not in item:
            for key in item[0].keys():
                if key not in temp_response:
                    temp_response[key] = []
                temp_response[key].append(item[0][key])
    for key, value in temp_response.items():
        try:
            if len(value) < 1:
                continue
            value = list(map(float, value))
            averaged_response[key] = sum(value) / float(len(value))
        except (ValueError, TypeError):
            try:
                value = list(map(int, value))
                sum(value) / float(len(value))
            except (ValueError, TypeError):
                try:
                    averaged_response[key] = most_common(value)
                except Exception:
                    pass
    return averaged_response