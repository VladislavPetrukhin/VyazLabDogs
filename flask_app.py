from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

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
                    from datetime import datetime
                    datetime.strptime(value, '%Y-%m-%d')
                except ValueError:
                    errors.append(f"{field}: неверный формат даты, ожидается YYYY-MM-DD")
    return errors

# Главная страница
@app.route('/')
def index():
    return render_template('index.html')

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

    # Получаем уникальные списки пород и мест размещения
    with get_db_connection() as conn:
        breeds = [row['breed_name'] for row in conn.execute("SELECT DISTINCT breed_name FROM breeds ORDER BY breed_name").fetchall()]
        locations = [row['location_name'] for row in conn.execute("SELECT DISTINCT location_name FROM locations ORDER BY location_name").fetchall()]

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        breed_name = request.form.get('breed_name')
        location_name = request.form.get('location_name')

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
                query += " AND d.name LIKE ?"
                params.append(f"%{name}%")
            if breed_name:
                query += " AND b.breed_name = ?"
                params.append(breed_name)
            if location_name:
                query += " AND l.location_name = ?"
                params.append(location_name)

            results = cursor.execute(query, params).fetchall()
            if not results:
                no_results = True

    return render_template('search.html', results=results, name=name, 
                           breed_name=breed_name, location_name=location_name, 
                           no_results=no_results, breeds=breeds, locations=locations)

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
        gettings = conn.execute("SELECT id, getting_by FROM getting ORDER BY getting_by").fetchall()
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

