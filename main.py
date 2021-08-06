import requests
import math
from tabulate import tabulate
from html.parser import HTMLParser


class RatingParser(HTMLParser):
    def __init__(self, html_table_class, column_names):
        super().__init__()
        self.html_table_class = html_table_class
        self.column_names = column_names
        self.in_table = False
        self.in_body = False
        self.in_td = False
        self.current_column = 0
        self.current_row = 0
        self.abiturients = []

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            for attr in attrs:
                name, value = attr
                if name == "class" and self.html_table_class in value:
                    self.in_table = True
        elif tag == "tbody" and self.in_table:
            self.in_body = True
        elif tag == "td" and self.in_body:
            self.in_td = True
            self.current_column += 1
        elif tag == "tr" and self.in_body:
            self.abiturients.append({})
            self.current_row += 1
            self.current_column = 0

    def handle_endtag(self, tag):
        if tag == "table":
            self.in_table = False
        elif tag == "tbody":
            self.in_body = False
        elif tag == "td":
            self.in_td = False

    def handle_data(self, data):
        if self.in_td and data.isprintable():
            if self.current_column in self.column_names:
                column_name = self.column_names[self.current_column]
                if column_name == "agreement":
                    data_lower = data.lower()
                    if "да" in data_lower and data_lower != "да":
                        data = "Да"
                elif column_name == "position" or column_name == "exam_result":
                    data = int(data)
                self.abiturients[self.current_row - 1][column_name] = data

    def get_abiturients(self):
        return self.abiturients[:]


def get_decimal_input(prompt, min, max, allow_blank=False):
    while True:
        value = input(prompt)
        if not value and allow_blank:
            return None
        if value.isdecimal():
            value = int(value)
            if min <= value <= max:
                return value


def print_abiturients(abiturients):
    print(abiturients)
    headers = ["МЕСТО", "БАЛЛЫ", "ОСНОВАНИЕ ПРИЕМА", "СОГЛАСИЕ"]
    table = []
    for abit in abiturients:
        position = abit["position"]
        result = abit["exam_result"]
        basis = abit.get("basis", 'Б')
        agreement = abit.get("agreement", "Нет")
        table.append([position, result, basis, agreement])
    print(tabulate(table, headers, tablefmt="fancy_grid"))


def analyze_abiturients(abiturients, cur_position):
    agreements_yes = 0
    agreements_no = 0
    agreements_other = 0
    for abit in abiturients:
        if cur_position != 1 and abit["position"] == cur_position:
            print("Над вами:")
            print(f"\tС согласием: {agreements_yes}")
            print(f"\tБез согласия: {agreements_no}")
            print(f"\tС согласием на другое направление: {agreements_other}")
        agreement = abit.get("agreement", "нет").lower()
        basis = abit.get("basis")
        if agreement == "да":
            agreements_yes += 1
        elif agreement == "нет":
            if basis:
                agreements_other += 1
            else:
                agreements_no += 1
        else:
            agreements_other += 1
    print()
    print(f"Всего абитуриентов: {len(abiturients)}")
    print(f"Всего абитуриентов с согласием: {agreements_yes}")
    print(f"Всего абитуриентов без согласия: {agreements_no}")
    print(f"Всего абитуриентов с согласием на другое направление: {agreements_other}")


universities = [
    {
        "name": "СПБгМТУ",
        "html_table_class": "table",
        "faculties":
        [
            {
                "name": "Информатика и вычислительная техника",
                "url": "https://abit.smtu.ru/viewrait/2/1/1/2/1/1/",
                "column_names": {1: "position", 8: "exam_result", 9: "basis", 11: "agreement"},
                "budget_places": 75
            },
            {
                "name": "Информационная безопасность",
                "url": "https://abit.smtu.ru/viewrait/3/1/1/2/1/1/",
                "column_names": {1: "position", 9: "exam_result", 10: "basis", 12: "agreement"},
                "budget_places": 33
            }
        ]
    },
    {
        "name": "НГТУ им. Алексеева",
        "html_table_class": "rating_fac",
        "faculties":
        [
            {
                "name": "Информатика и вычислительная техника",
                "url": "https://abit.nntu.ru/info/bak/konkurs/?learn_form_id=0&fac_id=281474976714124&specialization=&spec_id=281474976710932&commerce=1",
                "column_names": {1: "position", 3: "exam_result", 6: "basis", 7: "agreement"},
                "budget_places": 81
            },
            {
                "name": "Информационные системы и технологии",
                "url": "https://abit.nntu.ru/info/bak/konkurs/?learn_form_id=0&fac_id=281474976714124&specialization=&spec_id=281474976710935&commerce=1",
                "column_names": {1: "position", 3: "exam_result", 6: "basis", 7: "agreement"},
                "budget_places": 105
            }
        ]
    }
]

actions = [
    {
        "name": "Вывести список",
        "func": print_abiturients
    },
    {
        "name": "Анализ списка",
        "func": analyze_abiturients
    }
]


if __name__ == "__main__":
    print("Куда поступать:")
    for i in range(len(universities)):
        print(f"\t{i+1}. {universities[i]['name']}")
    print()
    university_id = get_decimal_input("Выберите один из перечисленных выше ВУЗ'ов (по номеру): ", 1, len(universities))
    university_id -= 1
    print()
    print("Какой факультет:")
    faculties = universities[university_id]["faculties"]
    for i in range(len(faculties)):
        print(f"\t{i+1}. {faculties[i]['name']}")
    print()
    faculty_id = get_decimal_input("Выберите один из перечисленных выше факультетов (по номеру): ", 1, len(faculties))
    faculty_id -= 1
    print()
    print("Выберите действие:")
    for i in range(len(actions)):
        print(f"\t{i+1}. {actions[i]['name']}")
    print()
    action_id = get_decimal_input("Выберите одно из перечисленных выше действий (по номеру): ", 1, len(actions))
    action_id -= 1
    print()
    if action_id == 0:
        abiturients_amount = get_decimal_input("Какое количество абитуриентов вывести (нажмите Enter, чтобы вывести всех): ", 0, math.inf, True)
    elif action_id == 1:
        my_position = get_decimal_input("Введите ваше текущее место в списках: ", 1, math.inf)
    print('-' * 50)
    print(f"Бюджетных мест: {faculties[faculty_id]['budget_places']}")

    university = universities[university_id]
    parser = RatingParser(university["html_table_class"], faculties[faculty_id]["column_names"])
    r = requests.get(faculties[faculty_id]["url"])
    parser.feed(r.text)

    action_func = actions[action_id]["func"]
    abiturients = parser.get_abiturients()
    if action_id == 0:
        print()
        action_func(abiturients if abiturients_amount is None else abiturients[:abiturients_amount])
    elif action_id == 1:
        action_func(abiturients, my_position)
