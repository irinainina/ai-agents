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
        "Я дизайнер. В чём ваша уникальность?",
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
        "Я дизайнер. У чому ваша унікальність?",
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
        "I'm a designer. What makes you unique?",
        "I am a developer. What modern technologies do you use?",
        "I'm a potential client. Why should I pay attention to you?",
      ],
      placeholder: "Are you a client, designer or developer? That way I can respond based on your interests...",
      image: "/1.jpg",
    },
  },

  project: {
    ru: {
      title: "Project Agent",
      description: "Я ваш личный гид по проектам Halo Lab.",
      examplesTitle: "Примеры вопросов, на которые я могу ответить:",
      examples: [
        "Я дизайнер, хочу увидеть интересные UI-решения",
        "Покажите проект с редизайном старого сайта",
        "Делали ли вы лендинг для SaaS-продукта?",
      ],
      placeholder: "Опишите какие проекты вас интересуют — я подберу похожие проекты...",
      image: "/4.jpg",
    },
    uk: {
      title: "Project Agent",
      description: "Я ваш особистий гід про проєкти Halo Lab.",
      examplesTitle: "Приклади запитань, на які я можу відповісти:",
      examples: [
        "Я дизайнер, хочу побачити цікаві UI-рішення",
        "Покажіть проєкт із редизайном старого сайту",
        "Чи робили ви лендинг для SaaS-продукту?",
      ],
      placeholder: "Опишіть, які проєкти вас цікавлять — я підберу схожі...",
      image: "/4.jpg",
    },
    en: {
      title: "Project Agent",
      description: "I'm your personal guide to Halo Lab's projects.",
      examplesTitle: "Examples of questions I can answer:",
      examples: [
        "I'm a designer, I want to see interesting UI solutions",
        "Show me a project with a redesign of an old site",
        "Have you made a landing page for a SaaS product?",
      ],
      placeholder: "Describe what projects you’re interested in — I’ll find similar ones...",
      image: "/4.jpg",
    },
  },

  copywriter: {
    ru: {
      title: "Copywriter Agent",
      description:
        "Я создаю контент для сайтов и соцсетей. Укажите тему статьи, я предложу вариант, который будет говорить с аудиторией на ее языке.",
      examplesTitle: "Примеры тем статей:",
      examples: ["5 причин обновить сайт", "Будущее дизайна в эпоху AI", "Почему плохой UX убивает конверсию."],
      placeholder: "Напишите тему статьи — я подготовлю текст, который раскроет её...",
      image: "/3.jpg",
    },
    uk: {
      title: "Copywriter Agent",
      description:
        "Я створюю контент для сайтів та соцмереж. Вкажіть тему статті, я запропоную варіант, який говоритиме з аудиторією її мовою.",
      examplesTitle: "Приклади тем статей:",
      examples: ["5 причин оновити сайт", "Майбутнє дизайну в епоху AI", "Чому поганий UX вбиває конверсію."],
      placeholder: "Напишіть тему статті — я підготую текст, який розкриє її...",
      image: "/3.jpg",
    },
    en: {
      title: "Copywriter Agent",
      description:
        "I create content for websites and social networks. Specify the topic of the article, I will offer an option that will speak to the audience in their language.",
      examplesTitle: "Examples of article topics:",
      examples: [
        "5 Reasons to Update Your Website",
        "The Future of Design in the Age of AI",
        "Why bad UX kills conversion.",
      ],
      placeholder: "Write the topic of the article - I will prepare the text that will reveal it...",
      image: "/3.jpg",
    },
  },
};

export default agentConfig;
