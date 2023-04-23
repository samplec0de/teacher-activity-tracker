--
-- PostgreSQL database dump
--

-- Dumped from database version 13.2 (Debian 13.2-1.pgdg100+1)
-- Dumped by pg_dump version 15.2

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

DROP DATABASE IF EXISTS motivation;
--
-- Name: motivation; Type: DATABASE; Schema: -; Owner: postgres
--

CREATE DATABASE motivation WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'en_US.utf8';


ALTER DATABASE motivation OWNER TO postgres;

\connect motivation

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA public;


ALTER SCHEMA public OWNER TO postgres;

--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA public IS 'standard public schema';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: activities; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.activities (
    activity_id integer NOT NULL,
    name text NOT NULL,
    lesson_id integer NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.activities OWNER TO postgres;

--
-- Name: activities_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.activities_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.activities_id_seq OWNER TO postgres;

--
-- Name: activities_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.activities_id_seq OWNED BY public.activities.activity_id;


--
-- Name: activity_records; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.activity_records (
    record_id integer NOT NULL,
    teacher_id integer NOT NULL,
    activity_id integer NOT NULL,
    hours numeric(5,2),
    comment text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.activity_records OWNER TO postgres;

--
-- Name: activity_records_record_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.activity_records_record_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.activity_records_record_id_seq OWNER TO postgres;

--
-- Name: activity_records_record_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.activity_records_record_id_seq OWNED BY public.activity_records.record_id;


--
-- Name: course_join_codes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.course_join_codes (
    code_id character varying(12) NOT NULL,
    course_id integer,
    comment text,
    activated_by_teacher_id integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.course_join_codes OWNER TO postgres;

--
-- Name: courses; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.courses (
    course_id integer NOT NULL,
    name text NOT NULL,
    description text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.courses OWNER TO postgres;

--
-- Name: courses_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.courses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.courses_id_seq OWNER TO postgres;

--
-- Name: courses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.courses_id_seq OWNED BY public.courses.course_id;


--
-- Name: excel_reports; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.excel_reports (
    report_id integer NOT NULL,
    file_data bytea,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.excel_reports OWNER TO postgres;

--
-- Name: excel_reports_report_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.excel_reports_report_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.excel_reports_report_id_seq OWNER TO postgres;

--
-- Name: excel_reports_report_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.excel_reports_report_id_seq OWNED BY public.excel_reports.report_id;


--
-- Name: lessons; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.lessons (
    lesson_id integer NOT NULL,
    date_from timestamp with time zone NOT NULL,
    topic text,
    course_id integer NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    date_to timestamp with time zone
);


ALTER TABLE public.lessons OWNER TO postgres;

--
-- Name: lessons_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.lessons_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.lessons_id_seq OWNER TO postgres;

--
-- Name: lessons_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.lessons_id_seq OWNED BY public.lessons.lesson_id;


--
-- Name: teacher_courses; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.teacher_courses (
    teacher_id integer,
    course_id integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.teacher_courses OWNER TO postgres;

--
-- Name: teachers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.teachers (
    comment text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    teacher_id integer NOT NULL,
    is_manager boolean DEFAULT false
);


ALTER TABLE public.teachers OWNER TO postgres;

--
-- Name: activities activity_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activities ALTER COLUMN activity_id SET DEFAULT nextval('public.activities_id_seq'::regclass);


--
-- Name: activity_records record_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activity_records ALTER COLUMN record_id SET DEFAULT nextval('public.activity_records_record_id_seq'::regclass);


--
-- Name: courses course_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.courses ALTER COLUMN course_id SET DEFAULT nextval('public.courses_id_seq'::regclass);


--
-- Name: excel_reports report_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.excel_reports ALTER COLUMN report_id SET DEFAULT nextval('public.excel_reports_report_id_seq'::regclass);


--
-- Name: lessons lesson_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.lessons ALTER COLUMN lesson_id SET DEFAULT nextval('public.lessons_id_seq'::regclass);


--
-- Data for Name: activities; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (19, 'Подготовка презентации', 26, '2023-04-22 21:12:26.143132');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (20, 'Запись видео', 26, '2023-04-22 21:12:33.026085');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (21, 'Подготовка теста', 26, '2023-04-22 21:12:39.133995');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (22, 'Подготовка презентации', 27, '2023-04-22 21:13:20.29119');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (23, 'Проверка домашнего задания', 27, '2023-04-22 21:13:26.885123');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (24, 'Запись видео', 27, '2023-04-22 21:13:32.697543');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (25, 'Подготовка презентации', 28, '2023-04-22 21:14:05.983043');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (26, 'Запись видео', 28, '2023-04-22 21:14:12.593071');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (27, 'Подготовка презентации', 29, '2023-04-22 21:14:38.79313');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (28, 'Проверка домашнего задания', 29, '2023-04-22 21:14:44.145714');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (29, 'Подготовка теста', 29, '2023-04-22 21:14:51.02215');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (30, 'Подготовка презентации', 30, '2023-04-22 21:15:33.016538');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (31, 'Запись видео', 30, '2023-04-22 21:15:38.492485');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (32, 'Подготовка теста', 30, '2023-04-22 21:15:46.208443');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (33, 'Подготовка презентации', 31, '2023-04-22 21:16:13.930967');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (34, 'Проверка домашнего задания', 31, '2023-04-22 21:16:24.628815');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (35, 'Запись видео', 31, '2023-04-22 21:16:31.844549');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (36, 'Подготовка презентации', 32, '2023-04-22 21:17:13.913118');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (37, 'Запись видео', 32, '2023-04-22 21:17:22.855665');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (38, 'Подготовка презентации', 33, '2023-04-22 21:18:09.117166');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (39, 'Проверка домашнего задания', 33, '2023-04-22 21:18:15.364398');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (40, 'Подготовка теста', 33, '2023-04-22 21:18:20.396001');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (41, 'Подготовка презентации', 34, '2023-04-22 21:18:51.847836');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (42, 'Запись видео', 34, '2023-04-22 21:18:58.358079');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (43, 'Подготовка теста', 34, '2023-04-22 21:19:03.903398');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (44, 'Подготовка презентации', 35, '2023-04-22 21:19:29.759451');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (45, 'Проверка домашнего задания', 35, '2023-04-22 21:19:36.844497');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (49, 'Тест', 37, '2023-04-22 22:22:33.346015');
INSERT INTO public.activities (activity_id, name, lesson_id, created_at) VALUES (46, 'Видео', 35, '2023-04-22 21:19:42.013436');


--
-- Data for Name: activity_records; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.activity_records (record_id, teacher_id, activity_id, hours, comment, created_at) VALUES (9, 131898478, 19, 2.00, '2', '2023-04-22 21:58:18.287134');
INSERT INTO public.activity_records (record_id, teacher_id, activity_id, hours, comment, created_at) VALUES (10, 131898478, 20, 1.00, '1', '2023-04-22 21:58:33.632238');
INSERT INTO public.activity_records (record_id, teacher_id, activity_id, hours, comment, created_at) VALUES (11, 131898478, 23, 2.00, NULL, '2023-04-22 21:58:51.287484');
INSERT INTO public.activity_records (record_id, teacher_id, activity_id, hours, comment, created_at) VALUES (12, 131898478, 49, 5.00, 'Я работал', '2023-04-22 22:26:22.086112');
INSERT INTO public.activity_records (record_id, teacher_id, activity_id, hours, comment, created_at) VALUES (13, 131898478, 35, 2.00, NULL, '2023-04-22 22:28:02.361982');
INSERT INTO public.activity_records (record_id, teacher_id, activity_id, hours, comment, created_at) VALUES (14, 131898478, 35, -2.00, '-2', '2023-04-22 22:28:31.295092');


--
-- Data for Name: course_join_codes; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.course_join_codes (code_id, course_id, comment, activated_by_teacher_id, created_at) VALUES ('TXq54kwlZjH6', 24, 'Примечание тест', NULL, '2023-04-22 14:41:05.702463');
INSERT INTO public.course_join_codes (code_id, course_id, comment, activated_by_teacher_id, created_at) VALUES ('a82TLzWc7FMP', 24, 'Мой код!', 131898478, '2023-04-22 15:03:34.051835');
INSERT INTO public.course_join_codes (code_id, course_id, comment, activated_by_teacher_id, created_at) VALUES ('hPMe5npAcv1h', 25, 'Для Андрея 2', 131898478, '2023-04-22 22:25:49.287227');


--
-- Data for Name: courses; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.courses (course_id, name, description, created_at) VALUES (24, 'Математика 5-6', 'Математика для 5-6 классов', '2023-04-22 14:22:53.665567');
INSERT INTO public.courses (course_id, name, description, created_at) VALUES (25, 'Программирование 7-8', 'Подготовка к олимпиадам по программированию для школьников 7-8 классов', '2023-04-22 22:21:12.019603');


--
-- Data for Name: excel_reports; Type: TABLE DATA; Schema: public; Owner: postgres
--

--
-- Data for Name: lessons; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.lessons (lesson_id, date_from, topic, course_id, created_at, date_to) VALUES (26, '2023-01-10 00:00:00+00', 'Основы комбинаторики', 24, '2023-04-22 21:12:19.332979', '2023-01-17 00:00:00+00');
INSERT INTO public.lessons (lesson_id, date_from, topic, course_id, created_at, date_to) VALUES (27, '2023-01-17 00:00:00+00', 'Введение в теорию чисел', 24, '2023-04-22 21:13:06.612021', '2023-02-17 00:00:00+00');
INSERT INTO public.lessons (lesson_id, date_from, topic, course_id, created_at, date_to) VALUES (28, '2023-01-24 00:00:00+00', 'Геометрические преобразования', 24, '2023-04-22 21:14:00.572644', '2023-02-17 00:00:00+00');
INSERT INTO public.lessons (lesson_id, date_from, topic, course_id, created_at, date_to) VALUES (29, '2023-01-31 00:00:00+00', 'Решение уравнений и неравенств', 24, '2023-04-22 21:14:31.089253', '2023-02-17 00:00:00+00');
INSERT INTO public.lessons (lesson_id, date_from, topic, course_id, created_at, date_to) VALUES (30, '2023-02-07 00:00:00+00', 'Системы линейных уравнений', 24, '2023-04-22 21:15:26.508318', '2023-03-17 00:00:00+00');
INSERT INTO public.lessons (lesson_id, date_from, topic, course_id, created_at, date_to) VALUES (31, '2023-02-14 00:00:00+00', 'Основы стереометрии', 24, '2023-04-22 21:16:08.076629', '2023-03-17 00:00:00+00');
INSERT INTO public.lessons (lesson_id, date_from, topic, course_id, created_at, date_to) VALUES (32, '2023-02-21 00:00:00+00', 'Вероятность и математическая статистика', 24, '2023-04-22 21:17:06.771508', '2023-03-17 00:00:00+00');
INSERT INTO public.lessons (lesson_id, date_from, topic, course_id, created_at, date_to) VALUES (33, '2023-02-28 00:00:00+00', 'Основы тригонометрии', 24, '2023-04-22 21:18:00.579455', '2023-04-17 00:00:00+00');
INSERT INTO public.lessons (lesson_id, date_from, topic, course_id, created_at, date_to) VALUES (34, '2023-03-07 00:00:00+00', 'Математическая логика и решение задач на логику', 24, '2023-04-22 21:18:45.705509', '2023-04-17 00:00:00+00');
INSERT INTO public.lessons (lesson_id, date_from, topic, course_id, created_at, date_to) VALUES (35, '2023-03-14 00:00:00+00', 'Решение задач на движение и скорость', 24, '2023-04-22 21:19:24.3484', '2023-04-17 00:00:00+00');
INSERT INTO public.lessons (lesson_id, date_from, topic, course_id, created_at, date_to) VALUES (38, '2023-03-10 00:00:00+00', 'C++', 25, '2023-04-23 19:03:47.390449', '2023-03-15 00:00:00+00');
INSERT INTO public.lessons (lesson_id, date_from, topic, course_id, created_at, date_to) VALUES (37, '2023-03-08 00:00:00+00', 'Python', 25, '2023-04-22 22:22:26.798656', '2023-03-13 00:00:00+00');


--
-- Data for Name: teacher_courses; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.teacher_courses (teacher_id, course_id, created_at) VALUES (131898478, 24, '2023-04-22 15:03:36.704994');
INSERT INTO public.teacher_courses (teacher_id, course_id, created_at) VALUES (131898478, 25, '2023-04-22 22:26:01.572505');


--
-- Data for Name: teachers; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.teachers (comment, created_at, teacher_id, is_manager) VALUES (NULL, '2023-04-16 10:45:35.442808', 438003435, false);
INSERT INTO public.teachers (comment, created_at, teacher_id, is_manager) VALUES (NULL, '2023-04-09 21:48:37.86559', 131898478, true);


--
-- Name: activities_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.activities_id_seq', 49, true);


--
-- Name: activity_records_record_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.activity_records_record_id_seq', 14, true);


--
-- Name: courses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.courses_id_seq', 25, true);


--
-- Name: excel_reports_report_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.excel_reports_report_id_seq', 6, true);


--
-- Name: lessons_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.lessons_id_seq', 38, true);


--
-- Name: activities activities_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activities
    ADD CONSTRAINT activities_pkey PRIMARY KEY (activity_id);


--
-- Name: activity_records activity_records_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activity_records
    ADD CONSTRAINT activity_records_pkey PRIMARY KEY (record_id);


--
-- Name: course_join_codes course_join_codes_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.course_join_codes
    ADD CONSTRAINT course_join_codes_code_key UNIQUE (code_id);


--
-- Name: course_join_codes course_join_codes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.course_join_codes
    ADD CONSTRAINT course_join_codes_pkey PRIMARY KEY (code_id);


--
-- Name: courses courses_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.courses
    ADD CONSTRAINT courses_pkey PRIMARY KEY (course_id);


--
-- Name: excel_reports excel_reports_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.excel_reports
    ADD CONSTRAINT excel_reports_pkey PRIMARY KEY (report_id);


--
-- Name: lessons lessons_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.lessons
    ADD CONSTRAINT lessons_pkey PRIMARY KEY (lesson_id);


--
-- Name: teachers teachers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teachers
    ADD CONSTRAINT teachers_pkey PRIMARY KEY (teacher_id);


--
-- Name: teacher_courses unique_teacher_course; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teacher_courses
    ADD CONSTRAINT unique_teacher_course UNIQUE (teacher_id, course_id);


--
-- Name: activities activities_lesson_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activities
    ADD CONSTRAINT activities_lesson_id_fkey FOREIGN KEY (lesson_id) REFERENCES public.lessons(lesson_id);


--
-- Name: activity_records activity_records_activity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activity_records
    ADD CONSTRAINT activity_records_activity_id_fkey FOREIGN KEY (activity_id) REFERENCES public.activities(activity_id);


--
-- Name: course_join_codes course_join_codes_course_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.course_join_codes
    ADD CONSTRAINT course_join_codes_course_id_fkey FOREIGN KEY (course_id) REFERENCES public.courses(course_id);


--
-- Name: teacher_courses fk_teachers; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teacher_courses
    ADD CONSTRAINT fk_teachers FOREIGN KEY (teacher_id) REFERENCES public.teachers(teacher_id);


--
-- Name: activity_records fk_teachers; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activity_records
    ADD CONSTRAINT fk_teachers FOREIGN KEY (teacher_id) REFERENCES public.teachers(teacher_id);


--
-- Name: lessons lessons_course_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.lessons
    ADD CONSTRAINT lessons_course_id_fkey FOREIGN KEY (course_id) REFERENCES public.courses(course_id);


--
-- Name: teacher_courses teacher_courses_course_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teacher_courses
    ADD CONSTRAINT teacher_courses_course_id_fkey FOREIGN KEY (course_id) REFERENCES public.courses(course_id);


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE USAGE ON SCHEMA public FROM PUBLIC;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

