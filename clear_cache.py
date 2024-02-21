from diskcache import Cache

cache = Cache('./cache')

def list_cache_keys():
    return list(cache.iterkeys())

def clear_data_cache():
    keys = list_cache_keys()
    if not keys:
        print("Cache is currently empty.")
        return
    
    print("Available cache keys:")
    for i, key in enumerate(keys, start=1):
        print(f"{i}. {key}")
    
    selection = input("Enter the number of the cache key you want to clear (0 to clear all): ")
    try:
        selection = int(selection)
        if selection == 0:
            for key in keys:
                cache.pop(key, None)
            print("Cleared all cache entries.")
        elif 0 < selection <= len(keys):
            selected_key = keys[selection - 1]
            cache.pop(selected_key, None)
            print(f"Cleared cache for key: {selected_key}")
        else:
            print("Invalid selection.")
    except ValueError:
        print("Please enter a valid number.")
        
if __name__ == "__main__":
    clear_data_cache();