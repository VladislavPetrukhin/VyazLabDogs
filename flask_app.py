from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

# Абсолютный путь к базе данных
DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

# Ограничения для валидации
VALIDATION_RULES = {
    'dogs': {
        'name': {'min_length': 5, 'max_length': 100},  # Имя собаки: 5-100 символов
        'birth_date': {'format': 'YYYY-MM-DD'},        # Дата рождения: формат YYYY-MM-DD
        'microchip_number': {'min_length': 10, 'max_length': 20},  # Номер микрочипа: 10-20 символов
        'registration_date': {'format': 'YYYY-MM-DD'}  # Дата регистрации: формат YYYY-MM-DD
    },
    'breeds': {
        'breed_name': {'min_length': 3, 'max_length': 100},  # Название породы: 3-100 символов
        'average_lifes': {'min': 5, 'max': 20}               # Средняя продолжительность жизни: 5-20 лет
    },
    'locations': {
        'location_name': {'min_length': 3, 'max_length': 100},  # Название места: 3-100 символов
        'address': {'min_length': 5, 'max_length': 200}         # Адрес: 5-200 символов
    },
    'vet_examinations': {
        'examination_date': {'format': 'YYYY-MM-DD'},  # Дата осмотра: формат YYYY-MM-DD
        'diagnosis': {'min_length': 5, 'max_length': 200},  # Диагноз: 5-200 символов
        'treatment': {'min_length': 5, 'max_length': 200}   # Лечение: 5-200 символов
    },
    'getting': {
        'getting_by': {'min_length': 3, 'max_length': 100},  # Кем получена: 3-100 символов
        'contact_info': {'min_length': 5, 'max_length': 100},  # Контактная информация: 5-100 символов
        'getting_type': {'min_length': 3, 'max_length': 50},   # Тип получения: 3-50 символов
        'reason': {'min_length': 5, 'max_length': 200}         # Причина: 5-200 символов
    }
}
TABLES = {
    'dogs': {
        'name': {'type': 'text', 'label': 'Имя собаки'},
        'birth_date': {'type': 'date', 'label': 'Дата рождения'},
        'breeds_id': {'type': 'number', 'label': 'Порода', 'has_options': 'breed_name'},
        'getting_id': {'type': 'number', 'label': 'Получение', 'has_options': 'getting_by'},
        'vet_examinations_id': {'type': 'number', 'label': 'Ветеринарный осмотр', 'has_options': 'examination_date'},
        'location_id': {'type': 'number', 'label': 'Место размещения', 'has_options': 'location_name'},
        'registration_date': {'type': 'date', 'label': 'Дата регистрации'},
        'microchip_number': {'type': 'text', 'label': 'Номер микрочипа'},
        'coat_type': {'type': 'number', 'label': 'Тип шерсти', 'has_options': 'coat_type_name'},
        'color_variations': {'type': 'number', 'label': 'Окрас', 'has_options': 'color_variations_name'},
        'temperament': {'type': 'number', 'label': 'Темперамент', 'has_options': 'temperament_name'},
        'size': {'type': 'number', 'label': 'Размер', 'has_options': 'size_name'}
    },
    'breeds': {
        'breed_name': {'type': 'text', 'label': 'Название породы'},
        'breed_group': {'type': 'text', 'label': 'Группа породы'},
        'origin_country': {'type': 'text', 'label': 'Страна происхождения'},
        'average_lifes': {'type': 'number', 'label': 'Средняя продолжительность жизни'},
        'typical_use': {'type': 'text', 'label': 'Типичное использование'},
        'common_health_issues': {'type': 'text', 'label': 'Распространенные проблемы со здоровьем'},
        'recommended_vaccinations': {'type': 'text', 'label': 'Рекомендуемые вакцинации'},
        'veterinary_care': {'type': 'text', 'label': 'Потребности в ветеринарном уходе'},
        'average_weight_male': {'type': 'number', 'label': 'Средний вес самцов'},
        'average_weight_female': {'type': 'number', 'label': 'Средний вес самок'},
        'trainability_level': {'type': 'text', 'label': 'Уровень обучаемости'},
        'recommended_training_age': {'type': 'number', 'label': 'Рекомендуемый возраст начала дрессировки'},
        'common_behavioral_issues': {'type': 'text', 'label': 'Распространенные поведенческие проблемы'},
        'preferred_training_methods': {'type': 'text', 'label': 'Предпочтительные методы дрессировки'},
        'typical_learning_period': {'type': 'number', 'label': 'Типичный период обучения'}
    },
    'vet_examinations': {
        'dog_id': {'type': 'number', 'label': 'ID собаки'},
        'examination_date': {'type': 'date', 'label': 'Дата осмотра'},
        'veterinarian_name': {'type': 'text', 'label': 'Имя ветеринара'},
        'diagnosis': {'type': 'text', 'label': 'Диагноз'},
        'treatment': {'type': 'text', 'label': 'Лечение'},
        'next_examination_date': {'type': 'date', 'label': 'Дата следующего осмотра'}
    },
    'locations': {
        'location_name': {'type': 'text', 'label': 'Название места'},
        'location_type': {'type': 'text', 'label': 'Тип места'},
        'address': {'type': 'text', 'label': 'Адрес'},
        'contact_info': {'type': 'text', 'label': 'Контактная информация'},
        'price': {'type': 'number', 'label': 'Стоимость'},
        'availability': {'type': 'number', 'label': 'Количество собак'},
        'website': {'type': 'text', 'label': 'Сайт'}
    },
    'getting': {
        'getting_by': {'type': 'text', 'label': 'Кем передана'},
        'contact_info': {'type': 'text', 'label': 'Контактная информация'},
        'getting_type': {'type': 'text', 'label': 'Тип передачи'},
        'reason': {'type': 'text', 'label': 'Причина передачи'}
    }
}
# Функция для валидации данных
def validate_data(data, rules):
    errors = []
    for field, value in data.items():
        if value is None or value == '':
            continue  # Пропускаем необязательные поля
        if field in rules:
            field_rules = rules[field]
            if 'min_length' in field_rules and len(value) < field_rules['min_length']:
                errors.append(f"{field}: длина должна быть не менее {field_rules['min_length']} символов")
            if 'max_length' in field_rules and len(value) > field_rules['max_length']:
                errors.append(f"{field}: длина не должна превышать {field_rules['max_length']} символов")
            if 'min' in field_rules or 'max' in field_rules:
                try:
                    num_value = float(value) if '.' in value else int(value)
                    if 'min' in field_rules and num_value < field_rules['min']:
                        errors.append(f"{field}: значение должно быть не менее {field_rules['min']}")
                    if 'max' in field_rules and num_value > field_rules['max']:
                        errors.append(f"{field}: значение не должно превышать {field_rules['max']}")
                except ValueError:
                    errors.append(f"{field}: должно быть числом")
            if 'format' in field_rules and field_rules['format'] == 'YYYY-MM-DD':
                try:
                    datetime.strptime(value, '%Y-%m-%d')
                except ValueError:
                    errors.append(f"{field}: неверный формат даты, ожидается YYYY-MM-DD")
    return errors

# Главная страница
@app.route('/')
def index():
    return render_template('index.html')