# Управление получением собак
@app.route('/getting', methods=['GET', 'POST'])
def getting():
    errors = []
    with get_db_connection() as conn:
        dogs = conn.execute("SELECT id, name FROM dogs ORDER BY name").fetchall()

    if request.method == 'POST':
        data = {
            'dog_id': request.form['dog_id'],
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
                    INSERT INTO getting (dog_id, getting_by, contact_info, getting_type, reason)
                    VALUES (?, ?, ?, ?, ?)
                """, (data['dog_id'], data['getting_by'], data['contact_info'], data['getting_type'], data['reason']))
                conn.commit()
    with get_db_connection() as conn:
        gettings = conn.execute("""
            SELECT g.id, d.name AS dog_name, g.getting_by, g.contact_info, g.getting_type, g.reason
            FROM getting g
            JOIN dogs d ON g.dog_id = d.id
            ORDER BY g.id
        """).fetchall()
    return render_template('getting.html', gettings=gettings, dogs=dogs, errors=errors)

# Статистика
@app.route('/stats')
def stats():
    with get_db_connection() as conn:
        by_breed = conn.execute("""
            SELECT b.breed_name, COUNT(d.id) AS dog_count 
            FROM dogs d 
            JOIN breeds b ON d.breeds_id = b.id 
            GROUP BY b.breed_name
        """).fetchall()
        by_location = conn.execute("""
            SELECT l.location_name, COUNT(d.id) AS dog_count 
            FROM dogs d 
            JOIN locations l ON d.location_id = l.id 
            GROUP BY l.location_name
        """).fetchall()
    return render_template('stats.html', by_breed=by_breed, by_location=by_location)

# Запросы
@app.route('/queries', methods=['GET', 'POST'])
def queries():
    attributes = {
    # Поля из таблицы dogs (Собаки)
    'name': {'table': 'd', 'column': 'name', 'type': 'text', 'label': 'Имя собаки'},
    'birth_date': {'table': 'd', 'column': 'birth_date', 'type': 'text', 'label': 'Дата рождения'},
    'breeds_id': {'table': 'd', 'column': 'breeds_id', 'type': 'number', 'label': 'ID породы'},
    'getting_id': {'table': 'd', 'column': 'getting_id', 'type': 'number', 'label': 'ID получения собаки'},
    'vet_examinations_id': {'table': 'd', 'column': 'vet_examinations_id', 'type': 'number', 'label': 'ID ветеринарного осмотра'},
    'location_id': {'table': 'd', 'column': 'location_id', 'type': 'number', 'label': 'ID места размещения'},
    'registration_date': {'table': 'd', 'column': 'registration_date', 'type': 'text', 'label': 'Дата регистрации'},
    'microchip_number': {'table': 'd', 'column': 'microchip_number', 'type': 'text', 'label': 'Номер микрочипа'},
    'coat_type': {'table': 'ct', 'column': 'coat_type_name', 'type': 'text', 'label': 'Тип шерсти'},
    'color_variations': {'table': 'cv', 'column': 'color_variations_name', 'type': 'text', 'label': 'Окрас'},
    'temperament': {'table': 't', 'column': 'temperament_name', 'type': 'text', 'label': 'Темперамент'},
    'size': {'table': 's', 'column': 'size_name', 'type': 'text', 'label': 'Размер'},

    # Поля из таблицы coat_type (Тип шерсти)
    'coat_type_name': {'table': 'ct', 'column': 'coat_type_name', 'type': 'text', 'label': 'Название типа шерсти'},

    # Поля из таблицы color_variations (Окрас)
    'color_variations_name': {'table': 'cv', 'column': 'color_variations_name', 'type': 'text', 'label': 'Название окраса'},

    # Поля из таблицы temperament (Темперамент)
    'temperament_name': {'table': 't', 'column': 'temperament_name', 'type': 'text', 'label': 'Название темперамента'},

    # Поля из таблицы size (Размер)
    'size_name': {'table': 's', 'column': 'size_name', 'type': 'text', 'label': 'Название размера'},

    # Поля из таблицы breeds (Породы)
    'breed_name': {'table': 'b', 'column': 'breed_name', 'type': 'text', 'label': 'Название породы'},
    'breed_group': {'table': 'b', 'column': 'breed_group', 'type': 'text', 'label': 'Группа породы'},
    'origin_country': {'table': 'b', 'column': 'origin_country', 'type': 'text', 'label': 'Страна происхождения'},
    'average_lifes': {'table': 'b', 'column': 'average_lifes', 'type': 'number', 'label': 'Средняя продолжительность жизни'},
    'typical_use': {'table': 'b', 'column': 'typical_use', 'type': 'text', 'label': 'Типичное использование'},
    'common_health_issues': {'table': 'b', 'column': 'common_health_issues', 'type': 'text', 'label': 'Распространенные проблемы со здоровьем'},
    'recommended_vaccinations': {'table': 'b', 'column': 'recommended_vaccinations', 'type': 'text', 'label': 'Рекомендуемые вакцинации'},
    'veterinary_care': {'table': 'b', 'column': 'veterinary_care', 'type': 'text', 'label': 'Потребности в ветеринарном уходе'},
    'average_weight_male': {'table': 'b', 'column': 'average_weight_male', 'type': 'number', 'label': 'Средний вес самцов'},
    'average_weight_female': {'table': 'b', 'column': 'average_weight_female', 'type': 'number', 'label': 'Средний вес самок'},
    'trainability_level': {'table': 'b', 'column': 'trainability_level', 'type': 'text', 'label': 'Уровень обучаемости'},
    'recommended_training_age': {'table': 'b', 'column': 'recommended_training_age', 'type': 'number', 'label': 'Рекомендуемый возраст начала дрессировки'},
    'common_behavioral_issues': {'table': 'b', 'column': 'common_behavioral_issues', 'type': 'text', 'label': 'Распространенные поведенческие проблемы'},
    'preferred_training_methods': {'table': 'b', 'column': 'preferred_training_methods', 'type': 'text', 'label': 'Предпочтительные методы дрессировки'},
    'typical_learning_period': {'table': 'b', 'column': 'typical_learning_period', 'type': 'number', 'label': 'Типичный период обучения'},

    # Поля из таблицы getting (Получение собаки)
    'getting_by': {'table': 'g', 'column': 'getting_by', 'type': 'text', 'label': 'Кем передана'},
    'contact_info': {'table': 'g', 'column': 'contact_info', 'type': 'text', 'label': 'Контактная информация'},
    'getting_type': {'table': 'g', 'column': 'getting_type', 'type': 'text', 'label': 'Тип передачи'},
    'reason': {'table': 'g', 'column': 'reason', 'type': 'text', 'label': 'Причина передачи'},

    # Поля из таблицы vet_examinations (Ветеринарные осмотры)
    'examination_date': {'table': 've', 'column': 'examination_date', 'type': 'text', 'label': 'Дата осмотра'},
    'veterinarian_name': {'table': 've', 'column': 'veterinarian_name', 'type': 'text', 'label': 'Имя ветеринара'},
    'diagnosis': {'table': 've', 'column': 'diagnosis', 'type': 'text', 'label': 'Диагноз'},
    'treatment': {'table': 've', 'column': 'treatment', 'type': 'text', 'label': 'Лечение'},
    'next_examination_date': {'table': 've', 'column': 'next_examination_date', 'type': 'text', 'label': 'Дата следующего осмотра'},

    # Поля из таблицы locations (Места размещения)
    'location_name': {'table': 'l', 'column': 'location_name', 'type': 'text', 'label': 'Название места'},
    'location_type': {'table': 'l', 'column': 'location_type', 'type': 'text', 'label': 'Тип места'},
    'address': {'table': 'l', 'column': 'address', 'type': 'text', 'label': 'Адрес'},
    'contact_info': {'table': 'l', 'column': 'contact_info', 'type': 'text', 'label': 'Контактная информация'},
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

    with get_db_connection() as conn:
        breeds = [row['breed_name'] for row in conn.execute("SELECT DISTINCT breed_name FROM breeds ORDER BY breed_name").fetchall()]
        locations = [row['location_name'] for row in conn.execute("SELECT DISTINCT location_name FROM locations ORDER BY location_name").fetchall()]

    if request.method == 'POST':
        selected_attribute1 = request.form.get('attribute1')
        search_min1 = request.form.get('search_min1')
        search_max1 = request.form.get('search_max1') or search_min1
        selected_attribute2 = request.form.get('attribute2')
        search_min2 = request.form.get('search_min2')
        search_max2 = request.form.get('search_max2') or search_min2

        if not selected_attribute1 or selected_attribute1 not in attributes:
            errors.append("Выберите корректный первый атрибут")
        elif not search_min1:
            errors.append("Введите минимальное значение для первого атрибута")
        else:
            attr_info1 = attributes[selected_attribute1]
            table1 = attr_info1['table']
            column1 = attr_info1['column']
            attr_type1 = attr_info1['type']

            try:
                if attr_type1 == 'number':
                    search_min1 = int(search_min1)
                    if search_max1:
                        search_max1 = int(search_max1)
                        if search_max1 < search_min1:
                            errors.append(f"Максимальное значение для '{attr_info1['label']}' должно быть больше минимального")
                            raise ValueError
                else:
                    search_max1 = search_min1

                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    query = """
                        SELECT d.id, d.name, b.breed_name, l.location_name, d.birth_date, d.registration_date, d.microchip_number
                        FROM dogs d
                        JOIN breeds b ON d.breeds_id = b.id
                        JOIN locations l ON d.location_id = l.id
                        JOIN coat_type ct ON d.coat_type = ct.id
                        JOIN color_variations cv ON d.color_variations = cv.id
                        JOIN temperament t ON d.temperament = t.id
                        JOIN size s ON d.size = s.id
                        WHERE {table1}.{column1} >= ? AND {table1}.{column1} <= ?
                    """.format(table1=table1, column1=column1)
                    params = [search_min1, search_max1]

                    if selected_attribute2 and search_min2:
                        attr_info2 = attributes[selected_attribute2]
                        table2 = attr_info2['table']
                        column2 = attr_info2['column']
                        attr_type2 = attr_info2['type']

                        if attr_type2 == 'number':
                            search_min2 = int(search_min2)
                            if search_max2:
                                search_max2 = int(search_max2)
                                if search_max2 < search_min2:
                                    errors.append(f"Максимальное значение для '{attr_info2['label']}' должно быть больше минимального")
                                    raise ValueError
                        else:
                            search_max2 = search_min2

                        query += " AND {table2}.{column2} >= ? AND {table2}.{column2} <= ?".format(table2=table2, column2=column2)
                        params.extend([search_min2, search_max2])

                    results = cursor.execute(query, tuple(params)).fetchall()

            except ValueError:
                if not errors:
                    errors.append(f"Значение для '{attr_info1['label']}' должно быть {'числом' if attr_type1 == 'number' else 'текстом'}")
            except sqlite3.OperationalError as e:
                errors.append(f"Ошибка базы данных: {str(e)}")

    return render_template('queries.html', attributes=attributes, results=results, 
                          selected_attribute1=selected_attribute1, search_min1=search_min1, search_max1=search_max1,
                          selected_attribute2=selected_attribute2, search_min2=search_min2, search_max2=search_max2,
                          errors=errors, breeds=breeds, locations=locations, numeric_attributes=numeric_attributes)

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