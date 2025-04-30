from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secret'

# Пути к базам данных
DB_PATH_1 = os.path.join(os.path.dirname(__file__), 'database1.db')
DB_PATH_2 = os.path.join(os.path.dirname(__file__), 'database2.db')

def get_db_connection():
    active_db = session.get('active_db', DB_PATH_1)  # По умолчанию первая база данных
    conn = sqlite3.connect(active_db, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn
    
@app.route('/switch_db/<int:db_number>')
def switch_db(db_number):
    if db_number == 1:
        session['active_db'] = DB_PATH_1
    elif db_number == 2:
        session['active_db'] = DB_PATH_2
    else:
        return "Неверный номер базы данных", 400
    return redirect(url_for('index'))

# Ограничения для валидации
VALIDATION_RULES = {
    'dogs': {
        'name': {'min_length': 3, 'max_length': 100},  # Имя собаки: 5-100 символов
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
    active_db = session.get('active_db', DB_PATH_1)  # По умолчанию DB_PATH_1, если сессия пуста
    if active_db == DB_PATH_1:
        active_db_number = 1
    elif active_db == DB_PATH_2:
        active_db_number = 2
    else:
        active_db_number = 0  # Если база не выбрана или путь некорректен
    return render_template('index.html', active_db_number=active_db_number)

@app.route('/simple_query', methods=['GET', 'POST'])
def simple_query():
    with get_db_connection() as conn:
        names = [row['name'] for row in conn.execute("SELECT DISTINCT name FROM dogs ORDER BY name").fetchall()]

    selected_name = request.form.get('name') if request.method == 'POST' else None
    dog_info = None
    if selected_name:
        with get_db_connection() as conn:
            dog_info = conn.execute("""
                SELECT DISTINCT
                    d.id AS dog_id, d.name, d.birth_date, d.registration_date, d.microchip_number,
                    b.breed_name, b.breed_group, b.origin_country, b.average_lifes, b.typical_use,
                    b.common_health_issues, b.recommended_vaccinations, b.veterinary_care,
                    b.average_weight_male, b.average_weight_female, b.trainability_level,
                    b.recommended_training_age, b.common_behavioral_issues, b.preferred_training_methods,
                    b.typical_learning_period,
                    l.location_name, l.location_type, l.address, l.contact_info, l.price,
                    l.availability, l.website,
                    ve.examination_date, ve.veterinarian_name, ve.diagnosis, ve.treatment, ve.next_examination_date,
                    g.getting_by, g.contact_info, g.getting_type, g.reason,
                    ct.coat_type_name, cv.color_variations_name, t.temperament_name, s.size_name
                FROM dogs d
                LEFT JOIN breeds b ON d.breeds_id = b.id
                LEFT JOIN locations l ON d.location_id = l.id
                LEFT JOIN vet_examinations ve ON d.vet_examinations_id = ve.id
                LEFT JOIN getting g ON d.getting_id = g.id
                LEFT JOIN coat_type ct ON d.coat_type = ct.id
                LEFT JOIN color_variations cv ON d.color_variations = cv.id
                LEFT JOIN temperament t ON d.temperament = t.id
                LEFT JOIN size s ON d.size = s.id
                WHERE d.name = ?
            """, (selected_name,)).fetchone()

    return render_template('simple_query.html', names=names, selected_name=selected_name, dog_info=dog_info)

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
@app.route('/check_related_data', methods=['POST'])
def check_related_data():
    table = request.form['table']  # Первая таблица
    attr1 = request.form['attr1']  # Первый атрибут
    value1 = request.form['value1']  # Значение первого атрибута
    table1 = request.form['table1']  # Вторая таблица

    if table not in TABLES or table1 not in TABLES:
        return jsonify({'has_data': False})

    # Определение связей для JOIN
    joins = {
        'dogs': '',
        'breeds': 'JOIN breeds b ON d.breeds_id = b.id',
        'locations': 'JOIN locations l ON d.location_id = l.id',
        'vet_examinations': 'JOIN vet_examinations ve ON d.vet_examinations_id = ve.id',
        'getting': 'JOIN getting g ON d.getting_id = g.id',
        'coat_type': 'JOIN coat_type ct ON d.coat_type = ct.id',
        'color_variations': 'JOIN color_variations cv ON d.color_variations = cv.id',
        'temperament': 'JOIN temperament t ON d.temperament = t.id',
        'size': 'JOIN size s ON d.size = s.id'
    }

    # Алиасы таблиц
    table_aliases = {
        'dogs': 'd',
        'breeds': 'b',
        'locations': 'l',
        'vet_examinations': 've',
        'getting': 'g',
        'coat_type': 'ct',
        'color_variations': 'cv',
        'temperament': 't',
        'size': 's'
    }

    # Поля в dogs, связанные с другими таблицами
    linked_fields = {
        'breeds': 'breeds_id',
        'locations': 'location_id',
        'vet_examinations': 'vet_examinations_id',
        'getting': 'getting_id',
        'coat_type': 'coat_type',
        'color_variations': 'color_variations',
        'temperament': 'temperament',
        'size': 'size'
    }

    join_str = joins.get(table, '')
    table_alias = table_aliases.get(table, 'd')
    where_clause = f"{table_alias}.{attr1} = ?"
    params = [value1]

    # Если вторая таблица не 'dogs', проверяем, что связанное поле не NULL
    if table1 != 'dogs' and table1 in linked_fields:
        where_clause += f" AND d.{linked_fields[table1]} IS NOT NULL"

    query = f"SELECT COUNT(*) FROM dogs d {join_str} WHERE {where_clause}"

    with get_db_connection() as conn:
        count = conn.execute(query, params).fetchone()[0]

    has_data = count > 0
    return jsonify({'has_data': has_data})
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
@app.route('/add_coat_type', methods=['POST'])
def add_coat_type():
    data = request.get_json()
    coat_type_name = data.get('coat_type_name')
    if not coat_type_name:
        return jsonify({'success': False, 'error': 'Название типа шерсти обязательно'})
    with get_db_connection() as conn:
        cursor = conn.execute('INSERT INTO coat_type (coat_type_name) VALUES (?)', (coat_type_name,))
        conn.commit()
        return jsonify({'success': True, 'id': cursor.lastrowid, 'coat_type_name': coat_type_name})

@app.route('/add_color_variations', methods=['POST'])
def add_color_variations():
    data = request.get_json()
    color_variations_name = data.get('color_variations_name')
    if not color_variations_name:
        return jsonify({'success': False, 'error': 'Название окраса обязательно'})
    with get_db_connection() as conn:
        cursor = conn.execute('INSERT INTO color_variations (color_variations_name) VALUES (?)', (color_variations_name,))
        conn.commit()
        return jsonify({'success': True, 'id': cursor.lastrowid, 'color_variations_name': color_variations_name})
        
@app.route('/add_breed', methods=['POST'])
def add_breed():
    data = request.get_json()
    breed_name = data.get('breed_name', '').strip()
    if not breed_name:
        return jsonify({'success': False, 'error': 'Название породы не указано'})
    
    # Валидация данных
    validation_data = {
        'breed_name': breed_name,
    }
    errors = validate_data(validation_data, VALIDATION_RULES['breeds'])
    if errors:
        return jsonify({'success': False, 'error': ', '.join(errors)})

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO breeds (
                breed_name, breed_group, origin_country, average_lifes, typical_use,
                common_health_issues, recommended_vaccinations, veterinary_care,
                average_weight_male, average_weight_female, trainability_level,
                recommended_training_age, common_behavioral_issues, preferred_training_methods,
                typical_learning_period
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            breed_name,
            data.get('breed_group'),
            data.get('origin_country'),
            data.get('average_lifes'),
            data.get('typical_use'),
            data.get('common_health_issues'),
            data.get('recommended_vaccinations'),
            data.get('veterinary_care'),
            data.get('average_weight_male'),
            data.get('average_weight_female'),
            data.get('trainability_level'),
            data.get('recommended_training_age'),
            data.get('common_behavioral_issues'),
            data.get('preferred_training_methods'),
            data.get('typical_learning_period')
        ))
        conn.commit()
        breed_id = cursor.lastrowid
    return jsonify({'success': True, 'id': breed_id, 'breed_name': breed_name})
    
@app.route('/add_temperament', methods=['POST'])
def add_temperament():
    data = request.get_json()
    temperament_name = data.get('temperament_name')
    if not temperament_name:
        return jsonify({'success': False, 'error': 'Название темперамента обязательно'})
    with get_db_connection() as conn:
        cursor = conn.execute('INSERT INTO temperament (temperament_name) VALUES (?)', (temperament_name,))
        conn.commit()
        return jsonify({'success': True, 'id': cursor.lastrowid, 'temperament_name': temperament_name})

@app.route('/add_size', methods=['POST'])
def add_size():
    data = request.get_json()
    size_name = data.get('size_name')
    if not size_name:
        return jsonify({'success': False, 'error': 'Название размера обязательно'})
    with get_db_connection() as conn:
        cursor = conn.execute('INSERT INTO size (size_name) VALUES (?)', (size_name,))
        conn.commit()
        return jsonify({'success': True, 'id': cursor.lastrowid, 'size_name': size_name})
        
ALLOWED_TABLES = ['dogs', 'breeds', 'locations', 'vet_examinations', 'getting', 'coat_type', 'color_variations', 'temperament', 'size']
# Маршрут для добавления нового значения
DEFAULT_VALUES = {
    'dogs': {'name': 'Неизвестная собака'},
    'breeds': {'breed_name': 'Неизвестная порода'},
    'locations': {'location_name': 'Неизвестное место'},
    'vet_examinations': {'examination_date': '2000-01-01'},
    'getting': {'getting_by': 'Неизвестный'},
    'coat_type': {'coat_type_name': 'Неизвестный тип шерсти'},
    'color_variations': {'color_variations_name': 'Неизвестный окрас'},
    'temperament': {'temperament_name': 'Неизвестный темперамент'},
    'size': {'size_name': 'Неизвестный размер'}
}

@app.route('/add_value', methods=['POST'])
def add_value():
    data = request.get_json()
    table = data.get('table')
    attribute = data.get('attribute')
    value = data.get('value')

    print(f"Adding value: table={table}, attribute={attribute}, value={value}")

    # Валидация входных данных
    if not table or table not in ALLOWED_TABLES:
        return jsonify({'success': False, 'error': 'Недопустимая таблица'})
    if not attribute or attribute not in TABLES.get(table, {}):
        return jsonify({'success': False, 'error': 'Недопустимый атрибут'})
    if not value or not value.strip():
        return jsonify({'success': False, 'error': 'Значение не указано'})

    # Валидация значения согласно VALIDATION_RULES
    validation_data = {attribute: value}
    errors = validate_data(validation_data, VALIDATION_RULES.get(table, {}))
    if errors:
        return jsonify({'success': False, 'error': ', '.join(errors)})

    # Подготовка данных для вставки
    insert_data = {attribute: value.strip()}
    required_fields = DEFAULT_VALUES.get(table, {})

    # Добавляем значения по умолчанию для обязательных полей, если они не указаны
    for field, default_value in required_fields.items():
        if field not in insert_data:
            insert_data[field] = default_value

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            columns = ', '.join(insert_data.keys())
            placeholders = ', '.join(['?' for _ in insert_data])
            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            cursor.execute(query, list(insert_data.values()))
            conn.commit()
        print(f"Successfully added value to {table}: {insert_data}")
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error adding value: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})
        

