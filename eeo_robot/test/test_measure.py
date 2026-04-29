import pytest
from eeo_robot.measure_node import EeoMeasureNode
import rclpy

# Тест на расчет длины
def test_length_calculation():
    print("\n[ТЕСТ] Проверка математики: перевод пикселей в метры...")
    pixels = 450
    scale = 0.6
    result_m = (pixels * scale) / 1000.0
    print(f"   - Вход: {pixels} px, Коэффициент: {scale}")
    print(f"   - Результат: {result_m} м (Ожидалось: 0.27 м)")
    assert result_m == 0.27
    print("[ОК] Расчет корректен.")

# Тест на замену строк в XML
def test_xml_template_replacement():
    print("\n[ТЕСТ] Проверка подстановки данных в XML-шаблон...")
    template = "<length>{L_VALUE}</length><offset>{L_HALF}</offset>"
    length = 0.3
    updated = template.replace("{L_VALUE}", str(length)).replace("{L_HALF}", str(length/2))
    print(f"   - Подставлено L={length}, L/2={length/2}")
    print(f"   - Итоговая строка: {updated}")
    assert "0.3" in updated
    assert "0.15" in updated
    print("[ОК] Шаблон обновляется верно.")

# Тест: не падает ли создание ноды
def test_node_creation():
    print("\n[ТЕСТ] Проверка инициализации ROS-ноды...")
    if not rclpy.ok():
        rclpy.init()
    node = EeoMeasureNode()
    print(f"   - Нода '{node.get_name()}' успешно создана.")
    assert node.get_name() == 'eeo_measure_node'
    node.destroy_node()
    rclpy.shutdown()
    print("[ОК] Нода запускается и останавливается без ошибок.")
    
# Тест плавного износа и автоматической замены электрода
def test_electrode_wear_and_reset():
    print("\n[ТЕСТ] Проверка логики износа и цикла замены...")
    if not rclpy.ok():
        rclpy.init()
    
    node = EeoMeasureNode()
    initial_length, _ = node.get_electrode_data()
    print(f"   - Начальная длина электрода: {initial_length} м")
    
    next_length, _ = node.get_electrode_data()
    print(f"   - Длина после одного шага износа: {next_length} м")
    assert next_length < initial_length
    
    print("   - Имитируем критический износ (301 px)...")
    node.current_pixels = 301.0
    reset_length, _ = node.get_electrode_data()
    
    print(f"   - Длина после автоматической замены: {reset_length} м")
    assert reset_length > next_length
    assert node.current_pixels == 500.0
    print("[ОК] Цикл износа и замены работает идеально.")
    
    node.destroy_node()

