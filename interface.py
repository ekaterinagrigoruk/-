import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import psycopg2


# Функция для подключения к базе данных
def connect_to_db():
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="021008",
            host="localhost",
            port="5432"
        )
        return conn
    except Exception as e:
        messagebox.showerror("Ошибка подключения", f"Не удалось подключиться к базе данных: {e}")
        return None


# Функция для добавления новой экспертизы
def add_new_inspection():
    add_window = tk.Toplevel(root)
    add_window.title("Добавить новую экспертизу")

    tk.Label(add_window, text="Имя эксперта:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    expert_name_entry = tk.Entry(add_window)
    expert_name_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

    tk.Label(add_window, text="Дата (ГГГГ-ММ-ДД):").grid(row=1, column=0, padx=10, pady=5, sticky="w")
    date_entry = tk.Entry(add_window)
    date_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

    tk.Label(add_window, text="Область:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
    region_entry = tk.Entry(add_window)
    region_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

    tk.Label(add_window, text="Населенный пункт:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
    locality_entry = tk.Entry(add_window)
    locality_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

    tk.Label(add_window, text="Район:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
    district_entry = tk.Entry(add_window)
    district_entry.grid(row=4, column=1, padx=10, pady=5, sticky="ew")

    tk.Label(add_window, text="Улица:").grid(row=5, column=0, padx=10, pady=5, sticky="w")
    street_entry = tk.Entry(add_window)
    street_entry.grid(row=5, column=1, padx=10, pady=5, sticky="ew")

    tk.Label(add_window, text="Дом:").grid(row=6, column=0, padx=10, pady=5, sticky="w")
    house_entry = tk.Entry(add_window)
    house_entry.grid(row=6, column=1, padx=10, pady=5, sticky="ew")

    tk.Label(add_window, text="Квартира:").grid(row=7, column=0, padx=10, pady=5, sticky="w")
    apartment_entry = tk.Entry(add_window)
    apartment_entry.grid(row=7, column=1, padx=10, pady=5, sticky="ew")

    def save_inspection():
        expert_name = expert_name_entry.get()
        date = date_entry.get()
        region = region_entry.get()
        locality = locality_entry.get()
        district = district_entry.get()
        street = street_entry.get()
        house = house_entry.get()
        apartment = apartment_entry.get()

        if not all([expert_name, date, region, locality, street, house]):
            messagebox.showerror("Ошибка ввода", "Пожалуйста, заполните все обязательные поля.")
            return

        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO objects (region, locality, district, street, house, apartment)
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING object_id
            """, (region, locality, district, street, house, apartment))
            object_id = cur.fetchone()[0]

            cur.execute("""
                INSERT INTO inspections (expert_id, object_id, inspection_date)
                VALUES (
                    (SELECT expert_id FROM experts WHERE expert_name = %s LIMIT 1),
                    %s,
                    %s
                ) RETURNING id
            """, (expert_name, object_id, date))
            inspection_id = cur.fetchone()[0]
            conn.commit()
            messagebox.showinfo("Успех", "Экспертиза успешно добавлена.")
            add_window.destroy()
            add_room_window(inspection_id)
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Ошибка", f"Не удалось добавить экспертизу: {e}")

    save_button = tk.Button(add_window, text="Сохранить", command=save_inspection)
    save_button.grid(row=8, column=0, columnspan=2, pady=10)

    for i in range(2):
        add_window.grid_columnconfigure(i, weight=1)


def add_room_window(inspection_id):
    room_window = tk.Toplevel(root)
    room_window.title("Добавить помещение")

    tk.Label(room_window, text="Наименование помещения:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    room_name_entry = tk.Entry(room_window)
    room_name_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

    tk.Label(room_window, text="Площадь (м2):").grid(row=1, column=0, padx=10, pady=5, sticky="w")
    area_entry = tk.Entry(room_window)
    area_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

    tk.Label(room_window, text="Высота потолков (м):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
    ceiling_height_entry = tk.Entry(room_window)
    ceiling_height_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

    def save_room():
        room_name = room_name_entry.get()
        area = area_entry.get()
        ceiling_height = ceiling_height_entry.get()

        if not all([room_name, area, ceiling_height]):
            messagebox.showerror("Ошибка ввода", "Пожалуйста, заполните все поля.")
            return

        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO rooms (inspection_id, room_name, area, ceiling_height)
                VALUES (%s, %s, %s, %s) RETURNING room_id
            """, (inspection_id, room_name, area, ceiling_height))
            room_id = cur.fetchone()[0]
            conn.commit()
            messagebox.showinfo("Успех", "Помещение успешно добавлено.")
            room_name_entry.delete(0, tk.END)
            area_entry.delete(0, tk.END)
            ceiling_height_entry.delete(0, tk.END)
            add_damage_window(inspection_id, room_id, room_name)
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Ошибка", f"Не удалось добавить помещение: {e}")

    save_button = tk.Button(room_window, text="Добавить помещение", command=save_room)
    save_button.grid(row=3, column=0, columnspan=2, pady=10)

    for i in range(2):
        room_window.grid_columnconfigure(i, weight=1)


def add_damage_window(inspection_id, room_id, room_name):
    damage_window = tk.Toplevel(root)
    damage_window.title(f"Добавить повреждение для {room_name}")

    tk.Label(damage_window, text="Элемент помещения:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    room_element_name_entry = tk.Entry(damage_window)
    room_element_name_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

    tk.Label(damage_window, text="Описание:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
    description_entry = tk.Entry(damage_window)
    description_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

    tk.Label(damage_window, text="Состояние:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
    condition_entry = tk.Entry(damage_window)
    condition_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

    def save_damage():
        room_element_name = room_element_name_entry.get()
        description = description_entry.get()
        condition = condition_entry.get()

        if not all([room_element_name, description, condition]):
            messagebox.showerror("Ошибка ввода", "Пожалуйста, заполните все поля.")
            return

        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO damages (inspection_id, room_id, room_element_name, description, condition)
                VALUES (%s, %s, %s, %s, %s) RETURNING damage_id
            """, (inspection_id, room_id, room_element_name, description, condition))
            damage_id = cur.fetchone()[0]
            conn.commit()
            messagebox.showinfo("Успех", "Повреждение успешно добавлено.")
            room_element_name_entry.delete(0, tk.END)
            description_entry.delete(0, tk.END)
            condition_entry.delete(0, tk.END)
            add_work_window(damage_id, room_element_name)
            add_material_window(damage_id, description)
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Ошибка", f"Не удалось добавить повреждение: {e}")

    save_button = tk.Button(damage_window, text="Добавить повреждение", command=save_damage)
    save_button.grid(row=3, column=0, columnspan=2, pady=10)

    for i in range(2):
        damage_window.grid_columnconfigure(i, weight=1)


def add_work_window(damage_id, element_name):
    work_window = tk.Toplevel(root)
    work_window.title("Добавить необходимые работы")

    # Загружаем список работ из базы данных для указанного элемента помещения
    try:
        cur = conn.cursor()
        cur.callproc("get_possible_works_for_element", [element_name])
        work_catalog = cur.fetchall()
        conn.commit()
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Ошибка", f"Не удалось загрузить список работ: {e}")
        return

    # Создаем выпадающий список для выбора работы
    work_label = tk.Label(work_window, text="Выберите работу:")
    work_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
    selected_work = tk.StringVar()
    work_dropdown = ttk.Combobox(work_window, textvariable=selected_work, state="readonly", width=30)
    work_dropdown.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
    work_dropdown["values"] = [work[1] for work in work_catalog]
    work_dropdown.current(0)  # Устанавливаем первый элемент списка по умолчанию

    tk.Label(work_window, text="Объем работы:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
    work_volume_entry = tk.Entry(work_window)
    work_volume_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

    tk.Label(work_window, text="Стоимость за единицу:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
    work_unit_cost_entry = tk.Entry(work_window)
    work_unit_cost_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

    def save_work():
        selected_work_id = work_catalog[work_dropdown.current()][0]
        work_volume = work_volume_entry.get()
        work_unit_cost = work_unit_cost_entry.get()

        if not all([work_volume, work_unit_cost]):
            messagebox.showerror("Ошибка ввода", "Пожалуйста, заполните все поля.")
            return

        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO repairs (damage_id, work_id, volume, unit_cost)
                VALUES (%s, %s, %s, %s)
            """, (damage_id, selected_work_id, work_volume, work_unit_cost))
            conn.commit()
            messagebox.showinfo("Успех", "Необходимые работы успешно добавлены.")
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Ошибка", f"Не удалось добавить необходимые работы: {e}")

    save_button = tk.Button(work_window, text="Сохранить", command=save_work)
    save_button.grid(row=3, column=0, columnspan=2, pady=10)

    tk.Button(work_window, text="Закрыть", command=work_window.destroy).grid(row=4, column=0, columnspan=2, pady=10)

    for i in range(2):
        work_window.grid_columnconfigure(i, weight=1)


def add_material_window(damage_id, description):
    material_window = tk.Toplevel(root)
    material_window.title(f"Добавить материалы для повреждения: {description}")

    tk.Label(material_window, text="Тип материала:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    material_type_entry = tk.Entry(material_window)
    material_type_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

    tk.Label(material_window, text="Единица измерения:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
    unit_entry = tk.Entry(material_window)
    unit_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

    tk.Label(material_window, text="Количество:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
    amount_entry = tk.Entry(material_window)
    amount_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

    def save_material():
        material_type = material_type_entry.get()
        unit = unit_entry.get()
        amount = amount_entry.get()

        if not all([material_type, unit, amount]):
            messagebox.showerror("Ошибка ввода", "Пожалуйста, заполните все поля.")
            return

        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO materials (damage_id, material_type, unit, amount)
                VALUES (%s, %s, %s, %s)
            """, (damage_id, material_type, unit, amount))
            conn.commit()
            messagebox.showinfo("Успех", "Материал успешно добавлен.")
            material_type_entry.delete(0, tk.END)
            unit_entry.delete(0, tk.END)
            amount_entry.delete(0, tk.END)
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Ошибка", f"Не удалось добавить материал: {e}")

    save_button = tk.Button(material_window, text="Добавить материал", command=save_material)
    save_button.grid(row=3, column=0, columnspan=2, pady=10)

    for i in range(2):
        material_window.grid_columnconfigure(i, weight=1)


def search_existing_inspections():
    search_window = tk.Toplevel(root)
    search_window.title("Поиск среди существующих экспертиз")
    search_window.geometry("600x400")

    tk.Label(search_window, text="Введите дату экспертизы (ГГГГ-ММ-ДД):").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    date_entry = tk.Entry(search_window)
    date_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

    def search_inspections():
        date = date_entry.get()

        if not date:
            messagebox.showerror("Ошибка ввода", "Пожалуйста, введите дату экспертизы.")
            return

        try:
            cur = conn.cursor()
            cur.callproc("search_inspections_by_date", [date])
            inspections = cur.fetchall()
            conn.commit()
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Ошибка", f"Не удалось выполнить запрос: {e}")
            return

        if inspections:
            choose_inspection_window = tk.Toplevel(search_window)
            choose_inspection_window.title("Выберите экспертизу")
            choose_inspection_window.geometry("600x400")

            tk.Label(choose_inspection_window, text="Выберите экспертизу:").pack(padx=10, pady=5)

            def select_inspection():
                selected_index = inspections_listbox.curselection()
                if selected_index:
                    selected_inspection_id = inspections[selected_index[0]][0]
                    add_functions_window(selected_inspection_id)
                    choose_inspection_window.destroy()
                else:
                    messagebox.showerror("Ошибка", "Пожалуйста, выберите экспертизу.")

            inspections_listbox = tk.Listbox(choose_inspection_window, selectmode="SINGLE", width=100)
            inspections_listbox.pack(padx=10, pady=5)
            for inspection in inspections:
                inspections_listbox.insert(tk.END, f"ID: {inspection[0]}, Эксперт: {inspection[1]}, Адрес: {inspection[2]}, Дата: {inspection[3]}")

            select_button = tk.Button(choose_inspection_window, text="Выбрать", command=select_inspection)
            select_button.pack(padx=10, pady=5)
        else:
            messagebox.showinfo("Результаты поиска", "По вашему запросу ничего не найдено.")

    search_button = tk.Button(search_window, text="Поиск", command=search_inspections)
    search_button.grid(row=1, column=0, columnspan=2, pady=10)

    for i in range(2):
        search_window.grid_columnconfigure(i, weight=1)


def add_functions_window(inspection_id):
    functions_window = tk.Toplevel(root)
    functions_window.title("Выберите функцию")

    def export_materials():
        try:
            cur = conn.cursor()
            cur.callproc("get_inspection_materials", [inspection_id])
            materials = cur.fetchall()
            conn.commit()

            with open(f"inspection_materials_{inspection_id}.txt", "w") as file:
                file.write("Матариал ID\tНазвание материала\tКоличество\tСтоимость за единицу\n")
                for material in materials:
                    file.write("\t".join(str(item) for item in material) + "\n")

            messagebox.showinfo("Успех", "Стоимость материалов экспертизы успешно экспортирована в файл.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать стоимость материалов: {e}")

    def export_damages():
        try:
            cur = conn.cursor()
            cur.callproc("get_inspection_damages", [inspection_id])
            damages = cur.fetchall()
            conn.commit()

            with open(f"inspection_damages_{inspection_id}.txt", "w") as file:
                file.write("Повреждение ID\tНазвание элемента\tОписание\tСостояние на момент осмотра\n")
                for damage in damages:
                    file.write("\t".join(str(item) for item in damage) + "\n")

            messagebox.showinfo("Успех", "Повреждения экспертизы успешно экспортированы в файл.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать повреждения: {e}")

    def export_work_costs():
        try:
            cur = conn.cursor()
            cur.callproc("get_inspection_work_costs", [inspection_id])
            work_costs = cur.fetchall()
            conn.commit()

            with open(f"inspection_work_costs_{inspection_id}.txt", "w") as file:
                file.write("Работа ID\tНазвание работы\tОбъем\tСтоимость за единицу\n")
                for work_cost in work_costs:
                    file.write("\t".join(str(item) for item in work_cost) + "\n")

            messagebox.showinfo("Успех", "Стоимость работ экспертизы успешно экспортирована в файл.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать стоимость работ: {e}")

    def export_material_costs():
        try:
            cur = conn.cursor()
            cur.callproc("get_inspection_material_costs", [inspection_id])
            material_costs = cur.fetchall()
            conn.commit()

            with open(f"inspection_material_costs_{inspection_id}.txt", "w") as file:
                file.write("Материал ID\tНазвание материала\tКоличество\tОбщая стоимость\n")
                for material_cost in material_costs:
                    file.write("\t".join(str(item) for item in material_cost) + "\n")

            messagebox.showinfo("Успех", "Стоимость материалов экспертизы успешно экспортирована в файл.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать стоимость материалов: {e}")

    def delete_inspection():
        confirmation = messagebox.askyesno("Удаление экспертизы", "Вы уверены, что хотите удалить выбранную экспертизу?")
        if confirmation:
            try:
                cur = conn.cursor()
                cur.execute("UPDATE inspections SET is_deleted = TRUE WHERE id = %s", (inspection_id,))
                conn.commit()
                messagebox.showinfo("Успех", "Экспертиза успешно отмечена как удаленная.")
                functions_window.destroy()
            except Exception as e:
                conn.rollback()
                messagebox.showerror("Ошибка", f"Не удалось отметить экспертизу как удаленную: {e}")

    tk.Button(functions_window, text="Экспорт материалов", command=export_materials).pack(padx=20, pady=10)
    tk.Button(functions_window, text="Экспорт повреждений", command=export_damages).pack(padx=20, pady=10)
    tk.Button(functions_window, text="Экспорт стоимости работ", command=export_work_costs).pack(padx=20, pady=10)
    tk.Button(functions_window, text="Экспорт стоимости материалов", command=export_material_costs).pack(padx=20, pady=10)
    tk.Button(functions_window, text="Удалить экспертизу", command=delete_inspection).pack(padx=20, pady=10)


# Создаем основное окно
root = tk.Tk()
root.title("Управление экспертизами")

# Подключаемся к базе данных
conn = connect_to_db()
if conn is None:
    root.destroy()  # Закрываем приложение, если не удалось подключиться к базе данных

# Добавляем заголовок
title_label = tk.Label(root, text="Управление экспертизами", font=("Helvetica", 16))
title_label.pack(pady=10)

# Добавляем кнопки
add_button = tk.Button(root, text="Добавить новую экспертизу", command=add_new_inspection, width=30)
add_button.pack(pady=10)

search_button = tk.Button(root, text="Поиск среди существующих экспертиз", command=search_existing_inspections,
                          width=30)
search_button.pack(pady=10)

# Запускаем основной цикл
root.mainloop()

# Закрываем соединение с базой данных при завершении работы программы
if conn:
    conn.close()