# Маршрут для получения атрибутов таблицы
@app.route('/get_attributes')
def get_attributes():
    table = request.args.get('table')
    attributes = {
        'dogs': {
            'name': {'type': 'text', 'label': 'Имя собаки'},
            'birth_date': {'type': 'date', 'label': 'Дата рождения'},
            'breeds_id': {'type': 'number', 'label': 'Порода', 'has_options': 'breed_name'},
            'getting_id': {'type': 'number', 'label': 'Получение', 'has_options': 'getting_by'},
            'vet_examinations_id': {'type': 'number', 'label': 'Ветеринарный осмотр', 'has_options': 'examination_date'},
            'location_id': {'type': 'number', 'label': 'Место размещения', 'has_options': 'location_name'},
            'registration_date': {'type': 'date', 'label': 'Дата регистрации'},
            'microchip_number': {'type': 'text', 'label': 'Номер микрочипа'},
            'coat_type': {'type': 'number', 'label': 'Тип шерсти', 'has_options': 'coat_type_name'},
            'color_variations': {'type': 'number', 'label': 'Окрас', 'has_options': 'color_variations_name'},
            'temperament': {'type': 'number', 'label': 'Темперамент', 'has_options': 'temperament_name'},
            'size': {'type': 'number', 'label': 'Размер', 'has_options': 'size_name'}
        },
        'breeds': {
            'breed_name': {'type': 'text', 'label': 'Название породы'},
            'breed_group': {'type': 'text', 'label': 'Группа породы'},
            'origin_country': {'type': 'text', 'label': 'Страна происхождения'},
            'average_lifes': {'type': 'number', 'label': 'Средняя продолжительность жизни'},
            'typical_use': {'type': 'text', 'label': 'Типичное использование'},
            'common_health_issues': {'type': 'text', 'label': 'Распространенные проблемы со здоровьем'},
            'recommended_vaccinations': {'type': 'text', 'label': 'Рекомендуемые вакцинации'},
            'veterinary_care': {'type': 'text', 'label': 'Потребности в ветеринарном уходе'},
            'average_weight_male': {'type': 'number', 'label': 'Средний вес самцов'},
            'average_weight_female': {'type': 'number', 'label': 'Средний вес самок'},
            'trainability_level': {'type': 'text', 'label': 'Уровень обучаемости'},
            'recommended_training_age': {'type': 'number', 'label': 'Рекомендуемый возраст начала дрессировки'},
            'common_behavioral_issues': {'type': 'text', 'label': 'Распространенные поведенческие проблемы'},
            'preferred_training_methods': {'type': 'text', 'label': 'Предпочтительные методы дрессировки'},
            'typical_learning_period': {'type': 'number', 'label': 'Типичный период обучения'}
        },
        'vet_examinations': {
            'dog_id': {'type': 'number', 'label': 'ID собаки'},
            'examination_date': {'type': 'date', 'label': 'Дата осмотра'},
            'veterinarian_name': {'type': 'text', 'label': 'Имя ветеринара'},
            'diagnosis': {'type': 'text', 'label': 'Диагноз'},
            'treatment': {'type': 'text', 'label': 'Лечение'},
            'next_examination_date': {'type': 'date', 'label': 'Дата следующего осмотра'}
        },
        'locations': {
            'location_name': {'type': 'text', 'label': 'Название места'},
            'location_type': {'type': 'text', 'label': 'Тип места'},
            'address': {'type': 'text', 'label': 'Адрес'},
            'contact_info': {'type': 'text', 'label': 'Контактная информация'},
            'price': {'type': 'number', 'label': 'Стоимость'},
            'availability': {'type': 'number', 'label': 'Количество собак'},
            'website': {'type': 'text', 'label': 'Сайт'}
        },
        'getting': {
            'getting_by': {'type': 'text', 'label': 'Кем передана'},
            'contact_info': {'type': 'text', 'label': 'Контактная информация'},
            'getting_type': {'type': 'text', 'label': 'Тип передачи'},
            'reason': {'type': 'text', 'label': 'Причина передачи'}
        }
    }
    return jsonify(attributes.get(table, {}))

# Новый маршрут для получения значений атрибута
@app.route('/get_attribute_values')
def get_attribute_values():
    table = request.args.get('table', '')
    attribute = request.args.get('attribute', '')
    if table in TABLES and attribute in TABLES[table]:
        attr_info = TABLES[table][attribute]
        column = attribute
        with get_db_connection() as conn:
            # Обработка внешних ключей
            if table == 'dogs' and attribute in ['breeds_id', 'location_id', 'vet_examinations_id', 'getting_id', 'coat_type', 'color_variations', 'temperament', 'size']:
                if attribute == 'breeds_id':
                    query = "SELECT DISTINCT b.breed_name FROM breeds b WHERE b.breed_name IS NOT NULL ORDER BY b.breed_name"
                    column_name = 'breed_name'
                elif attribute == 'location_id':
                    query = "SELECT DISTINCT l.location_name FROM locations l WHERE l.location_name IS NOT NULL ORDER BY l.location_name"
                    column_name = 'location_name'
                elif attribute == 'vet_examinations_id':
                    query = "SELECT DISTINCT ve.examination_date FROM vet_examinations ve WHERE ve.examination_date IS NOT NULL ORDER BY ve.examination_date"
                    column_name = 'examination_date'
                elif attribute == 'getting_id':
                    query = "SELECT DISTINCT g.getting_by FROM getting g WHERE g.getting_by IS NOT NULL ORDER BY g.getting_by"
                    column_name = 'getting_by'
                elif attribute == 'coat_type':
                    query = "SELECT DISTINCT ct.coat_type_name FROM coat_type ct WHERE ct.coat_type_name IS NOT NULL ORDER BY ct.coat_type_name"
                    column_name = 'coat_type_name'
                elif attribute == 'color_variations':
                    query = "SELECT DISTINCT cv.color_variations_name FROM color_variations cv WHERE cv.color_variations_name IS NOT NULL ORDER BY cv.color_variations_name"
                    column_name = 'color_variations_name'
                elif attribute == 'temperament':
                    query = "SELECT DISTINCT t.temperament_name FROM temperament t WHERE t.temperament_name IS NOT NULL ORDER BY t.temperament_name"
                    column_name = 'temperament_name'
                elif attribute == 'size':
                    query = "SELECT DISTINCT s.size_name FROM size s WHERE s.size_name IS NOT NULL ORDER BY s.size_name"
                    column_name = 'size_name'
                values = [row[column_name] for row in conn.execute(query).fetchall()]
            else:
                query = f"SELECT DISTINCT {column} FROM {table} WHERE {column} IS NOT NULL ORDER BY {column}"
                values = [row[column] for row in conn.execute(query).fetchall()]
            print(f"Table: {table}, Attribute: {attribute}, Values: {values}")  # Отладка
            return jsonify(values)
    return jsonify([])
    
# Маршрут для получения уникальных значений атрибута
@app.route('/get_values')
def get_values():
    table = request.args.get('table')
    attribute = request.args.get('attribute')
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = f"SELECT DISTINCT {attribute} FROM {table} ORDER BY {attribute}"
        values = [row[attribute] for row in cursor.execute(query).fetchall()]
    return jsonify(values)
    
@app.route('/get_filtered_values', methods=['GET', 'POST'])
def get_filtered_values():
    if request.method == 'POST':
        # Обработка POST-запроса (две таблицы)
        table1 = request.form.get('table1')
        attr1 = request.form.get('attr1')
        value1 = request.form.get('value1')
        table2 = request.form.get('table2')
        attr2 = request.form.get('attr2')

        # Валидация входных данных
        if not all([table1, attr1, value1, table2, attr2]):
            return jsonify({'error': 'Все параметры должны быть указаны'}), 400

        with get_db_connection() as conn:
            cursor = conn.cursor()
            if table1 == 'breeds' and table2 == 'dogs' and attr1 == 'id' and attr2 == 'name':
                query = """
                    SELECT DISTINCT d.name 
                    FROM dogs d
                    JOIN breeds b ON d.breeds_id = b.id
                    WHERE b.id = ?
                    ORDER BY d.name
                """
                values = [row['name'] for row in cursor.execute(query, (value1,)).fetchall()]
            else:
                # Общий случай для POST
                table_relationships = {
                    ('breeds', 'dogs'): ('b', 'd', 'JOIN dogs d ON d.breeds_id = b.id'),
                    ('dogs', 'vet_examinations'): ('d', 've', 'JOIN vet_examinations ve ON d.vet_examinations_id = ve.id'),
                    ('dogs', 'locations'): ('d', 'l', 'JOIN locations l ON d.location_id = l.id'),
                    ('dogs', 'getting'): ('d', 'g', 'JOIN getting g ON d.getting_id = g.id'),
                    ('breeds', 'locations'): ('b', 'l', 'JOIN dogs d ON d.breeds_id = b.id JOIN locations l ON d.location_id = l.id'),
                    ('breeds', 'vet_examinations'): ('b', 've', 'JOIN dogs d ON d.breeds_id = b.id JOIN vet_examinations ve ON d.vet_examinations_id = ve.id'),
                }
                if (table1, table2) in table_relationships:
                    alias0, alias1, join_condition = table_relationships[(table1, table2)]
                    query = f"""
                        SELECT DISTINCT {alias1}.{attr2}
                        FROM {table1} {alias0}
                        {join_condition}
                        WHERE {alias0}.{attr1} = ?
                        ORDER BY {alias1}.{attr2}
                    """
                    values = [row[attr2] for row in cursor.execute(query, (value1,)).fetchall()]
                else:
                    return jsonify({'error': f'Нет связи между {table1} и {table2}'}), 400
            return jsonify(values)

    else:
        # Обработка GET-запроса (одна или две таблицы)
        table0 = request.args.get('table0')  # Первая таблица
        table1 = request.args.get('table1')  # Вторая таблица (опционально)
        first_attr = request.args.get('first_attr')
        first_value = request.args.get('first_value')
        second_attr = request.args.get('second_attr')

        # Валидация входных данных
        if not all([table0, first_attr, first_value, second_attr]):
            return jsonify({'error': 'Все обязательные параметры должны быть указаны'}), 400

        # Словарь связей между таблицами
        table_relationships = {
            ('breeds', 'dogs'): ('b', 'd', 'JOIN dogs d ON d.breeds_id = b.id'),
            ('dogs', 'vet_examinations'): ('d', 've', 'JOIN vet_examinations ve ON d.vet_examinations_id = ve.id'),
            ('dogs', 'locations'): ('d', 'l', 'JOIN locations l ON d.location_id = l.id'),
            ('dogs', 'getting'): ('d', 'g', 'JOIN getting g ON d.getting_id = g.id'),
            ('breeds', 'locations'): ('b', 'l', 'JOIN dogs d ON d.breeds_id = b.id JOIN locations l ON d.location_id = l.id'),
            ('breeds', 'vet_examinations'): ('b', 've', 'JOIN dogs d ON d.breeds_id = b.id JOIN vet_examinations ve ON d.vet_examinations_id = ve.id'),
        }

        with get_db_connection() as conn:
            cursor = conn.cursor()
            if table1 and (table0, table1) in table_relationships:
                # Работа с двумя таблицами
                alias0, alias1, join_condition = table_relationships[(table0, table1)]
                query = f"""
                    SELECT DISTINCT {alias1}.{second_attr}
                    FROM {table0} {alias0}
                    {join_condition}
                    WHERE {alias0}.{first_attr} = ?
                    ORDER BY {alias1}.{second_attr}
                """
            else:
                # Работа с одной таблицей
                query = f"""
                    SELECT DISTINCT {second_attr}
                    FROM {table0}
                    WHERE {first_attr} = ?
                    ORDER BY {second_attr}
                """

            try:
                values = [row[0] for row in cursor.execute(query, (first_value,)).fetchall()]
                return jsonify(values)
            except sqlite3.OperationalError as e:
                return jsonify({'error': str(e)}), 500