@app.route('/get_second_values', methods=['POST'])
def get_second_values():
    table = request.form['table']  # Первая таблица
    attr1 = request.form['attr1']  # Первый атрибут
    value1 = request.form['value1']  # Значение первого атрибута
    table1 = request.form.get('table1')  # Вторая таблица
    attr2 = request.form['attr2']  # Второй атрибут

    print(f"Received: table={table}, attr1={attr1}, value1={value1}, table1={table1}, attr2={attr2}")

    if not table1 or table1 == table:
        table1 = table

    table_relationships = {
        ('breeds', 'dogs'): ('b', 'd', 'JOIN dogs d ON d.breeds_id = b.id'),
        ('breeds', 'locations'): ('b', 'l', 'JOIN dogs d ON d.breeds_id = b.id JOIN locations l ON d.location_id = l.id'),
        ('breeds', 'vet_examinations'): ('b', 've', 'JOIN dogs d ON d.breeds_id = b.id JOIN vet_examinations ve ON d.vet_examinations_id = ve.id'),
        ('breeds', 'getting'): ('b', 'g', 'JOIN dogs d ON d.breeds_id = b.id JOIN getting g ON d.getting_id = g.id'),
        ('dogs', 'breeds'): ('d', 'b', 'JOIN breeds b ON d.breeds_id = b.id'),
        ('dogs', 'locations'): ('d', 'l', 'JOIN locations l ON d.location_id = l.id'),
        ('dogs', 'vet_examinations'): ('d', 've', 'JOIN vet_examinations ve ON d.vet_examinations_id = ve.id'),
        ('dogs', 'getting'): ('d', 'g', 'JOIN getting g ON d.getting_id = g.id'),
        ('locations', 'dogs'): ('l', 'd', 'JOIN dogs d ON d.location_id = l.id'),
        ('locations', 'breeds'): ('l', 'b', 'JOIN dogs d ON d.location_id = l.id JOIN breeds b ON d.breeds_id = b.id'),
        ('locations', 'vet_examinations'): ('l', 've', 'JOIN dogs d ON d.location_id = l.id JOIN vet_examinations ve ON d.vet_examinations_id = ve.id'),
        ('locations', 'getting'): ('l', 'g', 'JOIN dogs d ON d.location_id = l.id JOIN getting g ON d.getting_id = g.id'),
        ('vet_examinations', 'dogs'): ('ve', 'd', 'JOIN dogs d ON d.vet_examinations_id = ve.id'),
        ('vet_examinations', 'breeds'): ('ve', 'b', 'JOIN dogs d ON d.vet_examinations_id = ve.id JOIN breeds b ON d.breeds_id = b.id'),
        ('vet_examinations', 'locations'): ('ve', 'l', 'JOIN dogs d ON d.vet_examinations_id = ve.id JOIN locations l ON d.location_id = l.id'),
        ('vet_examinations', 'getting'): ('ve', 'g', 'JOIN dogs d ON d.vet_examinations_id = ve.id JOIN getting g ON d.getting_id = g.id'),
        ('getting', 'dogs'): ('g', 'd', 'JOIN dogs d ON d.getting_id = g.id'),
        ('getting', 'breeds'): ('g', 'b', 'JOIN dogs d ON d.getting_id = g.id JOIN breeds b ON d.breeds_id = b.id'),
        ('getting', 'locations'): ('g', 'l', 'JOIN dogs d ON d.getting_id = g.id JOIN locations l ON d.location_id = l.id'),
        ('getting', 'vet_examinations'): ('g', 've', 'JOIN dogs d ON d.getting_id = g.id JOIN vet_examinations ve ON d.vet_examinations_id = ve.id'),
    }

    with get_db_connection() as conn:
        values = []
        try:
            if table == table1:
                if table == 'dogs' and attr2 in TABLES['dogs'] and 'has_options' in TABLES['dogs'][attr2]:
                    option_field = TABLES['dogs'][attr2]['has_options']
                    related_table = {
                        'breed_name': 'breeds',
                        'location_name': 'locations',
                        'examination_date': 'vet_examinations',
                        'getting_by': 'getting',
                        'coat_type_name': 'coat_type',
                        'color_variations_name': 'color_variations',
                        'temperament_name': 'temperament',
                        'size_name': 'size'
                    }.get(option_field, '')
                    if related_table:
                        query = f"""
                            SELECT DISTINCT {option_field}
                            FROM dogs d
                            JOIN {related_table} t ON d.{attr2} = t.id
                            WHERE d.{attr1} = ?
                            ORDER BY {option_field}
                        """
                        values = [row[option_field] for row in conn.execute(query, (value1,)).fetchall()]
                    else:
                        query = f"SELECT DISTINCT {attr2} FROM {table} WHERE {attr1} = ? ORDER BY {attr2}"
                        values = [row[attr2] for row in conn.execute(query, (value1,)).fetchall()]
                else:
                    query = f"SELECT DISTINCT {attr2} FROM {table} WHERE {attr1} = ? ORDER BY {attr2}"
                    values = [row[attr2] for row in conn.execute(query, (value1,)).fetchall()]
            elif (table, table1) in table_relationships:
                alias0, alias1, join_condition = table_relationships[(table, table1)]
                if table1 == 'dogs' and attr2 in TABLES['dogs'] and 'has_options' in TABLES['dogs'][attr2]:
                    option_field = TABLES['dogs'][attr2]['has_options']
                    related_table_info = {
                        'breed_name': ('b2', 'breeds', 'breeds_id'),
                        'location_name': ('l2', 'locations', 'location_id'),
                        'examination_date': ('ve2', 'vet_examinations', 'vet_examinations_id'),
                        'getting_by': ('g2', 'getting', 'getting_id'),
                        'coat_type_name': ('ct2', 'coat_type', 'coat_type'),
                        'color_variations_name': ('cv2', 'color_variations', 'color_variations'),
                        'temperament_name': ('t2', 'temperament', 'temperament'),
                        'size_name': ('s2', 'size', 'size')
                    }.get(option_field, (alias1, '', attr2))
                    join_alias, join_table, join_field = related_table_info
                    if join_table:
                        query = f"""
                            SELECT DISTINCT {join_alias}.{option_field}
                            FROM {table} {alias0}
                            {join_condition}
                            JOIN {join_table} {join_alias} ON {alias1}.{join_field} = {join_alias}.id
                            WHERE {alias0}.{attr1} = ?
                            ORDER BY {join_alias}.{option_field}
                        """
                        values = [row[option_field] for row in conn.execute(query, (value1,)).fetchall()]
                    else:
                        query = f"""
                            SELECT DISTINCT {alias1}.{attr2}
                            FROM {table} {alias0}
                            {join_condition}
                            WHERE {alias0}.{attr1} = ?
                            ORDER BY {alias1}.{attr2}
                        """
                        values = [row[attr2] for row in conn.execute(query, (value1,)).fetchall()]
                else:
                    query = f"""
                        SELECT DISTINCT {alias1}.{attr2}
                        FROM {table} {alias0}
                        {join_condition}
                        WHERE {alias0}.{attr1} = ?
                        ORDER BY {alias1}.{attr2}
                    """
                    values = [row[attr2] for row in conn.execute(query, (value1,)).fetchall()]
            else:
                print(f"No relationship found for table={table}, table1={table1}")
                return jsonify([])
        except sqlite3.OperationalError as e:
            print(f"SQL Error: {str(e)}, Query: {query}, Params: {value1}")
            return jsonify({'error': f"Ошибка базы данных: {str(e)}"})

        print(f"Second Values Query: {query}, Params: {value1}")
        print(f"Returned values: {values}")
        return jsonify([str(value) for value in values if value is not None])
        
