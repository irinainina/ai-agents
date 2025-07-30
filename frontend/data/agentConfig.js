const agentConfig = {
  research: {
    ru: {
      title: "Research Agent",
      description: "Я отвечаю на вопросы про технологии, тренды и подходы в веб-разработке",
      examplesTitle: "Примеры вопросов, на которые я могу ответить:",
      examples: [
        "Что такое Jamstack, его преимущества",
        "Какие особенности Tailwind?",
        "Расскажи о трендах веб-дизайна.",
      ],
      placeholder: "Задайте вопрос по разработке или технологиям...",
      image: "/2.jpg",
    },
    uk: {
      title: "Research Agent",
      description: "Я відповідаю на запитання про технології, тренди та підходи у веброзробці",
      examplesTitle: "Приклади запитань, на які я можу відповісти:",
      examples: [
        "Розкажи що таке Jamstack та якi його переваги?",
        "Які особливості Tailwind?",
        "Розкажи про напрямки веб дизайну",
      ],
      placeholder: "Поставте запитання про розробку чи технології...",
      image: "/2.jpg",
    },
    en: {
      title: "Research Agent",
      description: "I answer questions about technologies, trends, and web development approaches",
      examplesTitle: "Examples of questions I can answer:",
      examples: [
        "What is Jamstack and its benefits?",
        "What are Tailwind's features?",
        "Tell me about web design trends.",
      ],
      placeholder: "Ask a question about development or technologies...",
      image: "/2.jpg",
    },
  },

  welcome: {
    ru: {
      title: "Welcome Agent",
      description: "Я могу рассказать о Halo Lab с учётом ваших интересов.",
      examplesTitle: "Примеры вопросов, на которые я могу ответить:",
      examples: [
        "Я дизайнер. Как устроен ваш дизайн-процесс?",
        "Я разработчик. Какие современные технологии вы используете?",
        "Я потенциальный клиент. Почему мне стоит обратить на вас внимание?",
      ],
      placeholder: "Вы клиент , дизайнер или разработчик? Так я смогу ответить учитывая ваши интересы...",
      image: "/1.jpg",
    },
    uk: {
      title: "Welcome Agent",
      description: "Я можу розповісти про Halo Lab з урахуванням ваших інтересів.",
      examplesTitle: "Приклади запитань, на які я можу відповісти:",
      examples: [
        "Я дизайнер. Як влаштований ваш дизайн-процес?",
        "Я розробник. Які сучасні технології ви використовуєте?",
        "Я потенційний клієнт. Чому мені варто звернути на вас увагу?",
      ],
      placeholder: "Ви клієнт, дизайнер чи розробник? Так я зможу відповісти з урахуванням ваших інтересів...",
      image: "/1.jpg",
    },
    en: {
      title: "Welcome Agent",
      description: "I can tell you about Halo Lab based on your interests.",
      examplesTitle: "Examples of questions I can answer:",
      examples: [
        "I'm a designer. How does your design process work?",
        "I am a developer. What modern technologies do you use?",
        "I'm a potential client. Why should I pay attention to you?",
      ],
      placeholder: "Are you a client, designer or developer? That way I can respond based on your interests...",
      image: "/1.jpg",
    },
  },

  copywriter: {
    ru: {
      title: "Copywriter Agent",
      description:
        "Я создаю контент для сайтов, соцсетей, презентаций. Назовите тему или цель, я предложу варианты, которые говорят с аудиторией на ее языке.",
      examplesTitle: "Примеры вопросов, на которые я могу ответить:",
      examples: [
        "Статья: 5 причин обновить сайт",
        "Нужен пост в LinkedIn на тему `Будущее дизайна в эпоху AI`",
        "Напиши статью о том, как плохой UX убивает конверсию.",
      ],
      placeholder: "Опишите тему, формат и задачу — я подготовлю текст, который решит её...",
      image: "/3.jpg",
    },
    uk: {
      title: "Copywriter Agent",
      description:
        "Я створюю контент для сайтів, соцмереж, презентацій. Назвіть тему або мету — я запропоную варіанти, які говоритимуть мовою аудиторії.",
      examplesTitle: "Приклади запитань, на які я можу відповісти:",
      examples: [
        "Стаття: 5 причин оновити сайт",
        "Потрібен пост у LinkedIn на тему `Майбутнє дизайну в епоху AI`",
        "Напиши статтю про те, як поганий UX вбиває конверсію.",
      ],
      placeholder: "Опишіть тему, формат і задачу — я підготую текст, що її вирішить...",
      image: "/3.jpg",
    },
    en: {
      title: "Copywriter Agent",
      description:
        "I create content for websites, social media, and presentations. Give me a topic or goal, and I’ll offer ideas that speak your audience’s language.",
      examplesTitle: "Examples of questions I can answer:",
      examples: [
        "Article: 5 reasons to update your site",
        "Need a LinkedIn post on `The future of design in the AI era`",
        "Write an article on how bad UX kills conversion.",
      ],
      placeholder: "Describe the topic, format, and goal — I’ll prepare a text that gets it done...",
      image: "/3.jpg",
    },
  },
};

export default agentConfig;
