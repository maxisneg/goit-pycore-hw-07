from collections import UserDict
from datetime import datetime, timedelta

class Field:
    def __init__(self, value):
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        if not self.is_valid(new_value):
            error_message = getattr(self, 'validation_error_message', "Неваліднe значення")
            raise ValueError(f"{error_message}: '{new_value}'")
        self._value = new_value

    def is_valid(self, value):
        return bool(value)

    def __str__(self):
        return str(self._value)

    def __repr__(self):
        return f"{self.__class__.__name__}('{self._value}')"

    def __eq__(self, other):
        if isinstance(other, Field):
            return self.value == other.value
        return NotImplemented

    def __hash__(self):
        return hash(self.value)

class Name(Field):
    validation_error_message = "Ім'я не може бути порожнім"
    pass

class Phone(Field):
    validation_error_message = "Телефон має містити 10 цифр"
    def is_valid(self, value):
        return isinstance(value, str) and value.isdigit() and len(value) == 10

class Birthday(Field):
    validation_error_message = "Невірний формат дати. Використовуйте DD.MM.YYYY"

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        if isinstance(new_value, datetime):
             self._value = new_value
             return

        if not self.is_valid(new_value):
             raise ValueError(f"{self.validation_error_message}: '{new_value}'")

        try:
             self._value = datetime.strptime(new_value, '%d.%m.%Y')
        except (ValueError, TypeError):
             raise ValueError(f"{self.validation_error_message}: '{new_value}'")

    def is_valid(self, value):
         if not isinstance(value, str):
              return False
         try:
              datetime.strptime(value, '%d.%m.%Y')
              return True
         except (ValueError, TypeError):
              return False

    def __str__(self):
        return self._value.strftime('%d.%m.%Y') if hasattr(self, '_value') and self._value else "Не вказано"


class Record:
    def __init__(self, name_str: str):
        self.name = Name(name_str)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number_str: str):
        try:
            phone = Phone(phone_number_str)
            if phone.value not in [p.value for p in self.phones]:
                self.phones.append(phone)
                return True
            return False # Телефон вже існує
        except ValueError as e:
             # Повертаємо помилку для обробки вище
             raise ValueError(f"Не вдалося додати телефон {phone_number_str}: {e}")

    def remove_phone(self, phone_number_str: str):
        phone_to_remove = self.find_phone(phone_number_str)
        if phone_to_remove:
            self.phones.remove(phone_to_remove)
        else:
             raise ValueError(f"Телефон {phone_number_str} не знайдено для видалення.")

    def edit_phone(self, old_phone_number_str: str, new_phone_number_str: str):
        phone_to_edit = self.find_phone(old_phone_number_str)
        if not phone_to_edit:
             raise ValueError(f"Старий телефон {old_phone_number_str} не знайдено.")

        try:
            new_phone_temp = Phone(new_phone_number_str)
            if new_phone_temp.value != old_phone_number_str and new_phone_temp.value in [p.value for p in self.phones]:
                  raise ValueError(f"Новий номер {new_phone_temp.value} вже є у списку.")

            phone_to_edit.value = new_phone_number_str
        except ValueError as e:
             raise ValueError(f"Не вдалося змінити телефон: {e}")


    def find_phone(self, phone_number_str: str) -> Phone | None:
        for phone in self.phones:
            if phone.value == phone_number_str:
                return phone
        return None

    def add_birthday(self, birthday_str: str):
        try:
            # Створюємо об'єкт Birthday - валідація відбудеться автоматично
            new_birthday = Birthday(birthday_str)
            self.birthday = new_birthday
        except ValueError as e:
             raise ValueError(f"Не вдалося встановити день народження: {e}")

    def __str__(self):
        phones_str = '; '.join(p.value for p in self.phones) if self.phones else "Немає телефонів"
        birthday_str = f", День народження: {self.birthday}" if self.birthday else ""
        return f"Контакт: {self.name.value}, Телефони: {phones_str}{birthday_str}"

    def __repr__(self):
         return f"Record(name='{self.name.value}', phones={self.phones}, birthday={self.birthday})"


