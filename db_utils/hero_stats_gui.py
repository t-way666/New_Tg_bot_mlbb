import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import sys
import os
from hero_calculator import calculate_hero_stats

class HeroStatsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Калькулятор характеристик героев MLBB")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Получение списка героев из базы данных
        self.heroes = self.get_heroes_list()
        
        # Создание фреймов
        self.create_frames()
        
        # Создание элементов управления
        self.create_widgets()
        
        # Инициализация данных
        self.hero_stats = {}
        self.comparison_heroes = []
        
    def get_heroes_list(self):
        """Получает список героев из базы данных"""
        try:
            conn = sqlite3.connect('../db/characters.db')
            cursor = conn.cursor()
            cursor.execute("SELECT имя FROM hero_names ORDER BY имя")
            heroes = [row[0] for row in cursor.fetchall()]
            conn.close()
            return heroes
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка базы данных", f"Не удалось получить список героев: {e}")
            return []
    
    def create_frames(self):
        """Создает фреймы для размещения элементов"""
        # Фрейм для выбора героя
        self.selection_frame = ttk.LabelFrame(self.root, text="Выбор героя")
        self.selection_frame.pack(fill="x", padx=10, pady=5)
        
        # Фрейм для отображения характеристик
        self.stats_frame = ttk.LabelFrame(self.root, text="Характеристики героя")
        self.stats_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Фрейм для сравнения героев
        self.comparison_frame = ttk.LabelFrame(self.root, text="Сравнение героев")
        self.comparison_frame.pack(fill="x", padx=10, pady=5)
    
    def create_widgets(self):
        """Создает элементы управления"""
        # Элементы для выбора героя
        ttk.Label(self.selection_frame, text="Герой:").grid(row=0, column=0, padx=5, pady=5)
        self.hero_combobox = ttk.Combobox(self.selection_frame, values=self.heroes, width=20)
        self.hero_combobox.grid(row=0, column=1, padx=5, pady=5)
        self.hero_combobox.bind("<<ComboboxSelected>>", self.on_hero_selected)
        
        ttk.Label(self.selection_frame, text="Уровень:").grid(row=0, column=2, padx=5, pady=5)
        self.level_var = tk.StringVar(value="1")
        self.level_spinbox = ttk.Spinbox(self.selection_frame, from_=1, to=15, textvariable=self.level_var, width=5)
        self.level_spinbox.grid(row=0, column=3, padx=5, pady=5)
        self.level_var.trace_add("write", self.on_level_changed)
        
        ttk.Button(self.selection_frame, text="Рассчитать", command=self.calculate_stats).grid(row=0, column=4, padx=5, pady=5)
        
        # Создание текстового поля для отображения характеристик
        self.stats_text = tk.Text(self.stats_frame, wrap="word", width=80, height=20)
        self.stats_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Элементы для сравнения героев
        ttk.Label(self.comparison_frame, text="Добавить героя для сравнения:").grid(row=0, column=0, padx=5, pady=5)
        self.compare_hero_combobox = ttk.Combobox(self.comparison_frame, values=self.heroes, width=20)
        self.compare_hero_combobox.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(self.comparison_frame, text="Уровень:").grid(row=0, column=2, padx=5, pady=5)
        self.compare_level_var = tk.StringVar(value="1")
        self.compare_level_spinbox = ttk.Spinbox(self.comparison_frame, from_=1, to=15, textvariable=self.compare_level_var, width=5)
        self.compare_level_spinbox.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Button(self.comparison_frame, text="Добавить", command=self.add_hero_to_comparison).grid(row=0, column=4, padx=5, pady=5)
        ttk.Button(self.comparison_frame, text="Сравнить", command=self.compare_heroes).grid(row=0, column=5, padx=5, pady=5)
        ttk.Button(self.comparison_frame, text="Очистить", command=self.clear_comparison).grid(row=0, column=6, padx=5, pady=5)
        
        # Список героев для сравнения
        ttk.Label(self.comparison_frame, text="Герои для сравнения:").grid(row=1, column=0, padx=5, pady=5)
        self.comparison_list = tk.Listbox(self.comparison_frame, width=50, height=5)
        self.comparison_list.grid(row=1, column=1, columnspan=6, padx=5, pady=5, sticky="ew")
    
    def on_hero_selected(self, event=None):
        """Обработчик выбора героя"""
        self.calculate_stats()
    
    def on_level_changed(self, *args):
        """Обработчик изменения уровня"""
        try:
            level = int(self.level_var.get())
            if level < 1:
                self.level_var.set("1")
            elif level > 15:
                self.level_var.set("15")
            self.calculate_stats()
        except ValueError:
            pass
    
    def calculate_stats(self):
        """Рассчитывает и отображает характеристики выбранного героя"""
        hero_name = self.hero_combobox.get()
        if not hero_name:
            messagebox.showinfo("Информация", "Выберите героя")
            return
        
        try:
            level = int(self.level_var.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Уровень должен быть числом от 1 до 15")
            return
        
        stats = calculate_hero_stats(hero_name, level)
        if not stats:
            messagebox.showerror("Ошибка", f"Не удалось получить характеристики героя {hero_name}")
            return
        
        self.hero_stats = stats
        self.display_hero_stats(stats)
    
    def display_hero_stats(self, stats):
        """Отображает характеристики героя в текстовом поле"""
        self.stats_text.delete(1.0, tk.END)
        
        self.stats_text.insert(tk.END, f"Характеристики героя {stats['имя']} на уровне {stats['уровень']}:\n\n")
        
        # Группировка характеристик по категориям
        categories = {
            'Здоровье и мана': ['ОЗ', 'реген_ОЗ', 'мана/энергия', 'реген_маны/энергии'],
            'Атака и защита': ['физ_атака', 'физ_защита', 'маг_защита', 'маг_сила'],
            'Скорость': ['скорость_атаки', 'коэффициент_скорости_атаки_%', 'скорость_передвижения'],
            'Дальность атаки': ['мин._дальность_базовой_атаки', 'макс._дальность_базовой_атаки'],
            'Критический урон': ['шанс_крита', 'крит_урон'],
            'Проникновение': ['физ_проникновение', 'маг_проникновение', 'сокращение_перезарядки'],
            'Вампиризм': ['вампиризм', 'вампиризм_навыков'],
            'Защитные характеристики': ['устойчивость', 'уменьшение_крит_урона'],
            'Лечение': ['эффект_лечения', 'полученное_лечение']
        }
        
        for category, attrs in categories.items():
            self.stats_text.insert(tk.END, f"\n{category}:\n")
            for attr in attrs:
                if attr in stats:
                    self.stats_text.insert(tk.END, f"  {attr}: {stats[attr]}\n")
    
    def add_hero_to_comparison(self):
        """Добавляет героя в список для сравнения"""
        hero_name = self.compare_hero_combobox.get()
        if not hero_name:
            messagebox.showinfo("Информация", "Выберите героя для сравнения")
            return
        
        try:
            level = int(self.compare_level_var.get())
            if level < 1 or level > 15:
                messagebox.showerror("Ошибка", "Уровень должен быть от 1 до 15")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Уровень должен быть числом от 1 до 15")
            return
        
        # Проверяем, есть ли уже такой герой в списке
        for hero, lvl in self.comparison_heroes:
            if hero == hero_name and lvl == level:
                messagebox.showinfo("Информация", f"Герой {hero_name} (уровень {level}) уже добавлен в список")
                return
        
        self.comparison_heroes.append((hero_name, level))
        self.comparison_list.insert(tk.END, f"{hero_name} (уровень {level})")
    
    def clear_comparison(self):
        """Очищает список героев для сравнения"""
        self.comparison_heroes = []
        self.comparison_list.delete(0, tk.END)
    
    def compare_heroes(self):
        """Сравнивает выбранных героев"""
        if len(self.comparison_heroes) < 1:
            messagebox.showinfo("Информация", "Добавьте хотя бы одного героя для сравнения")
            return
        
        # Добавляем текущего героя, если он выбран
        current_hero = self.hero_combobox.get()
        if current_hero and self.hero_stats:
            # Проверяем, есть ли уже такой герой в списке
            current_level = self.hero_stats['уровень']
            current_hero_in_list = False
            for hero, lvl in self.comparison_heroes:
                if hero == current_hero and lvl == current_level:
                    current_hero_in_list = True
                    break
            
            if not current_hero_in_list:
                self.comparison_heroes.insert(0, (current_hero, current_level))
        
        if len(self.comparison_heroes) < 2:
            messagebox.showinfo("Информация", "Для сравнения нужно как минимум два героя")
            return
        
        # Получаем характеристики всех героев
        heroes_data = []
        for hero_name, level in self.comparison_heroes:
            stats = calculate_hero_stats(hero_name, level)
            if stats:
                heroes_data.append((hero_name, level, stats))
        
        if len(heroes_data) < 2:
            messagebox.showerror("Ошибка", "Не удалось получить характеристики героев для сравнения")
            return
        
        self.display_hero_comparison(heroes_data)
    
    def display_hero_comparison(self, heroes_data):
        """Отображает сравнение характеристик героев"""
        self.stats_text.delete(1.0, tk.END)
        
        # Вывод заголовка
        header = "Характеристика"
        for hero_name, hero_level, _ in heroes_data:
            header += f" | {hero_name} (ур.{hero_level})"
        self.stats_text.insert(tk.END, f"{header}\n")
        self.stats_text.insert(tk.END, "-" * len(header) + "\n")
        
        # Группировка характеристик по категориям
        categories = {
            'Здоровье и мана': ['ОЗ', 'реген_ОЗ', 'мана/энергия', 'реген_маны/энергии'],
            'Атака и защита': ['физ_атака', 'физ_защита', 'маг_защита', 'маг_сила'],
            'Скорость': ['скорость_атаки', 'коэффициент_скорости_атаки_%', 'скорость_передвижения'],
            'Дальность атаки': ['мин._дальность_базовой_атаки', 'макс._дальность_базовой_атаки'],
            'Критический урон': ['шанс_крита', 'крит_урон'],
            'Проникновение': ['физ_проникновение', 'маг_проникновение', 'сокращение_перезарядки'],
            'Вампиризм': ['вампиризм', 'вампиризм_навыков'],
            'Защитные характеристики': ['устойчивость', 'уменьшение_крит_урона'],
            'Лечение': ['эффект_лечения', 'полученное_лечение']
        }
        
        for category, attrs in categories.items():
            self.stats_text.insert(tk.END, f"\n{category}:\n")
            for attr in attrs:
                row = f"{attr}"
                for _, _, stats in heroes_data:
                    if attr in stats:
                        row += f" | {stats[attr]}"
                    else:
                        row += " | -"
                self.stats_text.insert(tk.END, row + "\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = HeroStatsApp(root)
    root.mainloop() 