# Маршрут для добавления нового значения
@app.route('/add_value', methods=['POST'])
def add_value():
    data = request.get_json()
    table = data.get('table')
    attribute = data.get('attribute')
    value = data.get('value')
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"INSERT INTO {table} ({attribute}) VALUES (?)", (value,))
            conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
                
# Маршрут для страницы "Запросы синхронизированные"
@app.route('/sync_queries', methods=['GET', 'POST'])
def sync_queries():
    # Инициализация переменных
    selected_table = None
    selected_attr1 = None
    selected_value1 = None
    selected_table1 = None
    selected_attr2 = None
    selected_value2 = None
    results = None
    errors = []
    values1 = []  # Инициализация по умолчанию
    values2 = []  # Инициализация по умолчанию

    # Список таблиц
    tables = {
        'dogs': 'Собаки',
        'breeds': 'Породы',
        'vet_examinations': 'Ветеринарные осмотры',
        'locations': 'Места размещения',
    }

    # Атрибуты для каждой таблицы
    attributes = {
        'dogs': {
            'name': {'type': 'text', 'label': 'Имя собаки'},
            'birth_date': {'type': 'date', 'label': 'Дата рождения'},
            'breeds_id': {'type': 'number', 'label': 'Порода', 'has_options': 'breed_name'},
            'getting_id': {'type': 'number', 'label': 'Получение', 'has_options': 'getting_by'},
            'vet_examinations_id': {'type': 'number', 'label': 'Ветеринарный осмотр', 'has_options': 'examination_date'},
            'location_id': {'type': 'number', 'label': 'Место размещения', 'has_options': 'location_name'},
            'registration_date': {'type': 'date', 'label': 'Дата регистрации'},
            'microchip_number': {'type': 'text', 'label': 'Номер микрочипа'},
            'coat_type': {'type': 'number', 'label': 'Тип шерсти', 'has_options': 'coat_type_name'},
            'color_variations': {'type': 'number', 'label': 'Окрас', 'has_options': 'color_variations_name'},
            'temperament': {'type': 'number', 'label': 'Темперамент', 'has_options': 'temperament_name'},
            'size': {'type': 'number', 'label': 'Размер', 'has_options': 'size_name'}
        },
        'breeds': {
            'breed_name': {'type': 'text', 'label': 'Название породы'},
            'breed_group': {'type': 'text', 'label': 'Группа породы'},
            'origin_country': {'type': 'text', 'label': 'Страна происхождения'},
            'average_lifes': {'type': 'number', 'label': 'Средняя продолжительность жизни'},
            'typical_use': {'type': 'text', 'label': 'Типичное использование'},
            'common_health_issues': {'type': 'text', 'label': 'Распространенные проблемы со здоровьем'},
            'recommended_vaccinations': {'type': 'text', 'label': 'Рекомендуемые вакцинации'},
            'veterinary_care': {'type': 'text', 'label': 'Потребности в ветеринарном уходе'},
            'average_weight_male': {'type': 'number', 'label': 'Средний вес самцов'},
            'average_weight_female': {'type': 'number', 'label': 'Средний вес самок'},
            'trainability_level': {'type': 'text', 'label': 'Уровень обучаемости'},
            'recommended_training_age': {'type': 'number', 'label': 'Рекомендуемый возраст начала дрессировки'},
            'common_behavioral_issues': {'type': 'text', 'label': 'Распространенные поведенческие проблемы'},
            'preferred_training_methods': {'type': 'text', 'label': 'Предпочтительные методы дрессировки'},
            'typical_learning_period': {'type': 'number', 'label': 'Типичный период обучения'}
        },
        'vet_examinations': {
            'dog_id': {'type': 'number', 'label': 'ID собаки'},
            'examination_date': {'type': 'date', 'label': 'Дата осмотра'},
            'veterinarian_name': {'type': 'text', 'label': 'Имя ветеринара'},
            'diagnosis': {'type': 'text', 'label': 'Диагноз'},
            'treatment': {'type': 'text', 'label': 'Лечение'},
            'next_examination_date': {'type': 'date', 'label': 'Дата следующего осмотра'}
        },
        'locations': {
            'location_name': {'type': 'text', 'label': 'Название места'},
            'location_type': {'type': 'text', 'label': 'Тип места'},
            'address': {'type': 'text', 'label': 'Адрес'},
            'contact_info': {'type': 'text', 'label': 'Контактная информация'},
            'price': {'type': 'number', 'label': 'Стоимость'},
            'availability': {'type': 'number', 'label': 'Количество собак'},
            'website': {'type': 'text', 'label': 'Сайт'}
        },
        'getting': {
            'getting_by': {'type': 'text', 'label': 'Кем передана'},
            'contact_info': {'type': 'text', 'label': 'Контактная информация'},
            'getting_type': {'type': 'text', 'label': 'Тип передачи'},
            'reason': {'type': 'text', 'label': 'Причина передачи'}
        }
    }

    if request.method == 'POST':
        selected_table = request.form.get('table')
        selected_table1 = request.form.get('table1')
        selected_attr1 = request.form.get('first_attribute')
        selected_value1 = request.form.get('first_value')
        selected_attr2 = request.form.get('second_attribute')
        selected_value2 = request.form.get('second_value')

        # Получаем атрибуты для выбранной таблицы
        attrs = attributes.get(selected_table, {}) if selected_table else {}
        attrs1 = attributes.get(selected_table1, {}) if selected_table1 else {}

        # Получаем уникальные значения для первого атрибута
        if selected_table and selected_attr1:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                query = f"SELECT DISTINCT {selected_attr1} FROM {selected_table} ORDER BY {selected_attr1}"
                values1 = [row[selected_attr1] for row in cursor.execute(query).fetchall()]

        # Получаем уникальные значения для второго атрибута с учетом первой таблицы и её значения
        if selected_table and selected_table1 and selected_attr2 and selected_value1:
            table_relationships = {
                ('breeds', 'dogs'): ('b', 'd', 'JOIN dogs d ON d.breeds_id = b.id'),
                ('dogs', 'vet_examinations'): ('d', 've', 'JOIN vet_examinations ve ON d.vet_examinations_id = ve.id'),
                ('dogs', 'locations'): ('d', 'l', 'JOIN locations l ON d.location_id = l.id'),
                ('dogs', 'getting'): ('d', 'g', 'JOIN getting g ON d.getting_id = g.id'),
                ('breeds', 'locations'): ('b', 'l', 'JOIN dogs d ON d.breeds_id = b.id JOIN locations l ON d.location_id = l.id'),
                ('breeds', 'vet_examinations'): ('b', 've', 'JOIN dogs d ON d.breeds_id = b.id JOIN vet_examinations ve ON d.vet_examinations_id = ve.id'),
            }
            if (selected_table, selected_table1) in table_relationships:
                alias0, alias1, join_condition = table_relationships[(selected_table, selected_table1)]
                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    query = f"""
                        SELECT DISTINCT {alias1}.{selected_attr2}
                        FROM {selected_table} {alias0}
                        {join_condition}
                        WHERE {alias0}.{selected_attr1} = ?
                        ORDER BY {alias1}.{selected_attr2}
                    """
                    try:
                        values2 = [row[selected_attr2] for row in cursor.execute(query, (selected_value1,)).fetchall()]
                    except sqlite3.OperationalError as e:
                        errors.append(f"Ошибка при получении значений второго атрибута: {str(e)}")
                        values2 = []
            else:
                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    query = f"SELECT DISTINCT {selected_attr2} FROM {selected_table} WHERE {selected_attr1} = ? ORDER BY {selected_attr2}"
                    try:
                        values2 = [row[selected_attr2] for row in cursor.execute(query, (selected_value1,)).fetchall()]
                    except sqlite3.OperationalError as e:
                        errors.append(f"Ошибка при получении значений второго атрибута: {str(e)}")
                        values2 = []

        # Валидация POST-запроса
        if not selected_table or selected_table not in tables:
            errors.append("Выберите первую таблицу")
        elif not selected_attr1 or selected_attr1 not in attrs:
            errors.append("Выберите первый атрибут")
        elif not selected_value1:
            errors.append("Выберите значение для первого атрибута")
        elif selected_attr2 and not selected_table1:
            errors.append("Выберите вторую таблицу, если выбран второй атрибут")
        elif selected_attr2 and selected_attr2 not in attrs1:
            errors.append("Выберите корректный второй атрибут")
        elif selected_attr2 and not selected_value2:
            errors.append("Выберите значение для второго атрибута")
        else:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                # Словарь связей между таблицами
                table_relationships = {
                    ('breeds', 'dogs'): ('b', 'd', 'JOIN dogs d ON d.breeds_id = b.id'),
                    ('dogs', 'vet_examinations'): ('d', 've', 'JOIN vet_examinations ve ON d.vet_examinations_id = ve.id'),
                    ('dogs', 'locations'): ('d', 'l', 'JOIN locations l ON d.location_id = l.id'),
                    ('dogs', 'getting'): ('d', 'g', 'JOIN getting g ON d.getting_id = g.id'),
                    ('breeds', 'locations'): ('b', 'l', 'JOIN dogs d ON d.breeds_id = b.id JOIN locations l ON d.location_id = l.id'),
                    ('breeds', 'vet_examinations'): ('b', 've', 'JOIN dogs d ON d.breeds_id = b.id JOIN vet_examinations ve ON d.vet_examinations_id = ve.id'),
                }

                if selected_table1 and (selected_table, selected_table1) in table_relationships:
                    alias0, alias1, join_condition = table_relationships[(selected_table, selected_table1)]
                    query = f"""
                        SELECT {alias1}.*
                        FROM {selected_table} {alias0}
                        {join_condition}
                        WHERE {alias0}.{selected_attr1} = ?
                    """
                    params = [selected_value1]
                    if selected_attr2 and selected_value2:
                        query += f" AND {alias1}.{selected_attr2} = ?"
                        params.append(selected_value2)
                else:
                    query = f"SELECT * FROM {selected_table} WHERE {selected_attr1} = ?"
                    params = [selected_value1]
                    if selected_attr2 and selected_value2:
                        query += f" AND {selected_attr2} = ?"
                        params.append(selected_value2)

                try:
                    results = cursor.execute(query, params).fetchall()
                except sqlite3.OperationalError as e:
                    errors.append(f"Ошибка базы данных: {str(e)}")

                # Сброс переменных после обработки
                selected_table = None
                selected_attr1 = None
                selected_value1 = None
                selected_table1 = None
                selected_attr2 = None
                selected_value2 = None

    # Передача данных в шаблон
    return render_template('sync_queries.html', tables=tables, attributes=attributes, results=results, errors=errors,
                           selected_table=selected_table, selected_table1=selected_table1,
                           selected_attr1=selected_attr1, selected_value1=selected_value1,
                           selected_attr2=selected_attr2, selected_value2=selected_value2,
                           values1=values1, values2=values2)