class AddressBook(UserDict):
    def add_record(self, record: Record):
        if not isinstance(record, Record):
            raise TypeError("Можна додавати лише об'єкти Record.")
        if record.name.value in self.data:
             print(f"Увага: Контакт {record.name.value} вже існує. Дані може бути оновлено.")
        self.data[record.name.value] = record

    def find(self, name_str: str) -> Record | None:
        return self.data.get(name_str)

    def delete(self, name_str: str):
        if name_str in self.data:
            del self.data[name_str]
        else:
             raise KeyError(f"Контакт '{name_str}' не знайдено для видалення.")

    def get_upcoming_birthdays(self) -> list:
        today = datetime.today().date()
        upcoming_birthdays = []
        days_in_advance = 7 # Дні наперед для перевірки

        for record in self.data.values():
            if record.birthday and record.birthday.value:
                bday_date = record.birthday.value.date()
                birthday_this_year = bday_date.replace(year=today.year)

                if birthday_this_year < today:
                    birthday_this_year = bday_date.replace(year=today.year + 1)

                delta_days = (birthday_this_year - today).days

                if 0 <= delta_days < days_in_advance:
                    # Визначаємо день тижня дня народження
                    bday_weekday = birthday_this_year.weekday() # 0 = Пн, 6 = Нд

                    # Визначаємо день привітання (перенос з вихідних на понеділок)
                    congrats_date = birthday_this_year
                    if bday_weekday == 5: # Субота
                        congrats_date = birthday_this_year + timedelta(days=2)
                    elif bday_weekday == 6: # Неділя
                        congrats_date = birthday_this_year + timedelta(days=1)

                    congrats_weekday_name = congrats_date.strftime('%A') # Назва дня тижня

                    upcoming_birthdays.append({
                        "name": record.name.value,
                        "congratulation_date_str": congrats_date.strftime('%d.%m.%Y'),
                        "congratulation_weekday": congrats_weekday_name
                    })

        # Групуємо за днем тижня для виводу
        grouped_birthdays = {}
        for item in upcoming_birthdays:
            day_name = item['congratulation_weekday']
            if day_name not in grouped_birthdays:
                grouped_birthdays[day_name] = []
            grouped_birthdays[day_name].append(item['name'])

        # Формуємо фінальний список рядків для виводу
        output_list = []
        # Виводимо по днях тижня, починаючи з понеділка (якщо є)
        week_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"] # "Saturday", "Sunday" не потрібні через перенос
        for day in week_order:
             if day in grouped_birthdays:
                   output_list.append(f"{day}: {', '.join(grouped_birthdays[day])}")

        return output_list


    def __str__(self):
        if not self.data:
            return "Ваша адресна книга ще порожня."
        return "\n".join(str(record) for record in self.data.values())


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return f"Помилка! {e}"
        except KeyError as e:
            return f"На жаль, контакт '{e}' не знайдено."
        except IndexError:
            return "Помилка: Недостатньо аргументів для команди."
        except TypeError as e:
             return f"Помилка типу даних: {e}"
        except Exception as e:
             return f"Сталася несподівана помилка: {e}"
    return inner


def parse_input(user_input):
    parts = user_input.split()
    command = parts[0].strip().lower()
    args = parts[1:]
    return command, args


@input_error
def add_contact(args, book: AddressBook):
    if len(args) != 2:
        raise ValueError("Потрібно вказати ім'я та телефон (10 цифр).")
    name, phone_str = args
    record = book.find(name)
    message = f"Телефон {phone_str} оновлено для контакту {name}."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = f"Контакт {name} успішно додано."
    # Додаємо телефон. Якщо він невалідний або вже існує, метод record.add_phone обробить це.
    if record.add_phone(phone_str):
         # Якщо телефон було успішно додано (не дублікат)
         if "додано" in message: # Якщо це був новий контакт
              message += f" з телефоном {phone_str}."
         else: # Якщо контакт оновлювався
              message = f"До контакту {name} додано новий телефон {phone_str}."
    else: # Якщо телефон не було додано (дублікат)
        if "додано" in message: # Новий контакт, але телефон - дублікат (малоймовірно тут)
             pass # Повідомлення "Контакт додано" достатньо
        else: # Існуючий контакт, і телефон - дублікат
             message = f"Телефон {phone_str} вже існує для контакту {name}."

    return message


