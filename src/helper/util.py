import time


def print_elasped_time(wrappee):
    def wrapper_fn(*args, **kwargs):
        start_time = time.time()
        result = wrappee(*args, **kwargs)
        end_time = time.time()
        print(f"WorkingTime[{wrappee.__name__}]: {end_time - start_time} (sec)")
        return result

    return wrapper_fn