@app.route('/add_breed', methods=['POST'])
def add_breed():
    data = request.get_json()
    breed_name = data.get('breed_name', '').strip()
    if not breed_name:
        return jsonify({'success': False, 'error': 'Название породы не указано'})
    if not (3 <= len(breed_name) <= 100):
        return jsonify({'success': False, 'error': 'Название породы должно быть от 3 до 100 символов'})

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO breeds (breed_name) VALUES (?)", (breed_name,))
        conn.commit()
    return jsonify({'success': True})

@app.route('/add_location', methods=['POST'])
def add_location():
    data = request.get_json()
    location_name = data.get('location_name', '').strip()
    if not location_name:
        return jsonify({'success': False, 'error': 'Название места не указано'})
    if not (3 <= len(location_name) <= 100):
        return jsonify({'success': False, 'error': 'Название места должно быть от 3 до 100 символов'})

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO locations (location_name) VALUES (?)", (location_name,))
        conn.commit()
    return jsonify({'success': True})

@app.route('/add_detailed', methods=['GET', 'POST'])
def add_detailed():
    errors = []

    # Получаем данные для выпадающих списков
    with get_db_connection() as conn:
        coat_types = conn.execute("SELECT id, coat_type_name FROM coat_type ORDER BY coat_type_name").fetchall()
        color_variations = conn.execute("SELECT id, color_variations_name FROM color_variations ORDER BY color_variations_name").fetchall()
        temperaments = conn.execute("SELECT id, temperament_name FROM temperament ORDER BY temperament_name").fetchall()
        sizes = conn.execute("SELECT id, size_name FROM size ORDER BY size_name").fetchall()

    if request.method == 'POST':
        # Собираем данные из формы
        dog_data = {
            'name': request.form['name'],
            'birth_date': request.form['birth_date'] or None,
            'registration_date': request.form['registration_date'] or None,
            'microchip_number': request.form['microchip_number'] or None
        }

        breed_data = {
            'breed_name': request.form['breed_name'],
            'breed_group': request.form['breed_group'] or None,
            'origin_country': request.form['origin_country'] or None,
            'average_lifes': request.form['average_lifes'] or None,
            'typical_use': request.form['typical_use'] or None,
            'common_health_issues': request.form['common_health_issues'] or None,
            'recommended_vaccinations': request.form['recommended_vaccinations'] or None,
            'veterinary_care': request.form['veterinary_care'] or None,
            'average_weight_male': request.form['average_weight_male'] or None,
            'average_weight_female': request.form['average_weight_female'] or None,
            'trainability_level': request.form['trainability_level'] or None,
            'recommended_training_age': request.form['recommended_training_age'] or None,
            'common_behavioral_issues': request.form['common_behavioral_issues'] or None,
            'preferred_training_methods': request.form['preferred_training_methods'] or None,
            'typical_learning_period': request.form['typical_learning_period'] or None
        }

        location_data = {
            'location_name': request.form['location_name'],
            'location_type': request.form['location_type'] or None,
            'address': request.form['address'] or None,
            'contact_info': request.form['location_contact_info'] or None,
            'price': request.form['price'] or None,
            'availability': request.form['availability'] or None,
            'website': request.form['website'] or None
        }

        getting_data = {
            'getting_by': request.form['getting_by'] or None,
            'contact_info': request.form['getting_contact_info'] or None,
            'getting_type': request.form['getting_type'] or None,
            'reason': request.form['reason'] or None
        }

        vet_examination_data = {
            'examination_date': request.form['examination_date'] or None,
            'veterinarian_name': request.form['veterinarian_name'] or None,
            'diagnosis': request.form['diagnosis'] or None,
            'treatment': request.form['treatment'] or None,
            'next_examination_date': request.form['next_examination_date'] or None
        }

        # Данные для выпадающих списков (ID)
        coat_type_id = request.form['coat_type'] or None
        color_variations_id = request.form['color_variations'] or None
        temperament_id = request.form['temperament'] or None
        size_id = request.form['size'] or None

        # Валидация данных
        errors.extend(validate_data(dog_data, VALIDATION_RULES['dogs']))
        errors.extend(validate_data(breed_data, VALIDATION_RULES['breeds']))
        errors.extend(validate_data(location_data, VALIDATION_RULES['locations']))
        errors.extend(validate_data(getting_data, VALIDATION_RULES['getting']))
        errors.extend(validate_data(vet_examination_data, VALIDATION_RULES['vet_examinations']))

        # Дополнительная валидация обязательных полей
        if not dog_data['name']:
            errors.append("Кличка собаки обязательна")
        if not breed_data['breed_name']:
            errors.append("Название породы обязательно")
        if not location_data['location_name']:
            errors.append("Название места размещения обязательно")

        if not errors:
            with get_db_connection() as conn:
                cursor = conn.cursor()

                # Добавление породы
                cursor.execute("""
                    INSERT INTO breeds (breed_name, breed_group, origin_country, average_lifes, typical_use,
                                        common_health_issues, recommended_vaccinations, veterinary_care,
                                        average_weight_male, average_weight_female, trainability_level,
                                        recommended_training_age, common_behavioral_issues, preferred_training_methods,
                                        typical_learning_period)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (breed_data['breed_name'], breed_data['breed_group'], breed_data['origin_country'],
                      breed_data['average_lifes'], breed_data['typical_use'], breed_data['common_health_issues'],
                      breed_data['recommended_vaccinations'], breed_data['veterinary_care'],
                      breed_data['average_weight_male'], breed_data['average_weight_female'],
                      breed_data['trainability_level'], breed_data['recommended_training_age'],
                      breed_data['common_behavioral_issues'], breed_data['preferred_training_methods'],
                      breed_data['typical_learning_period']))
                breed_id = cursor.lastrowid

                # Добавление места размещения
                cursor.execute("""
                    INSERT INTO locations (location_name, location_type, address, contact_info, price, availability, website)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (location_data['location_name'], location_data['location_type'], location_data['address'],
                      location_data['contact_info'], location_data['price'], location_data['availability'],
                      location_data['website']))
                location_id = cursor.lastrowid

                # Добавление записи о получении
                getting_id = None
                if getting_data['getting_by']:
                    cursor.execute("""
                        INSERT INTO getting (getting_by, contact_info, getting_type, reason)
                        VALUES (?, ?, ?, ?)
                    """, (getting_data['getting_by'], getting_data['contact_info'], getting_data['getting_type'],
                          getting_data['reason']))
                    getting_id = cursor.lastrowid

                # Добавление собаки
                cursor.execute("""
                    INSERT INTO dogs (name, birth_date, registration_date, microchip_number, breeds_id, location_id,
                                      coat_type, color_variations, temperament, size, getting_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (dog_data['name'], dog_data['birth_date'], dog_data['registration_date'],
                      dog_data['microchip_number'], breed_id, location_id, coat_type_id, color_variations_id,
                      temperament_id, size_id, getting_id))
                dog_id = cursor.lastrowid

                # Добавление ветеринарного осмотра
                vet_examination_id = None
                if vet_examination_data['examination_date']:
                    cursor.execute("""
                        INSERT INTO vet_examinations (dog_id, examination_date, veterinarian_name, diagnosis, treatment,
                                                      next_examination_date)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (dog_id, vet_examination_data['examination_date'], vet_examination_data['veterinarian_name'],
                          vet_examination_data['diagnosis'], vet_examination_data['treatment'],
                          vet_examination_data['next_examination_date']))
                    vet_examination_id = cursor.lastrowid

                # Обновление собаки с vet_examinations_id
                if vet_examination_id:
                    cursor.execute("UPDATE dogs SET vet_examinations_id = ? WHERE id = ?",
                                  (vet_examination_id, dog_id))

                conn.commit()
            return redirect(url_for('view'))

    return render_template('add_detailed.html', errors=errors, coat_types=coat_types,
                           color_variations=color_variations, temperaments=temperaments, sizes=sizes)

