import threading
import time
from tqdm import tqdm


def loading(fun, text, input_fun,*args, **kwargs):
    result = None  # Inicializa resultado
    # Inicia la barra de progreso
    with tqdm(total=100, desc=text, ncols=100) as pbar:
        def execute_fun():
            nonlocal result
            result = fun(input_fun, *args, **kwargs)

        thread = threading.Thread(target=execute_fun)
        thread.start()

        while thread.is_alive():
            time.sleep(0.02)
            pbar.update(1)

        thread.join()
        pbar.n = pbar.last_print_n = pbar.total
        pbar.refresh()

    return result
