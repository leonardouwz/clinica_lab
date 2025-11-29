"""
REQUISITO 5: Validaciones transaccionales para rangos normales
"""

def validar_rango_normal(valor, valor_min, valor_max):
    """
    Valida si un valor está dentro del rango normal
    
    Args:
        valor: Valor del análisis
        valor_min: Valor mínimo del rango normal
        valor_max: Valor máximo del rango normal
    
    Returns:
        tuple: (es_valido, mensaje)
    """
    if valor_min is None or valor_max is None:
        return True, "Sin rango de referencia definido"
    
    if valor < valor_min:
        return False, f"Valor por debajo del rango normal (mínimo: {valor_min})"
    elif valor > valor_max:
        return False, f"Valor por encima del rango normal (máximo: {valor_max})"
    else:
        return True, "Valor dentro del rango normal"


def obtener_nivel_alerta(valor, valor_min, valor_max):
    """
    Determina el nivel de alerta según qué tan fuera del rango está el valor
    
    Returns:
        str: 'NORMAL', 'LEVE', 'MODERADO', 'CRITICO'
    """
    if valor_min is None or valor_max is None:
        return 'NORMAL'
    
    rango = valor_max - valor_min
    
    if valor >= valor_min and valor <= valor_max:
        return 'NORMAL'
    
    if valor < valor_min:
        diferencia = valor_min - valor
        porcentaje = (diferencia / rango) * 100
        
        if porcentaje < 10:
            return 'LEVE'
        elif porcentaje < 30:
            return 'MODERADO'
        else:
            return 'CRITICO'
    
    if valor > valor_max:
        diferencia = valor - valor_max
        porcentaje = (diferencia / rango) * 100
        
        if porcentaje < 10:
            return 'LEVE'
        elif porcentaje < 30:
            return 'MODERADO'
        else:
            return 'CRITICO'
    
    return 'NORMAL'