# Просмотр собак
@app.route('/view')
def view():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = """
            SELECT d.id, d.name, b.breed_name, l.location_name, d.birth_date, d.registration_date, d.microchip_number,
                   ct.coat_type_name, cv.color_variations_name, t.temperament_name, s.size_name
            FROM dogs d
            JOIN breeds b ON d.breeds_id = b.id
            JOIN locations l ON d.location_id = l.id
            JOIN coat_type ct ON d.coat_type = ct.id
            JOIN color_variations cv ON d.color_variations = cv.id
            JOIN temperament t ON d.temperament = t.id
            JOIN size s ON d.size = s.id
            ORDER BY d.id
        """
        dogs = cursor.execute(query).fetchall()
    return render_template('view.html', dogs=dogs)

# Поиск собак
@app.route('/search', methods=['GET', 'POST'])
def search():
    results = None
    name = None
    breed_name = None
    location_name = None
    no_results = False

    with get_db_connection() as conn:
        breeds = [row['breed_name'] for row in conn.execute("SELECT DISTINCT breed_name FROM breeds ORDER BY breed_name").fetchall()]
        locations = [row['location_name'] for row in conn.execute("SELECT DISTINCT location_name FROM locations ORDER BY location_name").fetchall()]

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        breed_name = request.form.get('breed_name', '').strip()
        location_name = request.form.get('location_name', '').strip()

        print(f"Search input: name='{name}', breed_name='{breed_name}', location_name='{location_name}'")  # Отладка

        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT d.id, d.name, b.breed_name, l.location_name, d.birth_date, d.registration_date, d.microchip_number
                FROM dogs d
                JOIN breeds b ON d.breeds_id = b.id
                JOIN locations l ON d.location_id = l.id
                WHERE 1=1
            """
            params = []

            if name:
                query += " AND LOWER(TRIM(d.name)) LIKE LOWER(?)"
                params.append(f"%{name}%")
            if breed_name:
                params.append(breed_name)
            if location_name:
                query += " AND LOWER(TRIM(l.location_name)) = LOWER(?)"
                params.append(location_name)

            print(f"Query: {query}, Params: {params}")  # Отладка
            results = cursor.execute(query, params).fetchall()
            print(f"Results: {[dict(row) for row in results]}")  # Отладка
            if not results:
                no_results = True

    return render_template('search.html', results=results, name=name, 
                           breed_name=breed_name, location_name=location_name, 
                           no_results=no_results, breeds=breeds, locations=locations)


@app.route('/edit_vet_examination/<int:id>', methods=['GET', 'POST'])
def edit_vet_examination(id):
    errors = []
    with get_db_connection() as conn:
        dogs = conn.execute("SELECT id, name FROM dogs ORDER BY name").fetchall()

    if request.method == 'POST':
        data = {
            'dog_id': request.form['dog_id'],
            'examination_date': request.form['examination_date'],
            'diagnosis': request.form['diagnosis'],
            'treatment': request.form['treatment']
        }
        errors = validate_data(data, VALIDATION_RULES['vet_examinations'])
        if not errors:
            with get_db_connection() as conn:
                conn.execute("""
                    UPDATE vet_examinations 
                    SET dog_id = ?, examination_date = ?, diagnosis = ?, treatment = ?
                    WHERE id = ?
                """, (data['dog_id'], data['examination_date'], data['diagnosis'], data['treatment'], id))
                conn.commit()
            return redirect(url_for('vet_examinations'))

    with get_db_connection() as conn:
        exam = conn.execute("SELECT * FROM vet_examinations WHERE id = ?", (id,)).fetchone()
    return render_template('edit_vet_examination.html', exam=exam, dogs=dogs, errors=errors)
# Добавление собаки
@app.route('/add', methods=['GET', 'POST'])
def add():
    errors = []
    dogs = None
    
    with get_db_connection() as conn:
        breeds = conn.execute("SELECT id, breed_name FROM breeds ORDER BY breed_name").fetchall()
        locations = conn.execute("SELECT id, location_name FROM locations ORDER BY location_name").fetchall()
        coat_types = conn.execute("SELECT id, coat_type_name FROM coat_type ORDER BY coat_type_name").fetchall()
        color_variations = conn.execute("SELECT id, color_variations_name FROM color_variations ORDER BY color_variations_name").fetchall()
        temperaments = conn.execute("SELECT id, temperament_name FROM temperament ORDER BY temperament_name").fetchall()
        sizes = conn.execute("SELECT id, size_name FROM size ORDER BY size_name").fetchall()
        gettings = conn.execute(
            "SELECT id, getting_by FROM getting WHERE getting_by IS NOT NULL AND TRIM(getting_by) != '' ORDER BY getting_by").fetchall()
        for getting in gettings:
            print(f"ID: {getting['id']}, Getting_by: '{getting['getting_by']}'")
        vet_examinations = conn.execute("SELECT id, examination_date FROM vet_examinations ORDER BY examination_date").fetchall()

    if request.method == 'POST':
        data = {
            'name': request.form['name'],
            'breed_id': request.form['breed_id'],
            'location_id': request.form['location_id'] or None,
            'birth_date': request.form['birth_date'] or None,
            'registration_date': request.form['registration_date'] or None,
            'microchip_number': request.form['microchip_number'] or None,
            'coat_type': request.form['coat_type'] or None,
            'color_variations': request.form['color_variations'] or None,
            'temperament': request.form['temperament'] or None,
            'size': request.form['size'] or None,
            'getting_id': request.form['getting_id'] or None,
            'vet_examinations_id': request.form['vet_examinations_id'] or None
        }
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO dogs (name, breeds_id, location_id, birth_date, registration_date, microchip_number, coat_type, color_variations, temperament, size, getting_id, vet_examinations_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (data['name'], data['breed_id'], data['location_id'], data['birth_date'], data['registration_date'], 
                  data['microchip_number'], data['coat_type'], data['color_variations'], data['temperament'], 
                  data['size'], data['getting_id'], data['vet_examinations_id']))
            conn.commit()
            
            cursor.execute("SELECT dogs.id, dogs.name, breeds.breed_name, locations.location_name FROM dogs LEFT JOIN breeds ON dogs.breeds_id = breeds.id LEFT JOIN locations ON dogs.location_id = locations.id")
            dogs = cursor.fetchall()
            breeds = cursor.execute("SELECT id, breed_name FROM breeds").fetchall()
            locations = cursor.execute("SELECT id, location_name FROM locations").fetchall()
    else:
        with get_db_connection() as conn:
            dogs = conn.execute("""
                SELECT d.id, d.name, b.breed_name, l.location_name, d.birth_date, d.registration_date, d.microchip_number,
                       ct.coat_type_name, cv.color_variations_name, t.temperament_name, s.size_name, 
                       g.getting_by, ve.examination_date
                FROM dogs d
                LEFT JOIN breeds b ON d.breeds_id = b.id
                LEFT JOIN locations l ON d.location_id = l.id
                LEFT JOIN coat_type ct ON d.coat_type = ct.id
                LEFT JOIN color_variations cv ON d.color_variations = cv.id
                LEFT JOIN temperament t ON d.temperament = t.id
                LEFT JOIN size s ON d.size = s.id
                LEFT JOIN getting g ON d.getting_id = g.id
                LEFT JOIN vet_examinations ve ON d.vet_examinations_id = ve.id
                ORDER BY d.id
            """).fetchall()

    return render_template('add.html', errors=errors, dogs=dogs, breeds=breeds, locations=locations,
                           coat_types=coat_types, color_variations=color_variations, temperaments=temperaments,
                           sizes=sizes, gettings=gettings, vet_examinations=vet_examinations)
# Редактирование собаки
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    errors = []
    if request.method == 'POST':
        dog_data = {
            'name': request.form['name'],
            'birth_date': request.form['birth_date'],
            'microchip_number': request.form['microchip_number'],
            'registration_date': request.form['registration_date']
        }
        breeds_id = request.form['breeds_id']
        location_id = request.form['location_id']

        errors = validate_data(dog_data, VALIDATION_RULES['dogs'])
        if not errors:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE dogs 
                    SET name = ?, birth_date = ?, microchip_number = ?, registration_date = ?, breeds_id = ?, location_id = ?
                    WHERE id = ?
                """, (dog_data['name'], dog_data['birth_date'], dog_data['microchip_number'], 
                      dog_data['registration_date'], breeds_id, location_id, id))
                conn.commit()
            return redirect(url_for('view'))
    
    with get_db_connection() as conn:
        dog = conn.execute("""
            SELECT d.*, b.breed_name, l.location_name
            FROM dogs d 
            JOIN breeds b ON d.breeds_id = b.id
            JOIN locations l ON d.location_id = l.id
            WHERE d.id = ?
        """, (id,)).fetchone()
        breeds = conn.execute("SELECT id, breed_name FROM breeds").fetchall()
        locations = conn.execute("SELECT id, location_name FROM locations").fetchall()
    return render_template('edit.html', dog=dog, breeds=breeds, locations=locations, errors=errors)

