import logging

# Configuración básica del módulo de logging
logging.basicConfig(
    filename='mi_log_DBuilder.log',  # Nombre del archivo donde se guardarán los logs
    level=logging.INFO,                # Nivel de logging, INFO para registrar información general
    format='%(asctime)s - %(message)s' # Formato de los mensajes en el log, incluyendo la fecha y hora
)

def log_action_decorator(func):
    """
    Decorador que registra la ejecución de la función decorada.

    Este decorador registra cuando se inicia y finaliza la ejecución de la función,
    así como los argumentos que se le pasan.

    Args:
        func (callable): La función que se va a decorar.

    Returns:
        callable: La función decorada que registra su actividad.
    """
    def wrapper(*args, **kwargs):
        # Registro de la ejecución de la función con sus argumentos
        logging.info(f"Ejecutando {func.__name__} con argumentos: {args}, {kwargs}")
        result = func(*args, **kwargs)  # Llamada a la función original
        # Registro de la finalización de la ejecución
        logging.info(f"Finalizó la ejecución de {func.__name__}")
        return result  # Retorno del resultado de la función original
    return wrapper

def input_validation_decorator(valid_responses):
    """
    Decorador que valida la entrada de una función.

    Este decorador asegura que la respuesta proporcionada por el usuario esté dentro
    de un conjunto de respuestas válidas. Si la respuesta no es válida, se solicita al
    usuario que ingrese una opción válida.

    Args:
        valid_responses (list): Una lista de respuestas válidas aceptadas por la función decorada.

    Returns:
        callable: La función decorada que valida su entrada.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            while True:
                response = func(*args, **kwargs).strip().lower()  # Obtención de la respuesta del usuario
                if response in valid_responses:
                    return response  # Retorno de la respuesta válida
                else:
                    # Mensaje de error si la respuesta no es válida
                    print(f"Respuesta no reconocida. Por favor, ingrese una de las siguientes opciones: {', '.join(valid_responses)}")
        return wrapper
    return decorator