@input_error
def change_contact(args, book: AddressBook):
    if len(args) != 3:
        raise ValueError("Вкажіть ім'я, старий телефон та новий телефон.")
    name, old_phone, new_phone = args
    record = book.find(name)
    if record is None:
        raise KeyError(name)
    record.edit_phone(old_phone, new_phone)
    return f"Телефон для {name} успішно змінено з {old_phone} на {new_phone}."


@input_error
def show_phone(args, book: AddressBook):
    if len(args) != 1:
        raise ValueError("Потрібно вказати ім'я контакту.")
    name = args[0]
    record = book.find(name)
    if record is None:
        raise KeyError(name)
    if not record.phones:
        return f"У контакту {name} немає збережених телефонів."
    phone_list = ', '.join(p.value for p in record.phones)
    return f"Телефони контакту {name}: {phone_list}"


@input_error
def show_all(book: AddressBook):
    if not book.data:
        return "Адресна книга порожня."
    # Використовуємо __str__ для AddressBook, який вже форматує вивід
    return str(book)


@input_error
def add_birthday(args, book: AddressBook):
    if len(args) != 2:
        raise ValueError("Вкажіть ім'я та день народження у форматі DD.MM.YYYY.")
    name, birthday_str = args
    record = book.find(name)
    if record is None:
        raise KeyError(name)
    record.add_birthday(birthday_str)
    return f"День народження {birthday_str} додано для контакту {name}."


@input_error
def show_birthday(args, book: AddressBook):
    if len(args) != 1:
        raise ValueError("Вкажіть ім'я контакту.")
    name = args[0]
    record = book.find(name)
    if record is None:
        raise KeyError(name)
    if record.birthday is None:
        return f"У контакту {name} не вказано день народження."
    return f"День народження {name}: {record.birthday}" # Використовуємо __str__ для Birthday


@input_error
def birthdays(args, book: AddressBook):
    # Перевіряємо, чи не передано зайвих аргументів
    if args:
        raise ValueError("Команда 'birthdays' не приймає аргументів.")

    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        # Отримуємо поточний день тижня
        today_weekday = datetime.today().strftime('%A')
        # Визначаємо наступний понеділок
        days_until_monday = (7 - datetime.today().weekday()) % 7
        next_monday_date = (datetime.today() + timedelta(days=days_until_monday)).strftime('%d.%m.%Y')

        # Спеціальне повідомлення, якщо сьогодні понеділок і немає ДН на тиждень вперед
        if datetime.today().weekday() == 0:
             message = "Цього тижня (до наступного понеділка) днів народження немає."
        else:
             message = f"На наступному тижні (з {next_monday_date}) днів народження немає."

        return message

    result = "Наступні дні народження (привітання на робочий день):\n"
    result += "\n".join(upcoming)
    return result


def main():
    # Створення об'єкту книги при старті
    книга_контактів = AddressBook()
    print("Ласкаво просимо до бота-помічника!")

    while True:
        try:
            user_input = input("Введіть команду: ")
            # Перевірка на порожнє введення
            if not user_input.strip():
                continue
            command, args = parse_input(user_input)

            if command in ["close", "exit", "quit"]:
                print("До побачення! Гарного дня!")
                break

            elif command == "hello":
                print("Привіт! Чим можу допомогти?")

            elif command == "add":
                print(add_contact(args, книга_контактів))

            elif command == "change":
                 print(change_contact(args, книга_контактів))

            elif command == "phone":
                 print(show_phone(args, книга_контактів))

            elif command == "all":
                print("--- Всі контакти ---")
                print(show_all(книга_контактів))
                print("--------------------")

            elif command == "add-birthday":
                print(add_birthday(args, книга_контактів))

            elif command == "show-birthday":
                print(show_birthday(args, книга_контактів))

            elif command == "birthdays":
                print(birthdays(args, книга_контактів))

            else:
                print("Невідома команда. Спробуйте: hello, add, change, phone, all, add-birthday, show-birthday, birthdays, close, exit")

        except Exception as e:
            # Додатковий загальний перехват помилок на рівні циклу
            print(f"Сталася критична помилка: {e}. Спробуйте ще раз.")


# Запуск головної функції, якщо файл виконується як скрипт
if __name__ == "__main__":
    main()