@app.route('/sync_queries', methods=['GET', 'POST'])
def sync_queries():
    tables = {
        'dogs': 'Собаки',
        'breeds': 'Породы',
        'vet_examinations': 'Ветеринарные осмотры',
        'locations': 'Места размещения',
        'getting': 'Получение приютом',
    }
    attributes = TABLES

    # Table aliases for SQL queries
    table_aliases = {
        'dogs': 'd',
        'breeds': 'b',
        'locations': 'l',
        'vet_examinations': 've',
        'getting': 'g',
        'coat_type': 'ct',
        'color_variations': 'cv',
        'temperament': 't',
        'size': 's'
    }

    if request.method == 'POST':
        selected_table = request.form.get('table')
        selected_attr1 = request.form.get('first_attribute')
        selected_value1 = request.form.get('first_value')
        selected_table1 = request.form.get('table1')
        selected_attr2 = request.form.get('second_attribute')
        selected_value2 = request.form.get('second_value')

        print(f"Received: table={selected_table}, attr1={selected_attr1}, value1={selected_value1}, "
              f"table1={selected_table1}, attr2={selected_attr2}, value2={selected_value2}")

        errors = []
        results = []
        warning = None
        if not selected_table or selected_table not in tables:
            errors.append("Выберите первую таблицу")
        elif not selected_attr1 or selected_attr1 not in attributes[selected_table]:
            errors.append("Выберите первый атрибут")
        elif not selected_value1:
            errors.append("Выберите значение для первого атрибута")
        elif selected_table1 and not selected_table1 in tables:
            errors.append("Выберите корректную вторую таблицу")
        elif selected_attr2 and not selected_table1:
            errors.append("Выберите вторую таблицу, если выбран второй атрибут")
        elif selected_attr2 and selected_attr2 not in attributes.get(selected_table1, {}):
            errors.append("Выберите корректный второй атрибут")
        elif selected_attr2 and not selected_value2:
            errors.append("Выберите значение для второго атрибута")
        else:
            with get_db_connection() as conn:
                # Main table is always dogs for consistency
                main_table = 'dogs d'
                joins = [
                    'LEFT JOIN breeds b ON d.breeds_id = b.id',
                    'LEFT JOIN locations l ON d.location_id = l.id',
                    'LEFT JOIN vet_examinations ve ON d.vet_examinations_id = ve.id',
                    'LEFT JOIN getting g ON d.getting_id = g.id',
                    'LEFT JOIN coat_type ct ON d.coat_type = ct.id',
                    'LEFT JOIN color_variations cv ON d.color_variations = cv.id',
                    'LEFT JOIN temperament t ON d.temperament = t.id',
                    'LEFT JOIN size s ON d.size = s.id'
                ]

                where_clauses = []
                params = []

                # First condition
                if selected_table == 'dogs':
                    # Check if attr1 has has_options (e.g., breeds_id)
                    if selected_attr1 in TABLES['dogs'] and 'has_options' in TABLES['dogs'][selected_attr1]:
                        option_field = TABLES['dogs'][selected_attr1]['has_options']
                        related_table = {
                            'breed_name': 'b',
                            'location_name': 'l',
                            'examination_date': 've',
                            'getting_by': 'g',
                            'coat_type_name': 'ct',
                            'color_variations_name': 'cv',
                            'temperament_name': 't',
                            'size_name': 's'
                        }.get(option_field, 'd')
                        where_clauses.append(f"{related_table}.{option_field} = ?")
                    else:
                        where_clauses.append(f"d.{selected_attr1} = ?")
                    params.append(selected_value1)
                else:
                    alias = table_aliases[selected_table]
                    if selected_attr1 in TABLES[selected_table] and 'has_options' in TABLES[selected_table][selected_attr1]:
                        option_field = TABLES[selected_table][selected_attr1]['has_options']
                        where_clauses.append(f"{alias}.{option_field} = ?")
                    else:
                        where_clauses.append(f"{alias}.{selected_attr1} = ?")
                    params.append(selected_value1)

                # Second condition
                if selected_table1 and selected_attr2 and selected_value2:
                    alias = table_aliases[selected_table1]
                    if selected_table1 == 'dogs' and selected_attr2 in TABLES['dogs'] and 'has_options' in TABLES['dogs'][selected_attr2]:
                        option_field = TABLES['dogs'][selected_attr2]['has_options']
                        related_table = {
                            'breed_name': 'b',
                            'location_name': 'l',
                            'examination_date': 've',
                            'getting_by': 'g',
                            'coat_type_name': 'ct',
                            'color_variations_name': 'cv',
                            'temperament_name': 't',
                            'size_name': 's'
                        }.get(option_field, 'd')
                        where_clauses.append(f"{related_table}.{option_field} = ?")
                    elif selected_attr2 in TABLES[selected_table1] and 'has_options' in TABLES[selected_table1][selected_attr2]:
                        option_field = TABLES[selected_table1][selected_attr2]['has_options']
                        where_clauses.append(f"{alias}.{option_field} = ?")
                    else:
                        where_clauses.append(f"{alias}.{selected_attr2} = ?")
                    params.append(selected_value2)

                # Build SQL query
                query = f"""
                    SELECT DISTINCT
                        d.id AS dog_id, d.name, d.birth_date, d.registration_date, d.microchip_number,
                        b.breed_name, b.breed_group, b.origin_country, b.average_lifes, b.typical_use,
                        b.common_health_issues, b.recommended_vaccinations, b.veterinary_care,
                        b.average_weight_male, b.average_weight_female, b.trainability_level,
                        b.recommended_training_age, b.common_behavioral_issues, b.preferred_training_methods,
                        b.typical_learning_period,
                        l.location_name, l.location_type, l.address, l.contact_info AS location_contact_info,
                        l.price, l.availability, l.website,
                        ve.examination_date, ve.veterinarian_name, ve.diagnosis, ve.treatment, ve.next_examination_date,
                        g.getting_by, g.contact_info AS getting_contact_info, g.getting_type, g.reason,
                        ct.coat_type_name, cv.color_variations_name, t.temperament_name, s.size_name
                    FROM {main_table}
                    {' '.join(joins)}
                    WHERE {' AND '.join(where_clauses)}
                """
                print(f"Query: {query}, Params: {params}")

                try:
                    results = conn.execute(query, params).fetchall()
                    print(f"Results count: {len(results)}")  # Отладка: количество результатов
                    if not results:
                        warning = "Не найдены собаки, привязанные к таким значениям"
                        print(f"Warning set: {warning}")
                except sqlite3.OperationalError as e:
                    errors.append(f"Ошибка базы данных: {str(e)}")
                    print(f"SQL Error: {str(e)}, Query: {query}, Params: {params}")

        return render_template(
            'sync_queries.html',
            tables=tables,
            attributes=attributes,
            results=results,
            errors=errors,
            warning=warning,
            selected_table=selected_table,
            selected_table1=selected_table1,
            selected_attr1=selected_attr1,
            selected_value1=selected_value1,
            selected_attr2=selected_attr2,
            selected_value2=selected_value2
        )

    # Handle GET request
    return render_template('sync_queries.html', tables=tables, attributes=attributes)


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
        cursor.execute("""
            INSERT INTO locations (location_name, location_type, address, contact_info, price, availability, website)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (location_name, data.get('location_type'), data.get('address'), data.get('contact_info'),
              data.get('price'), data.get('availability'), data.get('website')))
        conn.commit()
        location_id = cursor.lastrowid
    return jsonify({'success': True, 'id': location_id, 'location_name': location_name})

@app.route('/add_getting', methods=['POST'])
def add_getting():
    data = request.get_json()
    getting_by = data.get('getting_by', '').strip()
    if not getting_by:
        return jsonify({'success': False, 'error': 'Кем передана не указано'})
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO getting (getting_by, contact_info, getting_type, reason)
            VALUES (?, ?, ?, ?)
        """, (getting_by, data.get('contact_info'), data.get('getting_type'), data.get('reason')))
        conn.commit()
        getting_id = cursor.lastrowid
    return jsonify({'success': True, 'id': getting_id, 'getting_by': getting_by})

