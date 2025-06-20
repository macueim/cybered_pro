create table if not exists public.users
(
    id              serial
        primary key,
    email           varchar(255)                                                  not null
        unique,
    first_name      varchar(100)                                                  not null,
    last_name       varchar(100)                                                  not null,
    hashed_password varchar(255)                                                  not null,
    role            varchar(20)              default 'student'::character varying not null,
    is_active       boolean                  default true                         not null,
    created_at      timestamp with time zone default CURRENT_TIMESTAMP,
    updated_at      timestamp with time zone default CURRENT_TIMESTAMP
);


create table if not exists public.courses
(
    id                 serial
        primary key,
    title              varchar(255)                           not null,
    description        text,
    instructor_id      integer                                not null
        references public.users,
    certification_type varchar(100),
    difficulty_level   varchar(20)                            not null,
    estimated_duration integer,
    is_published       boolean                  default false not null,
    created_at         timestamp with time zone default CURRENT_TIMESTAMP,
    updated_at         timestamp with time zone default CURRENT_TIMESTAMP
);

create table if not exists public.modules
(
    id          serial
        primary key,
    course_id   integer      not null
        references public.courses
            on delete cascade,
    title       varchar(255) not null,
    description text,
    order_index integer      not null,
    created_at  timestamp with time zone default CURRENT_TIMESTAMP,
    updated_at  timestamp with time zone default CURRENT_TIMESTAMP
);


create table if not exists public.lessons
(
    id           serial
        primary key,
    module_id    integer      not null
        references public.modules
            on delete cascade,
    title        varchar(255) not null,
    content_type varchar(50)  not null,
    content      text         not null,
    order_index  integer      not null,
    created_at   timestamp with time zone default CURRENT_TIMESTAMP,
    updated_at   timestamp with time zone default CURRENT_TIMESTAMP
);


create table if not exists public.enrollments
(
    id           serial
        primary key,
    user_id      integer                                                      not null
        references public.users,
    course_id    integer                                                      not null
        references public.courses
            on delete cascade,
    status       varchar(20)              default 'active'::character varying not null,
    progress     double precision         default 0.0                         not null,
    enrolled_at  timestamp with time zone default CURRENT_TIMESTAMP,
    completed_at timestamp with time zone,
    constraint unique_user_course
        unique (user_id, course_id)
);



create table if not exists public.assessments
(
    id                 serial
        primary key,
    course_id          integer                                not null
        references public.courses
            on delete cascade,
    module_id          integer
        references public.modules
            on delete cascade,
    title              varchar(255)                           not null,
    description        text,
    time_limit_minutes integer,
    passing_score      double precision         default 70.0  not null,
    is_published       boolean                  default false not null,
    created_at         timestamp with time zone default CURRENT_TIMESTAMP,
    updated_at         timestamp with time zone default CURRENT_TIMESTAMP
);


create table if not exists public.questions
(
    id            serial
        primary key,
    assessment_id integer                              not null
        references public.assessments
            on delete cascade,
    question_text text                                 not null,
    question_type varchar(20)                          not null,
    points        double precision         default 1.0 not null,
    created_at    timestamp with time zone default CURRENT_TIMESTAMP,
    updated_at    timestamp with time zone default CURRENT_TIMESTAMP
);


create table if not exists public.answers
(
    id          serial
        primary key,
    question_id integer                                not null
        references public.questions
            on delete cascade,
    answer_text text                                   not null,
    is_correct  boolean                  default false not null,
    explanation text,
    created_at  timestamp with time zone default CURRENT_TIMESTAMP,
    updated_at  timestamp with time zone default CURRENT_TIMESTAMP
);


create table if not exists public.user_assessments
(
    id            serial
        primary key,
    user_id       integer                                                           not null
        references public.users,
    assessment_id integer                                                           not null
        references public.assessments
            on delete cascade,
    score         double precision,
    start_time    timestamp with time zone default CURRENT_TIMESTAMP,
    end_time      timestamp with time zone,
    status        varchar(20)              default 'in_progress'::character varying not null
);



create table if not exists public.user_answers
(
    id                 serial
        primary key,
    user_assessment_id integer not null
        references public.user_assessments
            on delete cascade,
    question_id        integer not null
        references public.questions
            on delete cascade,
    answer_id          integer
                               references public.answers
                                   on delete set null,
    text_answer        text,
    is_correct         boolean,
    points_earned      double precision
);



create table if not exists public.user_lesson_progress
(
    id            serial
        primary key,
    user_id       integer                                not null
        references public.users,
    lesson_id     integer                                not null
        references public.lessons
            on delete cascade,
    completed     boolean                  default false not null,
    last_accessed timestamp with time zone default CURRENT_TIMESTAMP,
    constraint unique_user_lesson
        unique (user_id, lesson_id)
);


create table if not exists public.user_notes
(
    id         serial
        primary key,
    user_id    integer not null
        references public.users,
    lesson_id  integer not null
        references public.lessons
            on delete cascade,
    content    text    not null,
    created_at timestamp with time zone default CURRENT_TIMESTAMP,
    updated_at timestamp with time zone default CURRENT_TIMESTAMP
);


create table if not exists public.bookmarks
(
    id         serial
        primary key,
    user_id    integer not null
        references public.users,
    lesson_id  integer not null
        references public.lessons
            on delete cascade,
    created_at timestamp with time zone default CURRENT_TIMESTAMP,
    constraint unique_user_bookmark
        unique (user_id, lesson_id)
);



create table if not exists public.forum_topics
(
    id         serial
        primary key,
    course_id  integer      not null
        references public.courses
            on delete cascade,
    title      varchar(255) not null,
    content    text         not null,
    user_id    integer      not null
        references public.users,
    created_at timestamp with time zone default CURRENT_TIMESTAMP,
    updated_at timestamp with time zone default CURRENT_TIMESTAMP
);



create table if not exists public.forum_replies
(
    id         serial
        primary key,
    topic_id   integer not null
        references public.forum_topics
            on delete cascade,
    content    text    not null,
    user_id    integer not null
        references public.users,
    created_at timestamp with time zone default CURRENT_TIMESTAMP,
    updated_at timestamp with time zone default CURRENT_TIMESTAMP
);


create table if not exists public.certifications
(
    id           serial
        primary key,
    name         varchar(100) not null,
    description  text,
    requirements text,
    created_at   timestamp with time zone default CURRENT_TIMESTAMP
);


create table if not exists public.user_certifications
(
    id               serial
        primary key,
    user_id          integer not null
        references public.users,
    certification_id integer not null
        references public.certifications
            on delete cascade,
    issue_date       timestamp with time zone default CURRENT_TIMESTAMP,
    expiry_date      timestamp with time zone,
    certificate_url  varchar(255),
    constraint unique_user_certification
        unique (user_id, certification_id)
);

