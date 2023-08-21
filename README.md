# Bot_for_teacher
Коммерческий проект.
Суть бота - ученик записывается на урок к преподавателю 
английского языка. Данные ученика сохраняются в базу данных postgresql. 
Ученик может выбрать одно из трех действий: забронировать урок, 
отменить запланированный ранее, и связаться с учителем.



### Запуск задач сельдерея:
1. celery -A teach_bot.utils.tasks:app worker --loglevel=INFO --pool=solo
- запускает worker celery;
2. celery -A teach_bot.utils.tasks flower --loglevel=info
- запускает flower - это для мониторинга выполненных фоновых задач 
  (отправка отчета учителю);
3. celery -A teach_bot.utils.tasks:app beat --loglevel=INFO
- запускает непосредственно таски на выполнение.