# Управление породами
@app.route('/breeds', methods=['GET', 'POST'])
def breeds():
    errors = []
    if request.method == 'POST':
        data = {
            'breed_name': request.form['breed_name'],
            'average_lifes': request.form['average_lifes']
        }
        # Пример валидации (можно настроить под ваши нужды)
        if not (3 <= len(data['breed_name']) <= 100):
            errors.append("Название породы должно быть от 3 до 100 символов")
        if data['average_lifes'] and not (5 <= int(data['average_lifes']) <= 20):
            errors.append("Средняя продолжительность жизни должна быть от 5 до 20 лет")
        if not errors:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO breeds (breed_name, average_lifes)
                    VALUES (?, ?)
                """, (data['breed_name'], data['average_lifes'] or None))
                conn.commit()
    with get_db_connection() as conn:
        breeds = conn.execute("SELECT * FROM breeds ORDER BY breed_name").fetchall()
    return render_template('breeds.html', breeds=breeds, errors=errors)

# Управление местами размещения
@app.route('/locations', methods=['GET', 'POST'])
def locations():
    errors = []
    if request.method == 'POST':
        data = {
            'location_name': request.form['location_name'],
            'address': request.form['address']
        }
        # Пример валидации
        if not (3 <= len(data['location_name']) <= 100):
            errors.append("Название места должно быть от 3 до 100 символов")
        if not (5 <= len(data['address']) <= 200):
            errors.append("Адрес должен быть от 5 до 200 символов")
        if not errors:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO locations (location_name, address)
                    VALUES (?, ?)
                """, (data['location_name'], data['address']))
                conn.commit()
    with get_db_connection() as conn:
        locations = conn.execute("SELECT * FROM locations ORDER BY location_name").fetchall()
    return render_template('locations.html', locations=locations, errors=errors)

# Управление ветеринарными осмотрами
@app.route('/vet_examinations', methods=['GET', 'POST'])
def vet_examinations():
    errors = []
    with get_db_connection() as conn:
        dogs = conn.execute("SELECT id, name FROM dogs ORDER BY name").fetchall()

    if request.method == 'POST':
        data = {
            'dog_id': request.form['dog_id'],
            'examination_date': request.form['examination_date'],
            'diagnosis': request.form['diagnosis'],
            'treatment': request.form['treatment']
        }
        # Пример валидации
        if not (5 <= len(data['diagnosis']) <= 200):
            errors.append("Диагноз должен быть от 5 до 200 символов")
        if not (5 <= len(data['treatment']) <= 200):
            errors.append("Лечение должно быть от 5 до 200 символов")
        if not errors:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO vet_examinations (dog_id, examination_date, diagnosis, treatment)
                    VALUES (?, ?, ?, ?)
                """, (data['dog_id'], data['examination_date'], data['diagnosis'], data['treatment']))
                conn.commit()
    with get_db_connection() as conn:
        examinations = conn.execute("""
            SELECT ve.*, d.name AS dog_name
            FROM vet_examinations ve
            JOIN dogs d ON ve.dog_id = d.id
            ORDER BY ve.id
        """).fetchall()
    return render_template('vet_examinations.html', examinations=examinations, dogs=dogs, errors=errors)

@app.route('/getting', methods=['GET', 'POST'])
def getting():
    errors = []
    with get_db_connection() as conn:
        cursor = conn.cursor()
        dogs = cursor.execute("SELECT id, name FROM dogs ORDER BY name").fetchall()

    if request.method == 'POST':
        data = {
            'getting_by': request.form['getting_by'],
            'contact_info': request.form['contact_info'],
            'getting_type': request.form['getting_type'],
            'reason': request.form['reason']
        }
        errors = validate_data(data, VALIDATION_RULES['getting'])
        if not errors:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO getting (getting_by, contact_info, getting_type, reason)
                    VALUES (?, ?, ?, ?)
                """, (data['getting_by'], data['contact_info'], data['getting_type'], data['reason']))
                conn.commit()

    with get_db_connection() as conn:
        cursor = conn.cursor()
        gettings = cursor.execute("""
            SELECT g.id, g.getting_by, g.contact_info, g.getting_type, g.reason
            FROM getting g
            ORDER BY g.id
        """).fetchall()

    return render_template('getting.html', gettings=gettings, dogs=dogs, errors=errors)
  
