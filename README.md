
# wg_qr_generator

**wg_qr_generator** – это система автоматизации управления WireGuard, включающая генерацию конфигураций, создание QR-кодов, управление пользователями и очистку устаревших данных.

---

## Основные возможности

- **Генерация конфигураций**: Автоматическое создание конфигурационных файлов и QR-кодов для пользователей.
- **Управление сроком действия**: Проверка, продление, сброс срока действия аккаунтов.
- **Удаление устаревших данных**: Автоматическое удаление просроченных аккаунтов, IP-адресов и QR-кодов.
- **Синхронизация конфигураций**: Интеграция с сервером WireGuard.

---

## Установка и запуск

Для установки проекта, настройки окружения и запуска используйте одну строку:

```bash
git clone https://github.com/licht8/wg_qr_generator.git && cd wg_qr_generator && chmod +x run_project.sh && ./run_project.sh
```

### Что делает эта команда:
1. Клонирует репозиторий с проектом.
2. Переходит в директорию проекта.
3. Делает исполняемым Bash-скрипт `run_project.sh`.
4. Запускает скрипт `run_project.sh`, который:
   - Проверяет наличие необходимых инструментов (Git, Python 3.8+).
   - Создает виртуальное окружение и устанавливает зависимости.
   - Предлагает удобное меню для работы с проектом.

---

## Использование меню

После запуска `run_project.sh` вы получите удобное меню:

1. **Запуск тестов**: Проверяет основные модули проекта.
2. **Генерация конфигураций**: Создает новые конфигурации для пользователей.
3. **Выход**: Завершает работу программы.

Пример запуска:
- Для тестов:
  ```
  pytest
  ```
- Для генерации конфигурации:
  ```
  python3 main.py <nickname>
  ```

---

## Структура проекта

- `main.py` – основной скрипт для генерации конфигураций.
- `cleanup.py` – удаление устаревших записей.
- `manage_expiry.py` – управление сроками действия аккаунтов.
- `modules/` – вспомогательные модули (работа с ключами, IP-адресами и QR-кодами).
- `tests/` – тесты для проверки корректности работы модулей.

---

## Тестирование

Запуск тестов через меню или командой:
```bash
pytest
```

---

## Лицензия

Проект распространяется под лицензией [MIT](LICENSE).

---

## Контакты

Если у вас есть вопросы или предложения, свяжитесь с нами через [Issues](https://github.com/licht8/wg_qr_generator/issues).