@app.route('/add_vet_examination', methods=['POST'])
def add_vet_examination():
    data = request.get_json()
    examination_date = data.get('examination_date', '').strip()
    if not examination_date:
        return jsonify({'success': False, 'error': 'Дата осмотра не указана'})
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO vet_examinations (examination_date, veterinarian_name, diagnosis, treatment, next_examination_date)
            VALUES (?, ?, ?, ?, ?)
        """, (examination_date, data.get('veterinarian_name'), data.get('diagnosis'), data.get('treatment'),
              data.get('next_examination_date')))
        conn.commit()
        vet_id = cursor.lastrowid
    return jsonify({'success': True, 'id': vet_id, 'examination_date': examination_date})
@app.route('/add_detailed', methods=['GET', 'POST'])
def add_detailed():
    errors = []
    with get_db_connection() as conn:
        breeds = conn.execute("SELECT id, breed_name FROM breeds ORDER BY breed_name").fetchall()
        locations = conn.execute("SELECT id, location_name FROM locations ORDER BY location_name").fetchall()
        coat_types = conn.execute("SELECT id, coat_type_name FROM coat_type ORDER BY coat_type_name").fetchall()
        color_variations = conn.execute("SELECT id, color_variations_name FROM color_variations ORDER BY color_variations_name").fetchall()
        temperaments = conn.execute("SELECT id, temperament_name FROM temperament ORDER BY temperament_name").fetchall()
        sizes = conn.execute("SELECT id, size_name FROM size ORDER BY size_name").fetchall()
        gettings = conn.execute("SELECT id, getting_by FROM getting ORDER BY getting_by").fetchall()
        vet_examinations = conn.execute("SELECT id, examination_date FROM vet_examinations ORDER BY examination_date").fetchall()

    if request.method == 'POST':
        dog_data = {
            'name': request.form['name'],
            'birth_date': request.form['birth_date'] or None,
            'registration_date': request.form['registration_date'] or None,
            'microchip_number': request.form['microchip_number'] or None,
            'breeds_id': request.form['breeds_id'],
            'location_id': request.form['location_id'],
            'coat_type': request.form['coat_type'] or None,
            'color_variations': request.form['color_variations'] or None,
            'temperament': request.form['temperament'] or None,
            'size': request.form['size'] or None,
            'getting_id': request.form['getting_id'] or None,
            'vet_examinations_id': request.form['vet_examinations_id'] or None
        }
        errors = validate_data(dog_data, VALIDATION_RULES['dogs'])
        if not errors:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO dogs (name, birth_date, registration_date, microchip_number, breeds_id, location_id,
                                      coat_type, color_variations, temperament, size, getting_id, vet_examinations_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (dog_data['name'], dog_data['birth_date'], dog_data['registration_date'],
                      dog_data['microchip_number'], dog_data['breeds_id'], dog_data['location_id'],
                      dog_data['coat_type'], dog_data['color_variations'], dog_data['temperament'],
                      dog_data['size'], dog_data['getting_id'], dog_data['vet_examinations_id']))
                conn.commit()
            return redirect(url_for('view'))

    return render_template('add_detailed.html', errors=errors, breeds=breeds, locations=locations,
                           coat_types=coat_types, color_variations=color_variations, temperaments=temperaments,
                           sizes=sizes, gettings=gettings, vet_examinations=vet_examinations)

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
        gettings = conn.execute("SELECT id, getting_by FROM getting WHERE getting_by IS NOT NULL ORDER BY getting_by").fetchall()
        vet_examinations = conn.execute("SELECT id, examination_date FROM vet_examinations ORDER BY examination_date").fetchall()

    if request.method == 'POST':
        data = {
            'name': request.form['name'],
            'breeds_id': request.form['breeds_id'],
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

        errors = validate_data(data, VALIDATION_RULES['dogs'])
        if not errors:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO dogs (name, breeds_id, location_id, birth_date, registration_date, microchip_number,
                                      coat_type, color_variations, temperament, size, getting_id, vet_examinations_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (data['name'], data['breeds_id'], data['location_id'], data['birth_date'],
                      data['registration_date'], data['microchip_number'], data['coat_type'],
                      data['color_variations'], data['temperament'], data['size'], data['getting_id'],
                      data['vet_examinations_id']))
                conn.commit()
            return redirect(url_for('view'))

    with get_db_connection() as conn:
        dogs = conn.execute("""
            SELECT d.id, d.name, b.breed_name, l.location_name
            FROM dogs d
            LEFT JOIN breeds b ON d.breeds_id = b.id
            LEFT JOIN locations l ON d.location_id = l.id
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