@app.route('/edit_getting/<int:id>', methods=['GET', 'POST'])
def edit_getting(id):
    errors = []
    with get_db_connection() as conn:
        cursor = conn.cursor()
        dogs = cursor.execute("SELECT id, name FROM dogs ORDER BY name").fetchall()

    if request.method == 'POST':
        data = {
            'getting_by': request.form['getting_by'],
            'contact_info': request.form['contact_info'],
            'getting_type': request.form['getting_type'],
            'reason': request.form['reason']
        }
        errors = validate_data(data, VALIDATION_RULES['getting'])
        if not errors:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE getting 
                    SET getting_by = ?, contact_info = ?, getting_type = ?, reason = ?
                    WHERE id = ?
                """, (data['getting_by'], data['contact_info'], data['getting_type'], data['reason'], id))
                conn.commit()
            return redirect(url_for('getting'))

    with get_db_connection() as conn:
        cursor = conn.cursor()
        getting = cursor.execute("""
            SELECT id, getting_by, contact_info, getting_type, reason
            FROM getting 
            WHERE id = ?
        """, (id,)).fetchone()
        if not getting:
            errors.append("Запись не найдена")
    return render_template('edit_getting.html', getting=getting, dogs=dogs, errors=errors)  

# Статистика
@app.route('/stats')
def stats():
    with get_db_connection() as conn:
        by_breed = conn.execute("""
            SELECT b.breed_name, COALESCE(COUNT(d.id), 0) AS dog_count 
            FROM breeds b 
            LEFT JOIN dogs d ON d.breeds_id = b.id 
            GROUP BY b.breed_name
            ORDER BY b.breed_name
        """).fetchall()
        by_location = conn.execute("""
            SELECT l.location_name, COALESCE(COUNT(d.id), 0) AS dog_count 
            FROM locations l 
            LEFT JOIN dogs d ON d.location_id = l.id 
            GROUP BY l.location_name
            ORDER BY l.location_name
        """).fetchall()
    return render_template('stats.html', by_breed=by_breed, by_location=by_location)

# Запросы
@app.route('/queries', methods=['GET', 'POST'])
def queries():# В маршруте /queries
    attributes = {
    'name': {'table': 'd', 'column': 'name', 'type': 'text', 'label': 'Имя собаки'},
    'birth_date': {'table': 'd', 'column': 'birth_date', 'type': 'text', 'label': 'Дата рождения', 'is_date': True},
    'breeds_id': {'table': 'd', 'column': 'breeds_id', 'type': 'number', 'label': 'ID породы'},
    'getting_id': {'table': 'd', 'column': 'getting_id', 'type': 'number', 'label': 'ID получения собаки'},
    'vet_examinations_id': {'table': 'd', 'column': 'vet_examinations_id', 'type': 'number', 'label': 'ID ветеринарного осмотра'},
    'location_id': {'table': 'd', 'column': 'location_id', 'type': 'number', 'label': 'ID места размещения'},
    'registration_date': {'table': 'd', 'column': 'registration_date', 'type': 'text', 'label': 'Дата регистрации', 'is_date': True},
    'microchip_number': {'table': 'd', 'column': 'microchip_number', 'type': 'text', 'label': 'Номер микрочипа'},
    'coat_type': {'table': 'ct', 'column': 'coat_type_name', 'type': 'text', 'label': 'Тип шерсти', 'has_options': 'coat_type_name'},
    'color_variations': {'table': 'cv', 'column': 'color_variations_name', 'type': 'text', 'label': 'Окрас', 'has_options': 'color_variations_name'},
    'temperament': {'table': 't', 'column': 'temperament_name', 'type': 'text', 'label': 'Темперамент', 'has_options': 'temperament_name'},
    'size': {'table': 's', 'column': 'size_name', 'type': 'text', 'label': 'Размер', 'has_options': 'size_name'},
    'breed_name': {'table': 'b', 'column': 'breed_name', 'type': 'text', 'label': 'Название породы', 'has_options': 'breed_name'},
    'breed_group': {'table': 'b', 'column': 'breed_group', 'type': 'text', 'label': 'Группа породы', 'has_options': 'breed_group'},
    'origin_country': {'table': 'b', 'column': 'origin_country', 'type': 'text', 'label': 'Страна происхождения', 'has_options': 'origin_country'},
    'average_lifes': {'table': 'b', 'column': 'average_lifes', 'type': 'number', 'label': 'Средняя продолжительность жизни'},
    'typical_use': {'table': 'b', 'column': 'typical_use', 'type': 'text', 'label': 'Типичное использование', 'has_options': 'typical_use'},
    'common_health_issues': {'table': 'b', 'column': 'common_health_issues', 'type': 'text', 'label': 'Распространенные проблемы со здоровьем'},
    'recommended_vaccinations': {'table': 'b', 'column': 'recommended_vaccinations', 'type': 'text', 'label': 'Рекомендуемые вакцинации'},
    'veterinary_care': {'table': 'b', 'column': 'veterinary_care', 'type': 'text', 'label': 'Потребности в ветеринарном уходе'},
    'average_weight_male': {'table': 'b', 'column': 'average_weight_male', 'type': 'number', 'label': 'Средний вес самцов'},
    'average_weight_female': {'table': 'b', 'column': 'average_weight_female', 'type': 'number', 'label': 'Средний вес самок'},
    'trainability_level': {'table': 'b', 'column': 'trainability_level', 'type': 'text', 'label': 'Уровень обучаемости', 'has_options': 'trainability_level'},
    'recommended_training_age': {'table': 'b', 'column': 'recommended_training_age', 'type': 'number', 'label': 'Рекомендуемый возраст начала дрессировки'},
    'common_behavioral_issues': {'table': 'b', 'column': 'common_behavioral_issues', 'type': 'text', 'label': 'Распространенные поведенческие проблемы'},
    'preferred_training_methods': {'table': 'b', 'column': 'preferred_training_methods', 'type': 'text', 'label': 'Предпочтительные методы дрессировки'},
    'typical_learning_period': {'table': 'b', 'column': 'typical_learning_period', 'type': 'number', 'label': 'Типичный период обучения'},
    'getting_by': {'table': 'g', 'column': 'getting_by', 'type': 'text', 'label': 'Кем передана', 'has_options': 'getting_by'},
    'contact_info': {'table': 'g', 'column': 'contact_info', 'type': 'text', 'label': 'Контактная информация'},
    'getting_type': {'table': 'g', 'column': 'getting_type', 'type': 'text', 'label': 'Тип передачи', 'has_options': 'getting_type'},
    'reason': {'table': 'g', 'column': 'reason', 'type': 'text', 'label': 'Причина передачи'},
    'examination_date': {'table': 've', 'column': 'examination_date', 'type': 'text', 'label': 'Дата осмотра', 'is_date': True},
    'veterinarian_name': {'table': 've', 'column': 'veterinarian_name', 'type': 'text', 'label': 'Имя ветеринара'},
    'diagnosis': {'table': 've', 'column': 'diagnosis', 'type': 'text', 'label': 'Диагноз'},
    'treatment': {'table': 've', 'column': 'treatment', 'type': 'text', 'label': 'Лечение'},
    'next_examination_date': {'table': 've', 'column': 'next_examination_date', 'type': 'text', 'label': 'Дата следующего осмотра', 'is_date': True},
    'location_name': {'table': 'l', 'column': 'location_name', 'type': 'text', 'label': 'Название места', 'has_options': 'location_name'},
    'location_type': {'table': 'l', 'column': 'location_type', 'type': 'text', 'label': 'Тип места', 'has_options': 'location_type'},
    'address': {'table': 'l', 'column': 'address', 'type': 'text', 'label': 'Адрес'},
    'contact_info_loc': {'table': 'l', 'column': 'contact_info', 'type': 'text', 'label': 'Контактная информация (место)'},
    'price': {'table': 'l', 'column': 'price', 'type': 'number', 'label': 'Стоимость'},
    'availability': {'table': 'l', 'column': 'availability', 'type': 'number', 'label': 'Количество собак'},
    'website': {'table': 'l', 'column': 'website', 'type': 'text', 'label': 'Сайт'}
}
    
    numeric_attributes = [key for key, attr in attributes.items() if attr['type'] == 'number']
    results = None
    selected_attribute1 = None
    search_min1 = None
    search_max1 = None
    selected_attribute2 = None
    search_min2 = None
    search_max2 = None
    errors = []

    # Получаем варианты для полей с has_options
    options = {}
    with get_db_connection() as conn:
        breeds = [row['breed_name'] for row in conn.execute("SELECT DISTINCT breed_name FROM breeds ORDER BY breed_name").fetchall()]
        locations = [row['location_name'] for row in conn.execute("SELECT DISTINCT location_name FROM locations ORDER BY location_name").fetchall()]
        
        # Для таблицы breeds
        options['breed_name'] = [(row['breed_name'], row['breed_name']) for row in conn.execute("SELECT DISTINCT breed_name FROM breeds ORDER BY breed_name").fetchall()]
        options['breed_group'] = [(row['breed_group'], row['breed_group']) for row in conn.execute("SELECT DISTINCT breed_group FROM breeds WHERE breed_group IS NOT NULL ORDER BY breed_group").fetchall()]
        options['origin_country'] = [(row['origin_country'], row['origin_country']) for row in conn.execute("SELECT DISTINCT origin_country FROM breeds WHERE origin_country IS NOT NULL ORDER BY origin_country").fetchall()]
        options['typical_use'] = [(row['typical_use'], row['typical_use']) for row in conn.execute("SELECT DISTINCT typical_use FROM breeds WHERE typical_use IS NOT NULL ORDER BY typical_use").fetchall()]
        options['trainability_level'] = [(row['trainability_level'], row['trainability_level']) for row in conn.execute("SELECT DISTINCT trainability_level FROM breeds WHERE trainability_level IS NOT NULL ORDER BY trainability_level").fetchall()]
        
        # Для таблицы locations
        options['location_name'] = [(row['location_name'], row['location_name']) for row in conn.execute("SELECT DISTINCT location_name FROM locations ORDER BY location_name").fetchall()]
        options['location_type'] = [(row['location_type'], row['location_type']) for row in conn.execute("SELECT DISTINCT location_type FROM locations WHERE location_type IS NOT NULL ORDER BY location_type").fetchall()]
        
        # Для остальных таблиц
        options['coat_type_name'] = [(row['coat_type_name'], row['coat_type_name']) for row in conn.execute("SELECT DISTINCT coat_type_name FROM coat_type ORDER BY coat_type_name").fetchall()]
        options['color_variations_name'] = [(row['color_variations_name'], row['color_variations_name']) for row in conn.execute("SELECT DISTINCT color_variations_name FROM color_variations ORDER BY color_variations_name").fetchall()]
        options['temperament_name'] = [(row['temperament_name'], row['temperament_name']) for row in conn.execute("SELECT DISTINCT temperament_name FROM temperament ORDER BY temperament_name").fetchall()]
        options['size_name'] = [(row['size_name'], row['size_name']) for row in conn.execute("SELECT DISTINCT size_name FROM size ORDER BY size_name").fetchall()]
        options['getting_by'] = [(row['getting_by'], row['getting_by']) for row in conn.execute("SELECT DISTINCT getting_by FROM getting ORDER BY getting_by").fetchall()]
        options['getting_type'] = [(row['getting_type'], row['getting_type']) for row in conn.execute("SELECT DISTINCT getting_type FROM getting WHERE getting_type IS NOT NULL ORDER BY getting_type").fetchall()]
        
        print("Options:", {k: len(v) for k, v in options.items()})

    if request.method == 'POST':
        selected_attribute1 = request.form.get('attribute1', '')
        search_min1 = request.form.get('search_min1', '')
        search_max1 = request.form.get('search_max1', '')  # Оставляем пустым, если не указано
        selected_attribute2 = request.form.get('attribute2', '')
        search_min2 = request.form.get('search_min2', '')
        search_max2 = request.form.get('search_max2', '')  # Оставляем пустым, если не указано

        print(f"POST: selected_attribute1={selected_attribute1}, search_min1={search_min1}, search_max1={search_max1}")
        print(f"POST: selected_attribute2={selected_attribute2}, search_min2={search_min2}, search_max2={search_max2}")

        if not selected_attribute1 or selected_attribute1 not in attributes:
            errors.append("Выберите корректный первый атрибут")
        elif not search_min1 and not search_max1:
            errors.append("Введите хотя бы одно значение для первого атрибута")
        else:
            attr_info1 = attributes[selected_attribute1]
            table1 = attr_info1['table']
            column1 = attr_info1['column']
            attr_type1 = attr_info1['type']
            is_date1 = attr_info1.get('is_date', False)

            try:
                # Устанавливаем границы по умолчанию
                min_val1 = None
                max_val1 = None

                if attr_type1 == 'number':
                    if search_min1:
                        min_val1 = int(search_min1)
                    if search_max1:
                        max_val1 = int(search_max1)
                    if min_val1 is not None and max_val1 is not None and max_val1 < min_val1:
                        errors.append(
                            f"Максимальное значение для '{attr_info1['label']}' должно быть больше минимального")
                        raise ValueError
                    # Если не указана одна из границ, используем широкий диапазон
                    min_val1 = min_val1 if min_val1 is not None else -float('inf')
                    max_val1 = max_val1 if max_val1 is not None else float('inf')
                elif is_date1:
                    if search_min1:
                        min_val1 = datetime.strptime(search_min1, '%Y-%m-%d').date().isoformat()
                    if search_max1:
                        max_val1 = datetime.strptime(search_max1, '%Y-%m-%d').date().isoformat()
                    if min_val1 and max_val1 and max_val1 < min_val1:
                        errors.append(f"Максимальная дата для '{attr_info1['label']}' должна быть позже минимальной")
                        raise ValueError
                    # Если не указана одна из границ, используем широкий диапазон дат
                    min_val1 = min_val1 if min_val1 else '1970-01-01'
                    max_val1 = max_val1 if max_val1 else '9999-12-31'
                else:
                    # Для текста используем точное совпадение, если указана только одна граница
                    min_val1 = search_min1
                    max_val1 = search_max1 if search_max1 else search_min1

                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    query = """
                        SELECT 
                            d.id, d.name, d.birth_date, d.registration_date, d.microchip_number,
                            b.breed_name, b.breed_group, b.origin_country, b.average_lifes, b.typical_use, 
                            b.common_health_issues, b.recommended_vaccinations, b.veterinary_care, 
                            b.average_weight_male, b.average_weight_female, b.trainability_level, 
                            b.recommended_training_age, b.common_behavioral_issues, b.preferred_training_methods, 
                            b.typical_learning_period,
                            l.location_name, l.location_type, l.address, l.contact_info AS location_contact_info, 
                            l.price, l.availability, l.website,
                            ct.coat_type_name, cv.color_variations_name, t.temperament_name, s.size_name,
                            g.getting_by, g.contact_info AS getting_contact_info, g.getting_type, g.reason,
                            ve.examination_date, ve.veterinarian_name, ve.diagnosis, ve.treatment, ve.next_examination_date
                        FROM dogs d
                        LEFT JOIN breeds b ON d.breeds_id = b.id
                        LEFT JOIN locations l ON d.location_id = l.id
                        LEFT JOIN coat_type ct ON d.coat_type = ct.id
                        LEFT JOIN color_variations cv ON d.color_variations = cv.id
                        LEFT JOIN temperament t ON d.temperament = t.id
                        LEFT JOIN size s ON d.size = s.id
                        LEFT JOIN getting g ON d.getting_id = g.id
                        LEFT JOIN vet_examinations ve ON d.vet_examinations_id = ve.id
                        WHERE {table1}.{column1} >= ? AND {table1}.{column1} <= ?
                    """.format(table1=table1, column1=column1)
                    params = [min_val1, max_val1]

                    if selected_attribute2 and (search_min2 or search_max2):
                        attr_info2 = attributes[selected_attribute2]
                        table2 = attr_info2['table']
                        column2 = attr_info2['column']
                        attr_type2 = attr_info2['type']
                        is_date2 = attr_info2.get('is_date', False)

                        min_val2 = None
                        max_val2 = None

                        if attr_type2 == 'number':
                            if search_min2:
                                min_val2 = int(search_min2)
                            if search_max2:
                                max_val2 = int(search_max2)
                            if min_val2 is not None and max_val2 is not None and max_val2 < min_val2:
                                errors.append(
                                    f"Максимальное значение для '{attr_info2['label']}' должно быть больше минимального")
                                raise ValueError
                            min_val2 = min_val2 if min_val2 is not None else -float('inf')
                            max_val2 = max_val2 if max_val2 is not None else float('inf')
                        elif is_date2:
                            if search_min2:
                                min_val2 = datetime.strptime(search_min2, '%Y-%m-%d').date().isoformat()
                            if search_max2:
                                max_val2 = datetime.strptime(search_max2, '%Y-%m-%d').date().isoformat()
                            if min_val2 and max_val2 and max_val2 < min_val2:
                                errors.append(
                                    f"Максимальная дата для '{attr_info2['label']}' должна быть позже минимальной")
                                raise ValueError
                            min_val2 = min_val2 if min_val2 else '1970-01-01'
                            max_val2 = max_val2 if max_val2 else '9999-12-31'
                        else:
                            min_val2 = search_min2
                            max_val2 = search_max2 if search_max2 else search_min2

                        query += " AND {table2}.{column2} >= ? AND {table2}.{column2} <= ?".format(table2=table2,
                                                                                                   column2=column2)
                        params.extend([min_val2, max_val2])

                    results = cursor.execute(query, tuple(params)).fetchall()

            except ValueError:
                if not errors:
                    errors.append(
                        f"Значение для '{attr_info1['label']}' должно быть {'числом' if attr_type1 == 'number' else 'датой в формате YYYY-MM-DD' if is_date1 else 'текстом'}")
            except sqlite3.OperationalError as e:
                errors.append(f"Ошибка базы данных: {str(e)}")

    return render_template('queries.html', attributes=attributes, results=results, 
                          selected_attribute1=selected_attribute1, search_min1=search_min1, search_max1=search_max1,
                          selected_attribute2=selected_attribute2, search_min2=search_min2, search_max2=search_max2,
                          errors=errors, breeds=breeds, locations=locations, numeric_attributes=numeric_attributes,
                          options=options)

# Маршрут для редактирования локации
@app.route('/edit_location/<int:id>', methods=['GET', 'POST'])
def edit_location(id):
    conn = sqlite3.connect('dogs.db')
    if request.method == 'POST':
        # Обновление данных локации
        name = request.form['name']
        conn.execute('UPDATE locations SET name = ? WHERE id = ?', (name, id))
        conn.commit()
        conn.close()
        return redirect(url_for('locations'))
    # Отображение формы редактирования
    location = conn.execute('SELECT id, name FROM locations WHERE id = ?', (id,)).fetchone()
    conn.close()
    return render_template('edit_location.html', location=location)

# Маршрут для редактирования породы
@app.route('/edit_breed/<int:id>', methods=['GET', 'POST'])
def edit_breed(id):
    conn = sqlite3.connect('dogs.db')
    if request.method == 'POST':
        # Обновление данных породы
        name = request.form['name']
        conn.execute('UPDATE breeds SET name = ? WHERE id = ?', (name, id))
        conn.commit()
        conn.close()
        return redirect(url_for('breeds'))
    # Отображение формы редактирования
    breed = conn.execute('SELECT id, name FROM breeds WHERE id = ?', (id,)).fetchone()
    conn.close()
    return render_template('edit_breed.html', breed=breed)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
